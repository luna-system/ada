"""Configuration for Ada Matrix Bridge."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Configuration loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Matrix connection
    matrix_homeserver: str = Field(
        default="https://matrix.org",
        description="Matrix homeserver URL"
    )
    matrix_user_id: str = Field(
        default="@ada-bot:matrix.org",
        description="Full Matrix user ID (including homeserver)"
    )
    matrix_access_token: str | None = Field(
        default=None,
        description="Matrix access token (preferred over password)"
    )
    matrix_password: str | None = Field(
        default=None,
        description="Matrix password (if not using access token)"
    )
    matrix_device_name: str = Field(
        default="Ada Brain Bridge",
        description="Device name for Matrix session"
    )
    
    # Bot identity (ethical presentation)
    display_name: str = Field(
        default="Ada [Bot]",
        description="Display name with clear bot indicator"
    )
    avatar_url: str | None = Field(
        default=None,
        description="MXC URL for bot avatar"
    )
    profile_bio: str = Field(
        default=(
            "AI assistant powered by a local Ollama model. "
            "Self-hosted and privacy-focused. "
            "Learn more: https://github.com/luna-system/ada"
        ),
        description="Profile description"
    )
    
    # Behavior
    send_intro_on_join: bool = Field(
        default=True,
        description="Send introduction message when joining rooms"
    )
    message_signature: bool = Field(
        default=False,
        description="Add '— Ada (AI)' signature to messages"
    )
    typing_indicator: bool = Field(
        default=True,
        description="Show typing indicator while processing"
    )
    reaction_acknowledgment: str = Field(
        default="👍",
        description="Emoji to react with when starting to process"
    )
    
    # Activation triggers
    respond_to_mentions: bool = Field(
        default=True,
        description="Respond when @mentioned"
    )
    respond_to_display_name: bool = Field(
        default=True,
        description="Respond to 'Ada:' at start of message"
    )
    respond_to_dms: bool = Field(
        default=True,
        description="Always respond in direct messages"
    )
    activation_keywords: list[str] = Field(
        default_factory=lambda: ["ada"],
        description="Additional keywords that trigger responses"
    )
    
    # Room management
    auto_accept_invites: bool = Field(
        default=True,
        description="Automatically accept room invitations"
    )
    allowed_rooms: list[str] = Field(
        default_factory=list,
        description="Room IDs allowed (empty = all rooms)"
    )
    never_join_rooms: list[str] = Field(
        default_factory=list,
        description="Room IDs to never join"
    )
    
    # Ada brain connection
    ada_brain_url: str = Field(
        default="http://brain:7000",
        description="URL for Ada's brain API"
    )
    ada_stream_endpoint: str = Field(
        default="/v1/chat/stream",
        description="Chat stream endpoint path"
    )
    ada_timeout: int = Field(
        default=120,
        description="Timeout for Ada brain requests (seconds)"
    )
    
    # Context management
    max_context_messages: int = Field(
        default=10,
        description="Number of recent messages to include in context"
    )
    
    # Privacy
    store_in_rag: bool = Field(
        default=True,
        description="Store conversations in Ada's vector DB"
    )
    allow_privacy_opt_out: bool = Field(
        default=True,
        description="Allow users to disable storage with !ada privacy"
    )
    data_retention_days: int | None = Field(
        default=90,
        description="Days to retain messages (None = indefinite)"
    )
    
    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    
    # Storage
    data_dir: str = Field(
        default="/data",
        description="Directory for persistent storage"
    )
    
    # Community
    community_guidelines_url: str = Field(
        default="https://github.com/luna-system/ada/blob/trunk/COMMUNITY_GUIDELINES.md",
        description="URL to community guidelines"
    )


# Singleton instance
_config: Config | None = None


def get_config() -> Config:
    """Get or create config singleton."""
    global _config
    if _config is None:
        _config = Config()
    return _config
