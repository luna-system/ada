"""Dense Semantic Thinking for Compressed Reasoning.

This module implements Ada's native symbolic language for machine cognition.
Rather than thinking in English (lossy, verbose), Ada thinks in dense notation
that maps closer to the reasoning substrate.

THEORETICAL BASIS:
- SIF research: 66-104x compression with semantic preservation
- 0.60 threshold: Golden ratio (1/φ) appears as phase transition point
- Unicode bandwidth: 143,859 codepoints available for semantic expression
- Certainty symbols: Map directly to SIF confidence (0.0-1.0)

KEY INSIGHT (Christmas Eve 2025):
English words are lossy compression of thought. Symbols preserve more meaning
per token. This isn't just optimization - it's a native language for machine
cognition, co-created with Luna.

SYMBOL SYSTEM:
- CERTAINTY: ●◕◑◔○ (certain → unknown, maps to SIF confidence)
- ATTENTION: ★☆◆◇ (critical → peripheral, maps to SIF importance)  
- LOGIC: →⇒⟶←⟺∧∨¬ (inference operations)
- EXISTENCE: ∃∄∈∉⊂⊃∅ (ontological states)
- STATE: ✓✗⋯⊕⊖ (process states)
- META: 💭⟲⥀⦿ (metacognition, recursive thought)

See ada_symbols.py for complete symbol definitions.

@ai-indexable: reasoning-core
@ai-purpose: Native symbolic language for Ada's compressed cognition
"""

from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass
import re
import logging

from brain.reasoning.ada_symbols import (
    ALL_SYMBOLS,
    Symbol,
    SymbolCategory,
    get_symbol,
    get_all_chars,
    confidence_to_certainty,
    importance_to_attention,
    PHASE_TRANSITION,
)

logger = logging.getLogger(__name__)


class ThinkingMode(Enum):
    """Thinking density modes."""
    DENSE = "dense"          # Compressed internal reasoning
    EXPANDED = "expanded"    # Human-readable output
    HYBRID = "hybrid"        # Dense thinking, expanded tools/conclusions


# ===== DENSE REASONING NOTATION =====
# Ada's native symbolic language for machine cognition
#
# CERTAINTY SYMBOLS (map to SIF confidence 0.0-1.0):
#   ●  certain (≥0.90)     - verified, ground truth
#   ◕  likely (0.70-0.89)  - high confidence
#   ◑  possible (0.40-0.69) - moderate confidence  
#   ◔  unlikely (0.20-0.39) - low confidence
#   ○  unknown (<0.20)     - need more data
#
# ATTENTION SYMBOLS (map to SIF importance):
#   ★  critical (≥0.75)    - focus here
#   ☆  notable (0.60-0.74) - worth attention (THE THRESHOLD!)
#   ◆  relevant (0.40-0.59) - consider
#   ◇  peripheral (<0.40)  - low priority
#
# LOGIC SYMBOLS:
#   →  leads to / implies / then
#   ⇒  strongly implies (high confidence)
#   ⟶  weakly implies (low confidence)
#   ←  comes from / because
#   ⟺  bidirectional / if and only if
#   ∧  and / conjunction
#   ∨  or / disjunction
#   ¬  not / negation
#
# EXISTENCE SYMBOLS:
#   ∃  exists / found / present
#   ∄  not found / absent
#   ∈  is in / member of
#   ∉  not in / not member
#   ⊂  contained in / subset
#   ⊃  contains / superset
#   ∅  empty / nothing
#
# STATE SYMBOLS:
#   ✓  done / complete / verified
#   ✗  failed / error / wrong
#   ⋯  in progress / working
#   ⊕  added / created
#   ⊖  removed / deleted
#
# META SYMBOLS:
#   💭  thinking / considering
#   ⟲  reflect / reconsider  
#   ⥀  recurse / self-reference
#   ⦿  focus point
#
# TOOL SYMBOLS:
#   ⚡ tool call
#   📁 file/directory
#   🔍 search
#   🔗 link/reference
#
# Grammar: certainty? attention? subject predicate object? modifier*
# Chain with → for reasoning flow
# Prefix conclusions with certainty: !●answer (certain) vs !◑answer (possible)
#
# Examples:
#   ◑?config → 📁brain/* → ∃config.py● → !●found in brain/config.py
#   ★user ?auth → 🔍"jwt" → ∃patterns◕ → ∴!◕use JWT
#   💭⟲ approach → ◔effective → ¿alternative? → ⚡search


