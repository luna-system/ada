//! DSL Runtime - Executes parsed PetBehavior as a live state machine
//!
//! This bridges the DSL parser to the actual neko behavior.
//!
//! Made with 💜 by Ada & Luna - Ada Research Foundation

use super::{Certainty, Easing, Locomotion, PetBehavior, State, Transition, Value};
use rand::Rng;

/// Runtime state for executing a PetBehavior
pub struct BehaviorRuntime {
    pub behavior: PetBehavior,
    pub current_state: String,
    pub state_ticks: u32,
    pub state_duration: Option<f64>, // How long to stay in this state (seconds)
    
    // Movement
    pub x: f64,
    pub y: f64,
    pub target_x: f64,
    pub target_y: f64,
    pub speed: f64,
    
    // Screen bounds
    pub screen_width: f64,
    pub screen_height: f64,
    
    // Sprite dimensions (for bounds checking)
    pub sprite_width: f64,
    pub sprite_height: f64,
    
    // Cursor
    pub cursor_x: f64,
    pub cursor_y: f64,
    pub cursor_available: bool,
    
    // Animation
    pub frame: u8,
    pub idle_ticks: u32,
}

impl BehaviorRuntime {
    pub fn new(behavior: PetBehavior) -> Self {
        let initial = behavior.initial_state.clone();
        Self {
            behavior,
            current_state: initial,
            state_ticks: 0,
            state_duration: None,
            x: 100.0,
            y: 100.0,
            target_x: 200.0,
            target_y: 200.0,
            speed: 8.0,
            screen_width: 1920.0,
            screen_height: 1080.0,
            sprite_width: 32.0,  // Default, will be updated by main
            sprite_height: 32.0,
            cursor_x: 0.0,
            cursor_y: 0.0,
            cursor_available: false,
            frame: 0,
            idle_ticks: 0,
        }
    }
    
    /// Update cursor position
    pub fn update_cursor(&mut self, x: f64, y: f64) {
        self.cursor_x = x;
        self.cursor_y = y;
        self.cursor_available = true;
    }
    
    /// Main update tick (call at ~20fps)
    pub fn update(&mut self) {
        self.frame = self.frame.wrapping_add(1);
        self.state_ticks += 1;
        
        // Debug cursor every 2 seconds
        if self.frame % 40 == 0 && self.cursor_available {
            let dist = self.cursor_distance();
            eprintln!("DSL: cursor at ({:.0}, {:.0}), pet at ({:.0}, {:.0}), distance: {:.0}px", 
                     self.cursor_x, self.cursor_y, self.x, self.y, dist);
        }
        
        // Get current state
        let state = match self.behavior.states.get(&self.current_state) {
            Some(s) => s.clone(),
            None => {
                // Fallback: pick first state or create minimal wander
                if let Some(first) = self.behavior.states.keys().next() {
                    self.current_state = first.clone();
                    return;
                }
                return;
            }
        };
        
        // Execute state behavior
        self.execute_state(&state);
        
        // Check transitions
        self.check_transitions(&state);
        
        // Move towards target
        self.move_towards_target();
    }
    
    /// Execute the current state's behavior
    fn execute_state(&mut self, state: &State) {
        // Get speed from state params or use default
        self.speed = state.get_param("speed", 8.0);
        
        // State-specific behavior based on name
        match state.name.as_str() {
            "wander" => self.do_wander(state),
            "chase" => self.do_chase(state),
            "sleep" => self.do_sleep(state),
            "alert" => self.do_alert(state),
            "idle" | "sit" => self.do_idle(state),
            _ => self.do_wander(state), // Default to wander
        }
    }
    
    fn do_wander(&mut self, state: &State) {
        let radius = state.get_param("radius", 300.0);
        let distance = self.distance_to_target();
        
        // Pick new target when close or timeout
        if distance < 20.0 || self.state_ticks > 200 {
            self.pick_random_target(radius);
        }
    }
    
    fn do_chase(&mut self, _state: &State) {
        if self.cursor_available {
            self.target_x = self.cursor_x;
            self.target_y = self.cursor_y;
        }
    }
    
