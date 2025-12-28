"""
DateTime Specialist - Simple system datetime lookup for testing specialist system.

Provides current system time when Ada needs to know "what time is it" or similar.
Perfect for testing if the specialist system works without web dependencies!
"""
# @ai-indexable: specialist-plugin
# @ai-purpose: Get current system datetime when LLM asks about time/date
# @ai-activation-trigger: Bidirectional - LLM requests datetime info during generation
# @ai-priority: HIGH
# @ai-dependencies: None (uses system datetime)
# @ai-related: brain/specialists/bidirectional.py
# @ai-tool-use-pattern: LLM emits request → specialist executes → current time returned

import logging
import datetime
from typing import Dict, Any, Optional
from brain.specialists.protocol import (
    BaseSpecialist,
    SpecialistCapability, 
    SpecialistResult,
    SpecialistPriority
)

logger = logging.getLogger(__name__)


class DateTimeSpecialist(BaseSpecialist):
    """
    Simple datetime specialist for testing specialist system.
    
    Provides current system time when Ada asks about time, date, or "what time is it".
    Perfect for debugging the specialist architecture without web dependencies.
    """
    
    def __init__(self):
        """Initialize datetime specialist."""
        self._capability = SpecialistCapability(
            name="datetime",
            description="Get current system date and time",
            version="1.0.0",
            input_schema={
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string", 
                        "description": "Datetime format (iso, human, unix)",
                        "default": "human"
                    }
                },
                "required": []
            },
            output_schema={
                "type": "object",
                "properties": {
                    "current_datetime": {"type": "string"},
                    "format": {"type": "string"},
                    "timezone": {"type": "string"}
                }
            },
            context_priority=SpecialistPriority.HIGH,
            context_icon="🕐",
            tags=["time", "date", "current", "system"]
        )
    
    @property
    def capability(self) -> SpecialistCapability:
        """Return specialist capability metadata."""
        return self._capability
    
    async def process(self, format: str = "human", **kwargs) -> SpecialistResult:
        """
        Get current system datetime.
        
        Args:
            format: Output format - "human", "iso", or "unix"
            **kwargs: Additional parameters (ignored)
            
        Returns:
            SpecialistResult with current datetime information
        """
        try:
            now = datetime.datetime.now()
            
            if format == "iso":
                datetime_str = now.isoformat()
            elif format == "unix":
                datetime_str = str(int(now.timestamp()))
            else:  # human (default)
                datetime_str = now.strftime("%A, %B %d, %Y at %I:%M:%S %p")
            
            timezone_str = now.astimezone().tzname() or "Local"
            
            context_text = f"🕐 **Current System Time**\n"
            context_text += f"**Date & Time:** {datetime_str}\n"
            context_text += f"**Timezone:** {timezone_str}\n"
            context_text += f"**Unix Timestamp:** {int(now.timestamp())}\n"
            
            return SpecialistResult(
                specialist_name="datetime",
                context_text=context_text,
                success=True,
                metadata={
                    "current_datetime": datetime_str,
                    "format": format,
                    "timezone": timezone_str,
                    "unix_timestamp": int(now.timestamp())
                }
            )
            
        except Exception as e:
            logger.error(f"DateTime specialist error: {e}")
            return SpecialistResult(
                specialist_name="datetime",
                context_text="",
                success=False,
                error=f"Failed to get current time: {str(e)}"
            )
    
    def should_activate(self, request_context: dict) -> bool:
        """
        Determine if this specialist should activate for datetime requests.
        
        Args:
            request_context: Request metadata dict
            
        Returns:
            True if request seems to be asking about current time/date
        """
        prompt = request_context.get('prompt', '').lower()
        
        # Look for time/date related keywords
        time_keywords = [
            'what time', 'current time', 'time is it',
            'what date', 'current date', 'today is', 
            'datetime', 'timestamp', 'now is'
        ]
        
        # Activate if prompt contains any time-related keywords
        return any(keyword in prompt for keyword in time_keywords)
