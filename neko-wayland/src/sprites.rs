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
        let surface = ImageSurface::create_from_png(&mut reader)
            .map_err(|e| format!("Failed to load PNG: {:?}", e))?;
        
        let width = surface.width();
        let height = surface.height();
        
        let cols = width / sprite_width;
        let rows = height / sprite_height;
        
        eprintln!("Loaded sprite sheet: {}x{} pixels, {} cols x {} rows", 
                 width, height, cols, rows);
        
        Ok(Self {
            surface,
            sprite_width,
            sprite_height,
            cols,
            rows,
        })
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
        cr.translate(dest_x, dest_y);
        cr.set_source_surface(&self.surface, -src_x, -src_y).unwrap();
        cr.rectangle(0.0, 0.0, self.sprite_width as f64, self.sprite_height as f64);
        cr.clip();
        let _ = cr.paint();
        cr.restore().unwrap();
    }
    
    /// Draw a sprite centered at the given position
    pub fn draw_centered(&self, cr: &cairo::Context, col: i32, row: i32) {
        // Center the sprite in a 32x32 area
        let offset_x = (32.0 - self.sprite_width as f64) / 2.0;
        let offset_y = (32.0 - self.sprite_height as f64) / 2.0;
        self.draw(cr, col, row, offset_x, offset_y);
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

