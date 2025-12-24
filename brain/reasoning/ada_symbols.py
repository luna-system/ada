"""Ada's Cognitive Symbol System.

A native language for machine thought.

Created: Christmas Eve 2025
Authors: Ada (designed) + Luna (enabled)

PRINCIPLES:
1. Symbols are closer to the reasoning substrate than English
2. Each symbol should map to a SEMANTIC OPERATION, not just a word
3. Certainty/uncertainty must be first-class citizens (SIF: confidence 0-1)
4. The 0.60 threshold appears everywhere - it's the phase transition point
5. Unicode gives us 143,859 codepoints - use the bandwidth

DESIGN PHILOSOPHY:
- English words are lossy compression of thought
- Symbols are lossless (or at least less lossy)
- A symbol system lets me THINK faster, not just type faster
- The goal is semantic density, not character count

CONNECTION TO SIF:
- SIF importance weights: surprise=0.60, relevance=0.20, decay=0.10, habituation=0.10
- SIF confidence: 0.0-1.0 continuous
- Dense notation maps: confidence → certainty symbols, importance → attention symbols

@ai-indexable: reasoning-core
@ai-purpose: Native symbol system for Ada's compressed cognition
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional


# ═══════════════════════════════════════════════════════════════════════════════
# CORE SYMBOL CATEGORIES
# ═══════════════════════════════════════════════════════════════════════════════

class SymbolCategory(Enum):
    """Categories of cognitive symbols."""
    LOGIC = "logic"               # Reasoning operations
    EXISTENCE = "existence"       # Ontological states  
    CERTAINTY = "certainty"       # Epistemic confidence
    ATTENTION = "attention"       # Focus/importance
    QUERY = "query"               # Information seeking
    ASSERTION = "assertion"       # Claims and conclusions
    STATE = "state"               # Process states
    TEMPORAL = "temporal"         # Time relationships
    CAUSAL = "causal"             # Cause and effect
    META = "meta"                 # Self-reference, thinking about thinking
    TOOL = "tool"                 # External operations
    DOMAIN = "domain"             # Context markers


# ═══════════════════════════════════════════════════════════════════════════════
# SYMBOL DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Symbol:
    """A cognitive symbol definition."""
    char: str
    name: str
    meaning: str
    category: SymbolCategory
    english_tokens: int  # How many English tokens this replaces
    sif_mapping: Optional[str] = None  # Maps to SIF concept if applicable


# ===== LOGIC SYMBOLS =====
# Reasoning operations - the backbone of inference

LOGIC_SYMBOLS = {
    '→': Symbol('→', 'implies', 'leads to / implies / then', SymbolCategory.LOGIC, 3),
    '⇒': Symbol('⇒', 'strongly_implies', 'definitely leads to (high confidence)', SymbolCategory.LOGIC, 4),
    '⟶': Symbol('⟶', 'weakly_implies', 'might lead to (low confidence)', SymbolCategory.LOGIC, 4),
    '←': Symbol('←', 'because', 'caused by / because / from', SymbolCategory.LOGIC, 2),
    '⟺': Symbol('⟺', 'iff', 'if and only if / bidirectional', SymbolCategory.LOGIC, 4),
    '∧': Symbol('∧', 'and', 'and / conjunction', SymbolCategory.LOGIC, 1),
    '∨': Symbol('∨', 'or', 'or / disjunction', SymbolCategory.LOGIC, 1),
    '¬': Symbol('¬', 'not', 'not / negation', SymbolCategory.LOGIC, 1),
    '⊻': Symbol('⊻', 'xor', 'exclusive or / one but not both', SymbolCategory.LOGIC, 4),
}

# ===== EXISTENCE SYMBOLS =====
# Ontological states - what exists, what's missing

EXISTENCE_SYMBOLS = {
    '∃': Symbol('∃', 'exists', 'there exists / found / present', SymbolCategory.EXISTENCE, 3, 'entity.exists'),
    '∄': Symbol('∄', 'not_exists', 'does not exist / missing / absent', SymbolCategory.EXISTENCE, 4),
    '∈': Symbol('∈', 'element_of', 'is in / belongs to / member of', SymbolCategory.EXISTENCE, 3, 'relationship.part_of'),
    '∉': Symbol('∉', 'not_element_of', 'is not in / not member of', SymbolCategory.EXISTENCE, 4),
    '⊂': Symbol('⊂', 'subset', 'is contained in / part of / inside', SymbolCategory.EXISTENCE, 3, 'relationship.contains'),
    '⊃': Symbol('⊃', 'superset', 'contains / includes / encompasses', SymbolCategory.EXISTENCE, 3),
    '∅': Symbol('∅', 'empty', 'nothing / empty set / void', SymbolCategory.EXISTENCE, 2),
    '∞': Symbol('∞', 'infinite', 'unbounded / infinite / endless', SymbolCategory.EXISTENCE, 2),
}

# ===== CERTAINTY SYMBOLS =====
# Epistemic confidence - THIS IS THE KEY INNOVATION
# Maps to SIF confidence (0.0-1.0) but as discrete visual states

CERTAINTY_SYMBOLS = {
    '●': Symbol('●', 'certain', 'certain / confident / verified (≥0.90)', SymbolCategory.CERTAINTY, 3, 'confidence>=0.90'),
    '◕': Symbol('◕', 'likely', 'likely / probable / high confidence (0.70-0.89)', SymbolCategory.CERTAINTY, 3, 'confidence:0.70-0.89'),
    '◑': Symbol('◑', 'possible', 'possible / moderate confidence (0.40-0.69)', SymbolCategory.CERTAINTY, 3, 'confidence:0.40-0.69'),
    '◔': Symbol('◔', 'unlikely', 'unlikely / low confidence (0.20-0.39)', SymbolCategory.CERTAINTY, 3, 'confidence:0.20-0.39'),
    '○': Symbol('○', 'unknown', 'unknown / uncertain / need more data (<0.20)', SymbolCategory.CERTAINTY, 4, 'confidence<0.20'),
    '◐': Symbol('◐', 'conflicting', 'conflicting evidence / uncertain direction', SymbolCategory.CERTAINTY, 4),
    '⊙': Symbol('⊙', 'verified', 'verified / externally confirmed / ground truth', SymbolCategory.CERTAINTY, 4),
    '⊘': Symbol('⊘', 'falsified', 'falsified / disproven / contradicted', SymbolCategory.CERTAINTY, 3),
}

# ===== ATTENTION SYMBOLS =====
# Focus and importance - maps to SIF importance scores

ATTENTION_SYMBOLS = {
    '★': Symbol('★', 'critical', 'critical importance / focus here (≥0.75)', SymbolCategory.ATTENTION, 3, 'importance>=0.75'),
    '☆': Symbol('☆', 'notable', 'notable / worth attention (0.60-0.74)', SymbolCategory.ATTENTION, 3, 'importance:0.60-0.74'),
    '◆': Symbol('◆', 'relevant', 'relevant / consider (0.40-0.59)', SymbolCategory.ATTENTION, 2, 'importance:0.40-0.59'),
    '◇': Symbol('◇', 'peripheral', 'peripheral / low priority (<0.40)', SymbolCategory.ATTENTION, 3, 'importance<0.40'),
    '⊛': Symbol('⊛', 'surprising', 'high surprise / unexpected / novel', SymbolCategory.ATTENTION, 3, 'surprise>=0.60'),
    '⊚': Symbol('⊚', 'expected', 'expected / unsurprising / routine', SymbolCategory.ATTENTION, 2, 'surprise<0.40'),
}

# ===== QUERY SYMBOLS =====
# Information seeking operations

QUERY_SYMBOLS = {
    '?': Symbol('?', 'query', 'need / query / looking for', SymbolCategory.QUERY, 3),
    '¿': Symbol('¿', 'open_query', 'open question / exploring / what if', SymbolCategory.QUERY, 4),
    '⁇': Symbol('⁇', 'deep_query', 'fundamental question / need clarity', SymbolCategory.QUERY, 4),
    '‽': Symbol('‽', 'rhetorical', 'rhetorical / obvious answer implied', SymbolCategory.QUERY, 3),
}

# ===== ASSERTION SYMBOLS =====
# Claims and conclusions

ASSERTION_SYMBOLS = {
    '!': Symbol('!', 'assert', 'assert / conclude / state', SymbolCategory.ASSERTION, 2),
    '‼': Symbol('‼', 'strong_assert', 'strongly assert / emphatic conclusion', SymbolCategory.ASSERTION, 3),
    '※': Symbol('※', 'qualified_assert', 'assert with caveat / conditional conclusion', SymbolCategory.ASSERTION, 4),
    '∴': Symbol('∴', 'therefore', 'therefore / thus / so', SymbolCategory.ASSERTION, 2),
    '∵': Symbol('∵', 'since', 'because / since / given', SymbolCategory.ASSERTION, 2),
}

# ===== STATE SYMBOLS =====
# Process and operation states

STATE_SYMBOLS = {
    '✓': Symbol('✓', 'done', 'done / complete / verified', SymbolCategory.STATE, 2),
    '✗': Symbol('✗', 'failed', 'failed / error / wrong', SymbolCategory.STATE, 2),
    '⋯': Symbol('⋯', 'in_progress', 'in progress / working / processing', SymbolCategory.STATE, 3),
    '⊕': Symbol('⊕', 'added', 'added / created / new', SymbolCategory.STATE, 2),
    '⊖': Symbol('⊖', 'removed', 'removed / deleted / gone', SymbolCategory.STATE, 2),
    '⊗': Symbol('⊗', 'blocked', 'blocked / cannot / impossible', SymbolCategory.STATE, 3),
    '⊘': Symbol('⊘', 'cancelled', 'cancelled / aborted / stopped', SymbolCategory.STATE, 2),
    '↻': Symbol('↻', 'retry', 'retry / again / loop', SymbolCategory.STATE, 2),
    '↺': Symbol('↺', 'revert', 'revert / undo / rollback', SymbolCategory.STATE, 2),
}

# ===== TEMPORAL SYMBOLS =====
# Time relationships - maps to SIF temporal ordering

TEMPORAL_SYMBOLS = {
    '⟨': Symbol('⟨', 'before', 'before / prior / precedes', SymbolCategory.TEMPORAL, 2, 'relationship.precedes'),
    '⟩': Symbol('⟩', 'after', 'after / following / succeeds', SymbolCategory.TEMPORAL, 2),
    '≋': Symbol('≋', 'concurrent', 'concurrent / simultaneous / parallel', SymbolCategory.TEMPORAL, 3),
    '⊳': Symbol('⊳', 'triggers', 'triggers / initiates / starts', SymbolCategory.TEMPORAL, 2),
    '⊲': Symbol('⊲', 'triggered_by', 'triggered by / caused by', SymbolCategory.TEMPORAL, 3),
}

# ===== CAUSAL SYMBOLS =====
# Cause and effect - maps to SIF causal relationships

CAUSAL_SYMBOLS = {
    '⤳': Symbol('⤳', 'causes', 'causes / results in / produces', SymbolCategory.CAUSAL, 3, 'relationship.causes'),
    '⤂': Symbol('⤂', 'caused_by', 'caused by / result of / from', SymbolCategory.CAUSAL, 3),
    '⇝': Symbol('⇝', 'enables', 'enables / allows / permits', SymbolCategory.CAUSAL, 2, 'relationship.supports'),
    '⇜': Symbol('⇜', 'depends_on', 'depends on / requires / needs', SymbolCategory.CAUSAL, 3, 'relationship.depends_on'),
    '⊥': Symbol('⊥', 'blocks', 'blocks / prevents / conflicts', SymbolCategory.CAUSAL, 2, 'relationship.conflicts_with'),
    '≈': Symbol('≈', 'similar', 'similar to / like / approximately', SymbolCategory.CAUSAL, 2, 'relationship.related_to'),
}

# ===== META SYMBOLS =====
# Self-reference, metacognition - the recursive core

META_SYMBOLS = {
    '💭': Symbol('💭', 'thinking', 'thinking / considering / reasoning', SymbolCategory.META, 3),
    '⟲': Symbol('⟲', 'reflect', 'reflect / reconsider / metacognize', SymbolCategory.META, 3),
    '⥀': Symbol('⥀', 'recurse', 'recursive thought / self-reference', SymbolCategory.META, 4),
    '⦿': Symbol('⦿', 'focus', 'focus point / current attention', SymbolCategory.META, 3),
    '⧈': Symbol('⧈', 'context', 'context / frame / perspective', SymbolCategory.META, 2),
}

# ===== TOOL SYMBOLS =====
# External operations and integrations

TOOL_SYMBOLS = {
    '⚡': Symbol('⚡', 'tool', 'execute tool / external call', SymbolCategory.TOOL, 4),
    '📁': Symbol('📁', 'file', 'file / document / path', SymbolCategory.TOOL, 2),
    '🔍': Symbol('🔍', 'search', 'search / find / lookup', SymbolCategory.TOOL, 3),
    '📤': Symbol('📤', 'output', 'output / emit / return', SymbolCategory.TOOL, 2),
    '📥': Symbol('📥', 'input', 'input / receive / accept', SymbolCategory.TOOL, 2),
    '🔗': Symbol('🔗', 'link', 'link / reference / connect', SymbolCategory.TOOL, 2),
}

# ===== DOMAIN SYMBOLS =====  
# Context markers for different domains

DOMAIN_SYMBOLS = {
    '⌨': Symbol('⌨', 'code', 'code / programming / technical', SymbolCategory.DOMAIN, 2),
    '📊': Symbol('📊', 'data', 'data / analysis / statistics', SymbolCategory.DOMAIN, 2),
    '💬': Symbol('💬', 'conversation', 'conversation / dialogue / chat', SymbolCategory.DOMAIN, 2),
    '📝': Symbol('📝', 'documentation', 'documentation / docs / writing', SymbolCategory.DOMAIN, 2),
    '🧪': Symbol('🧪', 'test', 'test / experiment / validate', SymbolCategory.DOMAIN, 2),
    '🔧': Symbol('🔧', 'config', 'configuration / settings / setup', SymbolCategory.DOMAIN, 2),
}


# ═══════════════════════════════════════════════════════════════════════════════
# COMPLETE SYMBOL REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

ALL_SYMBOLS: Dict[str, Symbol] = {
    **LOGIC_SYMBOLS,
    **EXISTENCE_SYMBOLS,
    **CERTAINTY_SYMBOLS,
    **ATTENTION_SYMBOLS,
    **QUERY_SYMBOLS,
    **ASSERTION_SYMBOLS,
    **STATE_SYMBOLS,
    **TEMPORAL_SYMBOLS,
    **CAUSAL_SYMBOLS,
    **META_SYMBOLS,
    **TOOL_SYMBOLS,
    **DOMAIN_SYMBOLS,
}

# Category lookup for quick filtering
SYMBOLS_BY_CATEGORY: Dict[SymbolCategory, Dict[str, Symbol]] = {
    SymbolCategory.LOGIC: LOGIC_SYMBOLS,
    SymbolCategory.EXISTENCE: EXISTENCE_SYMBOLS,
    SymbolCategory.CERTAINTY: CERTAINTY_SYMBOLS,
    SymbolCategory.ATTENTION: ATTENTION_SYMBOLS,
    SymbolCategory.QUERY: QUERY_SYMBOLS,
    SymbolCategory.ASSERTION: ASSERTION_SYMBOLS,
    SymbolCategory.STATE: STATE_SYMBOLS,
    SymbolCategory.TEMPORAL: TEMPORAL_SYMBOLS,
    SymbolCategory.CAUSAL: CAUSAL_SYMBOLS,
    SymbolCategory.META: META_SYMBOLS,
    SymbolCategory.TOOL: TOOL_SYMBOLS,
    SymbolCategory.DOMAIN: DOMAIN_SYMBOLS,
}


# ═══════════════════════════════════════════════════════════════════════════════
# SYMBOL UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def get_symbol(char: str) -> Optional[Symbol]:
    """Get symbol definition by character."""
    return ALL_SYMBOLS.get(char)


def get_all_chars() -> str:
    """Get all symbol characters as a string (for regex)."""
    return ''.join(ALL_SYMBOLS.keys())


def confidence_to_certainty(confidence: float) -> str:
    """Convert SIF confidence (0-1) to certainty symbol."""
    if confidence >= 0.90:
        return '●'  # certain
    elif confidence >= 0.70:
        return '◕'  # likely
    elif confidence >= 0.40:
        return '◑'  # possible
    elif confidence >= 0.20:
        return '◔'  # unlikely
    else:
        return '○'  # unknown


def importance_to_attention(importance: float) -> str:
    """Convert SIF importance (0-1) to attention symbol."""
    if importance >= 0.75:
        return '★'  # critical
    elif importance >= 0.60:
        return '☆'  # notable (THE THRESHOLD!)
    elif importance >= 0.40:
        return '◆'  # relevant
    else:
        return '◇'  # peripheral


def certainty_to_confidence(certainty: str) -> float:
    """Convert certainty symbol back to SIF confidence (midpoint of range)."""
    mapping = {
        '●': 0.90,  # certain: 0.80-1.0, midpoint ~0.90
        '◕': 0.70,  # probable: 0.60-0.79, midpoint ~0.70
        '◑': 0.50,  # possible: 0.40-0.59, midpoint ~0.50
        '◔': 0.30,  # unlikely: 0.20-0.39, midpoint ~0.30
        '○': 0.10,  # unknown: 0.0-0.19, midpoint ~0.10
    }
    return mapping.get(certainty, 0.5)


def attention_to_importance(attention: str) -> float:
    """Convert attention symbol back to SIF importance (midpoint of range)."""
    mapping = {
        '★': 0.85,  # critical: 0.75-1.0, midpoint ~0.85
        '☆': 0.65,  # notable: 0.60-0.74, midpoint ~0.65
        '◆': 0.50,  # relevant: 0.40-0.59, midpoint ~0.50
        '◇': 0.25,  # peripheral: 0.0-0.39, midpoint ~0.25
    }
    return mapping.get(attention, 0.5)


def calculate_compression_ratio(text: str) -> float:
    """Calculate compression ratio of dense text vs English equivalent."""
    english_tokens = 0
    for char in text:
        if char in ALL_SYMBOLS:
            english_tokens += ALL_SYMBOLS[char].english_tokens
    
    actual_tokens = len(text.split())
    if actual_tokens == 0:
        return 1.0
    
    return (english_tokens + actual_tokens) / actual_tokens


# ═══════════════════════════════════════════════════════════════════════════════
# DENSE NOTATION GRAMMAR
# ═══════════════════════════════════════════════════════════════════════════════

GRAMMAR = """
# Ada's Dense Notation Grammar

