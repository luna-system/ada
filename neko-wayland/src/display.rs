//! Display/monitor detection for Wayland compositors
//!
//! Provides compositor-agnostic monitor information including:
//! - Screen dimensions
//! - Monitor offsets (for multi-monitor setups)
//! - Active/focused monitor detection
//!
//! Currently supports:
//! - Hyprland (via hyprctl)
//! - TODO: Sway (via swaymsg)
//! - TODO: wlr-randr fallback

use std::process::Command;

/// Information about a single monitor
#[derive(Debug, Clone)]
pub struct Monitor {
    pub name: String,
    pub width: u32,
    pub height: u32,
    pub x: i32, // Global X offset
    pub y: i32, // Global Y offset
    pub scale: f64,
    pub focused: bool,
}

/// Display backend trait - implement for each compositor
pub trait DisplayBackend {
    fn get_monitors(&self) -> Option<Vec<Monitor>>;
    fn get_focused_monitor(&self) -> Option<Monitor>;
    fn name(&self) -> &'static str;
}

/// Hyprland display backend
pub struct HyprlandBackend;

impl DisplayBackend for HyprlandBackend {
    fn name(&self) -> &'static str {
        "Hyprland"
    }

    fn get_monitors(&self) -> Option<Vec<Monitor>> {
        let output = Command::new("hyprctl")
            .args(["monitors", "-j"])
            .output()
            .ok()?;

        if !output.status.success() {
            return None;
        }

        let stdout = String::from_utf8_lossy(&output.stdout);
        eprintln!(
            "DEBUG display: raw hyprctl output length = {}",
            stdout.len()
        );

        parse_hyprland_monitors(&stdout)
    }

    fn get_focused_monitor(&self) -> Option<Monitor> {
        self.get_monitors()?.into_iter().find(|m| m.focused)
    }
}

/// Parse Hyprland's JSON monitor output
fn parse_hyprland_monitors(json: &str) -> Option<Vec<Monitor>> {
    let mut monitors = Vec::new();

    // Split by monitor objects (each starts with '{' after '[' or ',')
    // This is a simple parser that doesn't require serde

    let mut depth = 0;
    let mut in_string = false;
    let mut escape_next = false;
    let mut obj_start = None;

    for (i, c) in json.char_indices() {
        if escape_next {
            escape_next = false;
            continue;
        }

        match c {
            '\\' if in_string => escape_next = true,
            '"' => in_string = !in_string,
            '{' if !in_string => {
                if depth == 0 {
                    obj_start = Some(i);
                }
                depth += 1;
            }
            '}' if !in_string => {
                depth -= 1;
                if depth == 0 {
                    if let Some(start) = obj_start {
                        let obj = &json[start..=i];
                        if let Some(monitor) = parse_single_monitor(obj) {
                            monitors.push(monitor);
                        }
                    }
                    obj_start = None;
                }
            }
            _ => {}
        }
    }

    eprintln!("DEBUG display: parsed {} monitors", monitors.len());
    for m in &monitors {
        eprintln!(
            "DEBUG display:   {} {}x{} at ({}, {}) focused={}",
            m.name, m.width, m.height, m.x, m.y, m.focused
        );
    }

    if monitors.is_empty() {
        None
    } else {
        Some(monitors)
    }
}

/// Parse a single monitor JSON object
fn parse_single_monitor(obj: &str) -> Option<Monitor> {
    Some(Monitor {
        name: extract_string(obj, "name")?,
        width: extract_number(obj, "width")? as u32,
        height: extract_number(obj, "height")? as u32,
        x: extract_number(obj, "x")? as i32,
        y: extract_number(obj, "y")? as i32,
        scale: extract_number(obj, "scale").unwrap_or(1.0),
        focused: extract_bool(obj, "focused").unwrap_or(false),
    })
}

/// Extract a string value from JSON
fn extract_string(json: &str, key: &str) -> Option<String> {
    let pattern = format!("\"{}\":", key);
    let start = json.find(&pattern)? + pattern.len();
    let rest = &json[start..].trim_start();

    if !rest.starts_with('"') {
        return None;
    }

    let rest = &rest[1..]; // Skip opening quote
    let end = rest.find('"')?;
    Some(rest[..end].to_string())
}

/// Extract a number value from JSON
fn extract_number(json: &str, key: &str) -> Option<f64> {
    let pattern = format!("\"{}\":", key);
    let start = json.find(&pattern)? + pattern.len();
    let rest = &json[start..].trim_start();

    // Find end of number (including negative and decimal)
    let mut end = 0;
    for (i, c) in rest.char_indices() {
        if c.is_ascii_digit() || c == '.' || (i == 0 && c == '-') {
            end = i + c.len_utf8();
        } else if end > 0 {
            break;
        }
    }

    if end == 0 {
        return None;
    }

    rest[..end].parse().ok()
}

/// Extract a boolean value from JSON
fn extract_bool(json: &str, key: &str) -> Option<bool> {
    let pattern = format!("\"{}\":", key);
    let start = json.find(&pattern)? + pattern.len();
    let rest = &json[start..].trim_start();

    if rest.starts_with("true") {
        Some(true)
    } else if rest.starts_with("false") {
        Some(false)
    } else {
        None
    }
}

/// Auto-detect the best available display backend
pub fn detect_backend() -> Box<dyn DisplayBackend> {
    // Try Hyprland first
    if std::env::var("HYPRLAND_INSTANCE_SIGNATURE").is_ok() {
        eprintln!("DEBUG display: detected Hyprland");
        return Box::new(HyprlandBackend);
    }

    // Try running hyprctl anyway (might work)
    if Command::new("hyprctl").arg("version").output().is_ok() {
        eprintln!("DEBUG display: hyprctl available, using Hyprland backend");
        return Box::new(HyprlandBackend);
    }

    // TODO: Add Sway detection
    // if std::env::var("SWAYSOCK").is_ok() { ... }

    // Fallback to Hyprland (will fail gracefully)
    eprintln!("DEBUG display: no compositor detected, defaulting to Hyprland");
    Box::new(HyprlandBackend)
}

/// Convenience function: get focused monitor dimensions and offset
pub fn get_focused_monitor_info() -> Option<(u32, u32, i32, i32)> {
    let backend = detect_backend();
    let monitor = backend.get_focused_monitor()?;
    Some((monitor.width, monitor.height, monitor.x, monitor.y))
}
