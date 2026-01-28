//! VPet-style sprite loading
//!
//! VPet uses a folder-based sprite system:
//! - Individual PNG files named `frame_NNN_DDD.png` (frame number, duration in ms)
//! - Organized by: pet/animation/phase/mood/
//! - Three phases: A (start), B (loop), C (end)
//! - Multiple moods: Happy, Normal, PoorCondition, Ill
//!
//! Made with 💜 by Ada & Luna - Ada Research Foundation

use cairo::ImageSurface;
use std::path::{Path, PathBuf};
use std::collections::HashMap;

/// A single frame with its duration
#[derive(Debug, Clone)]
pub struct VPetFrame {
    pub surface: ImageSurface,
    pub duration_ms: u32,
}

/// A sequence of frames (e.g., "A_Happy", "B_Normal", "C_PoorCondition")
#[derive(Debug, Clone)]
pub struct VPetSequence {
    pub frames: Vec<VPetFrame>,
    pub total_duration_ms: u32,
}

impl VPetSequence {
    /// Get the frame at a specific time offset
    pub fn frame_at(&self, time_ms: u32) -> Option<&VPetFrame> {
        if self.frames.is_empty() {
            return None;
        }
        
        let time = time_ms % self.total_duration_ms;
        let mut accumulated = 0;
        
        for frame in &self.frames {
            accumulated += frame.duration_ms;
            if time < accumulated {
                return Some(frame);
            }
        }
        
        // Fallback to last frame
        self.frames.last()
    }
}

/// A complete VPet animation with all phases and moods
#[derive(Debug)]
pub struct VPetAnimation {
    pub name: String,
    pub sequences: HashMap<String, VPetSequence>, // e.g., "A_Happy", "B_Normal", "C_PoorCondition"
}

impl VPetAnimation {
    /// Load a VPet animation from a folder
    /// 
    /// Expected structure:
    /// ```
    /// animation_folder/
    ///   A_Happy/
    ///     frame_000_125.png
    ///     frame_001_125.png
    ///   B_Normal/
    ///     frame_000_125.png
    ///   C_Happy/
    ///     frame_000_125.png
    /// ```
    pub fn load<P: AsRef<Path>>(path: P) -> Result<Self, String> {
        let path = path.as_ref();
        let name = path.file_name()
            .and_then(|n| n.to_str())
            .unwrap_or("unknown")
            .to_string();
        
        let mut sequences = HashMap::new();
        
        // Read all subdirectories
        let entries = std::fs::read_dir(path)
            .map_err(|e| format!("Failed to read animation folder: {}", e))?;
        
        for entry in entries {
            let entry = entry.map_err(|e| format!("Failed to read entry: {}", e))?;
            let entry_path = entry.path();
            
            if !entry_path.is_dir() {
                continue;
            }
            
            let sequence_name = entry_path.file_name()
                .and_then(|n| n.to_str())
                .ok_or_else(|| "Invalid sequence name".to_string())?
                .to_string();
            
            // Load this sequence
            match Self::load_sequence(&entry_path) {
                Ok(sequence) => {
                    // Only log summary, not every frame
                    sequences.insert(sequence_name, sequence);
                }
                Err(e) => {
                    eprintln!("Warning: Failed to load sequence {}: {}", sequence_name, e);
                }
            }
        }
        
        if sequences.is_empty() {
            return Err("No valid sequences found in animation folder".to_string());
        }
        
        Ok(Self { name, sequences })
    }
    
