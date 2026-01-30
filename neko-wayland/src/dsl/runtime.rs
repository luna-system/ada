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
    pub target_speed: f64,              // Speed we're easing towards
    pub speed_transition_progress: f64, // 0.0 to 1.0

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
    pub frame_timer: u32,    // Ticks since last frame change
    pub frame_interval: u32, // Ticks between frame changes
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
            target_speed: 8.0,
            speed_transition_progress: 1.0, // Start fully transitioned
            screen_width: 1920.0,
            screen_height: 1080.0,
            sprite_width: 32.0, // Default, will be updated by main
            sprite_height: 32.0,
            cursor_x: 0.0,
            cursor_y: 0.0,
            cursor_available: false,
            frame: 0,
            idle_ticks: 0,
            frame_timer: 0,
            frame_interval: 5, // Default: change frame every 5 ticks (250ms at 20fps)
        }
    }

    /// Update cursor position
    pub fn update_cursor(&mut self, x: f64, y: f64) {
        self.cursor_x = x;
        self.cursor_y = y;
        self.cursor_available = true;
    }

    /// Normalize speed value to screen-relative pixels per tick
    /// Speed values in DSL are abstract (0-10 range), we convert to actual pixels
    /// based on screen size so movement feels consistent across different setups
    fn normalize_speed(&self, speed: f64) -> f64 {
        // Base speed: 1.0 = 1% of screen width per second
        // At 20fps, that's 0.05% per tick
        // For 1920px width: 1.0 speed = 0.96px/tick
        // For classic neko (32px sprite): multiply by sprite scale factor
        let base_speed_per_tick = (self.screen_width * 0.0005) * speed;

        // Scale by sprite size - larger sprites should move proportionally faster
        // to cover the same "visual distance"
        // Allow up to 10x scale for giant desktop pets!
        let sprite_scale = (self.sprite_width / 32.0).max(0.5).min(10.0);

        base_speed_per_tick * sprite_scale
    }

    /// Main update tick (call at ~20fps)
    pub fn update(&mut self) {
        // Update frame timer for animation
        self.frame_timer += 1;
        if self.frame_timer >= self.frame_interval {
            self.frame = self.frame.wrapping_add(1);
            self.frame_timer = 0;
        }

        self.state_ticks += 1;

        // Debug cursor every 2 seconds
        if self.frame % 40 == 0 && self.cursor_available {
            let dist = self.cursor_distance();
            eprintln!(
                "DSL: cursor at ({:.0}, {:.0}), pet at ({:.0}, {:.0}), distance: {:.0}px",
                self.cursor_x, self.cursor_y, self.x, self.y, dist
            );
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
        // Get speed from state params and normalize it
        let raw_speed = state.get_param("speed", 8.0);
        let new_target_speed = self.normalize_speed(raw_speed);

        // If target speed changed, start a smooth transition
        if (new_target_speed - self.target_speed).abs() > 0.1 {
            self.target_speed = new_target_speed;
            self.speed_transition_progress = 0.0;
        }

        // Smoothly ease current speed towards target speed
        if self.speed_transition_progress < 1.0 {
            self.speed_transition_progress += 0.05; // 20 frames (1 second) to fully transition
            self.speed_transition_progress = self.speed_transition_progress.min(1.0);

            // Apply easing to the speed transition
            let eased_progress = self.behavior.easing.apply(self.speed_transition_progress);
            self.speed = self.speed * (1.0 - eased_progress) + self.target_speed * eased_progress;
        } else {
            self.speed = self.target_speed;
        }

        // State-specific behavior based on name
        match state.name.as_str() {
            "wander" => self.do_wander(state),
            "chase" => self.do_chase(state),
            "sleep" => self.do_sleep(state),
            "alert" => self.do_alert(state),
            "scratch" => self.do_scratch(state),
            "wash" | "groom" => self.do_wash(state),
            "idle" | "sit" | "play" | "itch" => self.do_idle(state),
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

    fn do_scratch(&mut self, _state: &State) {
        // Stay still and scratch at the wall
        self.target_x = self.x;
        self.target_y = self.y;
        self.idle_ticks += 1;
    }

    fn do_wash(&mut self, _state: &State) {
        // Stay still and wash (lick paw)
        self.target_x = self.x;
        self.target_y = self.y;
        self.idle_ticks += 1;
    }

    /// Determine which edge we're closest to (for wall scratching animation)
    pub fn closest_edge(&self) -> &str {
        let dist_left = self.x;
        let dist_right = self.screen_width - self.sprite_width - self.x;
        let dist_top = self.y;
        let dist_bottom = self.screen_height - self.sprite_height - self.y;

        let min_dist = dist_left.min(dist_right).min(dist_top).min(dist_bottom);

        if min_dist == dist_left {
            "left"
        } else if min_dist == dist_right {
            "right"
        } else if min_dist == dist_top {
            "up"
        } else {
            "down"
        }
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
                    eprintln!(
                        "DSL: {} → {} (trigger: {}, certainty: {:.0}%)",
                        self.current_state,
                        transition.target_state,
                        trigger_desc,
                        transition.certainty.probability() * 100.0
                    );
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
                        let threshold = trigger.params.first().map(|v| v.sample()).unwrap_or(200.0);
                        let dist = self.cursor_distance();
                        dist < threshold
                    }
                    "cursor_far" => {
                        let threshold = trigger.params.first().map(|v| v.sample()).unwrap_or(400.0);
                        let dist = self.cursor_distance();
                        dist > threshold
                    }
                    "caught" => {
                        // Pet caught the cursor - check if we're very close
                        let threshold = trigger.params.first().map(|v| v.sample()).unwrap_or(50.0);
                        let dist = self.cursor_distance();
                        dist < threshold
                    }
                    "timeout" => {
                        let duration = trigger.params.first().map(|v| v.sample()).unwrap_or(5.0);
                        // Convert seconds to ticks (20fps)
                        self.state_ticks > (duration * 20.0) as u32
                    }
                    "idle" => {
                        let duration = trigger.params.first().map(|v| v.sample()).unwrap_or(3.0);
                        self.idle_ticks > (duration * 20.0) as u32
                    }
                    "click" => false, // TODO: implement click detection
                    "at_edge" => {
                        // Check if pet is at any screen edge
                        let threshold = trigger.params.first().map(|v| v.sample()).unwrap_or(50.0);

                        let at_left = self.x < threshold;
                        let at_right = self.x > (self.screen_width - self.sprite_width - threshold);
                        let at_top = self.y < threshold;
                        let at_bottom =
                            self.y > (self.screen_height - self.sprite_height - threshold);

                        at_left || at_right || at_top || at_bottom
                    }
                    "random" => {
                        // Random chance each tick
                        let chance = trigger.params.first().map(|v| v.sample()).unwrap_or(0.01);
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

        // Safety check: ensure we have enough room to move
        let max_x = (self.screen_width - self.sprite_width).max(0.0);
        let max_y = (self.screen_height - self.sprite_height).max(0.0);

        if max_x < 10.0 || max_y < 10.0 {
            eprintln!(
                "WARNING: Sprite too large for screen! sprite={}x{}, screen={}x{}",
                self.sprite_width, self.sprite_height, self.screen_width, self.screen_height
            );
            // Just stay where we are
            self.target_x = self.x.clamp(0.0, max_x);
            self.target_y = self.y.clamp(0.0, max_y);
            return;
        }

        self.target_x = (self.x + rng.gen_range(-radius..radius)).clamp(0.0, max_x);
        self.target_y = (self.y + rng.gen_range(-radius..radius)).clamp(0.0, max_y);
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

        // Apply easing to speed based on distance to target
        // This creates smooth acceleration/deceleration
        let max_ease_distance = 200.0; // Distance over which to apply easing
        let progress = (distance / max_ease_distance).min(1.0);

        // Use inverse easing - slow when far (starting), fast in middle, slow when close (stopping)
        let ease_factor = if progress > 0.5 {
            // Approaching target - ease out (slow down)
            let approach_progress = (1.0 - progress) * 2.0; // 0..1 as we get closer
            1.0 - self.behavior.easing.apply(approach_progress) * 0.7
        } else {
            // Starting movement - ease in (speed up)
            let start_progress = progress * 2.0; // 0..1 as we start moving
            0.3 + self.behavior.easing.apply(start_progress) * 0.7
        };

        let eased_speed = self.speed * ease_factor;

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
    let content =
        std::fs::read_to_string(path).map_err(|e| format!("Failed to read {}: {}", path, e))?;

    let behavior = super::parse_neko(&content)?;
    eprintln!(
        "DSL: Loaded '{}' with {} states",
        behavior.name,
        behavior.states.len()
    );

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

    let behavior = super::parse_neko(dsl).expect("Default behavior should parse");

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
