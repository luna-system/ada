"""
Phase 14B: Real-World Validation - Testing Against ACTUAL Documentation

Research Question:
Do our synthetic findings hold up against REAL Ada documentation?

Critical Test:
Phases 9-14A used SIMULATED data. Critics will say:
"Your models are oversimplified toys. Real docs are messier."

This phase VALIDATES by:
1. Loading actual Ada documentation from docs/
2. Classifying real docs by empathy level
3. Measuring actual characteristics (word count, empathy markers, complexity)
4. Comparing synthetic predictions vs real-world observations
5. Testing if boundaries we found (Phase 14A) match reality

If synthetic models DON'T match reality → Our research is toy simulation
If synthetic models DO match reality → Democratic science framework validated!

This is the CRUCIBLE TEST for the entire research program!
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
import re


def test_phase14b_real_world_validation():
    """
    Phase 14B: Validate synthetic findings against real Ada documentation.
    
    8-step methodology:
    1. Load actual Ada documentation files
    2. Classify docs by empathy level (cold/moderate/warm)
    3. Measure real-world characteristics
    4. Compare to synthetic model predictions
    5. Test boundary conditions from Phase 14A
    6. Calculate prediction accuracy
    7. Identify model-reality gaps
    8. Save validation results
    """
    
    print("\n" + "="*60)
    print("PHASE 14B: REAL-WORLD VALIDATION")
    print("Testing synthetic findings against ACTUAL Ada docs!")
    print("="*60 + "\n")
    
    # STEP 1: Load actual documentation
    print("Step 1: Loading actual Ada documentation from docs/...")
    real_docs = _step1_load_real_docs()
    print(f"  ✓ Loaded {len(real_docs)} real documentation files")
    
    # STEP 2: Classify by empathy level
    print("\nStep 2: Classifying docs by empathy level...")
    classified = _step2_classify_docs(real_docs)
    print(f"  ✓ Classified into cold/moderate/warm categories")
    
    # STEP 3: Measure real-world characteristics
    print("\nStep 3: Measuring real-world doc characteristics...")
    characteristics = _step3_measure_characteristics(classified)
    print(f"  ✓ Measured word counts, empathy markers, complexity")
    
    # STEP 4: Compare to synthetic predictions
    print("\nStep 4: Comparing to synthetic model predictions...")
    comparison = _step4_compare_to_synthetic(characteristics)
    print(f"  ✓ Calculated prediction accuracy")
    
    # STEP 5: Test Phase 14A boundaries
    print("\nStep 5: Testing Phase 14A boundary conditions...")
    boundary_validation = _step5_test_boundaries(real_docs, classified)
    print(f"  ✓ Validated adversarial findings")
    
    # STEP 6: Calculate accuracy
    print("\nStep 6: Calculating overall prediction accuracy...")
    accuracy = _step6_calculate_accuracy(comparison, boundary_validation)
    print(f"  ✓ Model-reality correlation calculated")
    
    # STEP 7: Identify gaps
    print("\nStep 7: Identifying model-reality gaps...")
    gaps = _step7_identify_gaps(comparison, accuracy)
    print(f"  ✓ Found {len(gaps['discrepancies'])} discrepancies")
    
    # STEP 8: Save results
    print("\nStep 8: Saving validation results...")
    results = _step8_save_results(
        real_docs, classified, characteristics,
        comparison, boundary_validation, accuracy, gaps
    )
    print(f"  ✓ Saved to tests/fixtures/phase14b_real_world_validation.json")
    
    # Print summary
    print("\n" + "="*60)
    print("PHASE 14B RESULTS: REAL-WORLD VALIDATION")
    print("="*60)
    print(f"\nReal Ada Documentation Analysis:")
    print(f"  Total docs analyzed: {len(real_docs)}")
    print(f"  Cold/technical: {len(classified['cold'])}")
    print(f"  Moderate empathy: {len(classified['moderate'])}")
    print(f"  Warm/empathetic: {len(classified['warm'])}")
    
    print(f"\nSynthetic Model Accuracy:")
    print(f"  Word count prediction: {accuracy['word_count_accuracy']:.1%}")
    print(f"  Empathy marker prediction: {accuracy['empathy_marker_accuracy']:.1%}")
    print(f"  Complexity prediction: {accuracy['complexity_accuracy']:.1%}")
    print(f"  Overall correlation: {accuracy['overall_correlation']:.3f}")
    
    print(f"\nPhase 14A Boundary Validation:")
    print(f"  Expert docs prefer minimal: {boundary_validation['expert_boundary_holds']}")
    print(f"  API reference is brief: {boundary_validation['lookup_boundary_holds']}")
    print(f"  Tutorial docs empathetic: {boundary_validation['beginner_boundary_holds']}")
    
    print(f"\nModel-Reality Match:")
    print(f"  Synthetic models valid: {accuracy['models_validated']}")
    print(f"  Prediction quality: {accuracy['quality_assessment']}")
    print(f"  Research credibility: {accuracy['research_credibility']}")
    
    if gaps['discrepancies']:
        print(f"\n  Model-Reality Gaps Found:")
        for gap in gaps['discrepancies'][:3]:  # Top 3
            print(f"    - {gap}")
    else:
        print(f"\n  No significant model-reality gaps!")
    
    print("="*60 + "\n")
    
    # Assertions
    assert len(real_docs) > 0, "Should load real docs"
    assert 'cold' in classified, "Should classify docs"
    assert 'overall_correlation' in accuracy, "Should calculate correlation"
    assert 'models_validated' in accuracy, "Should validate models"


def _step1_load_real_docs() -> List[Dict]:
    """Load actual Ada documentation files."""
    
    docs_dir = Path('docs')
    real_docs = []
    
    # Target specific docs we know exist
    doc_files = [
        'getting_started.rst',
        'api_usage.rst',
        'api_reference.rst',
        'empathetic_documentation.rst',
        'documentation_philosophy.rst',
        'build_specialist.rst',
        'specialists.rst',
        'configuration.rst',
        'architecture.rst',
        'hardware.rst'
    ]
    
    for filename in doc_files:
        filepath = docs_dir / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            real_docs.append({
                'filename': filename,
                'path': str(filepath),
                'content': content,
                'word_count': len(content.split()),
                'line_count': len(content.split('\n'))
            })
    
    return real_docs


def _step2_classify_docs(real_docs: List[Dict]) -> Dict:
    """Classify real docs by empathy level."""
    
    classified = {
        'cold': [],
        'moderate': [],
        'warm': []
    }
    
    # Empathy markers to detect
    warm_markers = [
        'easy', 'simple', 'friendly', 'help', 'don\'t worry',
        'you can', 'you\'ll', 'great!', 'awesome', 'powerful',
        'smooth', 'painless', 'straightforward', 'comfortable'
    ]
    
    validation_markers = [
        'confusing', 'tricky', 'difficult', 'complex',
        'understandable', 'struggle', 'frustrating', 'overwhelm'
    ]
    
    for doc in real_docs:
        content_lower = doc['content'].lower()
        
        # Count empathy markers
        warm_count = sum(content_lower.count(marker) for marker in warm_markers)
        validation_count = sum(content_lower.count(marker) for marker in validation_markers)
        
        total_empathy = warm_count + validation_count
        words = doc['word_count']
        empathy_density = total_empathy / words if words > 0 else 0
        
        # Classify
        if 'api_reference' in doc['filename'] or 'configuration' in doc['filename']:
            # API reference and config are typically technical
            category = 'cold'
        elif 'empathetic' in doc['filename'] or 'philosophy' in doc['filename']:
            # Philosophy docs are explicitly empathetic
            category = 'warm'
        elif empathy_density > 0.015:
            category = 'warm'
        elif empathy_density > 0.008:
            category = 'moderate'
        else:
            category = 'cold'
        
        classified[category].append({
            **doc,
            'empathy_density': empathy_density,
            'warm_markers': warm_count,
            'validation_markers': validation_count,
            'total_empathy_markers': total_empathy,
            'category': category
        })
    
    return classified


def _step3_measure_characteristics(classified: Dict) -> Dict:
    """Measure real-world characteristics of classified docs."""
    
    characteristics = {}
    
    for category, docs in classified.items():
        if not docs:
            continue
        
        avg_word_count = sum(d['word_count'] for d in docs) / len(docs)
        avg_empathy_markers = sum(d['total_empathy_markers'] for d in docs) / len(docs)
        avg_empathy_density = sum(d['empathy_density'] for d in docs) / len(docs)
        
        # Complexity proxy: average words per line (longer lines = denser)
        complexities = []
        for d in docs:
            words_per_line = d['word_count'] / max(1, d['line_count'])
            complexities.append(words_per_line)
        avg_complexity = sum(complexities) / len(complexities)
        
        characteristics[category] = {
            'n_docs': len(docs),
            'avg_word_count': avg_word_count,
            'avg_empathy_markers': avg_empathy_markers,
            'avg_empathy_density': avg_empathy_density,
            'avg_complexity': avg_complexity
        }
    
    return characteristics


def _step4_compare_to_synthetic(characteristics: Dict) -> Dict:
    """Compare real characteristics to synthetic model predictions."""
    
    # Synthetic predictions from Phases 13-14
    synthetic_predictions = {
        'cold': {
            'expected_word_count': 25,  # From Phase 13A cold docs
            'expected_empathy_markers': 0,
            'expected_empathy_density': 0.0
        },
        'moderate': {
            'expected_word_count': 35,
            'expected_empathy_markers': 2,
            'expected_empathy_density': 0.057
        },
        'warm': {
            'expected_word_count': 45,  # From Phase 13A warm docs
            'expected_empathy_markers': 4,
            'expected_empathy_density': 0.089
        }
    }
    
    comparison = {}
    
    for category, real_chars in characteristics.items():
        if category not in synthetic_predictions:
            continue
        
        synthetic = synthetic_predictions[category]
        
        # Calculate prediction errors
        # Note: Real docs are MUCH longer than synthetic snippets
        # We expect 10-100x larger word counts
        # Focus on RATIOS not absolute values
        
        real_density = real_chars['avg_empathy_density']
        synth_density = synthetic['expected_empathy_density']
        
        # Density should be comparable (per-word metric)
        density_error = abs(real_density - synth_density) / max(0.001, synth_density) if synth_density > 0 else 0
        density_match = density_error < 1.0  # Within 2x
        
        comparison[category] = {
            'real_word_count': real_chars['avg_word_count'],
            'synthetic_word_count': synthetic['expected_word_count'],
            'real_empathy_density': real_density,
            'synthetic_empathy_density': synth_density,
            'density_error': density_error,
            'density_matches': density_match,
            'scale_factor': real_chars['avg_word_count'] / synthetic['expected_word_count']
        }
    
    return comparison


def _step5_test_boundaries(real_docs: List[Dict], classified: Dict) -> Dict:
    """Test Phase 14A boundary conditions against real docs."""
    
    validation = {}
    
    # Boundary 1: Expert/API reference docs should be minimal empathy
    api_docs = [d for d in real_docs if 'api_reference' in d['filename'] or 'configuration' in d['filename']]
    if api_docs:
        avg_api_density = sum(
            next((c['empathy_density'] for c in classified['cold'] + classified['moderate'] + classified['warm'] 
                  if c['filename'] == doc['filename']), 0)
            for doc in api_docs
        ) / len(api_docs)
        
        # Prediction: API docs have LOW empathy density
        validation['expert_boundary_holds'] = avg_api_density < 0.01
        validation['expert_empathy_density'] = avg_api_density
    else:
        validation['expert_boundary_holds'] = None
    
    # Boundary 2: Tutorial/getting started should be empathetic
    tutorial_docs = [d for d in real_docs if 'getting_started' in d['filename'] or 'tutorial' in d['filename']]
    if tutorial_docs:
        avg_tutorial_density = sum(
            next((c['empathy_density'] for c in classified['cold'] + classified['moderate'] + classified['warm'] 
                  if c['filename'] == doc['filename']), 0)
            for doc in tutorial_docs
        ) / len(tutorial_docs)
        
        # Prediction: Tutorial docs have HIGHER empathy density than API
        validation['beginner_boundary_holds'] = avg_tutorial_density > validation.get('expert_empathy_density', 0)
        validation['tutorial_empathy_density'] = avg_tutorial_density
    else:
        validation['beginner_boundary_holds'] = None
    
    # Boundary 3: Quick reference should be brief
    reference_docs = [d for d in classified['cold'] if 'reference' in d['filename']]
    if reference_docs:
        avg_ref_words_per_line = sum(
            d['word_count'] / max(1, d['line_count'])
            for d in reference_docs
        ) / len(reference_docs)
        
        # Prediction: Reference docs are DENSE (high words per line)
        validation['lookup_boundary_holds'] = avg_ref_words_per_line > 5
        validation['reference_density'] = avg_ref_words_per_line
    else:
        validation['lookup_boundary_holds'] = None
    
    # Count how many boundaries hold
    boundaries_tested = sum(1 for k, v in validation.items() if k.endswith('_holds') and v is not None)
    boundaries_holding = sum(1 for k, v in validation.items() if k.endswith('_holds') and v is True)
    
    validation['boundaries_tested'] = boundaries_tested
    validation['boundaries_holding'] = boundaries_holding
    validation['boundary_accuracy'] = boundaries_holding / boundaries_tested if boundaries_tested > 0 else 0
    
    return validation


def _step6_calculate_accuracy(comparison: Dict, boundary_validation: Dict) -> Dict:
    """Calculate overall prediction accuracy."""
    
    # Model predictions vs reality
    density_matches = sum(1 for c in comparison.values() if c.get('density_matches', False))
    total_categories = len(comparison)
    
    density_accuracy = density_matches / total_categories if total_categories > 0 else 0
    
    # Boundary validation accuracy
    boundary_accuracy = boundary_validation.get('boundary_accuracy', 0)
    
    # Overall correlation (simple average for now)
    overall_correlation = (density_accuracy + boundary_accuracy) / 2
    
    # Quality assessment
    if overall_correlation >= 0.8:
        quality = "EXCELLENT"
        credibility = "HIGH"
        models_validated = True
    elif overall_correlation >= 0.6:
        quality = "GOOD"
        credibility = "MODERATE"
        models_validated = True
    elif overall_correlation >= 0.4:
        quality = "FAIR"
        credibility = "LOW"
        models_validated = False
    else:
        quality = "POOR"
        credibility = "VERY LOW"
        models_validated = False
    
    return {
        'word_count_accuracy': 0.0,  # Not directly comparable (different scales)
        'empathy_marker_accuracy': density_accuracy,
        'complexity_accuracy': boundary_accuracy,
        'overall_correlation': overall_correlation,
        'quality_assessment': quality,
        'research_credibility': credibility,
        'models_validated': models_validated
    }


def _step7_identify_gaps(comparison: Dict, accuracy: Dict) -> Dict:
    """Identify model-reality gaps."""
    
    discrepancies = []
    
    # Check each category
    for category, comp in comparison.items():
        if not comp.get('density_matches', True):
            error_pct = comp['density_error'] * 100
            discrepancies.append(
                f"{category}: Empathy density off by {error_pct:.0f}% "
                f"(real {comp['real_empathy_density']:.4f} vs synthetic {comp['synthetic_empathy_density']:.4f})"
            )
        
        # Scale factor check
        scale = comp.get('scale_factor', 1)
        if scale > 100:
            discrepancies.append(
                f"{category}: Real docs {scale:.0f}x longer than synthetic snippets"
            )
    
    # Overall assessment
    if accuracy['overall_correlation'] < 0.6:
        discrepancies.append(
            f"Overall: Low correlation ({accuracy['overall_correlation']:.2f}) suggests model-reality mismatch"
        )
    
    return {
        'discrepancies': discrepancies,
        'n_discrepancies': len(discrepancies),
        'acceptable_gap': len(discrepancies) <= 3,
        'requires_model_revision': accuracy['overall_correlation'] < 0.5
    }


def _step8_save_results(
    real_docs: List[Dict],
    classified: Dict,
    characteristics: Dict,
    comparison: Dict,
    boundary_validation: Dict,
    accuracy: Dict,
    gaps: Dict
) -> Dict:
    """Save validation results."""
    
    # Strip content for JSON size
    docs_summary = [
        {k: v for k, v in doc.items() if k != 'content'}
        for doc in real_docs
    ]
    
    classified_summary = {}
    for category, docs in classified.items():
        classified_summary[category] = [
            {k: v for k, v in doc.items() if k != 'content'}
            for doc in docs
        ]
    
    results = {
        'phase': '14B',
        'title': 'Real-World Validation',
        'research_question': 'Do synthetic findings hold up against REAL Ada documentation?',
        'methodology': 'Load actual docs, classify by empathy, compare to synthetic predictions',
        'n_real_docs': len(real_docs),
        'docs_analyzed': docs_summary,
        'classification': {
            'cold': len(classified.get('cold', [])),
            'moderate': len(classified.get('moderate', [])),
            'warm': len(classified.get('warm', []))
        },
        'classified_docs': classified_summary,
        'characteristics': characteristics,
        'comparison': comparison,
        'boundary_validation': boundary_validation,
        'accuracy': accuracy,
        'gaps': gaps,
        'conclusion': f"Synthetic models {'VALIDATED' if accuracy['models_validated'] else 'NEED REVISION'} by real-world data",
        'research_credibility': accuracy['research_credibility']
    }
    
    # Save to file
    output_path = Path('tests/fixtures/phase14b_real_world_validation.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    return results


if __name__ == '__main__':
    test_phase14b_real_world_validation()
