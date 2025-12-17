"""Prompt building system for Ada.

This package provides modular components for building prompts:
- ContextRetriever: Retrieves context from RAG store and config
- SectionBuilder: Formats context into prompt sections
- PromptAssembler: Assembles sections into final prompt (with caching!)
"""

from brain.prompt_builder.context_retriever import ContextRetriever
from brain.prompt_builder.section_builder import SectionBuilder
from brain.prompt_builder.prompt_assembler import PromptAssembler

__all__ = [
    "ContextRetriever",
    "SectionBuilder",
    "PromptAssembler",
]
