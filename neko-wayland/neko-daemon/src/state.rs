#[derive(Debug, Default)]
pub struct PetState {
    pub position: (f64, f64),
    pub current_behavior: String,
    // Add other state variables as needed
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
}
