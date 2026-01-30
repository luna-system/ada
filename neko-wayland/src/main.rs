//! neko-wayland - A cute desktop pet for Wayland/Hyprland
//!
//! Classic neko.exe behavior: a cat that chases your cursor around the screen!
//! Uses gtk4-layer-shell for proper Wayland overlay rendering.
//!
//! Made with 💜 by Ada & Luna - Ada Research Foundation

use glib::timeout_add_local;
use gtk::prelude::*;
use gtk::{glib, Application, DrawingArea};
use gtk4_layer_shell::{Edge, LayerShell};
use std::cell::RefCell;
use std::rc::Rc;
use std::sync::OnceLock;
use std::time::Duration;

mod app;
mod config;
mod cursor;
mod daemon_client;
mod display;
mod dsl;
mod neko;
mod pet;
mod sprite_source;
mod sprites;
mod ui;
mod vpet_sprites;

use dsl::{default_behavior, load_behavior};
use neko::Neko;

const APP_ID: &str = "dev.ada.neko-wayland";
const SPRITE_SIZE: i32 = 32;
const UPDATE_INTERVAL_MS: u64 = 50; // 20 FPS

/// Global config
static CLI_CONFIG: OnceLock<config::Config> = OnceLock::new();

fn main() -> glib::ExitCode {
    // Load config from file
    let mut config = config::Config::load().unwrap_or_else(|e| {
        eprintln!("Warning: Could not load config file: {}", e);
        eprintln!("Using default configuration");
        config::Config::default()
    });

    // Parse CLI args and merge (CLI wins)
    let args: Vec<String> = std::env::args().collect();

    // Check for help flag first
    if args.iter().any(|arg| arg == "--help" || arg == "-h") {
        config::Config::print_help();
        std::process::exit(0);
    }

    config.merge_cli_args(&args);

    let debug = config.window.debug;

    // Store config globally
    CLI_CONFIG.set(config).ok();

    // Filter out our custom args for GTK
    let gtk_args: Vec<String> = args
        .iter()
        .enumerate()
        .filter(|(i, arg)| {
            !matches!(
                arg.as_str(),
                "--algo"
                    | "-a"
                    | "--sprites"
                    | "-s"
                    | "--vpet"
                    | "-v"
                    | "--scale"
                    | "--dsl"
                    | "--debug"
            ) && (*i == 0
                || !matches!(
                    args.get(i - 1).map(|s| s.as_str()),
                    Some("--algo")
                        | Some("-a")
                        | Some("--sprites")
                        | Some("-s")
                        | Some("--vpet")
                        | Some("-v")
                        | Some("--scale")
                ))
        })
        .map(|(_, arg)| arg.clone())
        .collect();

    let app = Application::builder().application_id(APP_ID).build();

    app.connect_activate(build_ui);

    // Pass only GTK-compatible args
    app.run_with_args(&gtk_args)
}

