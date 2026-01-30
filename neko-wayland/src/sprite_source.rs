//! Unified sprite abstraction for neko-wayland
//!
//! Provides a common interface for different sprite types:
//! - Cairo drawing (procedural)
//! - Classic sprite sheets (grid-based PNG)
//! - VPet sprites (folder-based animations)
//!
//! Made with 💜 by Ada & Luna - Ada Research Foundation

use crate::dsl::BehaviorRuntime;
use crate::neko::Neko;
use crate::sprites;
use crate::vpet_sprites;
use std::cell::RefCell;
use std::rc::Rc;

/// Common interface for all sprite sources
pub trait SpriteSource {
    /// Get the sprite dimensions (width, height)
    fn dimensions(&self) -> (i32, i32);

    /// Draw the sprite at the current position
    /// The cairo context should already be scaled appropriately
    fn draw(&self, cr: &cairo::Context) -> Result<(), String>;

    /// Update animation state (for animated sprites)
    fn update(&mut self, _delta_ms: u32) {}
}

/// Unified sprite container that can hold any sprite type
pub enum SpriteContainer {
    /// Procedural cairo drawing (no external sprites)
    Cairo,
    /// Classic neko sprite sheet
    Classic(Rc<sprites::SpriteSheet>),
    /// VPet folder-based sprites
    VPet(Rc<RefCell<vpet_sprites::VPetSprites>>),
}

impl SpriteContainer {
    /// Get the sprite dimensions
    pub fn dimensions(&self) -> (i32, i32) {
        match self {
            SpriteContainer::Cairo => (sprites::NEKO_SPRITE_WIDTH, sprites::NEKO_SPRITE_HEIGHT),
            SpriteContainer::Classic(_) => {
                (sprites::NEKO_SPRITE_WIDTH, sprites::NEKO_SPRITE_HEIGHT)
            }
            SpriteContainer::VPet(vpet) => vpet
                .borrow()
                .sprite_dimensions()
                .unwrap_or((sprites::NEKO_SPRITE_WIDTH, sprites::NEKO_SPRITE_HEIGHT)),
        }
    }

    /// Draw using Neko state (for classic behavior)
    pub fn draw_with_neko(&self, cr: &cairo::Context, neko: &Neko) -> Result<(), String> {
        match self {
            SpriteContainer::Cairo => {
                neko.draw_with_sprites(cr, None);
                Ok(())
            }
            SpriteContainer::Classic(sheet) => {
                neko.draw_with_sprites(cr, Some(sheet.as_ref()));
                Ok(())
            }
            SpriteContainer::VPet(vpet) => {
                // Update VPet animation based on neko state
                let mut vpet_mut = vpet.borrow_mut();
                vpet_mut.set_animation_from_neko_state(neko.state);
                drop(vpet_mut); // Release borrow before drawing

                vpet.borrow().draw(cr)
            }
        }
    }

