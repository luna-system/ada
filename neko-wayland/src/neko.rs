//! Neko state machine and behavior
//!
//! Classic neko behavior with modern twists:
//! - Chase: Follow the cursor
//! - Wander: Random exploration
//! - Mixed: Alternate between chasing and wandering

use rand::Rng;

/// Behavior mode for the neko
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum BehaviorMode {
    /// Always chase the cursor
    Chase,
    /// Wander randomly, ignore cursor
    Wander,
    /// Mix of both - wander, notice cursor, chase, lose interest
    Mixed,
}

/// High-level behavior state for Mixed mode
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum BehaviorState {
    /// Wandering around randomly
    Wandering,
    /// Noticed the cursor, alert!
    Alerted,
    /// Actively chasing the cursor
    Chasing,
    /// Lost interest, transitioning back to wander
    LosingInterest,
}

/// Neko animation states
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum NekoState {
    // Idle states
    Sit,
    Yawn,
    Scratch,
    Wash,
    
    // Alert state
    Alert,
    
    // Running states (8 directions)
    RunN,
    RunNE,
    RunE,
    RunSE,
    RunS,
    RunSW,
    RunW,
    RunNW,
    
    // Sleeping states
    Sleep1,
    Sleep2,
}

impl NekoState {
    /// Get sprite sheet coordinates for this state
    /// 
    /// Standard neko sprite sheet layout (8 cols x 4-5 rows):
    /// Row 0: Awake(1), Yawn(2), Scratch(2), Wash(2), [1 unused]
    /// Row 1: Alert(1), Sleep(2), [5 unused]
    /// Row 2: N(2), NE(2), E(2), SE(2)
    /// Row 3: S(2), SW(2), W(2), NW(2)
    /// Row 4: [Pawprints - optional]
    pub fn sprite_coords(&self, frame: u8) -> (i32, i32) {
        let frame = (frame % 2) as i32;
        
        match self {
            // Row 0: Idle animations
            NekoState::Sit => (0, 0),           // Awake/Sit (single frame)
            NekoState::Yawn => (1 + frame, 0),  // Yawn (2 frames)
            NekoState::Scratch => (3 + frame, 0), // Scratch (2 frames)
            NekoState::Wash => (5 + frame, 0),  // Wash (2 frames)
            
            // Row 1: Alert and sleep
            NekoState::Alert => (0, 1),         // Alert (single frame)
            NekoState::Sleep1 => (1, 1),        // Sleep frame 1
            NekoState::Sleep2 => (2, 1),        // Sleep frame 2
            
            // Row 2: North, NE, East, SE
            NekoState::RunN => (0 + frame, 2),
            NekoState::RunNE => (2 + frame, 2),
            NekoState::RunE => (4 + frame, 2),
            NekoState::RunSE => (6 + frame, 2),
            
            // Row 3: South, SW, West, NW
            NekoState::RunS => (0 + frame, 3),
            NekoState::RunSW => (2 + frame, 3),
            NekoState::RunW => (4 + frame, 3),
            NekoState::RunNW => (6 + frame, 3),
        }
    }
}

/// The neko itself!
pub struct Neko {
    pub x: f64,
    pub y: f64,
    pub target_x: f64,
    pub target_y: f64,
    pub state: NekoState,
    pub frame: u8,
    pub idle_ticks: u32,
    pub speed: f64,
    
    // Behavior
    pub behavior_mode: BehaviorMode,
    pub behavior_state: BehaviorState,
    pub behavior_ticks: u32,
    
    // Screen bounds
    pub screen_width: f64,
    pub screen_height: f64,
    
    // Sprite dimensions (for bounds checking)
    pub sprite_width: f64,
    pub sprite_height: f64,
    
    // Cursor tracking
    pub cursor_x: f64,
    pub cursor_y: f64,
    pub cursor_available: bool,
    
    // Debug mode
    pub debug_mode: bool,
}

