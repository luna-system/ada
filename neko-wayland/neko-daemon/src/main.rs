use neko_daemon::ipc::run_ipc_server;
use anyhow::Result;

#[tokio::main]
async fn main() -> Result<()> {
    println!("Neko Daemon starting...");
    run_ipc_server().await?;
    println!("Neko Daemon stopped.");
    Ok(())
}