    /// Draw using DSL runtime state
    pub fn draw_with_runtime(
        &self,
        cr: &cairo::Context,
        runtime: &BehaviorRuntime,
    ) -> Result<(), String> {
        match self {
            SpriteContainer::Cairo => {
                // For now, cairo drawing is handled by ui::draw_pet
                // This is a placeholder for future sprite-based DSL rendering
                Ok(())
            }
            SpriteContainer::Classic(sheet) => {
                // Calculate movement direction
                let dx = runtime.target_x - runtime.x;
                let dy = runtime.target_y - runtime.y;

                // Map DSL state to NekoState with directional movement
                let mut neko_state = map_dsl_state_to_neko_with_direction(
                    &runtime.current_state,
                    runtime.is_moving(),
                    dx,
                    dy,
                );

                // Special case: if scratching, use directional wall scratch based on closest edge
                if runtime.current_state == "scratch" {
                    use crate::neko::NekoState;
                    neko_state = match runtime.closest_edge() {
                        "left" => NekoState::ScratchWallLeft,
                        "right" => NekoState::ScratchWallRight,
                        "up" => NekoState::ScratchWallUp,
                        "down" => NekoState::ScratchWallDown,
                        _ => NekoState::ScratchWallDown,
                    };
                }

                let (sprite_x, sprite_y) = neko_state.sprite_coords(runtime.frame);

                eprintln!("DEBUG Classic: state={}, moving={}, neko_state={:?}, coords=({},{}), pos=({:.0},{:.0})", 
                         runtime.current_state, runtime.is_moving(), neko_state, sprite_x, sprite_y, runtime.x, runtime.y);

                // Draw the sprite at (0,0) - the window is already positioned at runtime.x, runtime.y
                sheet.draw(cr, sprite_x, sprite_y, 0.0, 0.0);
                Ok(())
            }
            SpriteContainer::VPet(vpet) => {
                // Update VPet animation based on DSL state
                let mut vpet_mut = vpet.borrow_mut();
                vpet_mut.set_animation_from_dsl_state(&runtime.current_state);
                drop(vpet_mut); // Release borrow before drawing

                vpet.borrow().draw(cr)
            }
        }
    }

    /// Update animation state
    pub fn update(&mut self, delta_ms: u32) {
        if let SpriteContainer::VPet(vpet) = self {
            // VPet sprites track their own animation time
            // This is handled internally by the VPetSprites struct
            let _ = delta_ms; // Suppress unused warning for now
        }
    }
}

/// Helper to check if a sprite container is VPet
impl SpriteContainer {
    pub fn is_vpet(&self) -> bool {
        matches!(self, SpriteContainer::VPet(_))
    }

    pub fn is_classic(&self) -> bool {
        matches!(self, SpriteContainer::Classic(_))
    }

    pub fn is_cairo(&self) -> bool {
        matches!(self, SpriteContainer::Cairo)
    }
}

/// Map DSL state name to NekoState enum with directional movement
/// This allows classic sprite sheets to work with DSL behavior
fn map_dsl_state_to_neko_with_direction(
    state_name: &str,
    is_moving: bool,
    dx: f64,
    dy: f64,
) -> crate::neko::NekoState {
    use crate::neko::NekoState;
    use std::f64::consts::PI;

    // If moving, calculate direction based on movement vector
    if is_moving && (dx.abs() > 0.1 || dy.abs() > 0.1) {
        // Calculate angle in radians (-PI to PI)
        // Note: dy is negated because screen Y increases downward, but we want North to be "up"
        let angle = (-dy).atan2(dx);

        // Convert to 8 directions (0 = East, going counter-clockwise)
        // Each direction covers 45 degrees (PI/4 radians)
        let direction = ((angle + PI / 8.0) / (PI / 4.0)).floor() as i32;

        return match direction {
            -4 | 4 => NekoState::RunW, // West
            -3 => NekoState::RunSW,    // Southwest
            -2 => NekoState::RunS,     // South
            -1 => NekoState::RunSE,    // Southeast
            0 => NekoState::RunE,      // East
            1 => NekoState::RunNE,     // Northeast
            2 => NekoState::RunN,      // North
            3 => NekoState::RunNW,     // Northwest
            _ => NekoState::RunE,      // Fallback
        };
    }

    // Map state names to appropriate NekoState
    match state_name {
        "idle" | "sit" => NekoState::Sit,
        "wander" => NekoState::RunE, // Will be moving (direction calculated above)
        "chase" => NekoState::Alert, // Alert before running
        "play" | "itch" => NekoState::Itch, // Scratching ear
        "scratch" => NekoState::Itch, // Also ear scratching for now
        "wash" | "groom" => NekoState::Wash, // Licking paw
        "sleep" => NekoState::Sleep1,
        "alert" => NekoState::Alert,
        "eat" => NekoState::Wash, // Closest to eating
        "drink" => NekoState::Wash,
        _ => NekoState::Sit, // Default fallback
    }
}