    /// Load a single sequence (e.g., "A_Happy")
    fn load_sequence(path: &Path) -> Result<VPetSequence, String> {
        let mut frame_files: Vec<(PathBuf, u32, u32)> = Vec::new();
        
        // Read all PNG files
        let entries = std::fs::read_dir(path)
            .map_err(|e| format!("Failed to read sequence folder: {}", e))?;
        
        for entry in entries {
            let entry = entry.map_err(|e| format!("Failed to read entry: {}", e))?;
            let entry_path = entry.path();
            
            if entry_path.extension().and_then(|e| e.to_str()) != Some("png") {
                continue;
            }
            
            // Parse filename: frame_NNN_DDD.png or 中文名_NNN_DDD.png
            let filename = entry_path.file_stem()
                .and_then(|n| n.to_str())
                .ok_or_else(|| "Invalid filename".to_string())?;
            
            // Split by underscore and get last two parts (frame number and duration)
            let parts: Vec<&str> = filename.rsplitn(3, '_').collect();
            if parts.len() < 2 {
                eprintln!("Warning: Skipping file with unexpected name format: {}", filename);
                continue;
            }
            
            let duration_str = parts[0]; // Last part (rightmost)
            let frame_str = parts[1];    // Second to last
            
            let frame_num: u32 = frame_str.parse()
                .map_err(|_| format!("Invalid frame number in filename: {}", filename))?;
            let duration: u32 = duration_str.parse()
                .map_err(|_| format!("Invalid duration in filename: {}", filename))?;
            
            frame_files.push((entry_path, frame_num, duration));
        }
        
        if frame_files.is_empty() {
            return Err("No valid frame files found".to_string());
        }
        
        // Sort by frame number
        frame_files.sort_by_key(|(_, num, _)| *num);
        
        // Load frames
        let mut frames = Vec::new();
        let mut total_duration = 0;
        
        for (path, _num, duration) in frame_files {
            let file = std::fs::File::open(&path)
                .map_err(|e| format!("Failed to open frame: {}", e))?;
            let mut reader = std::io::BufReader::new(file);
            let surface = ImageSurface::create_from_png(&mut reader)
                .map_err(|e| format!("Failed to load PNG: {:?}", e))?;
            
            frames.push(VPetFrame {
                surface,
                duration_ms: duration,
            });
            total_duration += duration;
        }
        
        Ok(VPetSequence {
            frames,
            total_duration_ms: total_duration,
        })
    }
    
    /// Get a sequence by name (e.g., "A_Happy", "B_Normal")
    pub fn get_sequence(&self, name: &str) -> Option<&VPetSequence> {
        self.sequences.get(name)
    }
    
    /// Get available sequence names
    pub fn sequence_names(&self) -> Vec<String> {
        self.sequences.keys().cloned().collect()
    }
}

/// VPet sprite collection - manages multiple animations
pub struct VPetSprites {
    pub animations: HashMap<String, VPetAnimation>,
    pub current_animation: Option<String>,
    pub current_sequence: Option<String>,
    pub animation_start_time: std::time::Instant,
}

impl VPetSprites {
    /// Create a new empty sprite collection
    pub fn new() -> Self {
        Self {
            animations: HashMap::new(),
            current_animation: None,
            current_sequence: None,
            animation_start_time: std::time::Instant::now(),
        }
    }
    
    /// Load all animations from a pet folder
    /// 
    /// Expected structure:
    /// ```
    /// pet_folder/
    ///   IDEL/
    ///     Squat/
    ///       A_Happy/...
    ///   MOVE/
    ///     ...
    /// ```
    pub fn load_pet<P: AsRef<Path>>(path: P) -> Result<Self, String> {
        let path = path.as_ref();
        let mut sprites = Self::new();
        
        // Read all animation categories (IDEL, MOVE, etc.)
        let entries = std::fs::read_dir(path)
            .map_err(|e| format!("Failed to read pet folder: {}", e))?;
        
        for entry in entries {
            let entry = entry.map_err(|e| format!("Failed to read entry: {}", e))?;
            let category_path = entry.path();
            
            if !category_path.is_dir() {
                continue;
            }
            
            let category_name = category_path.file_name()
                .and_then(|n| n.to_str())
                .unwrap_or("unknown");
            
            // Read all animations in this category
            let anim_entries = std::fs::read_dir(&category_path)
                .map_err(|e| format!("Failed to read category folder: {}", e))?;
            
            for anim_entry in anim_entries {
                let anim_entry = anim_entry.map_err(|e| format!("Failed to read entry: {}", e))?;
                let anim_path = anim_entry.path();
                
                if !anim_path.is_dir() {
                    continue;
                }
                
                let anim_name = anim_path.file_name()
                    .and_then(|n| n.to_str())
                    .unwrap_or("unknown");
                
                let full_name = format!("{}_{}", category_name, anim_name);
                
                match VPetAnimation::load(&anim_path) {
                    Ok(animation) => {
                        sprites.animations.insert(full_name, animation);
                    }
                    Err(e) => {
                        eprintln!("Warning: Failed to load animation {}: {}", full_name, e);
                    }
                }
            }
        }
        
        if sprites.animations.is_empty() {
            return Err("No valid animations found in pet folder".to_string());
        }
        
        // Log summary instead of every frame
        eprintln!("VPet loaded: {} animations with {} total sequences", 
                 sprites.animations.len(),
                 sprites.animations.values().map(|a| a.sequences.len()).sum::<usize>());
        
        Ok(sprites)
    }
    
