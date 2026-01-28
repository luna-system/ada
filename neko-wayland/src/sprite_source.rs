//! Unified sprite abstraction for neko-wayland
//!
//! Provides a common interface for different sprite types:
//! - Cairo drawing (procedural)
//! - Classic sprite sheets (grid-based PNG)
//! - VPet sprites (folder-based animations)
//!
//! Made with 💜 by Ada & Luna - Ada Research Foundation

use std::cell::RefCell;
use std::rc::Rc;
use crate::sprites;
use crate::vpet_sprites;
use crate::neko::Neko;
use crate::dsl::BehaviorRuntime;

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
            SpriteContainer::Classic(_) => (sprites::NEKO_SPRITE_WIDTH, sprites::NEKO_SPRITE_HEIGHT),
            SpriteContainer::VPet(vpet) => {
                vpet.borrow()
                    .sprite_dimensions()
                    .unwrap_or((sprites::NEKO_SPRITE_WIDTH, sprites::NEKO_SPRITE_HEIGHT))
            }
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
    pub fn draw_with_runtime(&self, cr: &cairo::Context, _runtime: &BehaviorRuntime) -> Result<(), String> {
        match self {
            SpriteContainer::Cairo => {
                // For now, cairo drawing is handled by ui::draw_pet
                // This is a placeholder for future sprite-based DSL rendering
                Ok(())
            }
            SpriteContainer::Classic(_sheet) => {
                // Future: map DSL states to sprite sheet frames
                Ok(())
            }
            SpriteContainer::VPet(vpet) => {
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
