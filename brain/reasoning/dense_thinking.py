"""Dense Semantic Thinking for Compressed Reasoning.

HYPOTHESIS: Language models waste tokens on English verbosity during reasoning.
If we encourage compressed semantic notation during THINKING, then expand only
for FINAL OUTPUT, we can achieve:
- Faster reasoning (fewer tokens per semantic unit)
- More iterations within same context window
- Cleaner reasoning chains (less noise)

THEORETICAL BASIS:
- SIF research showed 66-104x compression with semantic preservation
- 0.60 importance threshold identifies semantically dense content
- Lojban/symbolic notation carries more meaning per token than English

EXPERIMENT DESIGN:
1. Dense prompt: Encourage symbolic/compressed thinking
2. Expansion step: Translate dense→English at convergence
3. Metrics: tokens/semantic-unit, reasoning speed, solution quality

@ai-indexable: reasoning-experiment
@ai-purpose: Compressed semantic reasoning for efficiency
"""

from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass
import re
import logging

logger = logging.getLogger(__name__)


class ThinkingMode(Enum):
    """Thinking density modes."""
    DENSE = "dense"          # Compressed internal reasoning
    EXPANDED = "expanded"    # Human-readable output
    HYBRID = "hybrid"        # Dense thinking, expanded tools/conclusions


# ===== DENSE REASONING NOTATION =====
# A minimal symbolic language for semantic reasoning
#
# Symbols:
#   →  leads to / implies / then
#   ←  comes from / because
#   ∃  exists / found / there is
#   ∄  not found / doesn't exist
#   ?  query / need / question
#   !  assert / conclude / answer
#   ∧  and / with / also
#   ∨  or / alternatively
#   ¬  not / without / except
#   ⊂  part of / inside / contains
#   ≈  similar to / like / approximately
#   ∴  therefore / so / thus
#   ∵  because / since / given
#   ⟹  strongly implies (high confidence)
#   ⟶  weakly implies (low confidence)
#   ✓  verified / confirmed / done
#   ✗  failed / error / wrong
#   ⚡ tool call
#   📁 file/directory
#   🔍 search
#   💭 thinking
#
# Grammar:
#   subject predicate [object] [modifier]
#   Minimal words, maximal symbols
#   Chain with → for reasoning flow
#
# Examples:
#   ?config location → 📁brain/* → ∃config.py ✓
#   user ?auth → ⚡search "authentication" → ∃jwt.py ∧ oauth.py → !use jwt


DENSE_SYSTEM_PROMPT = """
## DENSE THINKING MODE

Think in COMPRESSED SEMANTIC NOTATION to maximize reasoning efficiency.

### NOTATION:
→ leads-to  ← because  ∃ exists  ∄ not-found  ? query  ! answer
∧ and  ∨ or  ¬ not  ⊂ contains  ≈ similar  ∴ therefore  ∵ because
✓ done  ✗ fail  ⚡tool  📁file  🔍search  💭think

### FORMAT:
- Compress: "?config brain" not "I need to find configuration in brain folder"
- Chain: premise → inference → conclusion
- Tools: ⚡tool_name:{"param":"value"}
- Assert: !ANSWER: [conclusion]

### EXAMPLES:
?project structure → ⚡brain_list_dir:{"dir_path":"."} → ∃brain/ ∧ tests/ → 📁brain ⊂ core
user ?auth method → 🔍"authentication" → ∃jwt patterns → !ANSWER: use JWT

### RULES:
1. Minimize English words
2. Use symbols for logical flow  
3. Only expand to full English in !ANSWER
4. Keep each thought <50 tokens
"""


HYBRID_SYSTEM_PROMPT = """
## HYBRID THINKING MODE

Use compressed notation for INTERNAL reasoning, expand for CONCLUSIONS.

### DENSE NOTATION (for thinking):
→ leads-to  ? query  ! answer  ∃ exists  ∄ not-found
∧ and  ∨ or  ∴ therefore  ✓ done  ✗ fail
⚡ tool call  📁 file  🔍 search

### FORMAT:
- THINK lines: compressed (💭 ?goal → ⚡tool → result → inference)
- TOOL lines: TOOL_REQUEST[name:{"param":"value"}]
- ANSWER: Full English explanation

### EXAMPLE:
💭 ?config location → need brain/ contents
TOOL_REQUEST[brain_list_dir:{"dir_path":"brain"}]
💭 ∃config.py ✓ → settings here
!ANSWER: Configuration is in brain/config.py. It uses Pydantic Settings for environment-based configuration.
"""


