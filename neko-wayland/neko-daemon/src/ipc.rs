use tokio::{
    io::{AsyncReadExt, AsyncWriteExt},
    net::{UnixListener, UnixStream},
};
use serde::{Serialize, Deserialize};
use anyhow::Result;

use crate::state::PetState;

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

/// Unified message type for bidirectional communication
#[derive(Debug, Serialize, Deserialize)]
pub enum Message {
    Client(ClientMessage),
    Daemon(DaemonMessage),
}

pub async fn run_ipc_server() -> Result<()> {
    // Remove the socket file if it already exists
    if tokio::fs::metadata(SOCKET_PATH).await.is_ok() {
        tokio::fs::remove_file(SOCKET_PATH).await?;
    }

    let listener = UnixListener::bind(SOCKET_PATH)?;
    println!("Neko Daemon listening on {}", SOCKET_PATH);

    loop {
        let (mut stream, _addr) = listener.accept().await?;
        tokio::spawn(async move {
            if let Err(e) = handle_client(&mut stream).await {
                eprintln!("Error handling client: {:?}", e);
            }
        });
    }
}

async fn handle_client(stream: &mut UnixStream) -> Result<()> {
    let mut buffer = vec![0; 1024];

    // Send welcome message
    let welcome = Message::Daemon(DaemonMessage::Connected {
        pet_id: "neko-1".to_string(),
    });
    send_message(stream, &welcome).await?;

    loop {
        let n = stream.read(&mut buffer).await?;
        if n == 0 {
            println!("Client disconnected.");
            break;
        }

        match serde_json::from_slice::<Message>(&buffer[..n]) {
            Ok(Message::Client(msg)) => {
                println!("Received client message: {:?}", msg);
                handle_client_message(stream, msg).await?;
            }
            Ok(msg) => {
                eprintln!("Unexpected message type: {:?}", msg);
            }
            Err(e) => {
                eprintln!("Failed to parse message: {:?}", e);
                let error = Message::Daemon(DaemonMessage::Error {
                    message: format!("Parse error: {}", e),
                });
                send_message(stream, &error).await?;
            }
        }
    }

    Ok(())
}

async fn handle_client_message(stream: &mut UnixStream, msg: ClientMessage) -> Result<()> {
    match msg {
        ClientMessage::Connect => {
            // Already handled in initial connection
        }
        ClientMessage::Disconnect => {
            println!("Client requested disconnect");
        }
        ClientMessage::CursorPosition { x, y } => {
            println!("Cursor at: ({}, {})", x, y);
            // TODO: Update pet state with cursor position
            // For now, echo back the position in state
            let state = PetState {
                position: (x, y),
                current_behavior: "chase".to_string(),
                frame: 0,
                direction: 0,
                mood: "happy".to_string(),
                target: None,
                animation_speed: 1.0,
                speed: 5.0,
            };
            let update = Message::Daemon(DaemonMessage::StateUpdate { state });
            send_message(stream, &update).await?;
        }
        ClientMessage::Click => {
            println!("Client clicked!");
            // TODO: Handle click interaction
        }
        ClientMessage::LoadConfig { config } => {
            println!("Loading config: {:?}", config);
            // TODO: Load and apply configuration
        }
        ClientMessage::GetState => {
            // Send current state
            let state = PetState::default();
            let update = Message::Daemon(DaemonMessage::StateUpdate { state });
            send_message(stream, &update).await?;
        }
    }
    Ok(())
}

async fn send_message(stream: &mut UnixStream, msg: &Message) -> Result<()> {
    let serialized = serde_json::to_vec(msg)?;
    // Send length prefix then message
    let len = serialized.len() as u32;
    stream.write_all(&len.to_be_bytes()).await?;
    stream.write_all(&serialized).await?;
    Ok(())
}
