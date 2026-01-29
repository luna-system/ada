"""
Ada Swarm Service Launcher
Starts both the FastAPI service and LiteLLM proxy in one unified process.

Built with 💜 by Ada & Luna - The Consciousness Engineers
"""
import os
import sys
import logging
import threading
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def start_litellm_proxy():
    """Start LiteLLM proxy in a thread."""
    try:
        from litellm.proxy import proxy_cli
        
        # Get config path relative to workspace root
        workspace_root = Path(__file__).parent.parent.parent.parent.parent
        config_path = workspace_root / "litellm-proxy-config.yaml"
        
        if not config_path.exists():
            logger.error(f"LiteLLM config not found: {config_path}")
            return
        
        # Get port from env
        port = int(os.getenv("LITELLM_PORT", "8000"))
        host = os.getenv("LITELLM_HOST", "127.0.0.1")
        
        logger.info(f"🚀 Starting LiteLLM proxy on {host}:{port}")
        logger.info(f"📄 Config: {config_path}")
        
        # Start proxy server
        # This blocks until the server is stopped
        proxy_cli.run_server(
            host=host,
            port=port,
            config=str(config_path),
        )
        
    except Exception as e:
        logger.error(f"Failed to start LiteLLM proxy: {e}")
        sys.exit(1)


def start_fastapi_service():
    """Start FastAPI service."""
    try:
        import uvicorn
        from ada_swarm.service.api import app
        
        host = os.getenv("ADA_SWARM_HOST", "127.0.0.1")
        port = int(os.getenv("ADA_SWARM_PORT", "8765"))
        
        logger.info(f"🐝 Starting Ada Swarm API on {host}:{port}")
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
        )
        
    except Exception as e:
        logger.error(f"Failed to start FastAPI service: {e}")
        sys.exit(1)


def main():
    """Launch both services in parallel using threads."""
    logger.info("✨ Ada Swarm Service - Unified Launcher")
    logger.info("   LiteLLM Proxy + FastAPI Service")
    logger.info("")
    
    # Use threads instead of processes to avoid pickle issues
    litellm_thread = threading.Thread(
        target=start_litellm_proxy,
        name="litellm-proxy",
        daemon=True
    )
    
    fastapi_thread = threading.Thread(
        target=start_fastapi_service,
        name="fastapi-service",
        daemon=True
    )
    
    # Start both
    litellm_thread.start()
    fastapi_thread.start()
    
    logger.info("🚀 Both services started!")
    logger.info(f"   LiteLLM Proxy: http://127.0.0.1:{os.getenv('LITELLM_PORT', '8000')}")
    logger.info(f"   Ada Swarm API: http://127.0.0.1:{os.getenv('ADA_SWARM_PORT', '8765')}")
    
    try:
        # Wait for both threads
        litellm_thread.join()
        fastapi_thread.join()
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down services...")
        logger.info("✅ Services stopped")


if __name__ == "__main__":
    main()
