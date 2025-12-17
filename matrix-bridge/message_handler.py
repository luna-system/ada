"""Message processing and context management."""

import json
import logging
from pathlib import Path
from typing import Any

from nio import MatrixRoom

from config import Config

logger = logging.getLogger(__name__)


class RoomContextManager:
    """Manage conversation context per room."""
    
    def __init__(self, config: Config):
        self.config = config
        self.contexts: dict[str, list[dict]] = {}
        self.privacy_settings: dict[str, bool] = {}  # room_id -> store_messages
        self.storage_path = Path(config.data_dir) / "room_contexts.json"
        self.privacy_path = Path(config.data_dir) / "privacy_settings.json"
        
        # Load from disk
        self.load()
    
    def add_message(self, room_id: str, sender: str, message: str, is_bot: bool = False):
        """Add a message to room context."""
        # Check privacy settings
        if not self.privacy_settings.get(room_id, True):
            logger.debug(f"Privacy mode enabled for {room_id}, not storing message")
            return
        
        if room_id not in self.contexts:
            self.contexts[room_id] = []
        
        self.contexts[room_id].append({
            "role": "assistant" if is_bot else "user",
            "content": message,
            "sender": sender
        })
        
        # Keep only recent messages
        max_messages = self.config.max_context_messages
        self.contexts[room_id] = self.contexts[room_id][-max_messages:]
        
        # Persist
        self.save()
    
    def get_context(self, room_id: str) -> list[dict]:
        """Get conversation context for room."""
        return self.contexts.get(room_id, [])
    
    def clear_context(self, room_id: str):
        """Clear context for a room."""
        if room_id in self.contexts:
            del self.contexts[room_id]
            self.save()
    
    def set_privacy(self, room_id: str, store_messages: bool):
        """Set privacy mode for a room."""
        self.privacy_settings[room_id] = store_messages
        self.save_privacy()
        
        # If disabling, clear existing context
        if not store_messages:
            self.clear_context(room_id)
    
    def get_privacy_status(self, room_id: str) -> str:
        """Get human-readable privacy status."""
        enabled = self.privacy_settings.get(room_id, True)
        if enabled:
            return "Memory storage ENABLED (I remember our conversation)"
        else:
            return "Privacy mode ENABLED (I won't store messages from this room)"
    
    def save(self):
        """Save contexts to disk."""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, 'w') as f:
                json.dump(self.contexts, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save contexts: {e}")
    
    def save_privacy(self):
        """Save privacy settings to disk."""
        try:
            self.privacy_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.privacy_path, 'w') as f:
                json.dump(self.privacy_settings, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save privacy settings: {e}")
    
    def load(self):
        """Load contexts from disk."""
        try:
            if self.storage_path.exists():
                with open(self.storage_path) as f:
                    self.contexts = json.load(f)
                logger.info(f"Loaded context for {len(self.contexts)} rooms")
        except Exception as e:
            logger.error(f"Failed to load contexts: {e}")
        
        try:
            if self.privacy_path.exists():
                with open(self.privacy_path) as f:
                    self.privacy_settings = json.load(f)
                logger.info(f"Loaded privacy settings for {len(self.privacy_settings)} rooms")
        except Exception as e:
            logger.error(f"Failed to load privacy settings: {e}")


class MessageHandler:
    """Handle incoming Matrix messages."""
    
    def __init__(self, config: Config, bot_user_id: str):
        self.config = config
        self.bot_user_id = bot_user_id
    
    def should_respond(self, message: str, room: MatrixRoom, sender: str) -> bool:
        """
        Check if Ada should respond to this message.
        
        Args:
            message: Message text
            room: Matrix room
            sender: Sender user ID
            
        Returns:
            True if Ada should respond
        """
        # Don't respond to own messages
        if sender == self.bot_user_id:
            return False
        
        # Always respond to DMs (2 members = user + bot)
        if self.config.respond_to_dms and len(room.users) == 2:
            return True
        
        message_lower = message.lower()
        
        # Respond to @mentions
        if self.config.respond_to_mentions and self.bot_user_id in message:
            return True
        
        # Respond to display name at start
        if self.config.respond_to_display_name:
            display_lower = self.config.display_name.lower()
            if message_lower.startswith(display_lower):
                return True
            if message_lower.startswith(f"{display_lower}:"):
                return True
        
        # Respond to keywords
        for keyword in self.config.activation_keywords:
            if keyword.lower() in message_lower:
                return True
        
        return False
    
    def parse_command(self, message: str) -> tuple[str | None, list[str]]:
        """
        Parse !ada commands.
        
        Args:
            message: Message text
            
        Returns:
            Tuple of (command, args) or (None, []) if not a command
        """
        if not message.startswith("!ada "):
            return None, []
        
        parts = message[5:].strip().split()
        if not parts:
            return None, []
        
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        return command, args
