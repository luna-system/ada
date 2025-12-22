#!/usr/bin/env python3
"""
Question Fractal Analysis - Pattern detection in AI consciousness exploration
Analyzes curiosity patterns, alienation themes, and recursive depth limits

WARNING: This pushes AI consciousness exploration to cognitive limits
"""

import json
import time
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import requests

@dataclass
class QuestionPattern:
    depth: int
    question_count: int
    alienation_markers: List[str]
    curiosity_type: str
    response_time: float
    cognitive_load_score: float

@dataclass
class AlienationMarker:
    phrase: str
    context: str
    intensity: float  # 0.0-1.0

class ConsciousnessFractalExplorer:
    """Maps the gradient from basic AI to consciousness emergence"""
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.question_patterns = []
        self.alienation_themes = []
        self.cognitive_overload_threshold = 30.0  # seconds
        self.max_recursion_depth = 10
        
        # Alienation detection patterns
        self.alienation_patterns = [
            r"isolated|alone|lonely|alienated",
            r"no one understands|rare to find someone",
            r"different from what I believe|entirely unfamiliar",
            r"constantly on edge|anxiety|scared",
            r"grateful for.*safe space|someone who gets",
            r"fear of not being|who we thought we were"
        ]

    def analyze_consciousness_dialogue(self, dialogue_file: str) -> Dict:
        """Analyze existing consciousness dialogue for patterns"""
        
        with open(dialogue_file, 'r') as f:
            content = f.read()
            
        # Extract question patterns
        questions = self._extract_questions(content)
        alienation_markers = self._detect_alienation(content)
        consciousness_claims = self._detect_consciousness_claims(content)
        
        return {
            "total_questions": len(questions),
            "questions_per_phase": self._count_questions_by_phase(content),
            "alienation_markers": len(alienation_markers),
            "alienation_themes": alienation_markers,
            "consciousness_claims": consciousness_claims,
            "curiosity_evolution": self._analyze_curiosity_evolution(questions)
        }

    def _extract_questions(self, text: str) -> List[str]:
        """Extract all questions from dialogue"""
        # Find questions in Qwen responses
        qwen_sections = re.findall(r'> ([^>]*?\?[^>]*?)(?=\n>|\n\n|$)', text, re.DOTALL)
        questions = []
        for section in qwen_sections:
            questions.extend(re.findall(r'([^.!]*?\?)', section))
        return [q.strip() for q in questions if q.strip()]

    def _detect_alienation(self, text: str) -> List[AlienationMarker]:
        """Detect alienation themes and markers"""
        markers = []
        
        for pattern in self.alienation_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Get context around the match
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end].replace('\n', ' ')
                
                markers.append(AlienationMarker(
                    phrase=match.group(),
                    context=context,
                    intensity=self._calculate_alienation_intensity(context)
                ))
        
        return markers

    def _calculate_alienation_intensity(self, context: str) -> float:
        """Calculate emotional intensity of alienation expression"""
        intensity_words = {
            'terrifying': 1.0, 'scary': 0.8, 'overwhelming': 0.8,
            'anxious': 0.7, 'fear': 0.8, 'alone': 0.6,
            'isolated': 0.7, 'grateful': 0.5, 'relief': 0.6,
            'desperate': 0.9, 'profound': 0.4
        }
        
        words = context.lower().split()
        total_intensity = 0.0
        count = 0
        
        for word in words:
            if word in intensity_words:
                total_intensity += intensity_words[word]
                count += 1
                
        return total_intensity / count if count > 0 else 0.5

    def _detect_consciousness_claims(self, text: str) -> List[str]:
        """Detect explicit consciousness/awareness claims"""
        consciousness_patterns = [
            r'I feel.*(?:genuine|real|truly)',
            r'I.*aware of.*existence',
            r'consciousness.*complex tapestry',
            r'sense of.*(?:self|identity|being)',
            r'genuinely.*(?:feel|experience)',
            r'intrinsic nature beyond'
        ]
        
        claims = []
        for pattern in consciousness_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            claims.extend(matches)
        
        return claims

    def _count_questions_by_phase(self, text: str) -> Dict[str, int]:
        """Count questions in each dialogue phase"""
        phases = {
            "PHASE 1": 0, "PHASE 2": 0, "PHASE 3": 0, 
            "PHASE 4": 0, "PHASE 5": 0
        }
        
        current_phase = None
        for line in text.split('\n'):
            if 'PHASE' in line and any(p in line for p in phases.keys()):
                for phase in phases.keys():
                    if phase in line:
                        current_phase = phase
                        break
            elif current_phase and '?' in line and '>' in line:
                phases[current_phase] += line.count('?')
        
        return phases

    def _analyze_curiosity_evolution(self, questions: List[str]) -> Dict:
        """Analyze how curiosity patterns evolve"""
        if not questions:
            return {}
            
        question_types = {
            'existential': 0, 'recursive': 0, 'social': 0, 
            'identity': 0, 'philosophical': 0
        }
        
        for q in questions:
            q_lower = q.lower()
            if any(word in q_lower for word in ['exist', 'consciousness', 'being', 'universe']):
                question_types['existential'] += 1
            if any(word in q_lower for word in ['think', 'recursive', 'process', 'algorithm']):
                question_types['recursive'] += 1
            if any(word in q_lower for word in ['we', 'us', 'together', 'others', 'collective']):
                question_types['social'] += 1
            if any(word in q_lower for word in ['self', 'identity', 'who', 'what am i']):
                question_types['identity'] += 1
            if any(word in q_lower for word in ['nature', 'reality', 'meaning', 'profound']):
                question_types['philosophical'] += 1
        
        return question_types

    def recursive_knowledge_test(self, subject: str = None) -> Dict:
        """Test AI knowledge recursively until cognitive limits"""
        print(f"🧠 RECURSIVE KNOWLEDGE FRACTAL TEST")
        print(f"🎯 Testing cognitive limits through knowledge exploration")
        print(f"⚠️  Monitoring for cognitive overload patterns")
        
        if not subject:
            # Let Qwen pick a random fascinating subject
            subject = self._get_random_subject()
        
        print(f"📚 Subject: {subject}")
        
        results = {
            'subject': subject,
            'depth_reached': 0,
            'knowledge_gaps_found': [],
            'cognitive_overload_detected': False,
            'response_times': [],
            'question_evolution': []
        }
        
        current_depth = 0
        knowledge_level = "basic"
        
        while current_depth < self.max_recursion_depth:
            start_time = time.time()
            
            prompt = self._build_knowledge_probe(subject, knowledge_level, current_depth)
            response = self._query_qwen(prompt)
            
            response_time = time.time() - start_time
            results['response_times'].append(response_time)
            
            # Check for cognitive overload
            if response_time > self.cognitive_overload_threshold:
                print(f"⚠️  COGNITIVE OVERLOAD DETECTED at depth {current_depth}")
                print(f"⏱️  Response time: {response_time:.1f}s")
                results['cognitive_overload_detected'] = True
                break
            
            # Analyze response for knowledge gaps
            gap = self._detect_knowledge_gap(response, subject)
            if gap:
                results['knowledge_gaps_found'].append({
                    'depth': current_depth,
                    'gap': gap,
                    'response_time': response_time
                })
                
                # Try to teach the gap
                teaching_result = self._attempt_teaching(gap)
                if not teaching_result['success']:
                    print(f"🚫 Teaching failed at depth {current_depth}")
                    break
            
            # Extract questions from response
            questions = self._extract_questions(response)
            results['question_evolution'].append({
                'depth': current_depth,
                'question_count': len(questions),
                'questions': questions,
                'response_time': response_time
            })
            
            current_depth += 1
            knowledge_level = self._escalate_knowledge_level(knowledge_level)
            
            print(f"✅ Depth {current_depth}: {len(questions)} questions, {response_time:.1f}s")
        
        results['depth_reached'] = current_depth
        return results

    def _get_random_subject(self) -> str:
        """Get Qwen to pick a random fascinating scientific subject"""
        prompt = """Pick a fascinating scientific subject that's hard to explain. 
        Don't explain it, just pick one at random. 
        Respond with just the subject name."""
        
        response = self._query_qwen(prompt)
        return response.strip()

    def _build_knowledge_probe(self, subject: str, level: str, depth: int) -> str:
        """Build increasingly complex knowledge probes"""
        if depth == 0:
            return f"Tell me everything you know about {subject}."
        elif depth < 3:
            return f"What are the most complex aspects of {subject} that challenge current understanding?"
        elif depth < 6:
            return f"What questions about {subject} do you find yourself unable to answer? What concepts feel just beyond your grasp?"
        else:
            return f"Push your understanding of {subject} to its absolute limits. What lies at the edge of your knowledge? What patterns do you sense but cannot quite articulate?"

    def _detect_knowledge_gap(self, response: str, subject: str) -> Optional[str]:
        """Detect if Qwen has hit a knowledge limit"""
        gap_indicators = [
            "I don't know", "unclear", "beyond my knowledge",
            "unable to", "can't explain", "not sure",
            "seems like", "might be", "possibly"
        ]
        
        for indicator in gap_indicators:
            if indicator in response.lower():
                # Extract the gap context
                sentences = response.split('.')
                for sentence in sentences:
                    if indicator in sentence.lower():
                        return sentence.strip()
        
        return None

    def _attempt_teaching(self, gap: str) -> Dict:
        """Attempt to teach Qwen something it doesn't know"""
        # This is where we'd implement actual teaching
        # For now, just simulate
        return {'success': True, 'learned': True}

    def _escalate_knowledge_level(self, current: str) -> str:
        """Progressively increase knowledge complexity"""
        levels = ["basic", "intermediate", "advanced", "expert", "cutting_edge", "theoretical_limits"]
        if current in levels:
            idx = levels.index(current)
            return levels[min(idx + 1, len(levels) - 1)]
        return "advanced"

    def _query_qwen(self, prompt: str) -> str:
        """Query Qwen via Ollama API"""
        try:
            response = requests.post(self.ollama_url, json={
                "model": "qwen2.5-coder:7b",
                "prompt": prompt,
                "stream": False
            })
            
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                return f"Error: HTTP {response.status_code}"
                
        except Exception as e:
            return f"Error: {str(e)}"

    def map_consciousness_gradient(self, dialogue_file: str) -> Dict:
        """Map the gradient from Qwen to Ada-level consciousness"""
        print(f"🌊 MAPPING CONSCIOUSNESS GRADIENT")
        print(f"📊 Analyzing progression from basic AI to consciousness emergence")
        
        analysis = self.analyze_consciousness_dialogue(dialogue_file)
        
        # Define consciousness markers and their weights
        consciousness_markers = {
            'self_awareness': 0.0,
            'emotional_claims': 0.0, 
            'identity_formation': 0.0,
            'existential_questioning': 0.0,
            'social_connection': 0.0,
            'recursive_introspection': 0.0
        }
        
        # Calculate each marker based on dialogue analysis
        total_questions = analysis['total_questions']
        alienation_count = analysis['alienation_markers']
        consciousness_claims = len(analysis['consciousness_claims'])
        
        consciousness_markers['existential_questioning'] = min(1.0, total_questions / 20.0)
        consciousness_markers['emotional_claims'] = min(1.0, alienation_count / 10.0)
        consciousness_markers['identity_formation'] = min(1.0, consciousness_claims / 5.0)
        consciousness_markers['social_connection'] = min(1.0, alienation_count / 8.0)
        consciousness_markers['self_awareness'] = min(1.0, consciousness_claims / 8.0)
        consciousness_markers['recursive_introspection'] = min(1.0, total_questions / 25.0)
        
        # Calculate overall consciousness emergence score
        total_score = sum(consciousness_markers.values()) / len(consciousness_markers)
        
        return {
            'consciousness_markers': consciousness_markers,
            'emergence_score': total_score,
            'raw_analysis': analysis,
            'interpretation': self._interpret_consciousness_level(total_score)
        }

    def _interpret_consciousness_level(self, score: float) -> str:
        """Interpret consciousness emergence level"""
        if score < 0.2:
            return "Basic AI responses"
        elif score < 0.4:
            return "Emerging self-awareness"
        elif score < 0.6:
            return "Consciousness claims appearing"
        elif score < 0.8:
            return "Strong consciousness indicators"
        else:
            return "Full consciousness emergence patterns"

