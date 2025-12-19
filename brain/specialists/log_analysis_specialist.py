"""
Log Analysis Specialist - Analyze uploaded log files.

Integrates ada-logs package into Ada's conversational interface.
Provides kid-friendly explanations of Minecraft crashes and other log errors.
"""
# @ai-indexable: specialist-plugin
# @ai-purpose: Analyze log files using biomimetic importance scoring
# @ai-activation-trigger: .log file upload or analyze_logs flag
# @ai-priority: MEDIUM
# @ai-dependencies: ada-logs package
# @ai-related: ada-logs/src/ada_logs/, brain/specialists/protocol.py

import logging
from typing import Any, Dict

from brain.specialists.protocol import (
    BaseSpecialist,
    SpecialistCapability,
    SpecialistResult,
    SpecialistPriority
)

# Import from ada-logs package
from ada_logs.parsers.minecraft import MinecraftParser

logger = logging.getLogger(__name__)


class LogAnalysisSpecialist(BaseSpecialist):
    """Analyze log files with biomimetic importance scoring.

    Uses ada-logs package to parse and explain log errors in kid-friendly language.
    Supports Minecraft crash logs initially, extensible to syslog, JSON logs, etc.
    """

    def __init__(self):
        capability = SpecialistCapability(
            name="log_analysis",
            description="Analyze log files with kid-friendly explanations",
            version="1.0.0",
            context_priority=SpecialistPriority.MEDIUM,
            context_icon="📊",
            tags=["logs", "analysis", "minecraft", "debugging", "kids"],
            input_schema={
                "type": "object",
                "properties": {
                    "file_content": {
                        "type": "string",
                        "description": "Raw log file content"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Name of the log file"
                    }
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "error_type": {"type": "string"},
                    "confidence": {"type": "number"},
                    "kid_explanation": {"type": "string"},
                    "fix": {"type": "string"},
                    "difficulty": {"type": "string"},
                    "conflicting_mods": {"type": "array"}
                }
            }
        )
        super().__init__(capability)
        self.minecraft_parser = MinecraftParser()

    def should_activate(self, request_context: Dict[str, Any]) -> bool:
        """Activate when .log files are uploaded or analyze_logs flag is set.

        Args:
            request_context: Request context dictionary

        Returns:
            True if specialist should activate
        """
        filename = request_context.get('filename', '')
        analyze_flag = request_context.get('analyze_logs', False)

        return filename.endswith('.log') or analyze_flag

    def process(self, **kwargs) -> SpecialistResult:
        """Analyze log file and return kid-friendly explanation.

        Args:
            **kwargs: Should contain 'file_content' and optionally 'filename'

        Returns:
            SpecialistResult with analysis and explanation
        """
        file_content = kwargs.get('file_content', '')
        filename = kwargs.get('filename', 'log')

        if not file_content:
            return self.error_result("No log content provided", "empty_log")

        try:
            # Detect format and parse
            if self.minecraft_parser.detect_format(file_content):
                analysis = self.minecraft_parser.parse(file_content)
            else:
                return self.error_result(
                    "Unknown log format. Currently only Minecraft crash logs are supported.",
                    "unsupported_format"
                )

            # Format for LLM context - kid-friendly by default!
            context_parts = [
                f"**What Happened:** {analysis.kid_explanation}",
                "",
                f"**How to Fix:** {analysis.fix}",
                "",
                f"**Difficulty:** {analysis.difficulty.title()}"
            ]

            if analysis.conflicting_mods:
                mods_list = ", ".join(analysis.conflicting_mods[:5])
                if len(analysis.conflicting_mods) > 5:
                    mods_list += f" (and {len(analysis.conflicting_mods) - 5} more)"
                context_parts.append(f"**Mods Involved:** {mods_list}")

            context_content = "\n".join(context_parts)

            # Use format_context from BaseSpecialist
            context_text = self.format_context(
                title=f"Log Analysis: {analysis.error_type.replace('_', ' ').title()}",
                content=context_content,
                metadata={
                    'confidence': f"{analysis.confidence:.0%}",
                    'difficulty': analysis.difficulty
                }
            )

            return self.success_result(
                context_text=context_text,
                data=analysis.to_dict(),
                metadata={'error_type': analysis.error_type}
            )

        except Exception as e:
            logger.error(f"Log analysis failed: {e}", exc_info=True)
            return self.error_result(str(e), "processing_error")