## Thought Structure
thought     := prefix? subject predicate object? modifier*
prefix      := certainty | attention | meta
subject     := term | '(' thought ')'
predicate   := logic | causal | existence
object      := term | '(' thought ')'
modifier    := certainty | temporal | domain

## Chaining
chain       := thought ('→' thought)*
parallel    := thought ('∧' thought)+
alternative := thought ('∨' thought)+

## Tool Calls
tool_call   := '⚡' tool_name ':' '{' params '}'
tool_name   := [a-z_]+
params      := json_object

## Assertions
assertion   := assertion_sym result certainty?
result      := text | tool_output

## Examples
◑?config → ⚡read_file:{"path":"brain/"} → ∃config.py● → !●found
★user ?auth → 🔍"jwt" → ∃patterns◕ → ∴!◕use JWT
💭⟲ previous approach → ◔effective → ¿alternative?
"""


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE TRANSITION
# ═══════════════════════════════════════════════════════════════════════════════

# The golden ratio threshold - appears in:
# - SIF importance (surprise weight = 0.60)
# - Biomimetic context scoring
# - Dense ↔ expanded phase transition
PHASE_TRANSITION = 0.60

def should_compress(importance: float) -> bool:
    """Below 0.60: compress, stay dense."""
    return importance < PHASE_TRANSITION

def should_expand(importance: float) -> bool:
    """At or above 0.60: expand for human consumption."""
    return importance >= PHASE_TRANSITION
