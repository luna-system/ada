//! neko-wayland - A cute desktop pet for Wayland/Hyprland
//! 
//! Classic neko.exe behavior: a cat that chases your cursor around the screen!
//! Uses gtk4-layer-shell for proper Wayland overlay rendering.
//!
//! Made with 💜 by Ada & Luna - Ada Research Foundation

use gtk::prelude::*;
use gtk::{glib, Application, ApplicationWindow, DrawingArea};
use gtk4_layer_shell::{Edge, Layer, LayerShell};
use glib::timeout_add_local;
use std::cell::RefCell;
use std::rc::Rc;
use std::time::Duration;
use std::sync::OnceLock;

mod cursor;
mod display;
mod dsl;
mod neko;
mod sprites;
mod vpet_sprites;
mod config;

use neko::Neko;
use dsl::{BehaviorRuntime, default_behavior, load_behavior};

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
    
    // Check for NEKO_DEBUG environment variable
    if std::env::var("NEKO_DEBUG").is_ok() {
        config.window.debug = true;
    }
    
    // Store config globally
    CLI_CONFIG.set(config).ok();
    
    // Filter out our custom args for GTK
    let gtk_args: Vec<String> = args.iter()
        .enumerate()
        .filter(|(i, arg)| {
            !matches!(arg.as_str(), 
                "--algo" | "-a" | "--sprites" | "-s" | "--vpet" | "-v" | 
                "--scale" | "--dsl" | "--debug") &&
            (*i == 0 || !matches!(args.get(i - 1).map(|s| s.as_str()), 
                Some("--algo") | Some("-a") | Some("--sprites") | Some("-s") | 
                Some("--vpet") | Some("-v") | Some("--scale")))
        })
        .map(|(_, arg)| arg.clone())
        .collect();
    
    let app = Application::builder()
        .application_id(APP_ID)
        .build();

    app.connect_activate(build_ui);
    
    // Pass only GTK-compatible args
    app.run_with_args(&gtk_args)
}

/// Create a debug border window showing the wander bounds
fn create_debug_bounds_window(app: &Application, width: f64, height: f64) -> Option<ApplicationWindow> {
    let debug_mode = std::env::var("NEKO_DEBUG").is_ok();
    if !debug_mode {
        return None;
    }
    
    let window = ApplicationWindow::new(app);
    
    if gtk4_layer_shell::is_supported() {
        window.init_layer_shell();
        window.set_layer(Layer::Background); // Behind everything but desktop
        window.set_exclusive_zone(-1);
        window.set_keyboard_mode(gtk4_layer_shell::KeyboardMode::None);
        
        // Anchor to all edges to fill screen
        window.set_anchor(Edge::Top, true);
        window.set_anchor(Edge::Left, true);
        window.set_anchor(Edge::Bottom, true);
        window.set_anchor(Edge::Right, true);
    }
    
    window.set_decorated(false);
    
    let drawing_area = DrawingArea::new();
    let w = width;
    let h = height;
    
    drawing_area.set_draw_func(move |_area, cr, actual_w, actual_h| {
        // Clear with transparency
        cr.set_operator(cairo::Operator::Clear);
        let _ = cr.paint();
        cr.set_operator(cairo::Operator::Over);
        
        // Draw border showing wander bounds
        cr.set_source_rgba(0.0, 1.0, 1.0, 0.3); // Cyan, semi-transparent
        cr.set_line_width(5.0);
        
        // Draw the bounds we THINK we have
        cr.rectangle(50.0, 50.0, w - 100.0, h - 100.0);
        let _ = cr.stroke();
        
        // Draw the ACTUAL window size in magenta
        cr.set_source_rgba(1.0, 0.0, 1.0, 0.3);
        cr.rectangle(5.0, 5.0, actual_w as f64 - 10.0, actual_h as f64 - 10.0);
        let _ = cr.stroke();
        
        // Label
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.8);
        cr.select_font_face("monospace", cairo::FontSlant::Normal, cairo::FontWeight::Normal);
        cr.set_font_size(14.0);
        cr.move_to(60.0, 70.0);
        let _ = cr.show_text(&format!("Neko bounds: {:.0}x{:.0} | Actual: {}x{}", w, h, actual_w, actual_h));
    });
    
    window.set_child(Some(&drawing_area));
    window.present();
    
    eprintln!("DEBUG: Created bounds window (expected: {:.0}x{:.0})", width, height);
    
    Some(window)
}