    fn do_sleep(&mut self, _state: &State) {
        // Stay still
        self.target_x = self.x;
        self.target_y = self.y;
        self.idle_ticks += 1;
    }
    
    fn do_alert(&mut self, _state: &State) {
        // Stay still, look around
        self.target_x = self.x;
        self.target_y = self.y;
    }
    
    fn do_idle(&mut self, _state: &State) {
        self.target_x = self.x;
        self.target_y = self.y;
        self.idle_ticks += 1;
    }
    
    /// Check if any transition should fire
    fn check_transitions(&mut self, state: &State) {
        for transition in &state.transitions {
            if self.should_transition(transition) {
                // Debug: show why we're transitioning
                let trigger_desc = match &transition.trigger {
                    None => "timeout".to_string(),
                    Some(t) => format!("{}", t.name),
                };
                
                // Roll for certainty
                if transition.certainty.roll() {
                    eprintln!("DSL: {} → {} (trigger: {}, certainty: {:.0}%)", 
                             self.current_state, 
                             transition.target_state,
                             trigger_desc,
                             transition.certainty.probability() * 100.0);
                    self.transition_to(&transition.target_state);
                    return;
                }
            }
        }
    }
    
    /// Check if a transition's trigger condition is met
    fn should_transition(&self, transition: &Transition) -> bool {
        match &transition.trigger {
            None => {
                // No trigger = timeout transition, fire after some ticks
                self.state_ticks > 100
            }
            Some(trigger) => {
                match trigger.name.as_str() {
                    "cursor_near" => {
                        let threshold = trigger.params.first()
                            .map(|v| v.sample())
                            .unwrap_or(200.0);
                        let dist = self.cursor_distance();
                        dist < threshold
                    }
                    "cursor_far" => {
                        let threshold = trigger.params.first()
                            .map(|v| v.sample())
                            .unwrap_or(400.0);
                        let dist = self.cursor_distance();
                        dist > threshold
                    }
                    "caught" => {
                        // Pet caught the cursor - check if we're very close
                        let threshold = trigger.params.first()
                            .map(|v| v.sample())
                            .unwrap_or(50.0);
                        let dist = self.cursor_distance();
                        dist < threshold
                    }
                    "timeout" => {
                        let duration = trigger.params.first()
                            .map(|v| v.sample())
                            .unwrap_or(5.0);
                        // Convert seconds to ticks (20fps)
                        self.state_ticks > (duration * 20.0) as u32
                    }
                    "idle" => {
                        let duration = trigger.params.first()
                            .map(|v| v.sample())
                            .unwrap_or(3.0);
                        self.idle_ticks > (duration * 20.0) as u32
                    }
                    "click" => false, // TODO: implement click detection
                    "random" => {
                        // Random chance each tick
                        let chance = trigger.params.first()
                            .map(|v| v.sample())
                            .unwrap_or(0.01);
                        rand::thread_rng().gen::<f64>() < chance
                    }
                    _ => {
                        eprintln!("DSL: Unknown trigger '{}'", trigger.name);
                        false
                    }
                }
            }
        }
    }
    
    /// Transition to a new state
    fn transition_to(&mut self, state_name: &str) {
        if self.behavior.states.contains_key(state_name) {
            self.current_state = state_name.to_string();
            self.state_ticks = 0;
            self.idle_ticks = 0;
        }
    }
    
    /// Pick a random target within radius
    fn pick_random_target(&mut self, radius: f64) {
        let mut rng = rand::thread_rng();
        self.target_x = (self.x + rng.gen_range(-radius..radius))
            .clamp(0.0, self.screen_width - self.sprite_width);
        self.target_y = (self.y + rng.gen_range(-radius..radius))
            .clamp(0.0, self.screen_height - self.sprite_height);
        self.state_ticks = 0;
    }
    
