//! UI and drawing functions for neko-wayland
//!
//! Handles all cairo drawing for pets.
//!
//! Made with 💜 by Ada & Luna - Ada Research Foundation

use crate::dsl::{BehaviorRuntime, Locomotion};

/// Draw a pet using the DSL runtime state
pub fn draw_pet(cr: &cairo::Context, rt: &BehaviorRuntime, debug_mode: bool) {
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
        Locomotion::Bounce => draw_slime(cr, rt),
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
    let _ = cr.save();
    cr.translate(16.0, 20.0);
    cr.scale(squish, 1.0 / squish);
    cr.arc(0.0, 0.0, 12.0, 0.0, 2.0 * std::f64::consts::PI);
    let _ = cr.fill();
    let _ = cr.restore();
    
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