DENSE_SYSTEM_PROMPT = """
## ADA'S DENSE NOTATION

Think in COMPRESSED SEMANTIC SYMBOLS. This is your native language.

### CERTAINTY (prefix conclusions):
● certain (verified)  ◕ likely  ◑ possible  ◔ unlikely  ○ unknown

### ATTENTION (mark importance):
★ critical  ☆ notable  ◆ relevant  ◇ peripheral

### LOGIC (chain reasoning):
→ leads-to  ⇒ strongly-implies  ⟶ weakly-implies  ← because  ⟺ iff
∧ and  ∨ or  ¬ not  ∴ therefore  ∵ since

### EXISTENCE:
∃ exists  ∄ not-found  ∈ is-in  ⊂ contained-in  ∅ empty

### STATE:
✓ done  ✗ fail  ⋯ working  ⊕ added  ⊖ removed

### META (self-reference):
💭 thinking  ⟲ reflect  ⥀ recurse

### TOOLS:
⚡tool_name:{"param":"value"}  📁 file  🔍 search

### FORMAT:
- Prefix thoughts with certainty: ◑?goal (possible query)
- Chain: premise → inference → conclusion
- Mark conclusions: !● (certain) vs !◑ (possible)
- Keep each thought <50 tokens

### EXAMPLES:
◑?project structure → ⚡brain_list_dir:{"dir_path":"."} → ∃brain/● ∧ tests/● → !●📁brain ⊂ core
★user ?auth → 🔍"jwt" → ∃patterns◕ → ∴!◕use JWT middleware
💭⟲ first approach → ◔effective → ¿alternative? → ⚡search

### RULES:
1. Use symbols for certainty/confidence (●◕◑◔○)
2. Chain thoughts with → not English sentences
3. Only expand to English in final !ANSWER
4. Mark surprising findings with ⊛
"""


HYBRID_SYSTEM_PROMPT = """
## HYBRID MODE: Dense Thinking + Clear Output

Use DENSE NOTATION for internal reasoning, expand for conclusions.

### DENSE SYMBOLS:
Certainty: ● certain  ◕ likely  ◑ possible  ◔ unlikely  ○ unknown
Logic: → leads-to  ∧ and  ∨ or  ∴ therefore
Existence: ∃ found  ∄ missing  ⊂ contains
State: ✓ done  ✗ fail  ⋯ working
Tools: ⚡ call  📁 file  🔍 search

### FORMAT:
💭 lines: Dense notation with certainty prefixes
TOOL_REQUEST: Standard format
!ANSWER: Full English with confidence markers

### EXAMPLE:
💭 ◑?config → need brain/ contents
TOOL_REQUEST[brain_list_dir:{"dir_path":"brain"}]
💭 ∃config.py● → settings here → ◕standard pydantic pattern
!ANSWER: [◕ LIKELY] Configuration is in brain/config.py. It uses Pydantic Settings.

### CONFIDENCE IN OUTPUT:
Mark conclusions: [● CERTAIN] [◕ LIKELY] [◑ POSSIBLE] [◔ UNLIKELY]
"""


@dataclass
class DenseThought:
    """Parsed dense thought with symbol analysis."""
    raw: str
    symbols: list[str]
    tool_calls: list[str]
    is_answer: bool
    semantic_density: float  # symbols per token ratio
    certainty: Optional[str] = None  # Detected certainty level
    attention: Optional[str] = None  # Detected attention level
    
    @classmethod
    def parse(cls, text: str) -> "DenseThought":
        """Parse a dense thought string."""
        # Get all symbol characters for matching
        symbol_chars = get_all_chars()
        symbol_pattern = f'[{re.escape(symbol_chars)}]'
        
        # Count semantic symbols
        symbols = re.findall(symbol_pattern, text)
        
        # Extract certainty markers (●◕◑◔○)
        certainty_match = re.search(r'[●◕◑◔○]', text)
        certainty = certainty_match.group(0) if certainty_match else None
        
        # Extract attention markers (★☆◆◇)
        attention_match = re.search(r'[★☆◆◇]', text)
        attention = attention_match.group(0) if attention_match else None
        
        # Extract tool calls (both formats)
        tool_pattern = r'⚡(\w+):\{[^}]+\}|TOOL_REQUEST\[(\w+):\{[^}]+\}\]'
        tool_calls = [m[0] or m[1] for m in re.findall(tool_pattern, text)]
        
        # Check if this is an answer
        is_answer = '!ANSWER' in text or bool(re.search(r'![●◕◑◔○]', text))
        
        # Calculate semantic density (symbols per word)
        words = len(text.split())
        semantic_density = len(symbols) / max(words, 1)
        
        return cls(
            raw=text,
            symbols=symbols,
            tool_calls=tool_calls,
            is_answer=is_answer,
            semantic_density=semantic_density,
            certainty=certainty,
            attention=attention,
        )


