"""Phase 12B: Information Density 📊

Scientific Question:
"Does .ai/ structure have higher information density than narrative docs?"

Method:
- Calculate Shannon entropy (bits/token) for different doc types:
  1. .ai/ files (context.md, codebase-map.json)
  2. docs/ files (Sphinx RST documentation)
  3. Source code comments/docstrings
- Measure "knowledge units" per 1000 tokens:
  - Module locations
  - Dependency relationships
  - Purpose statements
  - Function signatures
- Calculate information density ratio

Expected Results:
- .ai/ entropy: 12-15 bits/token (structured, high signal)
- docs/ entropy: 8-10 bits/token (narrative, explanatory)
- comments: 6-8 bits/token (scattered, local context)
- Knowledge density .ai/ >> docs/ >> comments

Why This Is Meta-Science:
- Quantifies "structured > narrative" hypothesis
- Shows WHY .ai/ works (information theory!)
- Validates design decisions empirically
- Shows optimal documentation format

Democratic Science:
- Shannon entropy calculation
- Simple token counting
- Known information units
- Fast (<5min)
"""

import pytest
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
from collections import Counter
import math


@dataclass
class InformationDensityResults:
    """Results from information density analysis."""
    
    # Shannon entropy (bits/token)
    entropy_ai: float
    entropy_docs: float
    entropy_comments: float
    
    # Knowledge units per 1000 tokens
    knowledge_density_ai: float
    knowledge_density_docs: float
    knowledge_density_comments: float
    
    # Token statistics
    total_tokens_ai: int
    total_tokens_docs: int
    total_tokens_comments: int
    
    # Knowledge unit counts
    knowledge_units_ai: int
    knowledge_units_docs: int
    knowledge_units_comments: int
    
    # Ratios
    entropy_ratio_ai_to_docs: float
    density_ratio_ai_to_docs: float
    
    # Verdict
    most_dense: str
    least_dense: str
    structure_advantage: float  # How much better is .ai/?
    
    # Metadata
    timestamp: str
    
    def to_dict(self):
        return asdict(self)


