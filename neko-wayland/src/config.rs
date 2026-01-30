//! Configuration management for neko-wayland
//!
//! Supports both config files and CLI arguments.
//! CLI arguments override config file values.
//!
//! Config file location: ~/.config/neko-wayland/config.toml
//!
//! Made with 💜 by Ada & Luna - Ada Research Foundation

use serde::{Deserialize, Serialize};
use std::path::PathBuf;

/// Main configuration struct
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(default)]
pub struct Config {
    pub behavior: BehaviorConfig,
    pub sprites: SpriteConfig,
    pub window: WindowConfig,
    pub display: DisplayConfig,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(default)]
pub struct BehaviorConfig {
    /// Path to .neko DSL file
    pub algo_file: Option<String>,
    /// Use DSL runtime (vs hardcoded behavior)
    pub use_dsl: bool,
    /// Movement speed multiplier
    pub speed: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(default)]
pub struct SpriteConfig {
    /// Path to sprite sheet PNG (classic neko format)
    pub sprite_sheet: Option<String>,
    /// Path to VPet-style sprite folder
    pub vpet_folder: Option<String>,
    /// Scale factor for sprites (0.1-10.0)
    pub scale: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(default)]
pub struct WindowConfig {
    /// Enable debug visualization
    pub debug: bool,
    /// Window always on top
    pub always_on_top: bool,
    /// Use daemon for state management (thin client mode)
    pub use_daemon: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(default)]
pub struct DisplayConfig {
    /// Target monitor (0 = primary, 1 = secondary, etc.)
    pub monitor: Option<usize>,
    /// Use focused monitor
    pub use_focused: bool,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            behavior: BehaviorConfig::default(),
            sprites: SpriteConfig::default(),
            window: WindowConfig::default(),
            display: DisplayConfig::default(),
        }
    }
}

impl Default for BehaviorConfig {
    fn default() -> Self {
        Self {
            algo_file: None,
            use_dsl: false,
            speed: 1.0,
        }
    }
}

impl Default for SpriteConfig {
    fn default() -> Self {
        Self {
            sprite_sheet: None,
            vpet_folder: None,
            scale: 1.0,
        }
    }
}

impl Default for WindowConfig {
    fn default() -> Self {
        Self {
            debug: false,
            always_on_top: true,
            use_daemon: false,
        }
    }
}

impl Default for DisplayConfig {
    fn default() -> Self {
        Self {
            monitor: None,
            use_focused: true,
        }
    }
}

impl Config {
    /// Load config from file, or create default if it doesn't exist
    pub fn load() -> Result<Self, String> {
        let config_path = Self::config_path()?;

        if config_path.exists() {
            let contents = std::fs::read_to_string(&config_path)
                .map_err(|e| format!("Failed to read config file: {}", e))?;

            toml::from_str(&contents).map_err(|e| format!("Failed to parse config file: {}", e))
        } else {
            // Return default config
            Ok(Self::default())
        }
    }

    /// Save config to file
    pub fn save(&self) -> Result<(), String> {
        let config_path = Self::config_path()?;

        // Create config directory if it doesn't exist
        if let Some(parent) = config_path.parent() {
            std::fs::create_dir_all(parent)
                .map_err(|e| format!("Failed to create config directory: {}", e))?;
        }

        let contents = toml::to_string_pretty(self)
            .map_err(|e| format!("Failed to serialize config: {}", e))?;

        std::fs::write(&config_path, contents)
            .map_err(|e| format!("Failed to write config file: {}", e))?;

        Ok(())
    }

    /// Get the config file path
    pub fn config_path() -> Result<PathBuf, String> {
        let config_dir =
            dirs::config_dir().ok_or_else(|| "Could not find config directory".to_string())?;

        Ok(config_dir.join("neko-wayland").join("config.toml"))
    }

    /// Merge CLI arguments into config (CLI wins)
    pub fn merge_cli_args(&mut self, args: &[String]) {
        let mut i = 1; // Skip program name
        while i < args.len() {
            match args[i].as_str() {
                "--algo" | "-a" if i + 1 < args.len() => {
                    self.behavior.algo_file = Some(args[i + 1].clone());
                    self.behavior.use_dsl = true;
                    i += 2;
                }
                "--sprites" | "-s" if i + 1 < args.len() => {
                    self.sprites.sprite_sheet = Some(args[i + 1].clone());
                    i += 2;
                }
                "--vpet" | "-v" if i + 1 < args.len() => {
                    self.sprites.vpet_folder = Some(args[i + 1].clone());
                    i += 2;
                }
                "--scale" if i + 1 < args.len() => {
                    if let Ok(scale) = args[i + 1].parse::<f64>() {
                        if scale > 0.0 && scale <= 10.0 {
                            self.sprites.scale = scale;
                        }
                    }
                    i += 2;
                }
                "--dsl" => {
                    self.behavior.use_dsl = true;
                    i += 1;
                }
                "--daemon" => {
                    self.window.use_daemon = true;
                    i += 1;
                }
                "--debug" => {
                    self.window.debug = true;
                    i += 1;
                }
                _ => {
                    i += 1;
                }
            }
        }
    }

    /// Print help message
    pub fn print_help() {
        eprintln!(
            r#"neko-wayland - A cute desktop pet for Wayland/Hyprland

USAGE:
    neko-wayland [OPTIONS]

OPTIONS:
    -a, --algo <FILE>      Load behavior from a .neko DSL file
    -s, --sprites <FILE>   Load sprite sheet (PNG file, classic neko format)
    -v, --vpet <FOLDER>    Load VPet-style sprites from folder
    --scale <NUMBER>       Scale factor for sprites (0.1-10.0, default: 1.0)
    --dsl                  Use DSL runtime (default behavior if no file)
    --daemon               Use daemon for state management (thin client mode)
    --debug                Enable debug visualization
    -h, --help             Show this help message

CONFIG FILE:
    ~/.config/neko-wayland/config.toml

    CLI arguments override config file values.

EXAMPLES:
    neko-wayland                                    # Classic hardcoded behavior, cairo drawing
    neko-wayland --sprites classic_spritesheets/neko.png  # Use sprite sheet
    neko-wayland --vpet path/to/pet/vup             # Use VPet-style sprites
    neko-wayland --vpet path/to/pet/vup --scale 0.5 # VPet at half size
    neko-wayland --sprites neko.png --scale 2.0     # Classic neko at 2x size
    neko-wayland --dsl                              # DSL runtime with default behavior
    neko-wayland --algo lazy_cat.neko               # Custom behavior from file
    neko-wayland --daemon                           # Thin client mode (requires neko-daemon)

Made with 💜 by Ada & Luna - Ada Research Foundation
"#
        );
    }
}
