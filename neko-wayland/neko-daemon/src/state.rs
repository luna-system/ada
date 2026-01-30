use serde::{Deserialize, Serialize};

/// Complete pet state for daemon
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PetState {
    /// Pet position on screen
    pub position: (f64, f64),
    /// Current behavior state (wander, chase, sleep, etc.)
    pub current_behavior: String,
    /// Current animation frame
    pub frame: usize,
    /// Direction the pet is facing (0-7 for 8 directions)
    pub direction: i32,
    /// Current mood state
    pub mood: String,
    /// Target position (if chasing)
    pub target: Option<(f64, f64)>,
    /// Animation speed (frames per update)
    pub animation_speed: f64,
    /// Movement speed (pixels per tick)
    pub speed: f64,
}

impl Default for PetState {
    fn default() -> Self {
        Self {
            position: (0.0, 0.0),
            current_behavior: "idle".to_string(),
            frame: 0,
            direction: 2, // Facing down
            mood: "happy".to_string(),
            target: None,
            animation_speed: 1.0,
            speed: 5.0,
        }
    }
}

impl PetState {
    pub fn new() -> Self {
        Default::default()
    }

    pub fn update_position(&mut self, x: f64, y: f64) {
        self.position = (x, y);
    }

    pub fn set_behavior(&mut self, behavior: String) {
        self.current_behavior = behavior;
    }

    pub fn advance_frame(&mut self) {
        self.frame = (self.frame + 1) % 4; // Assuming 4 frames per animation
    }

    pub fn set_direction(&mut self, direction: i32) {
        self.direction = direction % 8;
    }
}
