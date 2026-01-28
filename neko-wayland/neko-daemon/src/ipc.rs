use tokio::{
    io::{AsyncReadExt, AsyncWriteExt},
    net::{UnixListener, UnixStream},
};
use serde::{Serialize, Deserialize};
use anyhow::Result;

const SOCKET_PATH: &str = "/tmp/neko-daemon.sock";

#[derive(Debug, Serialize, Deserialize)]
pub enum Message {
    Connect,
    Disconnect,
    CursorPosition { x: f64, y: f64 },
    StateUpdate { state: String }, // Placeholder for now
}

pub async fn run_ipc_server() -> Result<()> {
    // Remove the socket file if it already exists
    if tokio::fs::metadata(SOCKET_PATH).await.is_ok() {
        tokio::fs::remove_file(SOCKET_PATH).await?;
    }

    let listener = UnixListener::bind(SOCKET_PATH)?;
    println!("Listening on {}", SOCKET_PATH);

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
    loop {
        let n = stream.read(&mut buffer).await?;
        if n == 0 {
            // EOF, client disconnected
            println!("Client disconnected.");
            break;
        }

        let message: Message = serde_json::from_slice(&buffer[..n])?;
        println!("Received message: {:?}", message);

        // Simple response for now
        let response = Message::StateUpdate { state: "Acknowledged".to_string() };
        let serialized_response = serde_json::to_vec(&response)?;
        stream.write_all(&serialized_response).await?;
    }
    Ok(())
}