impl Neko {
    pub fn new() -> Self {
        Self {
            x: 100.0,
            y: 100.0,
            target_x: 200.0,
            target_y: 200.0,
            state: NekoState::Sit,
            frame: 0,
            idle_ticks: 0,
            speed: 8.0,
            behavior_mode: BehaviorMode::Mixed,
            behavior_state: BehaviorState::Wandering,
            behavior_ticks: 0,
            screen_width: 1920.0,
            screen_height: 1080.0,
            sprite_width: 32.0,  // Default to classic neko size
            sprite_height: 32.0,
            cursor_x: 0.0,
            cursor_y: 0.0,
            cursor_available: false,
            debug_mode: std::env::var("NEKO_DEBUG").is_ok(),
        }
    }

    /// Update cursor position from external source
    pub fn update_cursor(&mut self, x: f64, y: f64) {
        self.cursor_x = x;
        self.cursor_y = y;
        self.cursor_available = true;
    }

    /// Main update loop
    pub fn update(&mut self) {
        self.behavior_ticks += 1;
        
        // Slow down sprite animation - only update frame every 3 ticks
        // This gives us ~6-7 fps for sprite animation instead of 20fps
        if self.behavior_ticks % 3 == 0 {
            self.frame = self.frame.wrapping_add(1);
        }
        
        // Update target based on behavior mode
        match self.behavior_mode {
            BehaviorMode::Chase => self.update_chase(),
            BehaviorMode::Wander => self.update_wander(),
            BehaviorMode::Mixed => self.update_mixed(),
        }
        
        // Move towards target
        self.move_towards_target();
    }

    /// Chase mode: always follow cursor
    fn update_chase(&mut self) {
        if self.cursor_available {
            self.target_x = self.cursor_x;
            self.target_y = self.cursor_y;
        }
    }

    /// Wander mode: random exploration
    fn update_wander(&mut self) {
        let distance = self.distance_to_target();
        
        // Pick new random target when close or after timeout
        if distance < 20.0 || self.behavior_ticks > 200 {
            self.pick_random_target();
            self.behavior_ticks = 0;
        }
    }

    /// Mixed mode: state machine for natural cat behavior
    fn update_mixed(&mut self) {
        let cursor_distance = if self.cursor_available {
            ((self.cursor_x - self.x).powi(2) + (self.cursor_y - self.y).powi(2)).sqrt()
        } else {
            f64::MAX
        };
        
        // Debug cursor distance periodically
        if self.behavior_ticks % 40 == 1 && self.cursor_available {
            eprintln!("DEBUG mixed: cursor_dist={:.0}, state={:?}", cursor_distance, self.behavior_state);
        }
        
        match self.behavior_state {
            BehaviorState::Wandering => {
                // Wander around
                let distance = self.distance_to_target();
                if distance < 20.0 || self.behavior_ticks > 200 {
                    self.pick_random_target();
                    self.behavior_ticks = 0;
                }
                
                // Notice cursor if it's close - 600px range for big displays, high probability
                if cursor_distance < 600.0 && rand::thread_rng().gen_ratio(1, 10) {
                    eprintln!("DEBUG: Cat noticed cursor! Distance: {:.0}", cursor_distance);
                    self.behavior_state = BehaviorState::Alerted;
                    self.behavior_ticks = 0;
                    self.state = NekoState::Alert;
                }
            }
            
            BehaviorState::Alerted => {
                // Pause and look at cursor
                self.target_x = self.x; // Stay still
                self.target_y = self.y;
                
                if self.behavior_ticks > 30 {
                    // Decide to chase or ignore
                    if cursor_distance < 300.0 && rand::thread_rng().gen_ratio(3, 4) {
                        self.behavior_state = BehaviorState::Chasing;
                    } else {
                        self.behavior_state = BehaviorState::Wandering;
                    }
                    self.behavior_ticks = 0;
                }
            }
            
            BehaviorState::Chasing => {
                // Chase the cursor!
                if self.cursor_available {
                    self.target_x = self.cursor_x;
                    self.target_y = self.cursor_y;
                }
                
                // Lose interest after a while or if cursor is too far
                if self.behavior_ticks > 400 || cursor_distance > 600.0 {
                    if rand::thread_rng().gen_ratio(1, 60) {
                        eprintln!("DEBUG: Cat losing interest (timeout or too far)");
                        self.behavior_state = BehaviorState::LosingInterest;
                        self.behavior_ticks = 0;
                    }
                }
                
                // Also lose interest if we catch up
                if cursor_distance < 30.0 && self.behavior_ticks > 60 {
                    eprintln!("DEBUG: Cat caught cursor, losing interest");
                    self.behavior_state = BehaviorState::LosingInterest;
                    self.behavior_ticks = 0;
                }
            }
            
            BehaviorState::LosingInterest => {
                // Slow down, transition to idle
                self.speed = 4.0;
                
                if self.behavior_ticks > 40 {
                    self.behavior_state = BehaviorState::Wandering;
                    self.speed = 8.0;
                    self.behavior_ticks = 0;
                    self.pick_random_target();
                }
            }
        }
    }