    /// Set the current animation and sequence
    pub fn set_animation(&mut self, animation: &str, sequence: &str) {
        self.current_animation = Some(animation.to_string());
        self.current_sequence = Some(sequence.to_string());
        self.animation_start_time = std::time::Instant::now();
    }
    /// Map a DSL state name to an appropriate VPet animation
    /// Returns (animation_name, sequence_name) if a mapping exists
    pub fn map_dsl_state(&self, state_name: &str) -> Option<(String, String)> {
        // Map DSL state names to VPet animations
        match state_name {
            // Idle/sitting states
            "idle" | "sit" => {
                for (anim_name, animation) in &self.animations {
                    if anim_name.starts_with("IDEL_") {
                        if let Some(_) = animation.get_sequence("B_Normal") {
                            return Some((anim_name.clone(), "B_Normal".to_string()));
                        }
                    }
                }
            }
            
            // Movement states
            "wander" | "chase" | "run" => {
                for (anim_name, animation) in &self.animations {
                    if anim_name.starts_with("MOVE_") {
                        if let Some(_) = animation.get_sequence("B_Normal") {
                            return Some((anim_name.clone(), "B_Normal".to_string()));
                        }
                    }
                }
            }
            
            // Play state - look for play animations
            "play" => {
                for (anim_name, animation) in &self.animations {
                    if anim_name.to_lowercase().contains("play") {
                        if let Some(seq_name) = animation.sequence_names().first() {
                            return Some((anim_name.clone(), seq_name.clone()));
                        }
                    }
                }
                // Fall back to happy idle
                for (anim_name, animation) in &self.animations {
                    if anim_name.starts_with("IDEL_") {
                        if let Some(_) = animation.get_sequence("A_Happy") {
                            return Some((anim_name.clone(), "A_Happy".to_string()));
                        }
                    }
                }
            }
            
            // Sleep state
            "sleep" => {
                for (anim_name, animation) in &self.animations {
                    if anim_name.to_lowercase().contains("sleep") {
                        if let Some(seq_name) = animation.sequence_names().first() {
                            return Some((anim_name.clone(), seq_name.clone()));
                        }
                    }
                }
            }
            
            // Alert state
            "alert" => {
                for (anim_name, animation) in &self.animations {
                    if anim_name.starts_with("IDEL_") {
                        if let Some(_) = animation.get_sequence("A_Happy") {
                            return Some((anim_name.clone(), "A_Happy".to_string()));
                        }
                    }
                }
            }
            
            // Eating/drinking
            "eat" => {
                for (anim_name, animation) in &self.animations {
                    if anim_name.to_lowercase().contains("eat") {
                        if let Some(seq_name) = animation.sequence_names().first() {
                            return Some((anim_name.clone(), seq_name.clone()));
                        }
                    }
                }
            }
            
            "drink" => {
                for (anim_name, animation) in &self.animations {
                    if anim_name.to_lowercase().contains("drink") {
                        if let Some(seq_name) = animation.sequence_names().first() {
                            return Some((anim_name.clone(), seq_name.clone()));
                        }
                    }
                }
            }
            
            _ => {}
        }
        
        // Default fallback: idle animation
        for (anim_name, animation) in &self.animations {
            if anim_name.starts_with("IDEL_") {
                if let Some(_) = animation.get_sequence("B_Normal") {
                    return Some((anim_name.clone(), "B_Normal".to_string()));
                }
            }
        }
        
        None
    }
    
    /// Set animation based on DSL state name
    pub fn set_animation_from_dsl_state(&mut self, state_name: &str) {
        if let Some((anim, seq)) = self.map_dsl_state(state_name) {
            self.set_animation(&anim, &seq);
        }
    }
    
