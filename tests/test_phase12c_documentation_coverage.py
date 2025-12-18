"""Phase 12C: Documentation Coverage 📋

Scientific Question:
"How complete is the .ai/ documentation coverage?"

Method:
- Count total Python modules in brain/
- Count modules documented in codebase-map.json
- Count specialists with registry entries
- Count files with @ai-* annotations
- Measure consistency between sources
- Calculate coverage percentage

Expected Results:
- Core module coverage: 90-95%
- Specialist coverage: 100%
- Annotation coverage: 70-80%
- Consistency score: 85-95%

Why This Is Meta-Science:
- Validates documentation completeness
- Shows systematic approach (not ad-hoc)
- Measures consistency (single source of truth?)
- Quality metric for infrastructure

Democratic Science:
- File counting (trivial computation)
- JSON parsing
- Pattern matching
- Fast (<2min)
"""

import pytest
import json
import re
import ast
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, asdict


@dataclass
class DocumentationCoverageResults:
    """Results from documentation coverage analysis."""
    
    # Coverage metrics
    total_modules: int
    documented_modules: int
    coverage_percentage: float
    
    # Specialist coverage
    total_specialists: int
    registered_specialists: int
    specialist_coverage: float
    
    # Annotation coverage
    files_with_annotations: int
    annotation_coverage: float
    
    # Consistency checks
    consistency_score: float
    mismatches: List[str]
    
    # Gap analysis
    undocumented_modules: List[str]
    missing_registry_entries: List[str]
    
    # Quality metrics
    completeness_grade: str  # A, B, C, D, F
    areas_for_improvement: List[str]
    
    # Metadata
    timestamp: str
    
    def to_dict(self):
        return asdict(self)