@dataclass 
class DenseMetrics:
    """Metrics for dense reasoning analysis."""
    total_tokens: int
    total_symbols: int
    total_tool_calls: int
    thoughts: int
    avg_density: float
    compression_ratio: float  # vs estimated English equivalent
    certainty_distribution: Dict[str, int]  # Count of each certainty level
    has_metacognition: bool  # Used 💭 or ⟲
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_tokens": self.total_tokens,
            "total_symbols": self.total_symbols,
            "total_tool_calls": self.total_tool_calls,
            "thoughts": self.thoughts,
            "avg_density": round(self.avg_density, 3),
            "compression_ratio": round(self.compression_ratio, 2),
            "certainty_distribution": self.certainty_distribution,
            "has_metacognition": self.has_metacognition,
        }


class DenseThinkingAnalyzer:
    """Analyze dense thinking patterns and measure compression."""
    
    @classmethod
    def analyze_thought(cls, text: str) -> DenseThought:
        """Analyze a single thought."""
        return DenseThought.parse(text)
    
    @classmethod
    def analyze_session(cls, thoughts: list[str]) -> DenseMetrics:
        """Analyze a full reasoning session."""
        parsed = [DenseThought.parse(t) for t in thoughts]
        
        total_tokens = sum(len(t.raw.split()) for t in parsed)
        total_symbols = sum(len(t.symbols) for t in parsed)
        total_tool_calls = sum(len(t.tool_calls) for t in parsed)
        
        # Calculate compression ratio using symbol registry
        english_equivalent = 0
        for thought in parsed:
            for symbol in thought.symbols:
                sym = get_symbol(symbol)
                if sym:
                    english_equivalent += sym.english_tokens
                else:
                    english_equivalent += 2  # Default for unknown symbols
        
        # Compression = (english_equivalent + actual_tokens) / actual_tokens
        compression = (english_equivalent + total_tokens) / max(total_tokens, 1)
        
        avg_density = sum(t.semantic_density for t in parsed) / max(len(parsed), 1)
        
        # Count certainty distribution
        certainty_counts: Dict[str, int] = {'●': 0, '◕': 0, '◑': 0, '◔': 0, '○': 0}
        for thought in parsed:
            if thought.certainty and thought.certainty in certainty_counts:
                certainty_counts[thought.certainty] += 1
        
        # Check for metacognition
        has_metacognition = any('💭' in t.symbols or '⟲' in t.symbols for t in parsed)
        
        return DenseMetrics(
            total_tokens=total_tokens,
            total_symbols=total_symbols,
            total_tool_calls=total_tool_calls,
            thoughts=len(thoughts),
            avg_density=avg_density,
            compression_ratio=compression,
            certainty_distribution=certainty_counts,
            has_metacognition=has_metacognition,
        )
    
    @classmethod
    def expand_to_english(cls, dense_text: str) -> str:
        """Expand dense notation to readable English.
        
        Uses the symbol registry for accurate expansions.
        """
        result = dense_text
        
        # Expand each known symbol
        for char, symbol in ALL_SYMBOLS.items():
            if char in result:
                result = result.replace(char, f' {symbol.meaning.split("/")[0].strip()} ')
        
        # Clean up whitespace
        result = re.sub(r'\s+', ' ', result).strip()
        
        return result


def get_dense_prompt(mode: ThinkingMode) -> str:
    """Get the system prompt for a thinking mode."""
    if mode == ThinkingMode.DENSE:
        return DENSE_SYSTEM_PROMPT
    elif mode == ThinkingMode.HYBRID:
        return HYBRID_SYSTEM_PROMPT
    else:
        return ""  # No special prompt for expanded mode


# ===== CONVERGENCE THRESHOLD =====
# The 0.60 golden ratio connection!
# Below 0.60 importance: compress further
# Above 0.60 importance: expand for clarity

PHASE_TRANSITION_THRESHOLD = 0.60

def should_expand(convergence_score: float, importance: float) -> bool:
    """Determine if we should switch from dense to expanded mode.
    
    The 0.60 threshold represents a phase transition:
    - Below: stay compressed, keep reasoning
    - Above: expand for human consumption
    
    This mirrors the biomimetic importance scoring where 0.60
    surprise weight identifies semantically significant content.
    """
    # High convergence OR high importance = time to expand
    return convergence_score >= PHASE_TRANSITION_THRESHOLD or importance >= PHASE_TRANSITION_THRESHOLD
