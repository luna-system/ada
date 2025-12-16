"""Ada Matrix Bridge - Main bot logic."""

import asyncio
import logging
import sys
from pathlib import Path

from nio import (
    AsyncClient,
    InviteEvent,
    MatrixRoom,
    RoomMessageText,
    LoginResponse,
    SyncResponse
)

from ada_client import AdaBrainClient
from config import Config, get_config
from identity import get_intro_message, setup_bot_profile, should_send_intro
from message_handler import MessageHandler, RoomContextManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class AdaMatrixBridge:
    """Matrix bridge for Ada - connects Matrix chat to Ada's brain."""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = AsyncClient(config.matrix_homeserver, config.matrix_user_id)
        self.ada = AdaBrainClient(config)
        self.context_manager = RoomContextManager(config)
        self.message_handler = MessageHandler(config, config.matrix_user_id)
        
        # Track which rooms we've sent intro to
        self.sent_intros: set[str] = set()
        
        # Register callbacks
        self.client.add_event_callback(self.on_message, RoomMessageText)
        self.client.add_event_callback(self.on_invite, InviteEvent)
    
    async def on_invite(self, room: MatrixRoom, event: InviteEvent):
        """Handle room invitations."""
        room_id = room.room_id
        inviter = event.sender
        
        logger.info(f"Invited to {room_id} by {inviter}")
        
        # Check if room is on never-join list
        if room_id in self.config.never_join_rooms:
            logger.info(f"Room {room_id} is on never-join list, declining")
            await self.client.room_leave(room_id)
            return
        
        # Check if room is allowed (if allowlist exists)
        if self.config.allowed_rooms and room_id not in self.config.allowed_rooms:
            logger.info(f"Room {room_id} not in allowed list, declining")
            await self.client.room_leave(room_id)
            return
        
        # Auto-accept if configured
        if self.config.auto_accept_invites:
            logger.info(f"Auto-accepting invitation to {room_id}")
            await self.client.join(room_id)
            
            # Send introduction
            if self.config.send_intro_on_join:
                await self.send_intro(room_id)
        else:
            logger.info(f"Auto-accept disabled, ignoring invitation")
    
    async def send_intro(self, room_id: str):
        """Send introduction message to a room."""
        if should_send_intro(room_id, self.sent_intros):
            intro = get_intro_message(self.config)
            await self.client.room_send(
                room_id=room_id,
                message_type="m.room.message",
                content={
                    "msgtype": "m.text",
                    "body": intro
                }
            )
            self.sent_intros.add(room_id)
            logger.info(f"Sent introduction to {room_id}")
    
    async def on_message(self, room: MatrixRoom, event: RoomMessageText):
        """Handle incoming Matrix messages."""
        sender = event.sender
        message = event.body
        room_id = room.room_id
        
        # Skip if message is from ourselves
        if sender == self.client.user:
            return
        
        logger.debug(f"Message from {sender} in {room.display_name}: {message[:50]}...")
        
        # Check for commands first
        command, args = self.message_handler.parse_command(message)
        if command:
            await self.handle_command(room_id, sender, command, args)
            return
        
        # Check if we should respond
        if not self.message_handler.should_respond(message, room, sender):
            # Still store in context even if not responding
            self.context_manager.add_message(room_id, sender, message, is_bot=False)
            return
        
        logger.info(f"Responding to {sender} in {room.display_name}")
        
        # Show typing indicator
        if self.config.typing_indicator:
            await self.client.room_typing(room_id, True)
        
        # React to acknowledge (optional)
        if self.config.reaction_acknowledgment:
            try:
                await self.client.room_send(
                    room_id=room_id,
                    message_type="m.reaction",
                    content={
                        "m.relates_to": {
                            "rel_type": "m.annotation",
                            "event_id": event.event_id,
                            "key": self.config.reaction_acknowledgment
                        }
                    }
                )
            except Exception as e:
                logger.debug(f"Failed to send reaction: {e}")
        
        try:
            # Get conversation context
            context = self.context_manager.get_context(room_id)
            
            # Add current message to context
            self.context_manager.add_message(room_id, sender, message, is_bot=False)
            
            # Query Ada's brain (streaming)
            response_chunks = []
            async for chunk in self.ada.chat_stream(
                message=message,
                user_id=sender,
                room_id=room_id,
                conversation_history=context
            ):
                response_chunks.append(chunk)
            
            response = "".join(response_chunks)
            
            # Store Ada's response in context
            self.context_manager.add_message(room_id, self.client.user, response, is_bot=True)
            
            # Send response to Matrix
            await self.client.room_send(
                room_id=room_id,
                message_type="m.room.message",
                content={
                    "msgtype": "m.text",
                    "body": response,
                    "format": "org.matrix.custom.html",
                    "formatted_body": self.markdown_to_html(response)
                }
            )
            
            logger.info(f"Sent response to {room.display_name}")
        
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            error_msg = "Sorry, I encountered an error processing that message."
            await self.client.room_send(
                room_id=room_id,
                message_type="m.room.message",
                content={
                    "msgtype": "m.text",
                    "body": error_msg
                }
            )
        
        finally:
            # Stop typing indicator
            if self.config.typing_indicator:
                await self.client.room_typing(room_id, False)
    
    async def handle_command(self, room_id: str, sender: str, command: str, args: list[str]):
        """Handle !ada commands."""
        logger.info(f"Command from {sender}: !ada {command} {args}")
        
        response = None
        
        if command == "privacy":
            if not self.config.allow_privacy_opt_out:
                response = "Privacy commands are disabled on this instance."
            elif not args or args[0] == "status":
                response = self.context_manager.get_privacy_status(room_id)
            elif args[0] == "off":
                self.context_manager.set_privacy(room_id, False)
                response = "✅ Privacy mode enabled. I will no longer store messages from this room in my memory."
            elif args[0] == "on":
                self.context_manager.set_privacy(room_id, True)
                response = "✅ Memory storage enabled. I will remember our conversations in this room for context."
            else:
                response = "Usage: !ada privacy [on|off|status]"
        
        elif command == "clear":
            self.context_manager.clear_context(room_id)
            response = "✅ Cleared conversation context for this room."
        
        elif command == "help":
            response = """**Available commands:**
• !ada privacy on/off/status - Manage memory storage
• !ada clear - Clear conversation context
• !ada help - Show this help
• !ada status - Show system status

**To talk to me:** Just @mention me or start your message with "Ada:"
"""
        
        elif command == "status":
            brain_healthy = await self.ada.healthcheck()
            status = "✅ online" if brain_healthy else "❌ offline"
            response = f"""**Ada Status:**
• Brain: {status}
• Rooms: {len(self.client.rooms)}
• Memory: {"Enabled" if self.config.store_in_rag else "Disabled"}
• Version: 1.0.0-alpha
"""
        
        else:
            response = f"Unknown command: {command}. Try !ada help"
        
        if response:
            await self.client.room_send(
                room_id=room_id,
                message_type="m.room.message",
                content={
                    "msgtype": "m.text",
                    "body": response
                }
            )
    
    def markdown_to_html(self, text: str) -> str:
        """Convert basic markdown to HTML for Matrix."""
        # Simple conversions (enhance later with markdown library if needed)
        html = text.replace("\n", "<br/>")
        # Could add more sophisticated markdown parsing here
        return html
    
    async def start(self):
        """Start the bridge."""
        logger.info("=" * 60)
        logger.info("Starting Ada Matrix Bridge")
        logger.info("=" * 60)
        logger.info(f"Homeserver: {self.config.matrix_homeserver}")
        logger.info(f"User: {self.config.matrix_user_id}")
        logger.info(f"Display name: {self.config.display_name}")
        logger.info(f"Ada brain: {self.config.ada_brain_url}")
        
        # Check Ada brain health
        logger.info("Checking Ada brain health...")
        healthy = await self.ada.healthcheck()
        if healthy:
            logger.info("✅ Ada brain is healthy")
        else:
            logger.warning("⚠️  Ada brain is not responding (will retry during operation)")
        
        # Login
        logger.info("Logging in to Matrix...")
        if self.config.matrix_access_token:
            self.client.access_token = self.config.matrix_access_token
            self.client.user_id = self.config.matrix_user_id
            logger.info("Using provided access token")
        elif self.config.matrix_password:
            response = await self.client.login(self.config.matrix_password)
            if isinstance(response, LoginResponse):
                logger.info(f"✅ Logged in as {response.user_id}")
            else:
                logger.error(f"❌ Login failed: {response}")
                return
        else:
            logger.error("❌ No access token or password provided")
            return
        
        # Set up profile
        logger.info("Setting up bot profile...")
        await setup_bot_profile(self.client, self.config)
        logger.info(f"✅ Profile set: {self.config.display_name}")
        
        # Initial sync
        logger.info("Performing initial sync...")
        sync_response = await self.client.sync(timeout=30000)
        if isinstance(sync_response, SyncResponse):
            logger.info(f"✅ Synced. In {len(self.client.rooms)} rooms")
        
        # Start sync loop
        logger.info("=" * 60)
        logger.info("🤖 Ada is now online and listening")
        logger.info("=" * 60)
        
        try:
            await self.client.sync_forever(timeout=30000, full_state=True)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
        except Exception as e:
            logger.error(f"Sync loop error: {e}", exc_info=True)
        finally:
            await self.client.close()
            logger.info("Bridge shut down")


async def main():
    """Main entry point."""
    config = get_config()
    
    # Set log level from config
    logging.getLogger().setLevel(getattr(logging, config.log_level.upper()))
    
    bridge = AdaMatrixBridge(config)
    await bridge.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown complete")
