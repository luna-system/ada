//! Cursor/pointer tracking for Wayland
//!
//! On Hyprland, we use `hyprctl cursorpos` for cursor position.
//! Coordinates are adjusted for multi-monitor setups using the display module.

use std::process::Command;
use std::sync::OnceLock;

/// Cached monitor offset for coordinate correction
static MONITOR_OFFSET: OnceLock<(i32, i32)> = OnceLock::new();

/// Initialize cursor tracking with monitor offset
/// Call this once at startup after display detection
pub fn init_with_offset(x_offset: i32, y_offset: i32) {
    let _ = MONITOR_OFFSET.set((x_offset, y_offset));
    eprintln!("DEBUG cursor: using monitor offset ({}, {})", x_offset, y_offset);
}

/// Get the current cursor position (adjusted for monitor offset)
/// Returns (x, y) in monitor-local coordinates, or None if unavailable
pub fn get_cursor_position() -> Option<(f64, f64)> {
    get_hyprland_cursor()
}

/// Get cursor position via Hyprland IPC
fn get_hyprland_cursor() -> Option<(f64, f64)> {
    let output = Command::new("hyprctl")
        .arg("cursorpos")
        .output()
        .ok()?;
    
    if !output.status.success() {
        return None;
    }
    
    let stdout = String::from_utf8_lossy(&output.stdout);
    // Output format: "1234, 567" (x, y) - these are GLOBAL coordinates
    let parts: Vec<&str> = stdout.trim().split(',').collect();
    
    if parts.len() != 2 {
        eprintln!("DEBUG cursor: unexpected format: {:?}", stdout);
        return None;
    }
    
    let global_x: f64 = parts[0].trim().parse().ok()?;
    let global_y: f64 = parts[1].trim().parse().ok()?;
    
    // Adjust for monitor offset to get monitor-local coordinates
    let (offset_x, offset_y) = MONITOR_OFFSET.get().copied().unwrap_or((0, 0));
    let local_x = global_x - offset_x as f64;
    let local_y = global_y - offset_y as f64;
    
    Some((local_x, local_y))
}

/// Check if cursor tracking is available
pub fn is_available() -> bool {
    Command::new("hyprctl")
        .arg("cursorpos")
        .output()
        .map(|o| o.status.success())
        .unwrap_or(false)
}

// TODO: Add Sway cursor tracking
// fn get_sway_cursor() -> Option<(f64, f64)> {
//     // swaymsg -t get_cursor_position or similar
// }