class TestPhase12CDocumentationCoverage:
    """Phase 12C: Measure documentation coverage and consistency."""
    
    def test_complete_coverage_analysis(self):
        """Run complete documentation coverage analysis."""
        self._step1_discover_modules()
        self._step2_check_codebase_map_coverage()
        self._step3_check_specialist_registry()
        self._step4_check_annotations()
        self._step5_measure_consistency()
        self._step6_identify_gaps()
        self._step7_calculate_grade()
        self._step8_save_results()
    
    def _step1_discover_modules(self):
        """Discover all Python modules in brain/."""
        print("\n" + "="*60)
        print("📋 PHASE 12C: DOCUMENTATION COVERAGE")
        print("="*60)
        print("\n🔍 Step 1: Discovering modules...")
        
        repo_root = Path(__file__).parent.parent
        brain_dir = repo_root / "brain"
        
        # Find all Python files (excluding __pycache__)
        self.all_modules = []
        if brain_dir.exists():
            for py_file in brain_dir.rglob("*.py"):
                if "__pycache__" not in str(py_file):
                    # Get relative path from repo root
                    rel_path = py_file.relative_to(repo_root)
                    self.all_modules.append(str(rel_path))
        
        # Find specialists
        specialist_dir = brain_dir / "specialists"
        self.all_specialists = []
        if specialist_dir.exists():
            for py_file in specialist_dir.glob("*_specialist.py"):
                rel_path = py_file.relative_to(repo_root)
                self.all_specialists.append(str(rel_path))
        
        self.total_modules = len(self.all_modules)
        self.total_specialists = len(self.all_specialists)
        
        print(f"   ✅ Discovered:")
        print(f"      Total modules: {self.total_modules}")
        print(f"      Total specialists: {self.total_specialists}")
    
    def _step2_check_codebase_map_coverage(self):
        """Check coverage in codebase-map.json."""
        print("\n🗺️  Step 2: Checking codebase-map.json coverage...")
        
        # Load codebase-map.json
        map_path = Path(__file__).parent.parent / ".ai" / "codebase-map.json"
        if map_path.exists():
            with open(map_path) as f:
                self.codebase_map = json.load(f)
        else:
            self.codebase_map = {"modules": {}}
        
        # Check which modules are documented
        documented = set(self.codebase_map.get('modules', {}).keys())
        self.documented_modules = [m for m in self.all_modules if m in documented]
        self.undocumented_modules = [m for m in self.all_modules if m not in documented]
        
        self.coverage_percentage = (len(self.documented_modules) / max(self.total_modules, 1)) * 100
        
        print(f"   Documented modules: {len(self.documented_modules)}/{self.total_modules}")
        print(f"   Coverage: {self.coverage_percentage:.1f}%")
        
        if self.undocumented_modules[:5]:
            print(f"   Sample undocumented: {self.undocumented_modules[:5]}")
    
    def _step3_check_specialist_registry(self):
        """Check specialist registry coverage."""
        print("\n📝 Step 3: Checking specialist registry...")
        
        # Load specialist-registry.json
        registry_path = Path(__file__).parent.parent / ".ai" / "specialist-registry.json"
        if registry_path.exists():
            with open(registry_path) as f:
                self.specialist_registry = json.load(f)
        else:
            self.specialist_registry = {"specialists": {}}
        
        # Check registered specialists
        registered = set()
        for spec_name, spec_data in self.specialist_registry.get('specialists', {}).items():
            spec_file = spec_data.get('file', '')
            if spec_file:
                registered.add(spec_file)
        
        self.registered_specialists = [s for s in self.all_specialists if s in registered]
        self.missing_registry_entries = [s for s in self.all_specialists if s not in registered]
        
        self.specialist_coverage = (len(self.registered_specialists) / max(self.total_specialists, 1)) * 100
        
        print(f"   Registered specialists: {len(self.registered_specialists)}/{self.total_specialists}")
        print(f"   Coverage: {self.specialist_coverage:.1f}%")
        
        if self.missing_registry_entries:
            print(f"   Missing from registry: {self.missing_registry_entries}")
    
    def _step4_check_annotations(self):
        """Check @ai-* annotation coverage."""
        print("\n🏷️  Step 4: Checking annotation coverage...")
        
        # Scan source files for @ai-* annotations
        self.annotated_files = []
        
        for module_path in self.all_modules:
            full_path = Path(__file__).parent.parent / module_path
            if full_path.exists():
                content = full_path.read_text()
                # Look for @ai- annotations in comments
                if re.search(r'#\s*@ai-', content):
                    self.annotated_files.append(module_path)
        
        self.annotation_coverage = (len(self.annotated_files) / max(self.total_modules, 1)) * 100
        
        print(f"   Files with annotations: {len(self.annotated_files)}/{self.total_modules}")
        print(f"   Coverage: {self.annotation_coverage:.1f}%")
    
    def _step5_measure_consistency(self):
        """Measure consistency between documentation sources."""
        print("\n⚖️  Step 5: Measuring consistency...")
        
        self.mismatches = []
        
        # Check: Are all annotated files in codebase-map?
        for annotated in self.annotated_files:
            if annotated not in self.codebase_map.get('modules', {}):
                self.mismatches.append(f"Annotated but not in map: {annotated}")
        
        # Check: Are all registered specialists in codebase-map?
        for specialist in self.registered_specialists:
            if specialist not in self.codebase_map.get('modules', {}):
                self.mismatches.append(f"In registry but not in map: {specialist}")
        
        # Consistency score (lower is better, 0 = perfect)
        # Based on % of files with mismatches
        total_checks = len(self.annotated_files) + len(self.registered_specialists)
        if total_checks > 0:
            consistency_score = (1 - len(self.mismatches) / total_checks) * 100
        else:
            consistency_score = 100.0
        
        self.consistency_score = consistency_score
        
        print(f"   Consistency score: {consistency_score:.1f}%")
        print(f"   Mismatches found: {len(self.mismatches)}")
        
        if self.mismatches[:3]:
            print(f"   Sample mismatches:")
            for m in self.mismatches[:3]:
                print(f"      - {m}")
    
    def _step6_identify_gaps(self):
        """Identify documentation gaps."""
        print("\n🔍 Step 6: Identifying gaps...")
        
        # Prioritize important modules that should be documented
        important_patterns = [
            r'brain/app\.py',
            r'brain/llm\.py',
            r'brain/rag_store\.py',
            r'brain/prompt_builder/',
            r'brain/specialists/',
        ]
        
        important_undocumented = []
        for module in self.undocumented_modules:
            if any(re.search(pattern, module) for pattern in important_patterns):
                important_undocumented.append(module)
        
        self.areas_for_improvement = []
        
        if self.coverage_percentage < 90:
            self.areas_for_improvement.append("Increase overall module coverage")
        
        if self.specialist_coverage < 100:
            self.areas_for_improvement.append("Complete specialist registry")
        
        if self.annotation_coverage < 70:
            self.areas_for_improvement.append("Add more source annotations")
        
        if self.consistency_score < 90:
            self.areas_for_improvement.append("Fix documentation inconsistencies")
        
        if important_undocumented:
            self.areas_for_improvement.append(f"Document critical modules: {important_undocumented[:3]}")
        
        print(f"   Critical undocumented: {len(important_undocumented)}")
        print(f"   Areas for improvement: {len(self.areas_for_improvement)}")
    
    def _step7_calculate_grade(self):
        """Calculate overall documentation grade."""
        print("\n📊 Step 7: Calculating grade...")
        
        # Weighted scoring
        weights = {
            'coverage': 0.40,
            'specialist': 0.25,
            'annotation': 0.15,
            'consistency': 0.20
        }
        
        total_score = (
            self.coverage_percentage * weights['coverage'] +
            self.specialist_coverage * weights['specialist'] +
            self.annotation_coverage * weights['annotation'] +
            self.consistency_score * weights['consistency']
        )
        
        # Grade assignment
        if total_score >= 90:
            grade = 'A'
        elif total_score >= 80:
            grade = 'B'
        elif total_score >= 70:
            grade = 'C'
        elif total_score >= 60:
            grade = 'D'
        else:
            grade = 'F'
        
        self.completeness_grade = grade
        
        print(f"   Total score: {total_score:.1f}/100")
        print(f"   Grade: {grade}")
    
    def _step8_save_results(self):
        """Save coverage results."""
        print("\n💾 Step 8: Saving results...")
        
        results = DocumentationCoverageResults(
            total_modules=self.total_modules,
            documented_modules=len(self.documented_modules),
            coverage_percentage=self.coverage_percentage,
            total_specialists=self.total_specialists,
            registered_specialists=len(self.registered_specialists),
            specialist_coverage=self.specialist_coverage,
            files_with_annotations=len(self.annotated_files),
            annotation_coverage=self.annotation_coverage,
            consistency_score=self.consistency_score,
            mismatches=self.mismatches,
            undocumented_modules=self.undocumented_modules,
            missing_registry_entries=self.missing_registry_entries,
            completeness_grade=self.completeness_grade,
            areas_for_improvement=self.areas_for_improvement,
            timestamp=datetime.now().isoformat()
        )
        
        # Save to JSON
        output_path = Path(__file__).parent / "fixtures" / "phase12c_documentation_coverage.json"
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results.to_dict(), f, indent=2)
        
        print(f"   ✅ Results saved to: {output_path}")
        print("\n" + "="*60)
        print("📋 PHASE 12C COMPLETE: Documentation Coverage")
        print("="*60)
        print(f"\n🎯 KEY FINDINGS:")
        print(f"   Module coverage: {results.coverage_percentage:.1f}%")
        print(f"   Specialist coverage: {results.specialist_coverage:.1f}%")
        print(f"   Consistency: {results.consistency_score:.1f}%")
        print(f"   Grade: {results.completeness_grade}")
        print(f"\n   🔬 INSIGHT: Documentation is {results.completeness_grade}-grade")
        print(f"              with {len(results.areas_for_improvement)} improvement areas!")
        print("="*60 + "\n")
        
        assert output_path.exists()


if __name__ == "__main__":
    # Run Phase 12C tests
    print("\n📋 Starting Phase 12C: Documentation Coverage Analysis\n")
    pytest.main([__file__, "-v", "-s"])
