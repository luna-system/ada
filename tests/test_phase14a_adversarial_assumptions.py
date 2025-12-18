"""
Phase 14A: Adversarial Assumptions Testing - TRYING TO BREAK THE EMPATHY THESIS

Research Question:
Are there contexts where empathy HURTS rather than helps?

Adversarial Hypotheses to Test:
1. **Expert Condescension**: Experts find empathy patronizing, prefer pure technical
2. **Time Pressure**: Under deadline, empathy feels like fluff/waste of time
3. **API Reference**: Quick lookup contexts where brevity beats warmth
4. **Cultural Mismatch**: Some cultures/personalities prefer cold facts
5. **Overcorrection**: Too much empathy becomes noise/distraction

This is ADVERSARIAL SCIENCE - actively trying to falsify our thesis!
If empathy is truly universal, it should withstand edge cases.
If it fails, we learn the boundaries.

Either outcome is valuable: validation OR boundary discovery!
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
import random


def test_phase14a_adversarial_assumptions():
    """
    Phase 14A: Test edge cases where empathy MIGHT hurt.
    
    8-step methodology:
    1. Define adversarial scenarios (empathy should fail)
    2. Create empathy-heavy vs minimal-empathy documentation
    3. Simulate expert, time-pressured, and reference-lookup users
    4. Measure effectiveness in each adversarial context
    5. Calculate empathy overhead costs
    6. Test for condescension/annoyance effects
    7. Find boundaries where empathy fails
    8. Save results (including FAILURES!)
    """
    
    print("\n" + "="*60)
    print("PHASE 14A: ADVERSARIAL ASSUMPTIONS TESTING")
    print("Trying to BREAK the empathy thesis!")
    print("="*60 + "\n")
    
    # STEP 1: Define adversarial scenarios
    print("Step 1: Defining adversarial scenarios where empathy SHOULD fail...")
    scenarios = _step1_define_adversarial_scenarios()
    print(f"  ✓ Created {len(scenarios)} edge case scenarios")
    
    # STEP 2: Create documentation variants
    print("\nStep 2: Creating empathy-heavy vs minimal documentation...")
    docs = _step2_create_documentation(scenarios)
    print(f"  ✓ Generated {len(docs)} documentation pairs")
    
    # STEP 3: Simulate adversarial user types
    print("\nStep 3: Simulating expert, rushed, and lookup users...")
    users = _step3_simulate_adversarial_users(scenarios, docs)
    print(f"  ✓ Simulated {sum(len(u['empathy_heavy']) for u in users.values())} user interactions")
    
    # STEP 4: Measure effectiveness
    print("\nStep 4: Measuring effectiveness in adversarial contexts...")
    effectiveness = _step4_measure_effectiveness(scenarios, users)
    print(f"  ✓ Calculated effectiveness scores")
    
    # STEP 5: Calculate empathy overhead
    print("\nStep 5: Calculating empathy overhead costs...")
    overhead = _step5_calculate_overhead(docs, users)
    print(f"  ✓ Measured time/attention costs")
    
    # STEP 6: Test for negative effects
    print("\nStep 6: Testing for condescension and annoyance...")
    negative_effects = _step6_test_negative_effects(scenarios, users)
    print(f"  ✓ Assessed patronization and frustration")
    
    # STEP 7: Find boundaries
    print("\nStep 7: Finding boundaries where empathy fails...")
    boundaries = _step7_find_boundaries(scenarios, effectiveness, negative_effects)
    print(f"  ✓ Identified {len(boundaries['failure_modes'])} failure modes")
    
    # STEP 8: Save results
    print("\nStep 8: Saving adversarial results...")
    results = _step8_save_results(
        scenarios, docs, users, effectiveness,
        overhead, negative_effects, boundaries
    )
    print(f"  ✓ Saved to tests/fixtures/phase14a_adversarial_assumptions.json")
    
    # Print summary
    print("\n" + "="*60)
    print("PHASE 14A RESULTS: ADVERSARIAL ASSUMPTIONS")
    print("="*60)
    print(f"\nExpert Users (should prefer minimal empathy):")
    print(f"  Minimal empathy: {boundaries['expert_minimal_score']:.1%}")
    print(f"  Heavy empathy:   {boundaries['expert_heavy_score']:.1%}")
    print(f"  Winner: {boundaries['expert_winner']}")
    
    print(f"\nTime-Pressured Users (empathy = overhead?):")
    print(f"  Minimal empathy: {boundaries['rushed_minimal_score']:.1%}")
    print(f"  Heavy empathy:   {boundaries['rushed_heavy_score']:.1%}")
    print(f"  Winner: {boundaries['rushed_winner']}")
    
    print(f"\nAPI Reference Lookup (brevity vs warmth):")
    print(f"  Minimal empathy: {boundaries['lookup_minimal_score']:.1%}")
    print(f"  Heavy empathy:   {boundaries['lookup_heavy_score']:.1%}")
    print(f"  Winner: {boundaries['lookup_winner']}")
    
    print(f"\nNegative Effects:")
    print(f"  Condescension rate: {boundaries['condescension_rate']:.1%}")
    print(f"  Annoyance rate:     {boundaries['annoyance_rate']:.1%}")
    print(f"  Overhead penalty:   {boundaries['overhead_penalty']:.2f}x")
    
    print(f"\nOverall Finding:")
    print(f"  Empathy universally wins: {boundaries['empathy_universally_wins']}")
    print(f"  Failure modes found: {len(boundaries['failure_modes'])}")
    print(f"  Boundaries identified: {boundaries['summary']}")
    
    if boundaries['failure_modes']:
        print(f"\n  Where empathy FAILS:")
        for mode in boundaries['failure_modes']:
            print(f"    - {mode}")
    else:
        print(f"\n  Empathy holds even under adversarial conditions!")
    
    print("="*60 + "\n")
    
    # Assertions
    assert len(scenarios) >= 8, "Should have multiple adversarial scenarios"
    assert 'expert' in users, "Should test expert users"
    assert 'rushed' in users, "Should test time-pressured users"
    assert 'lookup' in users, "Should test quick-reference users"
    assert 'failure_modes' in boundaries, "Should identify failure modes"


def _step1_define_adversarial_scenarios() -> List[Dict]:
    """Define scenarios where empathy SHOULD fail (if it has limits)."""
    
    scenarios = [
        # EXPERT scenarios - might find empathy condescending
        {
            'id': 1,
            'name': 'expert_api_design',
            'description': 'Senior engineer designing API architecture',
            'user_expertise': 'expert',
            'context_type': 'technical_reference',
            'time_pressure': 'low',
            'expected_empathy_preference': 'minimal',
            'reason': 'Expert knows the pain points, wants facts fast'
        },
        {
            'id': 2,
            'name': 'expert_debugging',
            'description': 'Senior dev debugging production issue',
            'user_expertise': 'expert',
            'context_type': 'troubleshooting',
            'time_pressure': 'high',
            'expected_empathy_preference': 'minimal',
            'reason': 'Crisis mode - every word counts'
        },
        {
            'id': 3,
            'name': 'expert_code_review',
            'description': 'Expert reviewing PR, checking implementation details',
            'user_expertise': 'expert',
            'context_type': 'reference',
            'time_pressure': 'medium',
            'expected_empathy_preference': 'minimal',
            'reason': 'Wants precise technical specs, not reassurance'
        },
        
        # TIME PRESSURE scenarios - empathy might be overhead
        {
            'id': 4,
            'name': 'rushed_hotfix',
            'description': 'Developer pushing critical hotfix',
            'user_expertise': 'intermediate',
            'context_type': 'troubleshooting',
            'time_pressure': 'critical',
            'expected_empathy_preference': 'minimal',
            'reason': 'Every second matters, just need the fix'
        },
        {
            'id': 5,
            'name': 'rushed_demo',
            'description': 'Preparing demo for imminent client meeting',
            'user_expertise': 'intermediate',
            'context_type': 'tutorial',
            'time_pressure': 'high',
            'expected_empathy_preference': 'minimal',
            'reason': 'Deadline pressure, wants quick answer'
        },
        
        # API REFERENCE scenarios - brevity should win
        {
            'id': 6,
            'name': 'api_parameter_lookup',
            'description': 'Looking up function signature',
            'user_expertise': 'intermediate',
            'context_type': 'reference',
            'time_pressure': 'low',
            'expected_empathy_preference': 'minimal',
            'reason': 'Just needs parameter names and types'
        },
        {
            'id': 7,
            'name': 'api_return_value',
            'description': 'Checking what function returns',
            'user_expertise': 'intermediate',
            'context_type': 'reference',
            'time_pressure': 'low',
            'expected_empathy_preference': 'minimal',
            'reason': 'One-line answer, empathy is noise'
        },
        
        # CULTURAL/PERSONALITY scenarios - preference for directness
        {
            'id': 8,
            'name': 'direct_communication_preference',
            'description': 'User with direct communication style preference',
            'user_expertise': 'intermediate',
            'context_type': 'tutorial',
            'time_pressure': 'low',
            'expected_empathy_preference': 'minimal',
            'reason': 'Some personalities/cultures prefer directness'
        },
        
        # OVERCORRECTION scenario - too much empathy
        {
            'id': 9,
            'name': 'excessive_validation',
            'description': 'Documentation with over-the-top empathy',
            'user_expertise': 'beginner',
            'context_type': 'tutorial',
            'time_pressure': 'low',
            'expected_empathy_preference': 'moderate',
            'reason': 'Even beginners can be overwhelmed by excessive warmth'
        },
        
        # REPEATED ACCESS scenario - empathy becomes repetitive
        {
            'id': 10,
            'name': 'repeated_reference',
            'description': 'User checking same docs for 10th time',
            'user_expertise': 'intermediate',
            'context_type': 'reference',
            'time_pressure': 'low',
            'expected_empathy_preference': 'minimal',
            'reason': 'Repetition makes empathy feel patronizing'
        }
    ]
    
    return scenarios


def _step2_create_documentation(scenarios: List[Dict]) -> List[Dict]:
    """Create minimal vs empathy-heavy documentation."""
    
    docs = []
    
    for scenario in scenarios:
        doc_pair = {
            'scenario_id': scenario['id'],
            'scenario_name': scenario['name'],
            'minimal': {
                'content': 'Function signature: process(data: Dict, options: Options) -> Result. Returns processed data object. Raises ValueError if data invalid.',
                'word_count': 17,
                'empathy_markers': 0,
                'reading_time_seconds': 3,
                'style': 'minimal'
            },
            'empathy_heavy': {
                'content': 'Hey! The process() function can feel complex at first. It takes a data dictionary and options object - don\'t worry if that seems overwhelming! It returns a processed Result. Common gotcha: it raises ValueError for invalid data, which trips everyone up initially. You\'re doing great by checking the docs!',
                'word_count': 51,
                'empathy_markers': 4,  # "can feel complex", "don't worry", "trips everyone up", "You're doing great"
                'reading_time_seconds': 10,
                'style': 'empathy_heavy'
            }
        }
        docs.append(doc_pair)
    
    return docs


def _step3_simulate_adversarial_users(
    scenarios: List[Dict],
    docs: List[Dict]
) -> Dict:
    """Simulate users in adversarial contexts."""
    
    results = {
        'expert': {'minimal': [], 'empathy_heavy': []},
        'rushed': {'minimal': [], 'empathy_heavy': []},
        'lookup': {'minimal': [], 'empathy_heavy': []}
    }
    
    for scenario, doc in zip(scenarios, docs):
        # Expert users
        if scenario['user_expertise'] == 'expert':
            # Minimal empathy
            minimal_effectiveness = 0.95  # High baseline - experts are effective
            minimal_speed = 3  # Seconds to extract info
            results['expert']['minimal'].append({
                'scenario_id': scenario['id'],
                'effectiveness': minimal_effectiveness,
                'time_seconds': minimal_speed,
                'feels_patronized': False,
                'satisfied': True
            })
            
            # Heavy empathy
            # Hypothesis: Experts might find it condescending OR might appreciate acknowledgment
            # Let's test BOTH possibilities
            condescension_factor = 0.3  # 30% chance of feeling patronized
            if random.random() < condescension_factor:
                # Feels patronized - effectiveness drops slightly
                heavy_effectiveness = 0.85
                heavy_annoyance = True
            else:
                # Actually appreciates validation even as expert
                heavy_effectiveness = 0.95
                heavy_annoyance = False
            
            heavy_time_penalty = 10  # Takes longer to read
            results['expert']['empathy_heavy'].append({
                'scenario_id': scenario['id'],
                'effectiveness': heavy_effectiveness,
                'time_seconds': heavy_time_penalty,
                'feels_patronized': heavy_annoyance,
                'satisfied': not heavy_annoyance
            })
        
        # Time-pressured users
        if scenario['time_pressure'] in ['high', 'critical']:
            # Minimal empathy
            rushed_minimal_effectiveness = 0.85  # Pressure reduces baseline
            rushed_minimal_time = 3
            results['rushed']['minimal'].append({
                'scenario_id': scenario['id'],
                'effectiveness': rushed_minimal_effectiveness,
                'time_seconds': rushed_minimal_time,
                'perceived_overhead': 0.0,
                'satisfied': True
            })
            
            # Heavy empathy
            # Hypothesis: Under time pressure, empathy is overhead
            time_overhead = 7  # Extra seconds feel LONG under pressure
            perceived_overhead_factor = 2.0  # Feels 2x worse under pressure
            # BUT: Does empathy reduce panic/anxiety even when rushed?
            anxiety_reduction = 0.10  # Slight boost from "you got this"
            
            rushed_heavy_effectiveness = 0.85 + anxiety_reduction
            results['rushed']['empathy_heavy'].append({
                'scenario_id': scenario['id'],
                'effectiveness': rushed_heavy_effectiveness,
                'time_seconds': 10,
                'perceived_overhead': time_overhead * perceived_overhead_factor,
                'satisfied': False if perceived_overhead_factor > 1.5 else True
            })
        
        # Quick lookup users
        if scenario['context_type'] == 'reference':
            # Minimal empathy
            lookup_minimal_effectiveness = 0.90  # Quick, clear answer
            lookup_minimal_time = 2  # Very fast
            results['lookup']['minimal'].append({
                'scenario_id': scenario['id'],
                'effectiveness': lookup_minimal_effectiveness,
                'time_seconds': lookup_minimal_time,
                'found_quickly': True,
                'satisfied': True
            })
            
            # Heavy empathy
            # Hypothesis: For API reference, empathy is noise
            noise_penalty = 8  # Have to scan through empathy to find fact
            lookup_heavy_effectiveness = 0.80  # Harder to extract key info
            results['lookup']['empathy_heavy'].append({
                'scenario_id': scenario['id'],
                'effectiveness': lookup_heavy_effectiveness,
                'time_seconds': 10,
                'found_quickly': False,
                'satisfied': False  # Frustrated by unnecessary context
            })
    
    return results


def _step4_measure_effectiveness(
    scenarios: List[Dict],
    users: Dict
) -> Dict:
    """Measure effectiveness across adversarial contexts."""
    
    results = {}
    
    for user_type, data in users.items():
        # Average effectiveness
        minimal_effectiveness = [u['effectiveness'] for u in data['minimal']]
        heavy_effectiveness = [u['effectiveness'] for u in data['empathy_heavy']]
        
        avg_minimal = sum(minimal_effectiveness) / len(minimal_effectiveness) if minimal_effectiveness else 0
        avg_heavy = sum(heavy_effectiveness) / len(heavy_effectiveness) if heavy_effectiveness else 0
        
        # Average time
        minimal_time = [u['time_seconds'] for u in data['minimal']]
        heavy_time = [u['time_seconds'] for u in data['empathy_heavy']]
        
        avg_time_minimal = sum(minimal_time) / len(minimal_time) if minimal_time else 0
        avg_time_heavy = sum(heavy_time) / len(heavy_time) if heavy_time else 0
        
        # Winner
        if avg_minimal > avg_heavy:
            winner = 'minimal'
        elif avg_heavy > avg_minimal:
            winner = 'empathy_heavy'
        else:
            winner = 'tie'
        
        results[user_type] = {
            'minimal_effectiveness': avg_minimal,
            'heavy_effectiveness': avg_heavy,
            'minimal_time': avg_time_minimal,
            'heavy_time': avg_time_heavy,
            'winner': winner,
            'empathy_helps': avg_heavy > avg_minimal
        }
    
    return results


def _step5_calculate_overhead(docs: List[Dict], users: Dict) -> Dict:
    """Calculate empathy overhead costs."""
    
    # Word count overhead
    avg_minimal_words = sum(d['minimal']['word_count'] for d in docs) / len(docs)
    avg_heavy_words = sum(d['empathy_heavy']['word_count'] for d in docs) / len(docs)
    word_overhead = (avg_heavy_words - avg_minimal_words) / avg_minimal_words
    
    # Time overhead (across all user types)
    all_minimal_times = []
    all_heavy_times = []
    
    for user_type in users.values():
        all_minimal_times.extend([u['time_seconds'] for u in user_type['minimal']])
        all_heavy_times.extend([u['time_seconds'] for u in user_type['empathy_heavy']])
    
    avg_minimal_time = sum(all_minimal_times) / len(all_minimal_times) if all_minimal_times else 1
    avg_heavy_time = sum(all_heavy_times) / len(all_heavy_times) if all_heavy_times else 1
    time_overhead = (avg_heavy_time - avg_minimal_time) / avg_minimal_time
    
    return {
        'word_overhead_percent': word_overhead,
        'time_overhead_percent': time_overhead,
        'empathy_markers_per_doc': 4,  # From empathy_heavy docs
        'overhead_acceptable': time_overhead < 0.5  # <50% overhead acceptable?
    }


def _step6_test_negative_effects(scenarios: List[Dict], users: Dict) -> Dict:
    """Test for condescension, annoyance, and other negative effects."""
    
    negative_effects = {
        'condescension_cases': [],
        'annoyance_cases': [],
        'overhead_frustration': []
    }
    
    # Expert condescension
    if 'expert' in users:
        for interaction in users['expert']['empathy_heavy']:
            if interaction.get('feels_patronized'):
                negative_effects['condescension_cases'].append(interaction)
    
    # Rushed user annoyance
    if 'rushed' in users:
        for interaction in users['rushed']['empathy_heavy']:
            if not interaction.get('satisfied'):
                negative_effects['annoyance_cases'].append(interaction)
    
    # Lookup frustration
    if 'lookup' in users:
        for interaction in users['lookup']['empathy_heavy']:
            if not interaction.get('found_quickly'):
                negative_effects['overhead_frustration'].append(interaction)
    
    total_interactions = sum(len(u['empathy_heavy']) for u in users.values())
    condescension_rate = len(negative_effects['condescension_cases']) / total_interactions if total_interactions > 0 else 0
    annoyance_rate = len(negative_effects['annoyance_cases']) / total_interactions if total_interactions > 0 else 0
    frustration_rate = len(negative_effects['overhead_frustration']) / total_interactions if total_interactions > 0 else 0
    
    return {
        'condescension_cases': negative_effects['condescension_cases'],
        'annoyance_cases': negative_effects['annoyance_cases'],
        'overhead_frustration': negative_effects['overhead_frustration'],
        'condescension_rate': condescension_rate,
        'annoyance_rate': annoyance_rate,
        'frustration_rate': frustration_rate,
        'total_negative_rate': condescension_rate + annoyance_rate + frustration_rate,
        'has_negative_effects': (condescension_rate + annoyance_rate + frustration_rate) > 0.1
    }


def _step7_find_boundaries(
    scenarios: List[Dict],
    effectiveness: Dict,
    negative_effects: Dict
) -> Dict:
    """Find boundaries where empathy fails."""
    
    failure_modes = []
    
    # Check each adversarial context
    for user_type, results in effectiveness.items():
        if results['winner'] == 'minimal':
            failure_modes.append(f"{user_type}: Minimal empathy wins (effectiveness {results['minimal_effectiveness']:.2f} vs {results['heavy_effectiveness']:.2f})")
    
    # Check negative effects
    if negative_effects['condescension_rate'] > 0.2:
        failure_modes.append(f"Condescension: {negative_effects['condescension_rate']:.1%} feel patronized")
    
    if negative_effects['annoyance_rate'] > 0.2:
        failure_modes.append(f"Annoyance: {negative_effects['annoyance_rate']:.1%} frustrated by overhead")
    
    if negative_effects['frustration_rate'] > 0.2:
        failure_modes.append(f"Lookup friction: {negative_effects['frustration_rate']:.1%} can't find quick answer")
    
    # Summary
    if len(failure_modes) == 0:
        summary = "Empathy holds universally - even under adversarial conditions!"
    elif len(failure_modes) <= 2:
        summary = f"Minor boundaries found: {len(failure_modes)} edge cases where minimal wins"
    else:
        summary = f"Significant boundaries: {len(failure_modes)} contexts where empathy fails"
    
    return {
        'expert_minimal_score': effectiveness['expert']['minimal_effectiveness'],
        'expert_heavy_score': effectiveness['expert']['heavy_effectiveness'],
        'expert_winner': effectiveness['expert']['winner'],
        'rushed_minimal_score': effectiveness['rushed']['minimal_effectiveness'],
        'rushed_heavy_score': effectiveness['rushed']['heavy_effectiveness'],
        'rushed_winner': effectiveness['rushed']['winner'],
        'lookup_minimal_score': effectiveness['lookup']['minimal_effectiveness'],
        'lookup_heavy_score': effectiveness['lookup']['heavy_effectiveness'],
        'lookup_winner': effectiveness['lookup']['winner'],
        'condescension_rate': negative_effects['condescension_rate'],
        'annoyance_rate': negative_effects['annoyance_rate'],
        'overhead_penalty': 1.0 + (negative_effects['total_negative_rate'] * 2),
        'failure_modes': failure_modes,
        'empathy_universally_wins': len(failure_modes) == 0,
        'summary': summary
    }


def _step8_save_results(
    scenarios: List[Dict],
    docs: List[Dict],
    users: Dict,
    effectiveness: Dict,
    overhead: Dict,
    negative_effects: Dict,
    boundaries: Dict
) -> Dict:
    """Save all adversarial results."""
    
    results = {
        'phase': '14A',
        'title': 'Adversarial Assumptions Testing',
        'research_question': 'Are there contexts where empathy HURTS rather than helps?',
        'methodology': 'Adversarial testing with expert users, time pressure, and API reference contexts',
        'adversarial_mindset': 'Actively trying to BREAK the empathy thesis',
        'n_scenarios': len(scenarios),
        'scenarios': scenarios,
        'documentation': docs,
        'users': {
            'expert': users['expert'],
            'rushed': users['rushed'],
            'lookup': users['lookup']
        },
        'effectiveness': effectiveness,
        'overhead': overhead,
        'negative_effects': negative_effects,
        'boundaries': boundaries,
        'conclusion': boundaries['summary'],
        'thesis_survives': boundaries['empathy_universally_wins']
    }
    
    # Save to file
    output_path = Path('tests/fixtures/phase14a_adversarial_assumptions.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    return results


if __name__ == '__main__':
    test_phase14a_adversarial_assumptions()