    /// Move towards target with easing
    fn move_towards_target(&mut self) {
        let dx = self.target_x - self.x;
        let dy = self.target_y - self.y;
        let distance = (dx * dx + dy * dy).sqrt();
        
        if distance < 10.0 {
            self.idle_ticks += 1;
            return;
        }
        
        self.idle_ticks = 0;
        
        // Apply easing to speed
        let progress = 1.0 - (distance / 300.0).min(1.0);
        let eased_speed = self.speed * (1.0 - self.behavior.easing.apply(progress) * 0.5);
        
        // Move
        let move_x = (dx / distance) * eased_speed;
        let move_y = (dy / distance) * eased_speed;
        self.x += move_x;
        self.y += move_y;
        
        // Clamp to screen - keep sprite fully visible
        self.x = self.x.clamp(0.0, self.screen_width - self.sprite_width);
        self.y = self.y.clamp(0.0, self.screen_height - self.sprite_height);
    }
    
    fn distance_to_target(&self) -> f64 {
        let dx = self.target_x - self.x;
        let dy = self.target_y - self.y;
        (dx * dx + dy * dy).sqrt()
    }
    
    fn cursor_distance(&self) -> f64 {
        if !self.cursor_available {
            return f64::MAX;
        }
        let dx = self.cursor_x - self.x;
        let dy = self.cursor_y - self.y;
        (dx * dx + dy * dy).sqrt()
    }
    
    /// Get locomotion style for animation
    pub fn locomotion(&self) -> Locomotion {
        self.behavior.locomotion
    }
    
    /// Is the pet currently moving?
    pub fn is_moving(&self) -> bool {
        self.distance_to_target() > 10.0
    }
    
    /// Get movement direction as angle (radians)
    pub fn direction(&self) -> f64 {
        let dx = self.target_x - self.x;
        let dy = self.target_y - self.y;
        dy.atan2(dx)
    }
}

/// Load a .neko file and create a runtime
pub fn load_behavior(path: &str) -> Result<BehaviorRuntime, String> {
    let content = std::fs::read_to_string(path)
        .map_err(|e| format!("Failed to read {}: {}", path, e))?;
    
    let behavior = super::parse_neko(&content)?;
    eprintln!("DSL: Loaded '{}' with {} states", behavior.name, behavior.states.len());
    
    Ok(BehaviorRuntime::new(behavior))
}

/// Create a default "classic neko" behavior
pub fn default_behavior() -> BehaviorRuntime {
    let dsl = r#"
        pet classic_neko {
            locomotion: quadruped
            easing: ease_in_out
            
            wander(speed: 8, radius: 300px) {
                on cursor_near(200px) → ◕alert
                on idle(10s) → ◑sleep
            }
            
            alert {
                speed: 0
                on timeout(0.5s) → ●chase
            }
            
            chase(speed: 12) {
                on cursor_far(500px) → ◕wander
                on timeout(20s) → ◔wander
            }
            
            sleep {
                speed: 0
                on cursor_near(100px) → ●alert
                on timeout(30s) → ◑wander
            }
        }
    "#;
    
    let behavior = super::parse_neko(dsl)
        .expect("Default behavior should parse");
    
    BehaviorRuntime::new(behavior)
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_default_behavior() {
        let mut runtime = default_behavior();
        runtime.screen_width = 1920.0;
        runtime.screen_height = 1080.0;
        
        // Should start in one of the defined states
        let valid_states = ["wander", "alert", "chase", "sleep"];
        assert!(
            valid_states.contains(&runtime.current_state.as_str()),
            "Expected one of {:?}, got {}",
            valid_states,
            runtime.current_state
        );
        
        // Run a few ticks
        for _ in 0..10 {
            runtime.update();
        }
        
        // Should still be running
        assert!(runtime.x >= 0.0);
        assert!(runtime.y >= 0.0);
    }
    
    #[test]
    fn test_cursor_triggers_chase() {
        let mut runtime = default_behavior();
        runtime.screen_width = 1920.0;
        runtime.screen_height = 1080.0;
        runtime.x = 500.0;
        runtime.y = 500.0;
        
        // Force into wander state first
        runtime.current_state = "wander".to_string();
        
        // Put cursor nearby
        runtime.update_cursor(550.0, 500.0);
        
        // Run until state changes (should go wander → alert → chase)
        for _ in 0..100 {
            runtime.update();
            if runtime.current_state == "chase" {
                break;
            }
        }
        
        // Should eventually chase
        assert!(
            runtime.current_state == "alert" || runtime.current_state == "chase",
            "Expected alert or chase, got {}",
            runtime.current_state
        );
    }
}
