"""Minecraft crash log parser.

Parses Minecraft crash reports and provides kid-friendly explanations.
"""

import re
from typing import List, Optional
from ada_logs.core import LogAnalysis


class MinecraftParser:
    """Parser for Minecraft crash logs.

    Implements the LogParser protocol (duck typing).
    """

    def detect_format(self, log_content: str) -> bool:
        """Check if this is a Minecraft crash report.

        Args:
            log_content: Raw log file content

        Returns:
            True if this looks like a Minecraft crash report
        """
        # Minecraft crash reports have distinctive headers
        indicators = [
            "---- Minecraft Crash Report ----",
            "Minecraft Version:",
            "-- System Details --",
            "java.lang" # Java exceptions
        ]

        return any(indicator in log_content for indicator in indicators)

    def parse(self, log_content: str) -> LogAnalysis:
        """Parse Minecraft crash log and return analysis.

        Args:
            log_content: Raw crash log content

        Returns:
            LogAnalysis with error details and kid-friendly explanation

        Raises:
            ValueError: If log cannot be parsed
        """
        if not self.detect_format(log_content):
            raise ValueError("Not a valid Minecraft crash report")

        # Extract error type from exception
        error_type = self._detect_error_type(log_content)

        # Extract mods involved
        mods = self._extract_mods(log_content)

        # Get kid-friendly explanation and fix
        kid_explanation, fix, difficulty = self._get_explanation(error_type, mods, log_content)

        # Calculate confidence
        confidence = self._calculate_confidence(error_type, log_content)

        # Extract stack trace if available
        stack_trace = self._extract_stack_trace(log_content)

        return LogAnalysis(
            error_type=error_type,
            confidence=confidence,
            kid_explanation=kid_explanation,
            fix=fix,
            difficulty=difficulty,
            conflicting_mods=mods,
            stack_trace=stack_trace,
            common_causes=[],
            metadata={}
        )

    def _detect_error_type(self, log_content: str) -> str:
        """Detect the type of error from the crash log."""

        # OutOfMemoryError - very common
        if "OutOfMemoryError" in log_content or "Java heap space" in log_content:
            return "out_of_memory"

        # Mod conflicts - check for mixin errors with specific mods
        if "MixinTransformerError" in log_content or "Mixin transformation" in log_content:
            # Check for OptiFine + Sodium specifically
            if ("optifine" in log_content.lower() and "sodium" in log_content.lower()):
                return "mod_conflict"
            return "mod_conflict"

        # Generic mixin errors
        if "mixin" in log_content.lower() and "failed" in log_content.lower():
            return "mod_conflict"

        # NullPointerException
        if "NullPointerException" in log_content:
            return "null_pointer"

        # Class not found
        if "ClassNotFoundException" in log_content or "NoClassDefFoundError" in log_content:
            return "missing_dependency"

        # Default to unknown
        return "unknown_error"

    def _extract_mods(self, log_content: str) -> List[str]:
        """Extract mod names from the crash log."""
        mods = []

        # Look in the "Loaded Mods" or "Fabric Mods" section
        mod_section_match = re.search(
            r"(?:Fabric Mods|Loaded Mods):(.+?)(?:--|\n\n)",
            log_content,
            re.DOTALL
        )

        if mod_section_match:
            mod_section = mod_section_match.group(1)

            # Extract mod names (format: "modid: Mod Name version")
            mod_pattern = r"([a-z0-9_-]+):\s+([A-Za-z0-9 ]+)\s+[\d\.]+"
            for match in re.finditer(mod_pattern, mod_section):
                mod_id = match.group(1)
                mod_name = match.group(2).strip()

                # Add recognizable mod names
                if mod_id in ['optifine', 'sodium', 'iris', 'create', 'applied-energistics-2']:
                    mods.append(mod_name if mod_name else mod_id)
                elif len(mods) < 10:  # Don't collect too many
                    mods.append(mod_name if mod_name else mod_id)

        # Also check stack trace for mod mentions
        if "sodium" in log_content.lower():
            if "Sodium" not in mods:
                mods.append("Sodium")
        if "optifine" in log_content.lower():
            if "OptiFine" not in mods:
                mods.append("OptiFine")

        return mods

    def _get_explanation(self, error_type: str, mods: List[str], log_content: str) -> tuple[str, str, str]:
        """Get kid-friendly explanation and fix for the error.

        Returns:
            (explanation, fix, difficulty)
        """

        if error_type == "out_of_memory":
            return (
                "Minecraft ran out of memory! 🎮 It's like trying to fit too many toys in a small box - "
                "there just isn't enough space. This usually happens when you have lots of mods loaded "
                "or your render distance is really high.",

                "Give Minecraft more RAM in your launcher settings. Try 4-6 GB if you have mods. "
                "Also try lowering your render distance to 12 or less.",

                "easy"
            )

        elif error_type == "mod_conflict":
            # Check for specific conflicts
            if "OptiFine" in mods and "Sodium" in mods:
                return (
                    "OptiFine and Sodium are fighting! 🥊 They both try to make Minecraft run faster "
                    "and look prettier, but they do it in different ways that don't work together. "
                    "You can only use one at a time!",

                    "Remove OptiFine OR remove Sodium (not both!). Sodium is usually faster, so keep Sodium "
                    "and remove OptiFine. Just delete the OptiFine .jar file from your mods folder.",

                    "easy"
                )
            else:
                mod_names = ", ".join(mods[:3]) if mods else "some of your mods"
                return (
                    f"Some mods aren't playing nicely together! 🎮 {mod_names} might be trying to change "
                    "the same parts of Minecraft in different ways.",

                    "Try removing mods one at a time to find which ones don't work together. "
                    "Check CurseForge or Modrinth for compatibility info about your mods.",

                    "medium"
                )

        elif error_type == "null_pointer":
            return (
                "Something in Minecraft tried to use something that doesn't exist! It's like reaching "
                "for a toy that isn't there. This is usually a bug in a mod.",

                "Try updating your mods to the latest versions. If the crash keeps happening, report "
                "it to the mod author on CurseForge or GitHub.",

                "medium"
            )

        elif error_type == "missing_dependency":
            return (
                "A mod is looking for another mod (or library) that you don't have installed! "
                "It's like trying to play a game without all the pieces.",

                "Check which mods are required by reading the mod description on CurseForge. "
                "Install any required mods or libraries (like Fabric API).",

                "easy"
            )

        else:
            return (
                "Minecraft crashed, but we're not sure exactly why. 🤔 Don't worry - crashes happen! "
                "It could be a mod bug, a missing file, or something else.",

                "Try updating all your mods to the latest versions for your Minecraft version. "
                "If it keeps crashing, try removing mods one at a time to find the problem.",

                "medium"
            )

    def _calculate_confidence(self, error_type: str, log_content: str) -> float:
        """Calculate confidence score for the analysis.

        Returns:
            Float between 0.0 and 1.0
        """
        # High confidence for clear error types
        if error_type == "out_of_memory":
            return 0.95

        # High confidence for known mod conflicts
        if error_type == "mod_conflict":
            if "optifine" in log_content.lower() and "sodium" in log_content.lower():
                return 0.90
            return 0.75

        # Medium confidence for common errors
        if error_type in ["null_pointer", "missing_dependency"]:
            return 0.70

        # Lower confidence for unknown errors
        return 0.50

    def _extract_stack_trace(self, log_content: str) -> Optional[str]:
        """Extract the stack trace from the crash log."""
        # Find the main exception
        match = re.search(
            r"(java\.lang\.\w+(?:Error|Exception)[^\n]*(?:\n\s+at [^\n]+)+)",
            log_content
        )

        if match:
            return match.group(1)

        return None
