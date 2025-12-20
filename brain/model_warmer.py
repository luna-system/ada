"""
Adaptive Model Warming - Biomimetic Feature

Like motor cortex pre-activation, keeps models loaded when adapters
are actively connected, allowing fast response times (<200ms TTFT).

Neuroscience parallel:
- Motor preparation: Brain pre-fires neurons before movement
- Ada: Pre-warm models when adapters connect

December 2025 - luna-system
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Dict, Set, Optional
import httpx
import logging
from brain.config import OLLAMA_BASE_URL, OLLAMA_MODEL

logger = logging.getLogger(__name__)


@dataclass
class AdapterSession:
    """Active adapter session with preferred model."""
    adapter_id: str
    adapter_type: str  # 'vscode', 'cli', 'web', 'mcp', 'matrix'
    preferred_model: str
    connected_at: datetime
    last_activity: datetime
    keep_alive_duration: timedelta
    
    def to_dict(self):
        """Convert to JSON-serializable dict."""
        return {
            'adapter_id': self.adapter_id,
            'adapter_type': self.adapter_type,
            'preferred_model': self.preferred_model,
            'connected_at': self.connected_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'keep_alive_seconds': int(self.keep_alive_duration.total_seconds()),
        }


class ModelWarmer:
    """
    Biomimetic model warming based on active adapter sessions.
    
    Automatically manages which models stay loaded based on:
    - Which adapters are currently connected
    - Each adapter's preferred model
    - Session activity (heartbeat mechanism)
    
    Example:
        warmer = ModelWarmer()
        warmer.register_adapter("vscode-abc123", "vscode")
        # qwen2.5-coder:7b is now warm with 4h keep_alive
        
        warmer.register_adapter("web-xyz789", "web")
        # mistral:7b is also now warm with 2h keep_alive
        
        warmer.unregister_adapter("vscode-abc123")
        # qwen may cool down if no other sessions need it
    """
    
    # Adapter type → (model, keep_alive_duration)
    MODEL_PROFILES = {
        'vscode': ('qwen2.5-coder:7b', timedelta(hours=4)),
        'cli': ('qwen2.5-coder:7b', timedelta(hours=1)),
        'web': ('mistral:7b', timedelta(hours=2)),
        'mcp': ('qwen2.5-coder:7b', timedelta(hours=4)),
        'matrix': ('llama3.2:3b', timedelta(minutes=30)),
    }
    
    def __init__(self, ollama_base_url: str = OLLAMA_BASE_URL):
        self.active_sessions: Dict[str, AdapterSession] = {}
        self.ollama_base_url = ollama_base_url
        logger.info(f"ModelWarmer initialized with Ollama at {ollama_base_url}")
    
    def register_adapter(self, adapter_id: str, adapter_type: str) -> dict:
        """
        Register an adapter connection and warm its preferred model.
        
        Args:
            adapter_id: Unique session ID (e.g., "vscode-abc123")
            adapter_type: Type of adapter ('vscode', 'cli', 'web', etc.)
        
        Returns:
            dict with warm_model and keep_alive info
        """
        model, keep_alive = self.MODEL_PROFILES.get(
            adapter_type, 
            (OLLAMA_MODEL, timedelta(hours=1))
        )
        
        session = AdapterSession(
            adapter_id=adapter_id,
            adapter_type=adapter_type,
            preferred_model=model,
            connected_at=datetime.now(),
            last_activity=datetime.now(),
            keep_alive_duration=keep_alive
        )
        
        self.active_sessions[adapter_id] = session
        logger.info(f"Registered {adapter_type} adapter {adapter_id} → warming {model}")
        
        # Warm the model
        self._warm_model(model, keep_alive)
        
        return {
            'adapter_id': adapter_id,
            'warm_model': model,
            'keep_alive': str(keep_alive),
        }
    
    def unregister_adapter(self, adapter_id: str) -> dict:
        """
        Remove adapter and potentially cool down its model.
        
        Args:
            adapter_id: Session ID to remove
        
        Returns:
            dict with status
        """
        if adapter_id not in self.active_sessions:
            return {'status': 'not_found', 'adapter_id': adapter_id}
        
        session = self.active_sessions[adapter_id]
        model = session.preferred_model
        del self.active_sessions[adapter_id]
        
        logger.info(f"Unregistered {session.adapter_type} adapter {adapter_id}")
        
        # Check if any other sessions need this model
        required_models = self.get_required_models()
        if model not in required_models:
            logger.info(f"No more sessions need {model}, allowing cooldown")
            # Model will naturally cool down after its keep_alive expires
            # We don't forcefully unload it (let Ollama manage)
        
        return {
            'status': 'unregistered',
            'adapter_id': adapter_id,
            'model_still_needed': model in required_models,
        }
    
    def heartbeat(self, adapter_id: str) -> dict:
        """
        Update last activity timestamp for an adapter.
        
        Args:
            adapter_id: Session ID
        
        Returns:
            dict with status
        """
        if adapter_id not in self.active_sessions:
            return {'status': 'not_found', 'adapter_id': adapter_id}
        
        self.active_sessions[adapter_id].last_activity = datetime.now()
        
        return {
            'status': 'ok',
            'adapter_id': adapter_id,
            'last_activity': self.active_sessions[adapter_id].last_activity.isoformat(),
        }
    
    def get_required_models(self) -> Set[str]:
        """Get set of models that should currently be warm."""
        return {session.preferred_model for session in self.active_sessions.values()}
    
    def get_warm_pool_status(self) -> dict:
        """
        Get current warm pool status.
        
        Returns:
            dict with active models, sessions, and adapter counts
        """
        required_models = self.get_required_models()
        
        # Group sessions by model
        models_info = {}
        for model in required_models:
            sessions = [s for s in self.active_sessions.values() if s.preferred_model == model]
            adapter_types = {}
            for session in sessions:
                adapter_types[session.adapter_type] = adapter_types.get(session.adapter_type, 0) + 1
            
            models_info[model] = {
                'session_count': len(sessions),
                'adapter_types': adapter_types,
                'reason': ', '.join(f"{t} ({c})" for t, c in adapter_types.items()),
            }
        
        # Count adapters by type
        adapter_counts = {}
        for session in self.active_sessions.values():
            adapter_counts[session.adapter_type] = adapter_counts.get(session.adapter_type, 0) + 1
        
        return {
            'active_models': [
                {
                    'name': model,
                    'session_count': info['session_count'],
                    'reason': info['reason'],
                }
                for model, info in models_info.items()
            ],
            'active_adapters': [
                {'type': adapter_type, 'count': count}
                for adapter_type, count in adapter_counts.items()
            ],
            'total_sessions': len(self.active_sessions),
        }
    
    def cleanup_stale_sessions(self, max_idle: timedelta = timedelta(hours=12)) -> int:
        """
        Remove sessions that haven't sent heartbeat in max_idle time.
        
        Args:
            max_idle: Maximum idle time before considering session stale
        
        Returns:
            Number of sessions cleaned up
        """
        now = datetime.now()
        stale = []
        
        for adapter_id, session in self.active_sessions.items():
            if now - session.last_activity > max_idle:
                stale.append(adapter_id)
        
        for adapter_id in stale:
            self.unregister_adapter(adapter_id)
        
        if stale:
            logger.info(f"Cleaned up {len(stale)} stale sessions: {stale}")
        
        return len(stale)
    
    def _warm_model(self, model: str, keep_alive: timedelta):
        """
        Send warming request to Ollama.
        
        Args:
            model: Model name (e.g., "qwen2.5-coder:7b")
            keep_alive: How long to keep model loaded
        """
        try:
            # Convert timedelta to Ollama format (e.g., "4h", "30m")
            seconds = int(keep_alive.total_seconds())
            if seconds >= 3600:
                keep_alive_str = f"{seconds // 3600}h"
            else:
                keep_alive_str = f"{seconds // 60}m"
            
            url = f"{self.ollama_base_url}/api/generate"
            payload = {
                'model': model,
                'prompt': 'Hello',  # Minimal prompt to load model
                'stream': False,
                'keep_alive': keep_alive_str,
            }
            
            logger.info(f"Warming {model} with keep_alive={keep_alive_str}")
            
            # Fire and forget - don't wait for response
            # (Model will load in background)
            with httpx.Client(timeout=2.0) as client:
                client.post(url, json=payload, timeout=2.0)
            
            logger.info(f"Model {model} warming initiated")
        except Exception as e:
            logger.warning(f"Failed to warm model {model}: {e}")
            # Don't fail the registration if warming fails
            # Model will load on first request anyway


# Global instance
_model_warmer: Optional[ModelWarmer] = None


def get_model_warmer() -> ModelWarmer:
    """Get or create global ModelWarmer instance."""
    global _model_warmer
    if _model_warmer is None:
        _model_warmer = ModelWarmer()
    return _model_warmer
