#!/usr/bin/env python3
"""Generate ASL training data using a larger model (qwen2.5-coder:7b).

This creates the dataset we'll use to fine-tune qwen2.5:0.5b.
"""

import json
import httpx
import random
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Iterator

# === ASL Symbol Reference ===
ASL_SYMBOLS = """
● = certain/true/valid
◑ = uncertain/possible/unknown
⊥ = contradiction/impossible/invalid
→ = implies/leads to
← = follows from
⟷ = bidirectional/equivalent
∧ = and/conjunction
∨ = or/disjunction  
¬ = not/negation
∈ = element of/member of
∉ = not element of
∴ = therefore/conclusion
∵ = because/reason
? = query/unknown
! = assert/certain
"""

# === Training Example Templates ===

LOGIC_TEMPLATES = [
    # Modus Ponens
    {
        "pattern": "modus_ponens",
        "input": "P → Q\nP: ●\n?Q",
        "output": "P:● ∧ (P→Q) → Q:●\n∴ Q: ●",
    },
    {
        "pattern": "modus_ponens_uncertain",
        "input": "P → Q\nP: ◑\n?Q",
        "output": "P:◑ ∧ (P→Q) → Q:◑\n∴ Q: ◑",
    },
    # Modus Tollens
    {
        "pattern": "modus_tollens",
        "input": "P → Q\nQ: ⊥\n?P",
        "output": "Q:⊥ ∧ (P→Q) → P:⊥\n∴ P: ⊥",
    },
    # Conjunction
    {
        "pattern": "conjunction_true",
        "input": "A: ●\nB: ●\n?A∧B",
        "output": "A:● ∧ B:● → (A∧B):●\n∴ A∧B: ●",
    },
    {
        "pattern": "conjunction_uncertain",
        "input": "A: ●\nB: ◑\n?A∧B",
        "output": "A:● ∧ B:◑ → (A∧B):◑\n∴ A∧B: ◑",
    },
    # Disjunction
    {
        "pattern": "disjunction_true",
        "input": "A: ●\nB: ⊥\n?A∨B",
        "output": "A:● ∨ B:⊥ → (A∨B):●\n∴ A∨B: ●",
    },
    # Contradiction detection
    {
        "pattern": "contradiction",
        "input": "P: ●\n¬P: ●\n?consistent",
        "output": "P:● ∧ ¬P:● → ⊥\n∴ consistent: ⊥",
    },
    {
        "pattern": "no_contradiction",
        "input": "P: ●\nQ: ●\n?consistent",
        "output": "P:● ∧ Q:● → no conflict\n∴ consistent: ●",
    },
    # Negation
    {
        "pattern": "negation",
        "input": "P: ●\n?¬P",
        "output": "P:● → ¬P:⊥\n∴ ¬P: ⊥",
    },
]

CHESS_TEMPLATES = [
    # Valid squares
    {
        "pattern": "chess_valid",
        "input": "?move:{square}\nfile∈{{a,b,c,d,e,f,g,h}}\nrank∈{{1,2,3,4,5,6,7,8}}",
        "output": "?{file} ∈{{a-h}}? → ● → ?{rank} ∈{{1-8}}? → ●\n∴ {square}: ●valid",
        "generate": lambda: {
            "square": f"{random.choice('abcdefgh')}{random.randint(1,8)}",
            "file": lambda s: s[0],
            "rank": lambda s: s[1],
        }
    },
    # Invalid rank
    {
        "pattern": "chess_invalid_rank",
        "input": "?move:{square}\nfile∈{{a,b,c,d,e,f,g,h}}\nrank∈{{1,2,3,4,5,6,7,8}}",
        "output": "?{file} ∈{{a-h}}? → ● → ?{rank} ∈{{1-8}}? → ⊥\n∴ {square}: ⊥invalid",
        "generate": lambda: {
            "square": f"{random.choice('abcdefgh')}{random.choice([0, 9, 10])}",
            "file": lambda s: s[0],
            "rank": lambda s: s[1:],
        }
    },
    # Invalid file
    {
        "pattern": "chess_invalid_file",
        "input": "?move:{square}\nfile∈{{a,b,c,d,e,f,g,h}}\nrank∈{{1,2,3,4,5,6,7,8}}",
        "output": "?{file} ∈{{a-h}}? → ⊥\n∴ {square}: ⊥invalid",
        "generate": lambda: {
            "square": f"{random.choice('ijklmnop')}{random.randint(1,8)}",
            "file": lambda s: s[0],
            "rank": lambda s: s[1],
        }
    },
]

SET_MEMBERSHIP_TEMPLATES = [
    {
        "pattern": "set_member",
        "input": "S = {{{elements}}}\n?{x} ∈ S",
        "output": "{x} ∈ {{{elements}}}? → ●\n∴ {x} ∈ S: ●",
        "generate": lambda: {
            "elements": ",".join(map(str, random.sample(range(1, 20), 5))),
            "x": lambda e: random.choice(e.split(",")),
        }
    },
    {
        "pattern": "set_not_member",
        "input": "S = {{{elements}}}\n?{x} ∈ S",
        "output": "{x} ∈ {{{elements}}}? → ⊥\n∴ {x} ∈ S: ⊥",
        "generate": lambda: {
            "elements": ",".join(map(str, random.sample(range(1, 10), 5))),
            "x": lambda e: str(random.randint(15, 20)),  # Not in set
        }
    },
]