    /// Pick a random target within screen bounds
    fn pick_random_target(&mut self) {
        let mut rng = rand::thread_rng();
        
        // Bias towards staying somewhat near current position
        let range = 300.0;
        self.target_x = (self.x + rng.gen_range(-range..range))
            .clamp(0.0, self.screen_width - self.sprite_width);
        self.target_y = (self.y + rng.gen_range(-range..range))
            .clamp(0.0, self.screen_height - self.sprite_height);
    }

    /// Move towards the current target
    fn move_towards_target(&mut self) {
        let dx = self.target_x - self.x;
        let dy = self.target_y - self.y;
        let distance = (dx * dx + dy * dy).sqrt();
        
        if distance < 10.0 {
            // Close enough - go idle
            self.idle_ticks += 1;
            self.update_idle_state();
        } else {
            // Moving
            self.idle_ticks = 0;
            
            // Determine direction and set running state
            let angle = dy.atan2(dx);
            self.state = Self::direction_to_state(angle);
            
            // Move
            let move_x = (dx / distance) * self.speed;
            let move_y = (dy / distance) * self.speed;
            self.x += move_x;
            self.y += move_y;
            
            // Clamp to screen - keep sprite fully visible
            self.x = self.x.clamp(0.0, self.screen_width - self.sprite_width);
            self.y = self.y.clamp(0.0, self.screen_height - self.sprite_height);
        }
    }

    /// Update idle animation state
    fn update_idle_state(&mut self) {
        // Cycle through idle animations
        if self.idle_ticks > 60 && self.idle_ticks % 60 == 0 {
            let mut rng = rand::thread_rng();
            self.state = match rng.gen_range(0..10) {
                0..=4 => NekoState::Sit,
                5..=6 => NekoState::Yawn,
                7..=8 => NekoState::Scratch,
                9 => NekoState::Wash,
                _ => NekoState::Sit,
            };
        }
        
        // Fall asleep after long idle
        if self.idle_ticks > 300 {
            self.state = if (self.frame / 20) % 2 == 0 {
                NekoState::Sleep1
            } else {
                NekoState::Sleep2
            };
        }
    }

    /// Distance to current target
    fn distance_to_target(&self) -> f64 {
        let dx = self.target_x - self.x;
        let dy = self.target_y - self.y;
        (dx * dx + dy * dy).sqrt()
    }

    /// Convert angle to running state (8 directions)
    fn direction_to_state(angle: f64) -> NekoState {
        use std::f64::consts::PI;
        
        let angle = if angle < 0.0 { angle + 2.0 * PI } else { angle };
        let sector = ((angle + PI / 8.0) / (PI / 4.0)) as i32 % 8;
        
        match sector {
            0 => NekoState::RunE,
            1 => NekoState::RunSE,
            2 => NekoState::RunS,
            3 => NekoState::RunSW,
            4 => NekoState::RunW,
            5 => NekoState::RunNW,
            6 => NekoState::RunN,
            7 => NekoState::RunNE,
            _ => NekoState::RunE,
        }
    }

    /// Set a new target position (e.g., cursor position)
    pub fn set_target(&mut self, x: f64, y: f64) {
        self.target_x = x;
        self.target_y = y;
        
        // Wake up if sleeping!
        if matches!(self.state, NekoState::Sleep1 | NekoState::Sleep2) {
            self.state = NekoState::Alert;
            self.idle_ticks = 0;
        }
    }

