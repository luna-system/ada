"""Now Playing Specialist - Detects currently playing media.

This specialist queries the system (via MPRIS on Linux) to determine what
music or media is currently playing. Useful for context-aware responses.

@ai-indexable: specialist-plugin
@ai-purpose: Detect and report currently playing media via MPRIS
@ai-activation-trigger: User asks about music, media, or "what's playing"
@ai-priority: MEDIUM
"""
import asyncio
import logging
import re
from typing import Optional

from brain.specialists.protocol import (
    Specialist,
    SpecialistCapability,
    SpecialistResult,
    SpecialistPriority
)

logger = logging.getLogger(__name__)


class NowPlayingSpecialist:
    """Specialist for detecting currently playing media."""
    
    def __init__(self):
        self._capability = SpecialistCapability(
            name="now_playing",
            description="Detects currently playing music or media via MPRIS",
            version="1.0.0",
            context_priority=SpecialistPriority.MEDIUM,
            context_icon="🎵",
            tags=["media", "music", "system"],
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Optional search query"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "playing": {"type": "boolean"},
                    "title": {"type": "string"},
                    "artist": {"type": "string"},
                    "album": {"type": "string"},
                    "player": {"type": "string"}
                }
            }
        )
    
    @property
    def capability(self) -> SpecialistCapability:
        """Return specialist metadata."""
        return self._capability
    
    def should_activate(self, request_context: dict) -> bool:
        """
        Activate when user asks about music or media.
        
        Looks for keywords like:
        - "what am I listening to"
        - "what's playing"
        - "current song"
        - "now playing"
        """
        prompt = request_context.get("prompt", "").lower()
        
        # Keywords that suggest user wants to know what's playing
        keywords = [
            "listening to",
            "what's playing",
            "what is playing",
            "current song",
            "current track",
            "now playing",
            "what song",
            "what music",
            "playing now",
            "song playing"
        ]
        
        return any(keyword in prompt for keyword in keywords)
    
    async def process(self, **kwargs) -> SpecialistResult:
        """
        Query MPRIS for currently playing media.
        
        Returns:
            SpecialistResult with formatted context about current media
        """
        try:
            # Get player status
            status = await self._get_player_status()
            
            if not status:
                return SpecialistResult(
                    success=True,
                    specialist_name="now_playing",
                    context_text="🎵 **Media Status:** No music is currently playing.",
                    data={"playing": False}
                )
            
            # Format context for LLM with rich markdown
            context_lines = ["## 🎵 Now Playing"]
            context_lines.append("")  # Blank line for markdown
            
            if status.get("title"):
                context_lines.append(f"**{status['title']}**")
            if status.get("artist"):
                context_lines.append(f"*by {status['artist']}*")
            if status.get("album"):
                context_lines.append(f"📀 Album: *{status['album']}*")
            
            context_lines.append("")  # Blank line
            
            if status.get("player"):
                context_lines.append(f"🎧 Playing in: `{status['player']}`")
            
            # Hint to encourage contextual reasoning
            context_lines.append("")
            context_lines.append("---")
            context_lines.append("💡 *Consider: What can you tell Luna about this track, artist, or album based on your knowledge?*")
            
            context_text = "\n".join(context_lines)
            
            return SpecialistResult(
                success=True,
                specialist_name="now_playing",
                context_text=context_text,
                data=status,
                metadata={"source": "mpris"}
            )
        
        except Exception as e:
            logger.error(f"Error getting now playing info: {e}", exc_info=True)
            return SpecialistResult(
                success=False,
                specialist_name="now_playing",
                error=str(e),
                error_code="QUERY_FAILED"
            )
    
    async def _get_player_status(self) -> Optional[dict]:
        """
        Query playerctl for current media status.
        
        Returns:
            Dict with player status, or None if nothing playing
        """
        try:
            # Check if anything is playing
            proc = await asyncio.create_subprocess_exec(
                "playerctl", "status",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                # Nothing playing or no players available
                return None
            
            status_text = stdout.decode().strip()
            
            # Only proceed if actually playing
            if status_text.lower() != "playing":
                return None
            
            # Get metadata
            metadata = {}
            
            # Get title
            proc = await asyncio.create_subprocess_exec(
                "playerctl", "metadata", "title",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            if proc.returncode == 0:
                metadata["title"] = stdout.decode().strip()
            
            # Get artist
            proc = await asyncio.create_subprocess_exec(
                "playerctl", "metadata", "artist",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            if proc.returncode == 0:
                metadata["artist"] = stdout.decode().strip()
            
            # Get album
            proc = await asyncio.create_subprocess_exec(
                "playerctl", "metadata", "album",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            if proc.returncode == 0:
                metadata["album"] = stdout.decode().strip()
            
            # Get player name
            proc = await asyncio.create_subprocess_exec(
                "playerctl", "metadata", "xesam:playerName",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            if proc.returncode == 0:
                player_name = stdout.decode().strip()
                metadata["player"] = player_name if player_name else "Unknown"
            
            metadata["playing"] = True
            return metadata if metadata else None
        
        except FileNotFoundError:
            logger.warning("playerctl not found - install with: sudo apt install playerctl")
            return None
        except Exception as e:
            logger.error(f"Error querying playerctl: {e}")
            return None
