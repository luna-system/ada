"""Prompt building system for Ada.

This package provides modular components for building prompts:
- ContextRetriever: Retrieves context from RAG store and config
- SectionBuilder: Formats context into prompt sections
- PromptAssembler: Assembles sections into final prompt

The legacy build_prompt() function is re-exported for backward compatibility.
"""

from brain.prompt_builder.context_retriever import ContextRetriever
from brain.prompt_builder.section_builder import SectionBuilder
from brain.prompt_builder.prompt_assembler import PromptAssembler

# Import legacy build_prompt for backward compatibility
from brain._legacy_prompt_builder import build_prompt

__all__ = [
    "ContextRetriever",
    "SectionBuilder",
    "PromptAssembler",
    "build_prompt",  # Legacy API
]