fn build_ui(app: &Application) {
    // Check CLI config
    let default_config = config::Config::default();
    let config = CLI_CONFIG.get().unwrap_or(&default_config);
    let use_dsl = config.behavior.use_dsl;
    let debug = config.window.debug;

    // Debug: print environment info
    if debug {
        eprintln!("neko-wayland v0.1.0 - Ada Research Foundation");
        eprintln!(
            "DEBUG: WAYLAND_DISPLAY = {:?}",
            std::env::var("WAYLAND_DISPLAY")
        );
    }

    if use_dsl {
        if let Some(ref file) = config.behavior.algo_file {
            eprintln!("DSL: Loading behavior from {}", file);
        } else {
            eprintln!("DSL: Using default classic_neko behavior");
        }
    }

    // Check if layer shell is supported
    let layer_shell_supported = gtk4_layer_shell::is_supported();
    eprintln!("DEBUG: Layer shell supported = {}", layer_shell_supported);

    // Check cursor tracking
    let cursor_available = cursor::is_available();
    eprintln!("DEBUG: Cursor tracking available = {}", cursor_available);

    // Get display info using the new modular backend
    let backend = display::detect_backend();
    eprintln!("DEBUG: Using display backend: {}", backend.name());

    let (screen_w, screen_h, offset_x, offset_y) =
        if let Some(monitor) = backend.get_focused_monitor() {
            eprintln!(
                "DEBUG: Focused monitor: {} at ({}, {})",
                monitor.name, monitor.x, monitor.y
            );
            (
                monitor.width as f64,
                monitor.height as f64,
                monitor.x,
                monitor.y,
            )
        } else {
            eprintln!("DEBUG: No focused monitor found, using defaults");
            (1920.0, 1080.0, 0, 0)
        };

    // Initialize cursor with monitor offset
    cursor::init_with_offset(offset_x, offset_y);

    eprintln!(
        "DEBUG: Screen dimensions = {:.0}x{:.0}, offset = ({}, {})",
        screen_w, screen_h, offset_x, offset_y
    );

    if !layer_shell_supported {
        eprintln!("WARNING: Layer shell not supported - running as regular window.");
    }

    // Create debug bounds window first (if NEKO_DEBUG is set)
    let _bounds_window = app::create_debug_bounds_window(app, screen_w, screen_h);

    // Load sprites using the unified sprite container
    let sprite_container = pet::load_sprites(config);

    // Determine window size based on loaded sprites
    let scale = config.sprites.scale;
    let (base_w, base_h) = sprite_container.dimensions();
    let window_width = (base_w as f64 * scale) as i32;
    let window_height = (base_h as f64 * scale) as i32;
    eprintln!(
        "Window size set to: {}x{} (scale: {})",
        window_width, window_height, scale
    );

    // Create window using app module
    let window = app::create_pet_window(app, layer_shell_supported, window_width, window_height);

    // Create drawing area
    let drawing_area = DrawingArea::new();
    drawing_area.set_content_width(window_width);
    drawing_area.set_content_height(window_height);

    // Choose runtime based on CLI config
    if use_dsl {
        // DSL-driven behavior
        let runtime = Rc::new(RefCell::new({
            let mut rt = if let Some(ref file) = config.behavior.algo_file {
                match load_behavior(file) {
                    Ok(rt) => rt,
                    Err(e) => {
                        eprintln!("Error loading {}: {}", file, e);
                        eprintln!("Falling back to default behavior");
                        default_behavior()
                    }
                }
            } else {
                default_behavior()
            };
            rt.screen_width = screen_w;
            rt.screen_height = screen_h;

            // Set sprite dimensions from container
            let (w, h) = sprite_container.dimensions();
            rt.sprite_width = (w as f64 * scale).max(1.0);
            rt.sprite_height = (h as f64 * scale).max(1.0);
            eprintln!(
                "DEBUG: DSL sprite size set to {:.0}x{:.0} (scaled)",
                rt.sprite_width, rt.sprite_height
            );

            // Classic neko sprites have fewer frames, so slow down animation
            // VPet has many frames per animation, classic neko only has 2
            if sprite_container.is_classic() {
                rt.frame_interval = 10; // 500ms between frames for classic neko
                eprintln!("DEBUG: Classic sprite detected, frame_interval set to 10 (500ms)");
            }

            rt
        }));

        // Drawing for DSL runtime - use sprite container!
        let runtime_draw = runtime.clone();
        let sprite_container_draw = Rc::new(sprite_container);
        let debug_mode = config.window.debug;
        drawing_area.set_draw_func(move |_area, cr, _width, _height| {
            // Clear with transparency
            cr.set_operator(cairo::Operator::Clear);
            let _ = cr.paint();
            cr.set_operator(cairo::Operator::Over);

            // Scale the context
            cr.scale(scale, scale);

            let rt = runtime_draw.borrow();

            // Draw debug info if enabled
            if debug_mode {
                ui::draw_pet(cr, &rt, debug_mode);
            } else {
                // Use sprite container with DSL runtime state
                if let Err(e) = sprite_container_draw.draw_with_runtime(cr, &rt) {
                    eprintln!("Sprite draw error: {}", e);
                    // Fall back to cairo drawing
                    ui::draw_pet(cr, &rt, false);
                }
            }
        });

        window.set_child(Some(&drawing_area));

        // Animation loop for DSL runtime
        let runtime_update = runtime.clone();
        let drawing_area_update = drawing_area.clone();
        let window_update = window.clone();
        let use_layer_shell = layer_shell_supported;
        let frame_counter = Rc::new(RefCell::new(0u32));

        timeout_add_local(Duration::from_millis(UPDATE_INTERVAL_MS), move || {
            let mut rt = runtime_update.borrow_mut();
            let mut frames = frame_counter.borrow_mut();
            *frames += 1;

            // Update cursor
            if let Some((cx, cy)) = cursor::get_cursor_position() {
                rt.update_cursor(cx, cy);
            }

            // Update behavior
            rt.update();

            // Debug every 2 seconds
            if *frames % 40 == 0 {
                eprintln!(
                    "DSL: frame={}, state={}, pos=({:.0}, {:.0})",
                    *frames, rt.current_state, rt.x, rt.y
                );
            }

            // Update window position
            if use_layer_shell {
                window_update.set_margin(Edge::Left, rt.x as i32);
                window_update.set_margin(Edge::Top, rt.y as i32);
            }

            drawing_area_update.queue_draw();
            glib::ControlFlow::Continue
        });

        window.present();
        eprintln!("neko-wayland started with DSL runtime!");
    } else {
        // Classic hardcoded behavior
        let neko = Rc::new(RefCell::new({
            let mut n = Neko::new();
            n.screen_width = screen_w;
            n.screen_height = screen_h;

            // Set sprite dimensions from container
            let (w, h) = sprite_container.dimensions();
            n.sprite_width = (w as f64 * scale).max(1.0);
            n.sprite_height = (h as f64 * scale).max(1.0);
            eprintln!(
                "DEBUG: Neko sprite size set to {:.0}x{:.0} (scaled)",
                n.sprite_width, n.sprite_height
            );
            eprintln!(
                "DEBUG: Neko wander bounds set to {:.0}x{:.0}",
                screen_w, screen_h
            );
            n
        }));

        let neko_draw = neko.clone();
        let sprite_container_draw = Rc::new(sprite_container);
        let first_draw = Rc::new(RefCell::new(true));
        let first_draw_clone = first_draw.clone();
        drawing_area.set_draw_func(move |area, cr, width, height| {
            if *first_draw_clone.borrow() {
                eprintln!(
                    "DEBUG draw_func: actual size = {}x{}, content_size = {}x{}",
                    width,
                    height,
                    area.content_width(),
                    area.content_height()
                );
                *first_draw_clone.borrow_mut() = false;
            }

            // Clear with transparency
            cr.set_operator(cairo::Operator::Clear);
            let _ = cr.paint();
            cr.set_operator(cairo::Operator::Over);

            // Scale the context
            cr.scale(scale, scale);

            // Draw using the unified sprite container
            let neko = neko_draw.borrow();
            if let Err(e) = sprite_container_draw.draw_with_neko(cr, &neko) {
                eprintln!("Draw error: {}", e);
            }
        });

        window.set_child(Some(&drawing_area));

        let neko_update = neko.clone();
        let drawing_area_update = drawing_area.clone();
        let window_update = window.clone();
        let use_layer_shell = layer_shell_supported;
        let frame_counter = Rc::new(RefCell::new(0u32));
        let frame_counter_clone = frame_counter.clone();

        timeout_add_local(Duration::from_millis(UPDATE_INTERVAL_MS), move || {
            let mut neko = neko_update.borrow_mut();
            let mut frames = frame_counter_clone.borrow_mut();
            *frames += 1;

            if let Some((cx, cy)) = cursor::get_cursor_position() {
                neko.update_cursor(cx, cy);
                if *frames % 40 == 1 {
                    eprintln!("DEBUG cursor: ({:.0}, {:.0})", cx, cy);
                }
            } else if *frames % 40 == 1 {
                eprintln!("DEBUG cursor: unavailable");
            }

            neko.update();

            if *frames % 40 == 0 {
                eprintln!("DEBUG: frame={}, pos=({:.0}, {:.0}), target=({:.0}, {:.0}), state={:?}, behavior={:?}", 
                         *frames, neko.x, neko.y, neko.target_x, neko.target_y, neko.state, neko.behavior_state);
            }

            if use_layer_shell {
                window_update.set_margin(Edge::Left, neko.x as i32);
                window_update.set_margin(Edge::Top, neko.y as i32);
            }

            drawing_area_update.queue_draw();
            glib::ControlFlow::Continue
        });

        window.present();
        eprintln!(
            "neko-wayland started! Layer shell active: {}",
            window.is_layer_window()
        );
        eprintln!("Behavior mode: {:?}", neko.borrow().behavior_mode);
    }

    eprintln!("Press Ctrl+C to exit.");
}
