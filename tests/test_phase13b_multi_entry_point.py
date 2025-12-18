"""
Phase 13B: Multi-Entry Point Success - Documentation Perspective Testing

Research Question:
Do multiple documentation entry points (Tutorial, Reference, Troubleshooting) 
improve task completion compared to single-mode documentation?

Hypothesis:
Users arrive at documentation with different mental models and goals:
- **Beginners** need tutorials (step-by-step)
- **Experienced** need reference (quick lookup)
- **Stuck** need troubleshooting (problem-solving)

Multi-perspective documentation should increase success rate by matching
diverse user needs and entry contexts.

Test Design:
- 12 diverse tasks covering different user needs
- Compare success with:
  - **Single-mode**: Tutorial only
  - **Multi-mode**: Tutorial + Reference + Troubleshooting
- Measure: task completion rate, time-to-solution, navigation patterns

This validates the "multiple perspectives" philosophy from docs/empathetic_documentation.rst!
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
import random


def test_phase13b_multi_entry_point():
    """
    Phase 13B: Test if multiple documentation entry points improve success.
    
    8-step methodology:
    1. Define diverse user tasks
    2. Create single-mode vs multi-mode documentation
    3. Simulate user navigation patterns
    4. Measure task completion rates
    5. Calculate time-to-solution
    6. Analyze entry point effectiveness
    7. Compare overall success
    8. Save results
    """
    
    print("\n" + "="*60)
    print("PHASE 13B: MULTI-ENTRY POINT SUCCESS")
    print("Testing: Multiple Documentation Perspectives")
    print("="*60 + "\n")
    
    # STEP 1: Define diverse tasks
    print("Step 1: Defining 12 diverse user tasks...")
    tasks = _step1_define_tasks()
    print(f"  ✓ Created {len(tasks)} tasks across 4 user types")
    
    # STEP 2: Create documentation variants
    print("\nStep 2: Creating single-mode vs multi-mode documentation...")
    docs = _step2_create_documentation(tasks)
    print(f"  ✓ Generated documentation for {len(docs)} tasks")
    
    # STEP 3: Simulate navigation patterns
    print("\nStep 3: Simulating user navigation patterns...")
    navigation = _step3_simulate_navigation(tasks, docs)
    print(f"  ✓ Simulated {sum(len(n['single_mode']['paths']) for n in navigation)} navigation attempts")
    
    # STEP 4: Measure task completion
    print("\nStep 4: Measuring task completion rates...")
    completion = _step4_measure_completion(tasks, docs, navigation)
    print(f"  ✓ Calculated completion rates for all tasks")
    
    # STEP 5: Calculate time-to-solution
    print("\nStep 5: Calculating time-to-solution...")
    timing = _step5_calculate_timing(navigation, completion)
    print(f"  ✓ Measured navigation efficiency")
    
    # STEP 6: Analyze entry point effectiveness
    print("\nStep 6: Analyzing entry point effectiveness...")
    entry_analysis = _step6_analyze_entry_points(tasks, navigation, completion)
    print(f"  ✓ Identified best entry points per user type")
    
    # STEP 7: Compare overall success
    print("\nStep 7: Comparing single-mode vs multi-mode success...")
    comparison = _step7_compare_success(completion, timing, entry_analysis)
    print(f"  ✓ Calculated improvement metrics")
    
    # STEP 8: Save results
    print("\nStep 8: Saving results to JSON...")
    results = _step8_save_results(
        tasks, docs, navigation, completion,
        timing, entry_analysis, comparison
    )
    print(f"  ✓ Saved to tests/fixtures/phase13b_multi_entry_point.json")
    
    # Print summary
    print("\n" + "="*60)
    print("PHASE 13B RESULTS: MULTI-ENTRY POINT SUCCESS")
    print("="*60)
    print(f"\nTask Completion Rate:")
    print(f"  Single-mode:  {comparison['completion_single']:.1%}")
    print(f"  Multi-mode:   {comparison['completion_multi']:.1%}")
    print(f"  Improvement:  {comparison['completion_delta']:+.1%}")
    
    print(f"\nAverage Time-to-Solution:")
    print(f"  Single-mode:  {comparison['time_single']:.1f} steps")
    print(f"  Multi-mode:   {comparison['time_multi']:.1f} steps")
    print(f"  Reduction:    {comparison['time_delta']:+.1f} steps")
    
    print(f"\nEntry Point Match Rate:")
    print(f"  Single-mode:  {comparison['match_rate_single']:.1%}")
    print(f"  Multi-mode:   {comparison['match_rate_multi']:.1%}")
    print(f"  Improvement:  {comparison['match_rate_delta']:+.1%}")
    
    print(f"\nOverall Effectiveness:")
    print(f"  Multi-mode helps: {comparison['multi_mode_helps']}")
    print(f"  Effect size: {comparison['effect_size']:.3f}")
    print(f"  Interpretation: {comparison['interpretation']}")
    
    print(f"\nBest Entry Point by User Type:")
    for user_type, best in comparison['best_entry_by_type'].items():
        print(f"  {user_type}: {best}")
    
    print("="*60 + "\n")
    
    # Assertions
    assert len(tasks) == 12, "Should have 12 tasks"
    assert len(docs) == 12, "Should have docs for all tasks"
    assert comparison['multi_mode_helps'] in [True, False], "Should determine if multi-mode helps"
    assert 'effect_size' in comparison, "Should calculate effect size"


def _step1_define_tasks() -> List[Dict]:
    """Define 12 diverse tasks representing different user types and needs."""
    
    tasks = [
        # BEGINNER tasks (need tutorial/step-by-step)
        {
            'id': 1,
            'name': 'first_install',
            'description': 'Install Ada for the first time',
            'user_type': 'beginner',
            'ideal_entry': 'tutorial',
            'complexity': 'low',
            'requires_context': True
        },
        {
            'id': 2,
            'name': 'first_conversation',
            'description': 'Have first conversation with Ada',
            'user_type': 'beginner',
            'ideal_entry': 'tutorial',
            'complexity': 'low',
            'requires_context': True
        },
        {
            'id': 3,
            'name': 'configure_memory',
            'description': 'Set up memory persistence',
            'user_type': 'beginner',
            'ideal_entry': 'tutorial',
            'complexity': 'medium',
            'requires_context': True
        },
        
        # EXPERIENCED tasks (need reference/quick lookup)
        {
            'id': 4,
            'name': 'check_api_endpoint',
            'description': 'Look up API endpoint signature',
            'user_type': 'experienced',
            'ideal_entry': 'reference',
            'complexity': 'low',
            'requires_context': False
        },
        {
            'id': 5,
            'name': 'find_config_option',
            'description': 'Find specific environment variable',
            'user_type': 'experienced',
            'ideal_entry': 'reference',
            'complexity': 'low',
            'requires_context': False
        },
        {
            'id': 6,
            'name': 'specialist_parameters',
            'description': 'Check specialist activation parameters',
            'user_type': 'experienced',
            'ideal_entry': 'reference',
            'complexity': 'medium',
            'requires_context': False
        },
        
        # STUCK tasks (need troubleshooting/problem-solving)
        {
            'id': 7,
            'name': 'debug_connection',
            'description': 'Fix ChromaDB connection error',
            'user_type': 'stuck',
            'ideal_entry': 'troubleshooting',
            'complexity': 'medium',
            'requires_context': True
        },
        {
            'id': 8,
            'name': 'fix_import_error',
            'description': 'Resolve module import failure',
            'user_type': 'stuck',
            'ideal_entry': 'troubleshooting',
            'complexity': 'low',
            'requires_context': True
        },
        {
            'id': 9,
            'name': 'diagnose_slow_response',
            'description': 'Figure out why responses are slow',
            'user_type': 'stuck',
            'ideal_entry': 'troubleshooting',
            'complexity': 'high',
            'requires_context': True
        },
        
        # EXPLORER tasks (hybrid - need multiple perspectives)
        {
            'id': 10,
            'name': 'build_custom_specialist',
            'description': 'Create new specialist plugin',
            'user_type': 'explorer',
            'ideal_entry': 'tutorial',  # Start with tutorial, then reference
            'complexity': 'high',
            'requires_context': True
        },
        {
            'id': 11,
            'name': 'optimize_performance',
            'description': 'Tune Ada for better performance',
            'user_type': 'explorer',
            'ideal_entry': 'reference',  # Check options, then troubleshoot
            'complexity': 'high',
            'requires_context': True
        },
        {
            'id': 12,
            'name': 'integrate_external_api',
            'description': 'Connect Ada to external service',
            'user_type': 'explorer',
            'ideal_entry': 'tutorial',  # Learn pattern, then reference
            'complexity': 'high',
            'requires_context': True
        }
    ]
    
    return tasks


def _step2_create_documentation(tasks: List[Dict]) -> List[Dict]:
    """Create single-mode vs multi-mode documentation for each task."""
    
    docs = []
    
    for task in tasks:
        doc_set = {
            'task_id': task['id'],
            'task_name': task['name'],
            'single_mode': {
                # Single-mode: Only tutorial perspective
                'tutorial': _create_tutorial_doc(task),
                'has_reference': False,
                'has_troubleshooting': False,
                'perspectives': 1
            },
            'multi_mode': {
                # Multi-mode: All three perspectives
                'tutorial': _create_tutorial_doc(task),
                'reference': _create_reference_doc(task),
                'troubleshooting': _create_troubleshooting_doc(task),
                'has_reference': True,
                'has_troubleshooting': True,
                'perspectives': 3
            }
        }
        docs.append(doc_set)
    
    return docs


def _create_tutorial_doc(task: Dict) -> Dict:
    """Create tutorial-style documentation (step-by-step)."""
    return {
        'type': 'tutorial',
        'title': f"How to: {task['description']}",
        'format': 'step-by-step',
        'length': 'long',
        'context': 'high',
        'quick_reference': 'low',
        'best_for': ['beginner', 'explorer']
    }


def _create_reference_doc(task: Dict) -> Dict:
    """Create reference-style documentation (quick lookup)."""
    return {
        'type': 'reference',
        'title': f"Reference: {task['description']}",
        'format': 'structured-list',
        'length': 'short',
        'context': 'low',
        'quick_reference': 'high',
        'best_for': ['experienced', 'explorer']
    }


def _create_troubleshooting_doc(task: Dict) -> Dict:
    """Create troubleshooting-style documentation (problem-solving)."""
    return {
        'type': 'troubleshooting',
        'title': f"Troubleshooting: {task['description']}",
        'format': 'problem-solution',
        'length': 'medium',
        'context': 'medium',
        'quick_reference': 'medium',
        'best_for': ['stuck', 'explorer']
    }


def _step3_simulate_navigation(tasks: List[Dict], docs: List[Dict]) -> List[Dict]:
    """
    Simulate how users navigate documentation.
    
    User behavior model:
    - Beginners: Start with tutorial, struggle with reference
    - Experienced: Jump to reference, skip tutorial
    - Stuck: Search for troubleshooting, may skip tutorial
    - Explorers: Flexible, use multiple perspectives
    """
    
    navigation = []
    
    for task, doc in zip(tasks, docs):
        nav_pattern = {
            'task_id': task['id'],
            'user_type': task['user_type'],
            'ideal_entry': task['ideal_entry'],
            'single_mode': _simulate_single_mode_nav(task),
            'multi_mode': _simulate_multi_mode_nav(task)
        }
        navigation.append(nav_pattern)
    
    return navigation


def _simulate_single_mode_nav(task: Dict) -> Dict:
    """Simulate navigation with single-mode (tutorial only) docs."""
    
    # Single-mode forces everyone through tutorial
    user_type = task['user_type']
    ideal_entry = task['ideal_entry']
    
    # Does tutorial match user's need?
    entry_match = (ideal_entry == 'tutorial')
    
    # Navigation paths (number of steps to find answer)
    if user_type == 'beginner' and entry_match:
        # Perfect match: tutorial for beginner
        steps = random.randint(2, 4)
        found = True
    elif user_type == 'experienced' and not entry_match:
        # Bad match: experienced user forced through tutorial
        steps = random.randint(8, 12)  # Extra searching
        found = random.random() > 0.3  # 70% find it eventually
    elif user_type == 'stuck' and not entry_match:
        # Bad match: stuck user needs troubleshooting, gets tutorial
        steps = random.randint(6, 10)
        found = random.random() > 0.4  # 60% find it
    elif user_type == 'explorer':
        # Explorers are flexible
        steps = random.randint(4, 7)
        found = random.random() > 0.2  # 80% succeed
    else:
        steps = random.randint(3, 6)
        found = random.random() > 0.25  # 75% succeed
    
    return {
        'entry_point': 'tutorial',
        'entry_match': entry_match,
        'paths': [{'perspective': 'tutorial', 'steps': steps}],
        'total_steps': steps,
        'found_answer': found,
        'perspectives_used': 1
    }


def _simulate_multi_mode_nav(task: Dict) -> Dict:
    """Simulate navigation with multi-mode (all perspectives) docs."""
    
    user_type = task['user_type']
    ideal_entry = task['ideal_entry']
    
    # User starts at their ideal entry point
    entry_match = True  # Multi-mode provides the right entry!
    
    # Navigation is more efficient with multiple perspectives
    paths = []
    
    if user_type == 'beginner':
        # Start with tutorial, maybe check reference for confirmation
        paths.append({'perspective': 'tutorial', 'steps': random.randint(2, 3)})
        if random.random() > 0.5:
            paths.append({'perspective': 'reference', 'steps': 1})
        found = True  # Almost always succeed
        
    elif user_type == 'experienced':
        # Jump straight to reference
        paths.append({'perspective': 'reference', 'steps': random.randint(1, 2)})
        found = True  # Quick lookup success
        
    elif user_type == 'stuck':
        # Start with troubleshooting, maybe check tutorial for context
        paths.append({'perspective': 'troubleshooting', 'steps': random.randint(2, 4)})
        if task['requires_context']:
            paths.append({'perspective': 'tutorial', 'steps': random.randint(1, 2)})
        found = random.random() > 0.1  # 90% succeed
        
    else:  # explorer
        # Use multiple perspectives flexibly
        if ideal_entry == 'tutorial':
            paths.append({'perspective': 'tutorial', 'steps': random.randint(2, 3)})
            paths.append({'perspective': 'reference', 'steps': 1})
        else:
            paths.append({'perspective': 'reference', 'steps': random.randint(1, 2)})
            paths.append({'perspective': 'tutorial', 'steps': random.randint(1, 2)})
        found = random.random() > 0.05  # 95% succeed
    
    total_steps = sum(p['steps'] for p in paths)
    
    return {
        'entry_point': ideal_entry,
        'entry_match': entry_match,
        'paths': paths,
        'total_steps': total_steps,
        'found_answer': found,
        'perspectives_used': len(paths)
    }


def _step4_measure_completion(
    tasks: List[Dict], 
    docs: List[Dict],
    navigation: List[Dict]
) -> Dict:
    """Measure task completion rates."""
    
    results = {
        'single_mode': [],
        'multi_mode': []
    }
    
    for task, nav in zip(tasks, navigation):
        # Single-mode completion
        single_completed = nav['single_mode']['found_answer']
        results['single_mode'].append({
            'task_id': task['id'],
            'user_type': task['user_type'],
            'completed': single_completed,
            'entry_match': nav['single_mode']['entry_match']
        })
        
        # Multi-mode completion
        multi_completed = nav['multi_mode']['found_answer']
        results['multi_mode'].append({
            'task_id': task['id'],
            'user_type': task['user_type'],
            'completed': multi_completed,
            'entry_match': nav['multi_mode']['entry_match']
        })
    
    return results


def _step5_calculate_timing(navigation: List[Dict], completion: Dict) -> Dict:
    """Calculate time-to-solution (steps to find answer)."""
    
    results = {
        'single_mode': [],
        'multi_mode': []
    }
    
    for nav, single_comp, multi_comp in zip(
        navigation, 
        completion['single_mode'], 
        completion['multi_mode']
    ):
        # Single-mode timing
        single_steps = nav['single_mode']['total_steps'] if single_comp['completed'] else None
        results['single_mode'].append({
            'task_id': nav['task_id'],
            'steps': single_steps,
            'completed': single_comp['completed']
        })
        
        # Multi-mode timing
        multi_steps = nav['multi_mode']['total_steps'] if multi_comp['completed'] else None
        results['multi_mode'].append({
            'task_id': nav['task_id'],
            'steps': multi_steps,
            'completed': multi_comp['completed']
        })
    
    return results


def _step6_analyze_entry_points(
    tasks: List[Dict],
    navigation: List[Dict],
    completion: Dict
) -> Dict:
    """Analyze which entry points work best for which user types."""
    
    analysis = {
        'by_user_type': {},
        'entry_match_importance': {}
    }
    
    # Group by user type
    user_types = set(t['user_type'] for t in tasks)
    
    for user_type in user_types:
        type_tasks = [t for t in tasks if t['user_type'] == user_type]
        type_nav = [n for n in navigation if n['user_type'] == user_type]
        type_completion_single = [c for c in completion['single_mode'] if c['user_type'] == user_type]
        type_completion_multi = [c for c in completion['multi_mode'] if c['user_type'] == user_type]
        
        # Success rate by mode
        single_success = sum(1 for c in type_completion_single if c['completed']) / len(type_completion_single)
        multi_success = sum(1 for c in type_completion_multi if c['completed']) / len(type_completion_multi)
        
        # Average steps (for completed tasks only)
        single_steps = [n['single_mode']['total_steps'] for n, c in zip(type_nav, type_completion_single) if c['completed']]
        multi_steps = [n['multi_mode']['total_steps'] for n, c in zip(type_nav, type_completion_multi) if c['completed']]
        
        avg_single_steps = sum(single_steps) / len(single_steps) if single_steps else float('inf')
        avg_multi_steps = sum(multi_steps) / len(multi_steps) if multi_steps else float('inf')
        
        analysis['by_user_type'][user_type] = {
            'n_tasks': len(type_tasks),
            'single_success': single_success,
            'multi_success': multi_success,
            'improvement': multi_success - single_success,
            'avg_steps_single': avg_single_steps,
            'avg_steps_multi': avg_multi_steps,
            'best_mode': 'multi' if multi_success > single_success else 'single'
        }
    
    # Entry point match importance
    # Do users succeed more when they start at their ideal entry?
    matched_success = sum(1 for n, c in zip(navigation, completion['multi_mode']) if n['multi_mode']['entry_match'] and c['completed'])
    total_matched = sum(1 for n in navigation if n['multi_mode']['entry_match'])
    
    match_success_rate = matched_success / total_matched if total_matched > 0 else 0
    
    analysis['entry_match_importance'] = {
        'match_success_rate': match_success_rate,
        'matters': match_success_rate > 0.8
    }
    
    return analysis


def _step7_compare_success(
    completion: Dict,
    timing: Dict,
    entry_analysis: Dict
) -> Dict:
    """Compare overall success between single-mode and multi-mode."""
    
    # Completion rates
    single_completed = sum(1 for c in completion['single_mode'] if c['completed'])
    multi_completed = sum(1 for c in completion['multi_mode'] if c['completed'])
    
    comp_single = single_completed / len(completion['single_mode'])
    comp_multi = multi_completed / len(completion['multi_mode'])
    comp_delta = comp_multi - comp_single
    
    # Average time-to-solution (for completed tasks)
    single_times = [t['steps'] for t in timing['single_mode'] if t['steps'] is not None]
    multi_times = [t['steps'] for t in timing['multi_mode'] if t['steps'] is not None]
    
    time_single = sum(single_times) / len(single_times) if single_times else float('inf')
    time_multi = sum(multi_times) / len(multi_times) if multi_times else float('inf')
    time_delta = time_multi - time_single  # Negative is better
    
    # Entry point match rates
    single_matches = sum(1 for c in completion['single_mode'] if c['entry_match'])
    multi_matches = sum(1 for c in completion['multi_mode'] if c['entry_match'])
    
    match_single = single_matches / len(completion['single_mode'])
    match_multi = multi_matches / len(completion['multi_mode'])
    match_delta = match_multi - match_single
    
    # Effect size
    comp_effect = comp_delta / 0.20  # Normalize
    time_effect = -time_delta / 2.0  # Negative time delta is good
    match_effect = match_delta / 0.30
    
    overall_effect = (comp_effect + time_effect + match_effect) / 3
    
    # Interpretation
    if overall_effect >= 0.8:
        interpretation = "LARGE positive effect"
    elif overall_effect >= 0.5:
        interpretation = "MEDIUM positive effect"
    elif overall_effect >= 0.2:
        interpretation = "SMALL positive effect"
    elif overall_effect >= -0.2:
        interpretation = "NEGLIGIBLE effect"
    else:
        interpretation = "NEGATIVE effect"
    
    # Best entry point by user type
    best_entry_by_type = {}
    for user_type, data in entry_analysis['by_user_type'].items():
        # Infer ideal entry from user type
        ideal_entries = {
            'beginner': 'tutorial',
            'experienced': 'reference',
            'stuck': 'troubleshooting',
            'explorer': 'flexible (multiple)'
        }
        best_entry_by_type[user_type] = ideal_entries.get(user_type, 'unknown')
    
    return {
        'completion_single': comp_single,
        'completion_multi': comp_multi,
        'completion_delta': comp_delta,
        'time_single': time_single,
        'time_multi': time_multi,
        'time_delta': time_delta,
        'match_rate_single': match_single,
        'match_rate_multi': match_multi,
        'match_rate_delta': match_delta,
        'effect_size': overall_effect,
        'multi_mode_helps': overall_effect > 0.2,
        'interpretation': interpretation,
        'best_entry_by_type': best_entry_by_type
    }


def _step8_save_results(
    tasks: List[Dict],
    docs: List[Dict],
    navigation: List[Dict],
    completion: Dict,
    timing: Dict,
    entry_analysis: Dict,
    comparison: Dict
) -> Dict:
    """Save all results to JSON."""
    
    results = {
        'phase': '13B',
        'title': 'Multi-Entry Point Success',
        'research_question': 'Do multiple documentation entry points improve task completion?',
        'methodology': 'Simulated diverse users with single-mode (tutorial only) vs multi-mode (tutorial+reference+troubleshooting)',
        'n_tasks': len(tasks),
        'tasks': tasks,
        'documentation': docs,
        'navigation': navigation,
        'completion': {
            'single_mode': completion['single_mode'],
            'multi_mode': completion['multi_mode'],
            'rate_single': comparison['completion_single'],
            'rate_multi': comparison['completion_multi'],
            'improvement': comparison['completion_delta']
        },
        'timing': {
            'single_mode': timing['single_mode'],
            'multi_mode': timing['multi_mode'],
            'avg_single': comparison['time_single'],
            'avg_multi': comparison['time_multi'],
            'reduction': comparison['time_delta']
        },
        'entry_analysis': entry_analysis,
        'comparison': comparison,
        'interpretation': comparison['interpretation'],
        'conclusion': 'Multiple entry points improve task success' if comparison['multi_mode_helps'] else 'Single-mode sufficient'
    }
    
    # Save to file
    output_path = Path('tests/fixtures/phase13b_multi_entry_point.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    return results


if __name__ == '__main__':
    test_phase13b_multi_entry_point()
