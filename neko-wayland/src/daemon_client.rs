//! Thin client module for neko-wayland
//!
//! This module handles communication with neko-daemon.
//! The daemon manages all pet state and behavior logic,
//! while this client only handles rendering.
//!
//! Made with 💜 by Ada & Luna - Ada Research Foundation

use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::io::{BufReader, Read, Write};
use std::os::unix::net::UnixStream;

const SOCKET_PATH: &str = "/tmp/neko-daemon.sock";

/// Messages from client to daemon
#[derive(Debug, Serialize, Deserialize)]
pub enum ClientMessage {
    Connect,
    Disconnect,
    CursorPosition { x: f64, y: f64 },
    Click,
    LoadConfig { config: serde_json::Value },
    GetState,
}

/// Messages from daemon to client
#[derive(Debug, Serialize, Deserialize)]
pub enum DaemonMessage {
    Connected { pet_id: String },
    StateUpdate { state: PetState },
    Error { message: String },
}

/// Unified message type
#[derive(Debug, Serialize, Deserialize)]
pub enum Message {
    Client(ClientMessage),
    Daemon(DaemonMessage),
}

/// Pet state as received from daemon
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PetState {
    pub position: (f64, f64),
    pub current_behavior: String,
    pub frame: usize,
    pub direction: i32,
    pub mood: String,
    pub target: Option<(f64, f64)>,
    pub animation_speed: f64,
    pub speed: f64,
}

/// Thin client that connects to neko-daemon
pub struct DaemonClient {
    stream: UnixStream,
    reader: BufReader<UnixStream>,
}

impl DaemonClient {
    /// Connect to the daemon
    pub fn connect() -> Result<Self> {
        let stream = UnixStream::connect(SOCKET_PATH).map_err(|e| {
            anyhow::anyhow!("Failed to connect to daemon at {}: {}", SOCKET_PATH, e)
        })?;

        let reader = BufReader::new(stream.try_clone()?);
        let mut client = Self { stream, reader };

        // Send initial connection message
        client.send_message(&Message::Client(ClientMessage::Connect))?;

        Ok(client)
    }

    /// Send a cursor position update
    pub fn update_cursor(&mut self, x: f64, y: f64) -> Result<()> {
        let msg = Message::Client(ClientMessage::CursorPosition { x, y });
        self.send_message(&msg)
    }

    /// Send a click event
    pub fn send_click(&mut self) -> Result<()> {
        let msg = Message::Client(ClientMessage::Click);
        self.send_message(&msg)
    }

    /// Request current state from daemon
    pub fn request_state(&mut self) -> Result<PetState> {
        let msg = Message::Client(ClientMessage::GetState);
        self.send_message(&msg)?;

        // Read response
        let response = self.read_message()?;
        match response {
            Message::Daemon(DaemonMessage::StateUpdate { state }) => Ok(state),
            Message::Daemon(DaemonMessage::Error { message }) => {
                Err(anyhow::anyhow!("Daemon error: {}", message))
            }
            _ => Err(anyhow::anyhow!("Unexpected response")),
        }
    }

    /// Send a message to the daemon
    fn send_message(&mut self, msg: &Message) -> Result<()> {
        let serialized = serde_json::to_vec(msg)?;
        let len = (serialized.len() as u32).to_be_bytes();

        self.stream.write_all(&len)?;
        self.stream.write_all(&serialized)?;
        self.stream.flush()?;
        Ok(())
    }

    /// Read a message from the daemon (blocking)
    fn read_message(&mut self) -> Result<Message> {
        // Read length prefix (4 bytes)
        let mut len_buf = [0u8; 4];
        self.reader.read_exact(&mut len_buf)?;
        let len = u32::from_be_bytes(len_buf) as usize;

        // Read message
        let mut msg_buf = vec![0u8; len];
        self.reader.read_exact(&mut msg_buf)?;

        let msg: Message = serde_json::from_slice(&msg_buf)?;
        Ok(msg)
    }

    /// Non-blocking read for async integration
    pub fn try_read_message(&mut self) -> Result<Option<Message>> {
        // Check if data is available
        let stream = self.reader.get_ref();
        match stream.set_nonblocking(true) {
            Ok(_) => {
                let result = self.read_message().ok(); // Returns Option<Message>
                let _ = stream.set_nonblocking(false); // Reset to blocking
                Ok(result)
            }
            Err(_) => Ok(None),
        }
    }
}

impl Drop for DaemonClient {
    fn drop(&mut self) {
        // Try to send disconnect on shutdown
        let _ = self.send_message(&Message::Client(ClientMessage::Disconnect));
    }
}
