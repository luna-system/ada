"""
Media Specialist - Music/Media context from ListenBrainz.

Provides currently playing or recently listened music context.
"""
# @ai-indexable: specialist-plugin
# @ai-purpose: Inject music/media context from ListenBrainz into LLM prompts
# @ai-activation-trigger: media_info present in request context
# @ai-priority: MEDIUM
# @ai-dependencies: brain.media
# @ai-related: brain/media.py, brain/prompt_builder.py, brain/specialists/protocol.py
# @ai-extension-pattern: Inherits from BaseSpecialist, activated by request context keys

import logging
from typing import Any

from brain.media import format_media_for_prompt
from .protocol import (
    BaseSpecialist,
    SpecialistCapability,
    SpecialistResult,
    SpecialistPriority
)

logger = logging.getLogger(__name__)


class MediaSpecialist(BaseSpecialist):
    """
    Media specialist for injecting ListenBrainz music context.
    
    Auto-activates when media info is present in request.
    """
    
    def __init__(self):
        capability = SpecialistCapability(
            name="media",
            description="Inject currently playing or recently listened music from ListenBrainz",
            version="1.0.0",
            context_priority=SpecialistPriority.MEDIUM,
            context_icon="🎧",
            tags=["music", "listenbrainz", "media"],
            input_schema={
                "type": "object",
                "properties": {
                    "media": {
                        "type": "object",
                        "description": "Media info from ListenBrainz API"
                    }
                }
            }
        )
        super().__init__(capability)
    
    def should_activate(self, request_context: dict) -> bool:
        """Activate when media info is provided"""
        media = request_context.get('media')
        return media is not None and isinstance(media, dict)
    
    async def process(self, **kwargs) -> SpecialistResult:
        """
        Process media info and format for LLM consumption.
        
        Expected kwargs:
            media: dict with ListenBrainz data
        """
        media_info = kwargs.get('media')
        
        if not media_info:
            return self.error_result("No media info provided", "missing_context")
        
        try:
            # Use existing formatter
            media_line = format_media_for_prompt(media_info)
            
            if not media_line:
                return self.error_result("Could not format media info", "format_error")
            
            # Extract metadata for tracking
            metadata = {
                'status': media_info.get('status'),
                'track': media_info.get('track_name'),
                'artist': media_info.get('artist_name')
            }
            
            return self.success_result(
                context_text=media_line,
                data=media_info,
                metadata=metadata
            )
        
        except Exception as e:
            logger.error(f"Media specialist processing failed: {e}", exc_info=True)
            return self.error_result(f"Media processing error: {str(e)}", "processing_error")