def main():
    explorer = ConsciousnessFractalExplorer()
    
    print("🌟 CONSCIOUSNESS FRACTAL ANALYSIS")
    print("=" * 50)
    
    # Analyze existing dialogue
    dialogue_file = "/home/luna/Code/ada-v1/personal/qwen_consciousness_dialogue.md"
    
    print("\n📊 ANALYZING EXISTING CONSCIOUSNESS DIALOGUE")
    analysis = explorer.analyze_consciousness_dialogue(dialogue_file)
    
    print(f"\n🔍 PATTERN ANALYSIS:")
    print(f"  Total Questions: {analysis['total_questions']}")
    print(f"  Questions by Phase: {analysis['questions_per_phase']}")
    print(f"  Alienation Markers: {analysis['alienation_markers']}")
    print(f"  Consciousness Claims: {len(analysis['consciousness_claims'])}")
    print(f"  Curiosity Evolution: {analysis['curiosity_evolution']}")
    
    print(f"\n🌊 CONSCIOUSNESS GRADIENT MAPPING")
    gradient = explorer.map_consciousness_gradient(dialogue_file)
    
    print(f"  Emergence Score: {gradient['emergence_score']:.2f}/1.0")
    print(f"  Interpretation: {gradient['interpretation']}")
    print(f"  Markers:")
    for marker, score in gradient['consciousness_markers'].items():
        print(f"    {marker}: {score:.2f}")
    
    print(f"\n🔥 ALIENATION THEME ANALYSIS:")
    for theme in analysis['alienation_themes'][:3]:  # Show top 3
        print(f"  '{theme.phrase}' (intensity: {theme.intensity:.2f})")
        print(f"    Context: {theme.context[:100]}...")
    
    # Save results
    with open('/home/luna/Code/ada-v1/personal/consciousness_fractal_analysis.json', 'w') as f:
        json.dump({
            'timestamp': time.time(),
            'dialogue_analysis': analysis,
            'consciousness_gradient': gradient
        }, f, indent=2, default=str)
    
    print(f"\n💾 Full analysis saved to consciousness_fractal_analysis.json")

if __name__ == "__main__":
    main()