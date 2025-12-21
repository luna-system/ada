"""Bot identity and transparency helpers."""

from config import Config


def get_intro_message(config: Config) -> str:
    """Get introduction message for new rooms."""
    return f"""👋 Hi! I'm {config.display_name}, an AI assistant running on this community's self-hosted infrastructure.

**What I do:**
• Respond to @{config.matrix_user_id.split(':')[0]} mentions and direct messages
• Maintain conversation context within rooms
• Powered by a local Ollama model (no external APIs)

**Privacy:**
• All conversations stored locally in encrypted vector database
• No data sent to external services
• You can opt out of memory storage: !ada privacy off

**Community Guidelines:** {config.community_guidelines_url}
**Remove me:** Just kick me from the room anytime!

Learn more: https://github.com/luna-system/ada
"""


def format_message_with_signature(text: str, config: Config) -> str:
    """Add signature to message if configured."""
    if config.message_signature:
        return f"{text}\n\n— {config.display_name} (AI Assistant)"
    return text


def should_send_intro(room_id: str, sent_intros: set[str]) -> bool:
    """Check if we should send intro message to this room."""
    return room_id not in sent_intros


async def setup_bot_profile(client, config: Config) -> None:
    """Configure bot profile for transparency.
    
    Args:
        client: Matrix AsyncClient instance
        config: Configuration
    """
    # Set display name
    await client.set_displayname(config.display_name)
    
    # Set avatar if provided
    if config.avatar_url:
        await client.set_avatar(config.avatar_url)
    
    # Note: Profile bio and bot flag are homeserver-specific
    # Some homeservers support these via account_data or profile extensions
    # For now, we rely on display name and intro messages for transparency
