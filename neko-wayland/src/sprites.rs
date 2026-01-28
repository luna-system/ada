//! Sprite sheet loading and management
//!
//! Classic neko sprite sheets are 32x32 pixels per frame,
//! arranged in a grid with different animations in rows.
//!
//! Made with 💜 by Ada & Luna - Ada Research Foundation

use cairo::{ImageSurface, Format};
use std::path::Path;
use crate::neko::NekoState;

/// A loaded sprite sheet
pub struct SpriteSheet {
    surface: ImageSurface,
    sprite_width: i32,
    sprite_height: i32,
    cols: i32,
    rows: i32,
}

impl SpriteSheet {
    /// Load a sprite sheet from a PNG file
    pub fn load<P: AsRef<Path>>(path: P, sprite_width: i32, sprite_height: i32) -> Result<Self, String> {
        let file = std::fs::File::open(path.as_ref())
            .map_err(|e| format!("Failed to open sprite sheet: {}", e))?;
        
        let mut reader = std::io::BufReader::new(file);
        let mut surface = ImageSurface::create_from_png(&mut reader)
            .map_err(|e| format!("Failed to load PNG: {:?}", e))?;
        
        let width = surface.width();
        let height = surface.height();
        
        let cols = width / sprite_width;
        let rows = height / sprite_height;
        
        eprintln!("Loaded sprite sheet: {}x{} pixels, {} cols x {} rows", 
                 width, height, cols, rows);
        
        // Apply color keying to make blue/cyan transparent
        // Classic neko uses cyan (#008080 or similar) as the background
        surface = Self::apply_color_key(surface)?;
        
        Ok(Self {
            surface,
            sprite_width,
            sprite_height,
            cols,
            rows,
        })
    }
    
    /// Apply color keying to make blue/cyan pixels transparent
    fn apply_color_key(mut surface: ImageSurface) -> Result<ImageSurface, String> {
        let width = surface.width();
        let height = surface.height();
        
        // Create a new surface with alpha
        let mut new_surface = ImageSurface::create(Format::ARgb32, width, height)
            .map_err(|e| format!("Failed to create surface: {:?}", e))?;
        
        // First, read all the pixel data from the source
        let pixel_data: Vec<u8> = {
            let data = surface.data()
                .map_err(|e| format!("Failed to get surface data: {:?}", e))?;
            data.to_vec()
        };
        
        // Now write to the new surface
        {
            let mut new_data = new_surface.data()
                .map_err(|e| format!("Failed to get new surface data: {:?}", e))?;
            
            // Process each pixel
            for i in (0..pixel_data.len()).step_by(4) {
                let b = pixel_data[i] as u32;
                let g = pixel_data[i + 1] as u32;
                let r = pixel_data[i + 2] as u32;
                
                // Check if this is a blue/cyan pixel (classic neko background)
                // Cyan is roughly RGB(0, 128-255, 128-255) or similar blues
                let is_blue = b > 100 && g > 100 && r < 50;
                
                if is_blue {
                    // Make it transparent
                    new_data[i] = 0;
                    new_data[i + 1] = 0;
                    new_data[i + 2] = 0;
                    new_data[i + 3] = 0;
                } else {
                    // Copy the pixel
                    new_data[i] = pixel_data[i];
                    new_data[i + 1] = pixel_data[i + 1];
                    new_data[i + 2] = pixel_data[i + 2];
                    new_data[i + 3] = pixel_data[i + 3];
                }
            }
        }
        
        Ok(new_surface)
    }

    /// Create a placeholder sprite sheet (for testing without assets)
    pub fn placeholder(sprite_width: i32, sprite_height: i32, cols: i32, rows: i32) -> Result<Self, String> {
        let width = sprite_width * cols;
        let height = sprite_height * rows;
        
        let surface = ImageSurface::create(Format::ARgb32, width, height)
            .map_err(|e| format!("Failed to create surface: {:?}", e))?;
        
        // Draw placeholder sprites
        let cr = cairo::Context::new(&surface)
            .map_err(|e| format!("Failed to create context: {:?}", e))?;
        
        for row in 0..rows {
            for col in 0..cols {
                let x = (col * sprite_width) as f64;
                let y = (row * sprite_height) as f64;
                
                // Background
                cr.set_source_rgba(0.9, 0.7, 0.5, 1.0);
                cr.rectangle(x, y, sprite_width as f64, sprite_height as f64);
                let _ = cr.fill();
                
                // Border
                cr.set_source_rgba(0.0, 0.0, 0.0, 0.3);
                cr.rectangle(x + 0.5, y + 0.5, sprite_width as f64 - 1.0, sprite_height as f64 - 1.0);
                let _ = cr.stroke();
            }
        }
        
        Ok(Self {
            surface,
            sprite_width,
            sprite_height,
            cols,
            rows,
        })
    }

    /// Draw a sprite at the given position
    pub fn draw(&self, cr: &cairo::Context, col: i32, row: i32, dest_x: f64, dest_y: f64) {
        if col >= self.cols || row >= self.rows {
            return;
        }
        
        let src_x = (col * self.sprite_width) as f64;
        let src_y = (row * self.sprite_height) as f64;
        
        cr.save().unwrap();
        
        // Set up clipping region for this sprite
        cr.rectangle(dest_x, dest_y, self.sprite_width as f64, self.sprite_height as f64);
        cr.clip();
        
        // Draw the sprite with color keying for blue background
        // Classic neko uses cyan/blue as transparent color
        cr.set_source_surface(&self.surface, dest_x - src_x, dest_y - src_y).unwrap();
        
        // Use operator to handle transparency
        // The blue pixels should already be transparent if the PNG has alpha
        // But if not, we'll need to do color keying
        let _ = cr.paint();
        
        cr.restore().unwrap();
    }
    
    /// Draw a sprite centered at the given position (for 32x32 window)
    pub fn draw_centered(&self, cr: &cairo::Context, col: i32, row: i32) {
        // Draw at 0,0 - the sprite should fill the 32x32 window exactly
        self.draw(cr, col, row, 0.0, 0.0);
    }

    /// Get sprite dimensions
    pub fn sprite_size(&self) -> (i32, i32) {
        (self.sprite_width, self.sprite_height)
    }
    
    /// Get the sprite coordinates for a neko state
    pub fn coords_for_state(&self, state: NekoState, frame: u8) -> (i32, i32) {
        state.sprite_coords(frame)
    }
}

/// Standard neko sprite sheet layout
/// 
/// Row 0: Sit(2), Yawn(2), Scratch(2), Wash(2)
/// Row 1: Alert(2), Sleep(2), [unused]
/// Row 2: RunN(2), RunNE(2), RunE(2), RunSE(2)
/// Row 3: RunS(2), RunSW(2), RunW(2), RunNW(2)
/// Row 4: [Pawprints - optional, some sprites don't have this]
pub const NEKO_SPRITE_WIDTH: i32 = 32;
pub const NEKO_SPRITE_HEIGHT: i32 = 32;
pub const NEKO_COLS: i32 = 8;
pub const NEKO_ROWS: i32 = 4;  // Minimum rows (some have 5 for pawprints)