fn build_ui(app: &Application) {
    // Debug: print environment info
    eprintln!("neko-wayland v0.1.0 - Ada Research Foundation");
    eprintln!("DEBUG: WAYLAND_DISPLAY = {:?}", std::env::var("WAYLAND_DISPLAY"));
    
    // Check CLI config
    let default_config = config::Config::default();
    let config = CLI_CONFIG.get().unwrap_or(&default_config);
    let use_dsl = config.behavior.use_dsl;
    
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
    
    let (screen_w, screen_h, offset_x, offset_y) = if let Some(monitor) = backend.get_focused_monitor() {
        eprintln!("DEBUG: Focused monitor: {} at ({}, {})", monitor.name, monitor.x, monitor.y);
        (monitor.width as f64, monitor.height as f64, monitor.x, monitor.y)
    } else {
        eprintln!("DEBUG: No focused monitor found, using defaults");
        (1920.0, 1080.0, 0, 0)
    };
    
    // Initialize cursor with monitor offset
    cursor::init_with_offset(offset_x, offset_y);
    
    eprintln!("DEBUG: Screen dimensions = {:.0}x{:.0}, offset = ({}, {})", 
             screen_w, screen_h, offset_x, offset_y);
    
    if !layer_shell_supported {
        eprintln!("WARNING: Layer shell not supported - running as regular window.");
    }
    
    // Create debug bounds window first (if NEKO_DEBUG is set)
    let _bounds_window = create_debug_bounds_window(app, screen_w, screen_h);

    // Create window
    let window = ApplicationWindow::new(app);
    
    // Initialize layer shell BEFORE any other window configuration
    if layer_shell_supported {
        window.init_layer_shell();
        window.set_layer(Layer::Overlay);
        window.set_exclusive_zone(-1); // Don't reserve space
        window.set_keyboard_mode(gtk4_layer_shell::KeyboardMode::None);
        
        // Anchor to top-left corner - margins will offset from there
        window.set_anchor(Edge::Top, true);
        window.set_anchor(Edge::Left, true);
        window.set_anchor(Edge::Bottom, false);
        window.set_anchor(Edge::Right, false);
        
        // Initial position
        window.set_margin(Edge::Left, 100);
        window.set_margin(Edge::Top, 100);
    }
    
    window.set_default_size(SPRITE_SIZE, SPRITE_SIZE);
    window.set_decorated(false);
    
    // Enable transparency - critical for the pet to float on desktop!
    // We need to set CSS to make the window background transparent
    let css_provider = gtk::CssProvider::new();
    css_provider.load_from_data("window { background-color: transparent; }");
    
    use gtk::prelude::WidgetExt;
    gtk::style_context_add_provider_for_display(
        &WidgetExt::display(&window),
        &css_provider,
        gtk::STYLE_PROVIDER_PRIORITY_APPLICATION,
    );
    
    // Determine sprite size based on what we're loading
    let (base_width, base_height) = if config.sprites.vpet_folder.is_some() {
        // VPet sprites are typically larger - we'll detect actual size after loading
        (SPRITE_SIZE, SPRITE_SIZE) // Placeholder, will be updated
    } else {
        // Classic neko or cairo drawing
        (SPRITE_SIZE, SPRITE_SIZE)
    };
    
    let scale = config.sprites.scale;
    let window_width = (base_width as f64 * scale) as i32;
    let window_height = (base_height as f64 * scale) as i32;
    
    // Create drawing area
    let drawing_area = DrawingArea::new();
    drawing_area.set_content_width(window_width);
    drawing_area.set_content_height(window_height);

    // Load sprite sheet if specified
    let sprite_sheet = if let Some(ref sprite_path) = config.sprites.sprite_sheet {
        eprintln!("Loading sprite sheet: {}", sprite_path);
        match sprites::SpriteSheet::load(sprite_path, sprites::NEKO_SPRITE_WIDTH, sprites::NEKO_SPRITE_HEIGHT) {
            Ok(sheet) => {
                eprintln!("Sprite sheet loaded successfully!");
                Some(Rc::new(sheet))
            }
            Err(e) => {
                eprintln!("Failed to load sprite sheet: {}", e);
                eprintln!("Falling back to cairo drawing");
                None
            }
        }
    } else {
        None
    };
    
    // Load VPet sprites if specified
    let vpet_sprites = if let Some(ref vpet_path) = config.sprites.vpet_folder {
        eprintln!("Loading VPet sprites from: {}", vpet_path);
        match vpet_sprites::VPetSprites::load_pet(vpet_path) {
            Ok(mut sprites) => {
                eprintln!("VPet sprites loaded successfully!");
                eprintln!("Available animations: {:?}", sprites.animations.keys().collect::<Vec<_>>());
                
                // Set a default animation (try first available)
                let first_anim = sprites.animations.keys().next().cloned();
                if let Some(anim_name) = first_anim {
                    if let Some(animation) = sprites.animations.get(&anim_name) {
                        if let Some(seq_name) = animation.sequence_names().first().cloned() {
                            eprintln!("Starting with animation: {} / {}", anim_name, seq_name);
                            sprites.set_animation(&anim_name, &seq_name);
                        }
                    }
                }
                
                // Get sprite dimensions and update window size
                if let Some((w, h)) = sprites.sprite_dimensions() {
                    eprintln!("VPet sprite size: {}x{}", w, h);
                    let scaled_w = (w as f64 * scale) as i32;
                    let scaled_h = (h as f64 * scale) as i32;
                    drawing_area.set_content_width(scaled_w);
                    drawing_area.set_content_height(scaled_h);
                    eprintln!("Window size set to: {}x{} (scale: {})", scaled_w, scaled_h, scale);
                }
                
                Some(Rc::new(RefCell::new(sprites)))
            }
            Err(e) => {
                eprintln!("Failed to load VPet sprites: {}", e);
                eprintln!("Falling back to cairo drawing");
                None
            }
        }
    } else {
        None
    };

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
            
            // Set sprite dimensions based on what we loaded
            if let Some(ref vpet) = vpet_sprites {
                if let Some((w, h)) = vpet.borrow().sprite_dimensions() {
                    rt.sprite_width = (w as f64 * scale).max(1.0);
                    rt.sprite_height = (h as f64 * scale).max(1.0);
                    eprintln!("DEBUG: DSL sprite size set to {:.0}x{:.0} (scaled)", rt.sprite_width, rt.sprite_height);
                }
            } else if sprite_sheet.is_some() {
                rt.sprite_width = 32.0 * scale;
                rt.sprite_height = 32.0 * scale;
                eprintln!("DEBUG: DSL sprite size set to {:.0}x{:.0} (scaled)", rt.sprite_width, rt.sprite_height);
            } else {
                rt.sprite_width = 32.0 * scale;
                rt.sprite_height = 32.0 * scale;
            }
            
            rt
        }));
        
        // Drawing for DSL runtime (reuse neko drawing for now)
        let runtime_draw = runtime.clone();
        let debug_mode = std::env::var("NEKO_DEBUG").is_ok();
        drawing_area.set_draw_func(move |_area, cr, _width, _height| {
            let rt = runtime_draw.borrow();
            draw_pet(cr, &rt, debug_mode);
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
                eprintln!("DSL: frame={}, state={}, pos=({:.0}, {:.0})", 
                         *frames, rt.current_state, rt.x, rt.y);
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
            
            // Set sprite dimensions based on what we loaded
            if let Some(ref vpet) = vpet_sprites {
                if let Some((w, h)) = vpet.borrow().sprite_dimensions() {
                    n.sprite_width = (w as f64 * scale).max(1.0);
                    n.sprite_height = (h as f64 * scale).max(1.0);
                    eprintln!("DEBUG: Neko sprite size set to {:.0}x{:.0} (scaled)", n.sprite_width, n.sprite_height);
                }
            } else if sprite_sheet.is_some() {
                // Classic sprite sheet is 32x32
                n.sprite_width = 32.0 * scale;
                n.sprite_height = 32.0 * scale;
                eprintln!("DEBUG: Neko sprite size set to {:.0}x{:.0} (scaled)", n.sprite_width, n.sprite_height);
            } else {
                // Cairo drawing is also 32x32
                n.sprite_width = 32.0 * scale;
                n.sprite_height = 32.0 * scale;
            }
            
            eprintln!("DEBUG: Neko wander bounds set to {:.0}x{:.0}", screen_w, screen_h);
            n
        }));

        let neko_draw = neko.clone();
        let sprite_draw = sprite_sheet.clone();
        let vpet_draw = vpet_sprites.clone();
        let first_draw = Rc::new(RefCell::new(true));
        let first_draw_clone = first_draw.clone();
        drawing_area.set_draw_func(move |area, cr, width, height| {
            if *first_draw_clone.borrow() {
                eprintln!("DEBUG draw_func: actual size = {}x{}, content_size = {}x{}", 
                         width, height,
                         area.content_width(), area.content_height());
                *first_draw_clone.borrow_mut() = false;
            }
            
            // Clear with transparency
            cr.set_operator(cairo::Operator::Clear);
            let _ = cr.paint();
            cr.set_operator(cairo::Operator::Over);
            
            // Priority: VPet > SpriteSheet > Cairo
            if let Some(ref vpet) = vpet_draw {
                // Scale the context
                cr.scale(scale, scale);
                
                // Draw VPet sprite
                let vpet = vpet.borrow();
                if let Err(e) = vpet.draw(cr) {
                    eprintln!("VPet draw error: {}", e);
                }
            } else if sprite_draw.is_some() {
                // Scale for sprite sheet
                cr.scale(scale, scale);
                
                let neko = neko_draw.borrow();
                neko.draw_with_sprites(cr, sprite_draw.as_ref().map(|s| s.as_ref()));
            } else {
                // Cairo drawing - scale it too!
                cr.scale(scale, scale);
                
                let neko = neko_draw.borrow();
                neko.draw_with_sprites(cr, None);
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
        eprintln!("neko-wayland started! Layer shell active: {}", window.is_layer_window());
        eprintln!("Behavior mode: {:?}", neko.borrow().behavior_mode);
    }
    
    eprintln!("Press Ctrl+C to exit.");
}

/// Draw a pet using the DSL runtime state
fn draw_pet(cr: &cairo::Context, rt: &BehaviorRuntime, debug_mode: bool) {
    // Clear with transparency
    cr.set_operator(cairo::Operator::Clear);
    let _ = cr.paint();
    cr.set_operator(cairo::Operator::Over);
    
    if debug_mode {
        // Debug outline
        cr.set_source_rgba(1.0, 0.0, 1.0, 1.0);
        cr.set_line_width(2.0);
        cr.rectangle(1.0, 1.0, 30.0, 30.0);
        let _ = cr.stroke();
        
        // State indicator
        let state_color = match rt.current_state.as_str() {
            "wander" => (0.5, 0.5, 0.5),
            "alert" => (1.0, 1.0, 0.0),
            "chase" => (1.0, 0.5, 0.0),
            "sleep" => (0.3, 0.3, 0.8),
            _ => (0.5, 0.5, 0.5),
        };
        cr.set_source_rgb(state_color.0, state_color.1, state_color.2);
        cr.arc(28.0, 4.0, 3.0, 0.0, 2.0 * std::f64::consts::PI);
        let _ = cr.fill();
    }
    
    // Draw based on locomotion type
    match rt.locomotion() {
        dsl::Locomotion::Bounce => draw_slime(cr, rt),
        _ => draw_cat_simple(cr, rt),
    }
}

/// Draw a simple cat face
fn draw_cat_simple(cr: &cairo::Context, rt: &BehaviorRuntime) {
    // Body
    cr.set_source_rgb(0.9, 0.7, 0.5);
    cr.arc(16.0, 18.0, 14.0, 0.0, 2.0 * std::f64::consts::PI);
    let _ = cr.fill();
    
    // Ears
    cr.move_to(4.0, 8.0);
    cr.line_to(8.0, 0.0);
    cr.line_to(12.0, 8.0);
    cr.close_path();
    let _ = cr.fill();
    
    cr.move_to(20.0, 8.0);
    cr.line_to(24.0, 0.0);
    cr.line_to(28.0, 8.0);
    cr.close_path();
    let _ = cr.fill();
    
    // Eyes - change based on state
    cr.set_source_rgb(0.0, 0.0, 0.0);
    match rt.current_state.as_str() {
        "sleep" => {
            cr.set_line_width(2.0);
            cr.move_to(8.0, 14.0);
            cr.line_to(12.0, 14.0);
            cr.move_to(20.0, 14.0);
            cr.line_to(24.0, 14.0);
            let _ = cr.stroke();
        }
        "alert" | "chase" => {
            cr.arc(10.0, 14.0, 4.0, 0.0, 2.0 * std::f64::consts::PI);
            let _ = cr.fill();
            cr.arc(22.0, 14.0, 4.0, 0.0, 2.0 * std::f64::consts::PI);
            let _ = cr.fill();
            cr.set_source_rgb(1.0, 1.0, 1.0);
            cr.arc(11.0, 13.0, 1.5, 0.0, 2.0 * std::f64::consts::PI);
            let _ = cr.fill();
            cr.arc(23.0, 13.0, 1.5, 0.0, 2.0 * std::f64::consts::PI);
            let _ = cr.fill();
        }
        _ => {
            cr.arc(10.0, 14.0, 3.0, 0.0, 2.0 * std::f64::consts::PI);
            let _ = cr.fill();
            cr.arc(22.0, 14.0, 3.0, 0.0, 2.0 * std::f64::consts::PI);
            let _ = cr.fill();
        }
    }
    
    // Nose
    cr.set_source_rgb(1.0, 0.6, 0.6);
    cr.move_to(16.0, 18.0);
    cr.line_to(14.0, 21.0);
    cr.line_to(18.0, 21.0);
    cr.close_path();
    let _ = cr.fill();
}

/// Draw a bouncy slime friend!
fn draw_slime(cr: &cairo::Context, rt: &BehaviorRuntime) {
    // Squish based on movement
    let squish = if rt.is_moving() {
        1.0 + (rt.frame as f64 * 0.3).sin() * 0.1
    } else {
        1.0
    };
    
    // Body - green blob
    cr.set_source_rgba(0.3, 0.9, 0.4, 0.8);
    cr.save();
    cr.translate(16.0, 20.0);
    cr.scale(squish, 1.0 / squish);
    cr.arc(0.0, 0.0, 12.0, 0.0, 2.0 * std::f64::consts::PI);
    let _ = cr.fill();
    cr.restore();
    
    // Highlight
    cr.set_source_rgba(1.0, 1.0, 1.0, 0.4);
    cr.arc(12.0, 14.0, 4.0, 0.0, 2.0 * std::f64::consts::PI);
    let _ = cr.fill();
    
    // Eyes
    cr.set_source_rgb(0.0, 0.0, 0.0);
    cr.arc(12.0, 18.0, 2.0, 0.0, 2.0 * std::f64::consts::PI);
    let _ = cr.fill();
    cr.arc(20.0, 18.0, 2.0, 0.0, 2.0 * std::f64::consts::PI);
    let _ = cr.fill();
    
    // Smile
    cr.set_line_width(1.5);
    cr.arc(16.0, 20.0, 4.0, 0.2, std::f64::consts::PI - 0.2);
    let _ = cr.stroke();
}