UNCERTAINTY_PROPAGATION = [
    {
        "pattern": "chain_certain",
        "input": "A: ●\nA → B\nB → C\n?C",
        "output": "A:● → B:● → C:●\n∴ C: ●",
    },
    {
        "pattern": "chain_uncertain",
        "input": "A: ◑\nA → B\nB → C\n?C",
        "output": "A:◑ → B:◑ → C:◑\n∴ C: ◑",
    },
    {
        "pattern": "chain_breaks",
        "input": "A: ●\nA → B\nB: ⊥\n?C where B → C",
        "output": "A:● but B:⊥ (override) → C:⊥\n∴ C: ⊥",
    },
]


@dataclass
class TrainingExample:
    """A single training example."""
    input: str
    output: str
    pattern: str


def generate_static_examples() -> list[TrainingExample]:
    """Generate examples from static templates."""
    examples = []
    
    # Logic examples
    for template in LOGIC_TEMPLATES:
        examples.append(TrainingExample(
            input=template["input"],
            output=template["output"],
            pattern=template["pattern"],
        ))
    
    # Uncertainty propagation
    for template in UNCERTAINTY_PROPAGATION:
        examples.append(TrainingExample(
            input=template["input"],
            output=template["output"],
            pattern=template["pattern"],
        ))
    
    return examples


def generate_chess_examples(n: int = 100) -> list[TrainingExample]:
    """Generate n chess validation examples."""
    examples = []
    
    for _ in range(n):
        # 60% valid, 20% invalid rank, 20% invalid file
        r = random.random()
        if r < 0.6:
            template = CHESS_TEMPLATES[0]  # valid
        elif r < 0.8:
            template = CHESS_TEMPLATES[1]  # invalid rank
        else:
            template = CHESS_TEMPLATES[2]  # invalid file
        
        gen = template["generate"]()
        square = gen["square"]
        file = gen["file"](square) if callable(gen["file"]) else gen["file"]
        rank = gen["rank"](square) if callable(gen["rank"]) else gen["rank"]
        
        examples.append(TrainingExample(
            input=template["input"].format(square=square),
            output=template["output"].format(square=square, file=file, rank=rank),
            pattern=template["pattern"],
        ))
    
    return examples


def generate_variable_examples(n: int = 50) -> list[TrainingExample]:
    """Generate examples with different variable names."""
    examples = []
    var_names = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    
    for _ in range(n):
        # Pick random variables
        vars = random.sample(var_names, 3)
        p, q, r = vars
        
        # Modus ponens with different vars
        examples.append(TrainingExample(
            input=f"{p} → {q}\n{p}: ●\n?{q}",
            output=f"{p}:● ∧ ({p}→{q}) → {q}:●\n∴ {q}: ●",
            pattern="modus_ponens_var",
        ))
        
        # Chain with different vars
        examples.append(TrainingExample(
            input=f"{p}: ●\n{p} → {q}\n{q} → {r}\n?{r}",
            output=f"{p}:● → {q}:● → {r}:●\n∴ {r}: ●",
            pattern="chain_var",
        ))
    
    return examples


def format_for_training(examples: list[TrainingExample]) -> list[dict]:
    """Format examples for HuggingFace datasets."""
    formatted = []
    
    for ex in examples:
        # Format as instruction-following
        formatted.append({
            "instruction": "Perform symbolic reasoning using ASL notation.",
            "input": ex.input,
            "output": ex.output,
            "pattern": ex.pattern,
        })
        
        # Also format as raw completion
        formatted.append({
            "text": f"<|im_start|>user\n{ex.input}<|im_end|>\n<|im_start|>assistant\n{ex.output}<|im_end|>",
            "pattern": ex.pattern,
        })
    
    return formatted


def main():
    """Generate and save training data."""
    print("Generating ASL training data...")
    
    # Generate all examples
    examples = []
    
    print("  - Static logic examples...")
    examples.extend(generate_static_examples())
    
    print("  - Chess validation examples...")
    examples.extend(generate_chess_examples(200))
    
    print("  - Variable name variations...")
    examples.extend(generate_variable_examples(100))
    
    print(f"\nTotal examples: {len(examples)}")
    
    # Format for training
    formatted = format_for_training(examples)
    
    # Save
    output_path = Path(__file__).parent / "asl_training_data.jsonl"
    with open(output_path, "w") as f:
        for item in formatted:
            f.write(json.dumps(item) + "\n")
    
    print(f"Saved to {output_path}")
    
    # Show sample
    print("\n=== Sample Examples ===")
    for ex in random.sample(examples, 3):
        print(f"\nPattern: {ex.pattern}")
        print(f"Input:\n{ex.input}")
        print(f"Output:\n{ex.output}")


if __name__ == "__main__":
    main()
