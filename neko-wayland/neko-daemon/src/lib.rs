pub mod ipc;
pub mod state;
pub mod behavior;

// Re-export common types
pub use state::PetState;
pub use ipc::{ClientMessage, DaemonMessage, Message};