    /// Draw the neko sprite (placeholder)
    pub fn draw(&self, cr: &cairo::Context) {
        self.draw_with_sprites(cr, None);
    }
    
    /// Draw the neko, optionally using a sprite sheet
    pub fn draw_with_sprites(&self, cr: &cairo::Context, sprites: Option<&crate::sprites::SpriteSheet>) {
        let (sprite_col, sprite_row) = self.state.sprite_coords(self.frame);
        
        // Clear with transparency
        cr.set_operator(cairo::Operator::Clear);
        let _ = cr.paint();
        cr.set_operator(cairo::Operator::Over);
        
        // Debug mode: draw larger area with info
        if self.debug_mode {
            self.draw_debug(cr);
            return;
        }
        
        // Use sprites if available, otherwise fall back to cairo drawing
        if let Some(sheet) = sprites {
            sheet.draw_centered(cr, sprite_col, sprite_row);
        } else {
            self.draw_cat(cr);
        }
    }
    
    /// Draw debug visualization
    fn draw_debug(&self, cr: &cairo::Context) {
        // Draw OUTER debug outline - bright magenta, should be at exact edges
        // If this gets clipped, we know the layer is smaller than expected!
        cr.set_source_rgba(1.0, 0.0, 1.0, 1.0); // Bright magenta
        cr.set_line_width(3.0);
        cr.rectangle(1.5, 1.5, 29.0, 29.0); // Inset slightly so stroke is visible
        let _ = cr.stroke();
        
        // Draw inner debug outline - green, shows the "safe" drawing area
        cr.set_source_rgba(0.0, 1.0, 0.0, 0.7);
        cr.set_line_width(1.0);
        cr.rectangle(4.0, 4.0, 24.0, 24.0);
        let _ = cr.stroke();
        
        // Draw crosshairs at center (16, 16) to verify coordinate system
        cr.set_source_rgba(1.0, 1.0, 0.0, 0.5); // Yellow
        cr.set_line_width(1.0);
        cr.move_to(16.0, 0.0);
        cr.line_to(16.0, 32.0);
        cr.move_to(0.0, 16.0);
        cr.line_to(32.0, 16.0);
        let _ = cr.stroke();
        
        // Draw the cat
        self.draw_cat(cr);
        
        // Draw target indicator (small red dot showing direction to target)
        let rel_target_x = self.target_x - self.x;
        let rel_target_y = self.target_y - self.y;
        let target_dist = (rel_target_x.powi(2) + rel_target_y.powi(2)).sqrt();
        
        // Normalize and scale to fit within sprite area (max 12px from center)
        if target_dist > 1.0 {
            let scale = 12.0 / target_dist.max(12.0);
            let dot_x = 16.0 + rel_target_x * scale;
            let dot_y = 16.0 + rel_target_y * scale;
            
            cr.set_source_rgba(1.0, 0.0, 0.0, 0.8); // Red
            cr.arc(dot_x, dot_y, 3.0, 0.0, 2.0 * std::f64::consts::PI);
            let _ = cr.fill();
        }
        
        // Draw cursor indicator (blue dot showing direction to cursor)
        if self.cursor_available {
            let rel_cursor_x = self.cursor_x - self.x;
            let rel_cursor_y = self.cursor_y - self.y;
            let cursor_dist = (rel_cursor_x.powi(2) + rel_cursor_y.powi(2)).sqrt();
            
            // Normalize and scale to fit within sprite area
            if cursor_dist > 1.0 {
                let scale = 14.0 / cursor_dist.max(14.0);
                let dot_x = 16.0 + rel_cursor_x * scale;
                let dot_y = 16.0 + rel_cursor_y * scale;
                
                cr.set_source_rgba(0.0, 0.5, 1.0, 0.8); // Blue
                cr.arc(dot_x, dot_y, 4.0, 0.0, 2.0 * std::f64::consts::PI);
                let _ = cr.fill();
            }
        }
        
        // Draw behavior state indicator (top-right corner)
        let state_color = match self.behavior_state {
            BehaviorState::Wandering => (0.5, 0.5, 0.5), // Gray
            BehaviorState::Alerted => (1.0, 1.0, 0.0),   // Yellow
            BehaviorState::Chasing => (1.0, 0.5, 0.0),   // Orange
            BehaviorState::LosingInterest => (0.5, 0.0, 0.5), // Purple
        };
        cr.set_source_rgb(state_color.0, state_color.1, state_color.2);
        cr.arc(28.0, 4.0, 3.0, 0.0, 2.0 * std::f64::consts::PI);
        let _ = cr.fill();
    }
    