class TestPhase12BInformationDensity:
    """Phase 12B: Measure information density of documentation types."""
    
    def test_complete_information_density_analysis(self):
        """Run complete information density analysis."""
        self._step1_collect_documentation()
        self._step2_tokenize_content()
        self._step3_calculate_shannon_entropy()
        self._step4_count_knowledge_units()
        self._step5_calculate_densities()
        self._step6_compare_formats()
        self._step7_interpret_results()
        self._step8_save_results()
    
    def _step1_collect_documentation(self):
        """Collect all documentation sources."""
        print("\n" + "="*60)
        print("📊 PHASE 12B: INFORMATION DENSITY")
        print("="*60)
        print("\n📚 Step 1: Collecting documentation...")
        
        repo_root = Path(__file__).parent.parent
        
        # Collect .ai/ files
        ai_dir = repo_root / ".ai"
        self.ai_content = []
        if ai_dir.exists():
            for file_path in ai_dir.glob("*.md"):
                self.ai_content.append(file_path.read_text())
            for file_path in ai_dir.glob("*.json"):
                self.ai_content.append(file_path.read_text())
        
        # Collect docs/ files
        docs_dir = repo_root / "docs"
        self.docs_content = []
        if docs_dir.exists():
            for file_path in docs_dir.glob("*.rst"):
                self.docs_content.append(file_path.read_text())
            for file_path in docs_dir.glob("*.md"):
                self.docs_content.append(file_path.read_text())
        
        # Collect source code comments
        brain_dir = repo_root / "brain"
        self.comments_content = []
        if brain_dir.exists():
            for file_path in brain_dir.glob("**/*.py"):
                content = file_path.read_text()
                # Extract comments and docstrings
                comments = re.findall(r'#.*$|""".*?"""|\'\'\'.*?\'\'\'', content, re.MULTILINE | re.DOTALL)
                self.comments_content.extend(comments)
        
        print(f"   ✅ Collected:")
        print(f"      .ai/ files: {len(self.ai_content)} files")
        print(f"      docs/ files: {len(self.docs_content)} files")
        print(f"      Source comments: {len(self.comments_content)} items")
    
    def _step2_tokenize_content(self):
        """Tokenize all content."""
        print("\n🔤 Step 2: Tokenizing content...")
        
        # Simple word-based tokenization
        def tokenize(text: str) -> List[str]:
            # Lowercase and split on whitespace/punctuation
            tokens = re.findall(r'\w+', text.lower())
            return tokens
        
        self.ai_tokens = []
        for content in self.ai_content:
            self.ai_tokens.extend(tokenize(content))
        
        self.docs_tokens = []
        for content in self.docs_content:
            self.docs_tokens.extend(tokenize(content))
        
        self.comments_tokens = []
        for content in self.comments_content:
            self.comments_tokens.extend(tokenize(content))
        
        self.total_tokens_ai = len(self.ai_tokens)
        self.total_tokens_docs = len(self.docs_tokens)
        self.total_tokens_comments = len(self.comments_tokens)
        
        print(f"   ✅ Token counts:")
        print(f"      .ai/: {self.total_tokens_ai:,} tokens")
        print(f"      docs/: {self.total_tokens_docs:,} tokens")
        print(f"      comments: {self.total_tokens_comments:,} tokens")
    
    def _step3_calculate_shannon_entropy(self):
        """Calculate Shannon entropy for each document type."""
        print("\n📈 Step 3: Calculating Shannon entropy...")
        
        def calculate_entropy(tokens: List[str]) -> float:
            """Calculate Shannon entropy in bits per token."""
            if not tokens:
                return 0.0
            
            # Count token frequencies
            token_counts = Counter(tokens)
            total = len(tokens)
            
            # Calculate probabilities
            probs = [count / total for count in token_counts.values()]
            
            # Shannon entropy: H = -Σ p(x) * log2(p(x))
            entropy = -sum(p * math.log2(p) for p in probs if p > 0)
            
            return entropy
        
        self.entropy_ai = calculate_entropy(self.ai_tokens)
        self.entropy_docs = calculate_entropy(self.docs_tokens)
        self.entropy_comments = calculate_entropy(self.comments_tokens)
        
        print(f"   Shannon entropy (bits/token):")
        print(f"      .ai/: {self.entropy_ai:.2f}")
        print(f"      docs/: {self.entropy_docs:.2f}")
        print(f"      comments: {self.entropy_comments:.2f}")
    
    def _step4_count_knowledge_units(self):
        """Count discrete knowledge units in each format."""
        print("\n📝 Step 4: Counting knowledge units...")
        
        # Knowledge units are:
        # - Module locations (file paths)
        # - Dependency relationships (imports/imported_by)
        # - Purpose statements
        # - Function/class definitions
        
        # For .ai/
        ai_text = " ".join(self.ai_content)
        self.knowledge_units_ai = 0
        
        # Count file paths
        self.knowledge_units_ai += len(re.findall(r'brain/[\w/]+\.py', ai_text))
        
        # Count relationships (imports, imported_by)
        self.knowledge_units_ai += len(re.findall(r'"imports":|"imported_by":', ai_text))
        
        # Count purpose statements
        self.knowledge_units_ai += len(re.findall(r'"purpose":', ai_text))
        
        # Count type definitions
        self.knowledge_units_ai += len(re.findall(r'"type":', ai_text))
        
        # For docs/
        docs_text = " ".join(self.docs_content)
        self.knowledge_units_docs = 0
        
        # Count code blocks (examples)
        self.knowledge_units_docs += len(re.findall(r'```|::\n\n', docs_text))
        
        # Count section headers
        self.knowledge_units_docs += len(re.findall(r'^#+\s|\n={3,}|\n-{3,}', docs_text, re.MULTILINE))
        
        # Count file references
        self.knowledge_units_docs += len(re.findall(r'brain/[\w/]+\.py|\.rst', docs_text))
        
        # For comments
        comments_text = " ".join(self.comments_content)
        self.knowledge_units_comments = 0
        
        # Count function/class definitions
        self.knowledge_units_comments += len(re.findall(r'def\s+\w+|class\s+\w+', comments_text))
        
        # Count parameter descriptions
        self.knowledge_units_comments += len(re.findall(r'Args:|Returns:|Raises:', comments_text))
        
        # Count TODO/FIXME/NOTE markers
        self.knowledge_units_comments += len(re.findall(r'TODO|FIXME|NOTE|XXX', comments_text))
        
        print(f"   Knowledge units:")
        print(f"      .ai/: {self.knowledge_units_ai}")
        print(f"      docs/: {self.knowledge_units_docs}")
        print(f"      comments: {self.knowledge_units_comments}")
    
    def _step5_calculate_densities(self):
        """Calculate knowledge density (units per 1000 tokens)."""
        print("\n📊 Step 5: Calculating knowledge densities...")
        
        # Density = (knowledge_units / total_tokens) * 1000
        self.knowledge_density_ai = (self.knowledge_units_ai / max(self.total_tokens_ai, 1)) * 1000
        self.knowledge_density_docs = (self.knowledge_units_docs / max(self.total_tokens_docs, 1)) * 1000
        self.knowledge_density_comments = (self.knowledge_units_comments / max(self.total_tokens_comments, 1)) * 1000
        
        print(f"   Knowledge density (units per 1000 tokens):")
        print(f"      .ai/: {self.knowledge_density_ai:.1f}")
        print(f"      docs/: {self.knowledge_density_docs:.1f}")
        print(f"      comments: {self.knowledge_density_comments:.1f}")
    
    def _step6_compare_formats(self):
        """Compare documentation formats."""
        print("\n⚖️  Step 6: Comparing formats...")
        
        # Calculate ratios
        self.entropy_ratio = self.entropy_ai / max(self.entropy_docs, 0.1)
        self.density_ratio = self.knowledge_density_ai / max(self.knowledge_density_docs, 0.1)
        
        # Rank by density
        densities = {
            '.ai/': self.knowledge_density_ai,
            'docs/': self.knowledge_density_docs,
            'comments': self.knowledge_density_comments
        }
        sorted_densities = sorted(densities.items(), key=lambda x: x[1], reverse=True)
        
        self.most_dense = sorted_densities[0][0]
        self.least_dense = sorted_densities[-1][0]
        
        # Structure advantage (how much better is .ai/ vs average of others?)
        avg_other = (self.knowledge_density_docs + self.knowledge_density_comments) / 2
        self.structure_advantage = (self.knowledge_density_ai - avg_other) / avg_other if avg_other > 0 else 0
        
        print(f"   Entropy ratio (.ai/ / docs/): {self.entropy_ratio:.2f}x")
        print(f"   Density ratio (.ai/ / docs/): {self.density_ratio:.2f}x")
        print(f"   Most dense: {self.most_dense}")
        print(f"   Least dense: {self.least_dense}")
        print(f"   Structure advantage: {self.structure_advantage:.1%}")
    
    def _step7_interpret_results(self):
        """Interpret density results."""
        print("\n🔬 Step 7: Interpreting results...")
        
        print(f"\n   📌 KEY INSIGHTS:")
        print(f"      .ai/ has {self.entropy_ratio:.1f}x higher entropy than docs/")
        print(f"      .ai/ has {self.density_ratio:.1f}x more knowledge units per token")
        print(f"      Structure provides {self.structure_advantage:.0%} more information density")
        
        # Practical interpretation
        if self.density_ratio > 2.0:
            interpretation = "DRAMATICALLY higher"
        elif self.density_ratio > 1.5:
            interpretation = "SIGNIFICANTLY higher"
        elif self.density_ratio > 1.2:
            interpretation = "MODERATELY higher"
        else:
            interpretation = "COMPARABLE"
        
        print(f"\n   🎯 Verdict: .ai/ structure has {interpretation}")
        print(f"              information density vs narrative docs!")
    
    def _step8_save_results(self):
        """Save information density results."""
        print("\n💾 Step 8: Saving results...")
        
        results = InformationDensityResults(
            entropy_ai=self.entropy_ai,
            entropy_docs=self.entropy_docs,
            entropy_comments=self.entropy_comments,
            knowledge_density_ai=self.knowledge_density_ai,
            knowledge_density_docs=self.knowledge_density_docs,
            knowledge_density_comments=self.knowledge_density_comments,
            total_tokens_ai=self.total_tokens_ai,
            total_tokens_docs=self.total_tokens_docs,
            total_tokens_comments=self.total_tokens_comments,
            knowledge_units_ai=self.knowledge_units_ai,
            knowledge_units_docs=self.knowledge_units_docs,
            knowledge_units_comments=self.knowledge_units_comments,
            entropy_ratio_ai_to_docs=self.entropy_ratio,
            density_ratio_ai_to_docs=self.density_ratio,
            most_dense=self.most_dense,
            least_dense=self.least_dense,
            structure_advantage=self.structure_advantage,
            timestamp=datetime.now().isoformat()
        )
        
        # Save to JSON
        output_path = Path(__file__).parent / "fixtures" / "phase12b_information_density.json"
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results.to_dict(), f, indent=2)
        
        print(f"   ✅ Results saved to: {output_path}")
        print("\n" + "="*60)
        print("📊 PHASE 12B COMPLETE: Information Density")
        print("="*60)
        print(f"\n🎯 KEY FINDINGS:")
        print(f"   Entropy ratio: {results.entropy_ratio_ai_to_docs:.2f}x")
        print(f"   Density ratio: {results.density_ratio_ai_to_docs:.2f}x")
        print(f"   Structure advantage: {results.structure_advantage:.0%}")
        print(f"   Most dense: {results.most_dense}")
        print(f"\n   🔬 INSIGHT: Structured docs have {results.density_ratio_ai_to_docs:.1f}x more")
        print("              information per token!")
        print("="*60 + "\n")
        
        assert output_path.exists()


if __name__ == "__main__":
    # Run Phase 12B tests
    print("\n📊 Starting Phase 12B: Information Density Analysis\n")
    pytest.main([__file__, "-v", "-s"])