    /// Map a neko state to an appropriate VPet animation
    /// Returns (animation_name, sequence_name) if a mapping exists
    pub fn map_neko_state(&self, state: crate::neko::NekoState) -> Option<(String, String)> {
        use crate::neko::NekoState;
        
        // Try to find appropriate animations based on neko state
        match state {
            // Idle states - look for IDEL (idle) animations
            NekoState::Sit | NekoState::Yawn | NekoState::Scratch | NekoState::Wash => {
                // Try to find any IDEL animation
                for (anim_name, animation) in &self.animations {
                    if anim_name.starts_with("IDEL_") {
                        // Prefer B_Normal for looping idle
                        if let Some(_) = animation.get_sequence("B_Normal") {
                            return Some((anim_name.clone(), "B_Normal".to_string()));
                        }
                        // Fall back to first available sequence
                        if let Some(seq_name) = animation.sequence_names().first() {
                            return Some((anim_name.clone(), seq_name.clone()));
                        }
                    }
                }
            }
            
            // Alert state - look for alert or idle animations
            NekoState::Alert => {
                // Try IDEL animations with A_Happy (alert/excited)
                for (anim_name, animation) in &self.animations {
                    if anim_name.starts_with("IDEL_") {
                        if let Some(_) = animation.get_sequence("A_Happy") {
                            return Some((anim_name.clone(), "A_Happy".to_string()));
                        }
                    }
                }
            }
            
            // Running states - look for MOVE animations
            NekoState::RunN | NekoState::RunNE | NekoState::RunE | NekoState::RunSE |
            NekoState::RunS | NekoState::RunSW | NekoState::RunW | NekoState::RunNW => {
                // Try to find any MOVE animation
                for (anim_name, animation) in &self.animations {
                    if anim_name.starts_with("MOVE_") {
                        // Prefer B_Normal for looping movement
                        if let Some(_) = animation.get_sequence("B_Normal") {
                            return Some((anim_name.clone(), "B_Normal".to_string()));
                        }
                        // Fall back to first available sequence
                        if let Some(seq_name) = animation.sequence_names().first() {
                            return Some((anim_name.clone(), seq_name.clone()));
                        }
                    }
                }
            }
            
            // Sleep states - look for sleep animations
            NekoState::Sleep1 | NekoState::Sleep2 => {
                // Try to find sleep animation
                for (anim_name, animation) in &self.animations {
                    if anim_name.to_lowercase().contains("sleep") {
                        if let Some(seq_name) = animation.sequence_names().first() {
                            return Some((anim_name.clone(), seq_name.clone()));
                        }
                    }
                }
                // Fall back to idle
                for (anim_name, animation) in &self.animations {
                    if anim_name.starts_with("IDEL_") {
                        if let Some(seq_name) = animation.sequence_names().first() {
                            return Some((anim_name.clone(), seq_name.clone()));
                        }
                    }
                }
            }
        }
        
        None
    }
    
    /// Set animation based on neko state
    pub fn set_animation_from_neko_state(&mut self, state: crate::neko::NekoState) {
        if let Some((anim, seq)) = self.map_neko_state(state) {
            self.set_animation(&anim, &seq);
        }
    }
    
    /// Get the current frame to draw
    pub fn current_frame(&self) -> Option<&ImageSurface> {
        let anim_name = self.current_animation.as_ref()?;
        let seq_name = self.current_sequence.as_ref()?;
        
        let animation = self.animations.get(anim_name)?;
        let sequence = animation.get_sequence(seq_name)?;
        
        let elapsed_ms = self.animation_start_time.elapsed().as_millis() as u32;
        let frame = sequence.frame_at(elapsed_ms)?;
        
        Some(&frame.surface)
    }
    
    /// Get the dimensions of the current frame (or first available frame)
    pub fn sprite_dimensions(&self) -> Option<(i32, i32)> {
        // Try current frame first
        if let Some(surface) = self.current_frame() {
            return Some((surface.width(), surface.height()));
        }
        
        // Fall back to first available frame
        for animation in self.animations.values() {
            for sequence in animation.sequences.values() {
                if let Some(frame) = sequence.frames.first() {
                    return Some((frame.surface.width(), frame.surface.height()));
                }
            }
        }
        
        None
    }
    
    /// Draw the current frame (not centered, at actual size)
    pub fn draw(&self, cr: &cairo::Context) -> Result<(), String> {
        let surface = self.current_frame()
            .ok_or_else(|| "No current frame".to_string())?;
        
        cr.set_source_surface(surface, 0.0, 0.0)
            .map_err(|e| format!("Failed to set source: {:?}", e))?;
        cr.paint()
            .map_err(|e| format!("Failed to paint: {:?}", e))?;
        
        Ok(())
    }
    
    /// Draw the current frame centered in a specific window size
    pub fn draw_centered(&self, cr: &cairo::Context, window_width: i32, window_height: i32) -> Result<(), String> {
        let surface = self.current_frame()
            .ok_or_else(|| "No current frame".to_string())?;
        
        let width = surface.width() as f64;
        let height = surface.height() as f64;
        
        // Center in window
        let x = (window_width as f64 - width) / 2.0;
        let y = (window_height as f64 - height) / 2.0;
        
        cr.set_source_surface(surface, x, y)
            .map_err(|e| format!("Failed to set source: {:?}", e))?;
        cr.paint()
            .map_err(|e| format!("Failed to paint: {:?}", e))?;
        
        Ok(())
    }
}

impl Default for VPetSprites {
    fn default() -> Self {
        Self::new()
    }
}