@dataclass
class DenseThought:
    """Parsed dense thought."""
    raw: str
    symbols: list[str]
    tool_calls: list[str]
    is_answer: bool
    semantic_density: float  # symbols per token ratio
    
    @classmethod
    def parse(cls, text: str) -> "DenseThought":
        """Parse a dense thought string."""
        # Count semantic symbols
        symbols = re.findall(r'[→←∃∄?!∧∨¬⊂≈∴∵⟹⟶✓✗⚡📁🔍💭]', text)
        
        # Extract tool calls
        tool_pattern = r'⚡(\w+):\{[^}]+\}|TOOL_REQUEST\[(\w+):\{[^}]+\}\]'
        tool_calls = [m[0] or m[1] for m in re.findall(tool_pattern, text)]
        
        # Check if this is an answer
        is_answer = '!ANSWER' in text or text.strip().startswith('!')
        
        # Calculate semantic density (symbols per word)
        words = len(text.split())
        semantic_density = len(symbols) / max(words, 1)
        
        return cls(
            raw=text,
            symbols=symbols,
            tool_calls=tool_calls,
            is_answer=is_answer,
            semantic_density=semantic_density
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
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_tokens": self.total_tokens,
            "total_symbols": self.total_symbols,
            "total_tool_calls": self.total_tool_calls,
            "thoughts": self.thoughts,
            "avg_density": round(self.avg_density, 3),
            "compression_ratio": round(self.compression_ratio, 2),
        }


class DenseThinkingAnalyzer:
    """Analyze dense thinking patterns and measure compression."""
    
    # Estimated English token equivalents for symbols
    SYMBOL_TOKEN_VALUES = {
        '→': 3,   # "leads to" / "then"
        '←': 2,   # "because"
        '∃': 3,   # "there exists" / "found"
        '∄': 4,   # "does not exist"
        '?': 2,   # "need to find"
        '!': 2,   # "I conclude"
        '∧': 1,   # "and"
        '∨': 1,   # "or"
        '¬': 1,   # "not"
        '⊂': 3,   # "is contained in"
        '≈': 2,   # "is similar to"
        '∴': 2,   # "therefore"
        '∵': 2,   # "because"
        '✓': 2,   # "confirmed"
        '✗': 2,   # "failed"
        '⚡': 4,  # "I will use tool"
        '📁': 2,  # "file/directory"
        '🔍': 3,  # "searching for"
        '💭': 3,  # "I am thinking"
    }
    
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
        
        # Calculate compression ratio
        # How many English tokens would these symbols represent?
        english_equivalent = 0
        for thought in parsed:
            for symbol in thought.symbols:
                english_equivalent += cls.SYMBOL_TOKEN_VALUES.get(symbol, 2)
        
        # Compression = (english_equivalent + actual_tokens) / actual_tokens
        # Higher = more compressed
        compression = (english_equivalent + total_tokens) / max(total_tokens, 1)
        
        avg_density = sum(t.semantic_density for t in parsed) / max(len(parsed), 1)
        
        return DenseMetrics(
            total_tokens=total_tokens,
            total_symbols=total_symbols,
            total_tool_calls=total_tool_calls,
            thoughts=len(thoughts),
            avg_density=avg_density,
            compression_ratio=compression,
        )
    
    @classmethod
    def expand_to_english(cls, dense_text: str) -> str:
        """Expand dense notation to readable English.
        
        This is a simple expansion - a real implementation might use
        the LLM itself to expand more naturally.
        """
        expansions = {
            '→': ' leads to ',
            '←': ' because ',
            '∃': ' found ',
            '∄': ' not found ',
            '?': ' need ',
            '!': ' conclude: ',
            '∧': ' and ',
            '∨': ' or ',
            '¬': ' not ',
            '⊂': ' contains ',
            '≈': ' is similar to ',
            '∴': ' therefore ',
            '∵': ' because ',
            '✓': ' (confirmed) ',
            '✗': ' (failed) ',
            '⚡': ' [tool: ',
            '📁': ' file ',
            '🔍': ' search ',
            '💭': ' thinking: ',
        }
        
        result = dense_text
        for symbol, expansion in expansions.items():
            result = result.replace(symbol, expansion)
        
        return result.strip()


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
