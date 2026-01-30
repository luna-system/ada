//! Pet behavior coordinator for neko-wayland
//!
//! Handles sprite loading, behavior initialization, and update loop coordination.
//!
//! Made with 💜 by Ada & Luna - Ada Research Foundation

use crate::config::Config;
use crate::sprite_source::SpriteContainer;
use crate::sprites;
use crate::vpet_sprites;
use std::cell::RefCell;
use std::rc::Rc;

/// Load sprites based on config and return a unified SpriteContainer
pub fn load_sprites(config: &Config) -> SpriteContainer {
    // Priority: VPet > Classic sprite sheet > Cairo
    if let Some(ref vpet_path) = config.sprites.vpet_folder {
        eprintln!("Loading VPet sprites from: {}", vpet_path);
        match vpet_sprites::VPetSprites::load_pet(vpet_path) {
            Ok(mut sprites) => {
                eprintln!("VPet sprites loaded successfully!");
                eprintln!(
                    "Available animations: {:?}",
                    sprites.animations.keys().collect::<Vec<_>>()
                );

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

                // Log sprite dimensions
                if let Some((w, h)) = sprites.sprite_dimensions() {
                    eprintln!("VPet sprite size: {}x{}", w, h);
                }

                return SpriteContainer::VPet(Rc::new(RefCell::new(sprites)));
            }
            Err(e) => {
                eprintln!("Failed to load VPet sprites: {}", e);
                eprintln!("Falling back to cairo drawing");
            }
        }
    }

    if let Some(ref sprite_path) = config.sprites.sprite_sheet {
        eprintln!("Loading sprite sheet: {}", sprite_path);
        match sprites::SpriteSheet::load(
            sprite_path,
            sprites::NEKO_SPRITE_WIDTH,
            sprites::NEKO_SPRITE_HEIGHT,
        ) {
            Ok(sheet) => {
                eprintln!("Sprite sheet loaded successfully!");
                return SpriteContainer::Classic(Rc::new(sheet));
            }
            Err(e) => {
                eprintln!("Failed to load sprite sheet: {}", e);
                eprintln!("Falling back to cairo drawing");
            }
        }
    }

    SpriteContainer::Cairo
}
