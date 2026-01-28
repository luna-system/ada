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

mod cursor;
mod display;
mod dsl;
mod neko;
mod sprites;

use neko::Neko;

const APP_ID: &str = "dev.ada.neko-wayland";
const SPRITE_SIZE: i32 = 32;
const UPDATE_INTERVAL_MS: u64 = 50; // 20 FPS

fn main() -> glib::ExitCode {
    let app = Application::builder()
        .application_id(APP_ID)
        .build();

    app.connect_activate(build_ui);
    app.run()
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
        // This is how we position the window freely on screen
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
    
    // Make window transparent
    // Note: This requires compositor support for ARGB visuals
    
    // Create drawing area
    let drawing_area = DrawingArea::new();
    drawing_area.set_content_width(SPRITE_SIZE);
    drawing_area.set_content_height(SPRITE_SIZE);

    // Neko state - use actual screen dimensions!
    let neko = Rc::new(RefCell::new({
        let mut n = Neko::new();
        n.screen_width = screen_w;
        n.screen_height = screen_h;
        eprintln!("DEBUG: Neko wander bounds set to {:.0}x{:.0}", screen_w, screen_h);
        n
    }));

    // Set up drawing with transparency
    let neko_draw = neko.clone();
    let first_draw = Rc::new(RefCell::new(true));
    let first_draw_clone = first_draw.clone();
    drawing_area.set_draw_func(move |area, cr, width, height| {
        // Log actual dimensions on first draw
        if *first_draw_clone.borrow() {
            eprintln!("DEBUG draw_func: actual size = {}x{}, content_size = {}x{}", 
                     width, height,
                     area.content_width(), area.content_height());
            *first_draw_clone.borrow_mut() = false;
        }
        let neko = neko_draw.borrow();
        neko.draw(cr);
    });

    window.set_child(Some(&drawing_area));

    // Animation/update loop
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
        
        // Update cursor position
        if let Some((cx, cy)) = cursor::get_cursor_position() {
            neko.update_cursor(cx, cy);
            // Debug cursor every 2 seconds
            if *frames % 40 == 1 {
                eprintln!("DEBUG cursor: ({:.0}, {:.0})", cx, cy);
            }
        } else if *frames % 40 == 1 {
            eprintln!("DEBUG cursor: unavailable");
        }
        
        // Update neko state
        neko.update();
        
        // Debug output every 2 seconds (40 frames at 20fps)
        if *frames % 40 == 0 {
            eprintln!("DEBUG: frame={}, pos=({:.0}, {:.0}), target=({:.0}, {:.0}), state={:?}, behavior={:?}", 
                     *frames, neko.x, neko.y, neko.target_x, neko.target_y, neko.state, neko.behavior_state);
        }
        
        // Update window position
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
    eprintln!("Press Ctrl+C to exit.");
}