    /// Draw the cat face
    fn draw_cat(&self, cr: &cairo::Context) {
        // Background circle (body)
        cr.set_source_rgb(0.9, 0.7, 0.5); // Tan
        cr.arc(16.0, 18.0, 14.0, 0.0, 2.0 * std::f64::consts::PI);
        let _ = cr.fill();
        
        // Ears
        cr.set_source_rgb(0.9, 0.7, 0.5);
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
        
        // Inner ears
        cr.set_source_rgb(1.0, 0.8, 0.8);
        cr.move_to(6.0, 7.0);
        cr.line_to(8.0, 2.0);
        cr.line_to(10.0, 7.0);
        cr.close_path();
        let _ = cr.fill();
        
        cr.move_to(22.0, 7.0);
        cr.line_to(24.0, 2.0);
        cr.line_to(26.0, 7.0);
        cr.close_path();
        let _ = cr.fill();
        
        // Eyes - change based on state
        cr.set_source_rgb(0.0, 0.0, 0.0);
        match self.state {
            NekoState::Sleep1 | NekoState::Sleep2 => {
                // Closed eyes (lines)
                cr.set_line_width(2.0);
                cr.move_to(8.0, 14.0);
                cr.line_to(12.0, 14.0);
                cr.move_to(20.0, 14.0);
                cr.line_to(24.0, 14.0);
                let _ = cr.stroke();
            }
            NekoState::Alert => {
                // Wide eyes!
                cr.arc(10.0, 14.0, 4.0, 0.0, 2.0 * std::f64::consts::PI);
                let _ = cr.fill();
                cr.arc(22.0, 14.0, 4.0, 0.0, 2.0 * std::f64::consts::PI);
                let _ = cr.fill();
                // Pupils
                cr.set_source_rgb(1.0, 1.0, 1.0);
                cr.arc(11.0, 13.0, 1.5, 0.0, 2.0 * std::f64::consts::PI);
                let _ = cr.fill();
                cr.arc(23.0, 13.0, 1.5, 0.0, 2.0 * std::f64::consts::PI);
                let _ = cr.fill();
            }
            _ => {
                // Normal eyes
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
        
        // Mouth
        cr.set_source_rgb(0.0, 0.0, 0.0);
        cr.set_line_width(1.0);
        cr.move_to(16.0, 21.0);
        cr.line_to(16.0, 24.0);
        cr.move_to(16.0, 24.0);
        cr.curve_to(12.0, 26.0, 12.0, 24.0, 14.0, 23.0);
        cr.move_to(16.0, 24.0);
        cr.curve_to(20.0, 26.0, 20.0, 24.0, 18.0, 23.0);
        let _ = cr.stroke();
        
        // Whiskers
        cr.set_line_width(1.0);
        cr.move_to(2.0, 16.0);
        cr.line_to(10.0, 18.0);
        cr.move_to(2.0, 20.0);
        cr.line_to(10.0, 20.0);
        cr.move_to(2.0, 24.0);
        cr.line_to(10.0, 22.0);
        cr.move_to(22.0, 18.0);
        cr.line_to(30.0, 16.0);
        cr.move_to(22.0, 20.0);
        cr.line_to(30.0, 20.0);
        cr.move_to(22.0, 22.0);
        cr.line_to(30.0, 24.0);
        let _ = cr.stroke();
    }
}

impl Default for Neko {
    fn default() -> Self {
        Self::new()
    }
}
