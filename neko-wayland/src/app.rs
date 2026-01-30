//! Application setup and window management for neko-wayland
//!
//! Handles GTK application initialization, layer-shell configuration,
//! and window creation.
//!
//! Made with 💜 by Ada & Luna - Ada Research Foundation

use gtk::prelude::*;
use gtk::{Application, ApplicationWindow, DrawingArea};
use gtk4_layer_shell::{Edge, Layer, LayerShell};

/// Create the main pet window with layer-shell configuration
pub fn create_pet_window(
    app: &Application,
    layer_shell_supported: bool,
    window_width: i32,
    window_height: i32,
) -> ApplicationWindow {
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

    window.set_default_size(window_width, window_height);
    window.set_decorated(false);

    // Enable transparency - critical for the pet to float on desktop!
    setup_transparency(&window);

    window
}

/// Setup window transparency using CSS
pub fn setup_transparency(window: &ApplicationWindow) {
    let css_provider = gtk::CssProvider::new();
    css_provider.load_from_data("window { background-color: transparent; }");

    use gtk::prelude::WidgetExt;
    gtk::style_context_add_provider_for_display(
        &WidgetExt::display(window),
        &css_provider,
        gtk::STYLE_PROVIDER_PRIORITY_APPLICATION,
    );
}

/// Create a debug border window showing the wander bounds
pub fn create_debug_bounds_window(
    app: &Application,
    width: f64,
    height: f64,
) -> Option<ApplicationWindow> {
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
        cr.select_font_face(
            "monospace",
            cairo::FontSlant::Normal,
            cairo::FontWeight::Normal,
        );
        cr.set_font_size(14.0);
        cr.move_to(60.0, 70.0);
        let _ = cr.show_text(&format!(
            "Neko bounds: {:.0}x{:.0} | Actual: {}x{}",
            w, h, actual_w, actual_h
        ));
    });

    window.set_child(Some(&drawing_area));
    window.present();

    eprintln!(
        "DEBUG: Created bounds window (expected: {:.0}x{:.0})",
        width, height
    );

    Some(window)
}
