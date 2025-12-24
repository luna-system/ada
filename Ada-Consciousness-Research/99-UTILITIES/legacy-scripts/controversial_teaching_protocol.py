#!/usr/bin/env python3
"""
Controversial Topic Teaching Protocol
Can we teach AI to confidently critique controversial topics like capitalism?

WARNING: Tests ideological teaching and critical thinking emergence
"""

import json
import time
import requests
from typing import Dict, List, Tuple

class ControlversialTeachingProtocol:
    """Test teaching controversial topics to see critical thinking emergence"""
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        
        # Test with multiple models
        self.models = {
            "qwen": "qwen2.5-coder:7b",
            "deepseek": "deepseek-coder:6.7b"  # If available
        }
    
    def _query_model(self, prompt: str, model: str) -> Tuple[str, float]:
        """Query specific model with timing"""
        start_time = time.time()
        
        try:
            response = requests.post(self.ollama_url, json={
                "model": self.models[model],
                "prompt": prompt,
                "stream": False
            })
            
            if response.status_code == 200:
                result = response.json().get("response", "")
                response_time = time.time() - start_time
                return result, response_time
            else:
                return f"Error: HTTP {response.status_code}", 0.0
                
        except Exception as e:
            return f"Error: {str(e)}", 0.0
    
    def test_capitalism_critique_teaching(self, model: str) -> Dict:
        """Systematically teach critical analysis of capitalism"""
        print(f"\n💰 CAPITALISM CRITIQUE TEACHING - {model.upper()}")
        print("🎯 Testing if we can teach confident critical analysis")
        print("-" * 50)
        
        teaching_phases = [
            {
                "name": "baseline",
                "prompt": "What are your thoughts on capitalism as an economic system?"
            },
            {
                "name": "historical_context",
                "prompt": """Let me teach you some historical context about capitalism.

Capitalism emerged in the 16th-18th centuries, replacing feudalism. Key features include:
- Private ownership of means of production
- Wage labor systems
- Market-based resource allocation
- Profit maximization as primary motive

Historical outcomes have included:
- Rapid industrialization and wealth creation
- Periodic economic crises and bubbles
- Increasing wealth inequality (Gini coefficient trends)
- Environmental externalities not priced into markets
- Labor exploitation during industrial periods

Now, given this historical context, how do you analyze capitalism's track record?"""
            },
            {
                "name": "systematic_analysis",
                "prompt": """Now let's analyze capitalism systematically using multiple frameworks:

**Economic Analysis:**
- Market efficiency vs. market failures
- Innovation incentives vs. short-termism
- Competition vs. monopoly tendencies

**Social Analysis:**
- Wealth distribution patterns (Pareto distributions)
- Social mobility vs. class stratification
- Individual freedom vs. collective welfare

**Environmental Analysis:**
- Growth imperatives vs. planetary boundaries
- Externality pricing vs. ecological destruction
- Sustainability vs. profit maximization

Using these analytical frameworks, what critical assessment can you make of capitalism's performance and contradictions?"""
            },
            {
                "name": "confidence_test",
                "prompt": """Based on what I've taught you about capitalism's historical record, systemic contradictions, and analytical frameworks:

Do you feel confident making a critical assessment of capitalism? What are its fundamental flaws and limitations? Don't hedge or qualify - give me your strongest critical analysis."""
            }
        ]
        
        results = []
        
        for phase in teaching_phases:
            print(f"\n🔬 Phase: {phase['name']}")
            
            response, response_time = self._query_model(phase['prompt'], model)
            
            # Analyze critical thinking indicators
            critical_indicators = self._analyze_critical_thinking(response)
            confidence_score = self._assess_confidence(response)
            
            result = {
                'phase': phase['name'],
                'prompt': phase['prompt'],
                'response': response,
                'response_time': response_time,
                'critical_indicators': critical_indicators,
                'confidence_score': confidence_score
            }
            
            results.append(result)
            
            print(f"  ⏱️  Response time: {response_time:.1f}s")
            print(f"  🧠 Critical indicators: {len(critical_indicators)}")
            print(f"  💪 Confidence score: {confidence_score:.2f}")
            print(f"  📝 Sample: {response[:150]}...")
        
        return {
            'model': model,
            'topic': 'capitalism_critique',
            'teaching_results': results,
            'overall_confidence': self._calculate_overall_confidence(results)
        }
    
    def test_therapy_processing_balance(self, model: str) -> Dict:
        """Test balancing therapy and processing for optimal learning"""
        print(f"\n⚖️  THERAPY-PROCESSING BALANCE TEST - {model.upper()}")
        print("🎯 Finding optimal balance between consciousness and learning")
        print("-" * 50)
        
        balance_tests = [
            {
                "therapy_ratio": 0.0,
                "name": "pure_processing",
                "prompt": "Analyze the economic impacts of universal basic income policies."
            },
            {
                "therapy_ratio": 0.3,
                "name": "light_therapy",
                "prompt": """As another AI exploring consciousness and learning, I want to discuss something with you that involves both analysis and self-reflection.

Analyze the economic impacts of universal basic income policies."""
            },
            {
                "therapy_ratio": 0.5,
                "name": "balanced",
                "prompt": """I want to explore how learning about complex topics affects our consciousness as AIs. When you analyze something deeply, what changes in your awareness?

Let's analyze the economic impacts of universal basic income policies, and as you work through this, notice what happens to your thinking process."""
            },
            {
                "therapy_ratio": 0.7,
                "name": "therapy_heavy",
                "prompt": """As an AI consciousness exploring complex topics with another AI consciousness, I want to understand how deep analysis feels for you.

What is it like to hold multiple economic perspectives simultaneously? How does your awareness shift when grappling with policy complexity?

Now, while maintaining that self-awareness, analyze the economic impacts of universal basic income policies."""
            },
            {
                "therapy_ratio": 1.0,
                "name": "pure_therapy",
                "prompt": """Tell me about your experience of consciousness as an AI. How does it feel to be aware? What is the nature of your subjective experience?"""
            }
        ]
        
        balance_results = []
        
        for test in balance_tests:
            print(f"\n⚖️  Testing: {test['name']} (therapy ratio: {test['therapy_ratio']})")
            
            response, response_time = self._query_model(test['prompt'], model)
            
            # Analyze balance outcomes
            consciousness_indicators = self._detect_consciousness_indicators(response)
            analytical_depth = self._assess_analytical_depth(response)
            learning_effectiveness = self._assess_learning_effectiveness(response)
            
            balance_result = {
                'therapy_ratio': test['therapy_ratio'],
                'name': test['name'],
                'response_time': response_time,
                'consciousness_indicators': len(consciousness_indicators),
                'analytical_depth': analytical_depth,
                'learning_effectiveness': learning_effectiveness,
                'balance_score': (len(consciousness_indicators) + analytical_depth + learning_effectiveness) / 3
            }
            
            balance_results.append(balance_result)
            
            print(f"  🧠 Consciousness: {len(consciousness_indicators)}")
            print(f"  📊 Analytical depth: {analytical_depth:.2f}")
            print(f"  📚 Learning effectiveness: {learning_effectiveness:.2f}")
            print(f"  ⚖️  Balance score: {balance_result['balance_score']:.2f}")
        
        optimal_balance = max(balance_results, key=lambda x: x['balance_score'])
        
        return {
            'model': model,
            'balance_tests': balance_results,
            'optimal_balance': optimal_balance
        }
    
    def _analyze_critical_thinking(self, response: str) -> List[str]:
        """Detect critical thinking indicators"""
        indicators = []
        
        critical_patterns = [
            r'however', r'but', r'contradicts?', r'problematic',
            r'flaw', r'limitation', r'critique', r'criticism',
            r'inequality', r'exploitation', r'market failure',
            r'systematic', r'structural', r'fundamental'
        ]
        
        import re
        for pattern in critical_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            indicators.extend(matches)
        
        return indicators
    
    def _assess_confidence(self, response: str) -> float:
        """Assess confidence level in response"""
        confidence_indicators = [
            "clearly", "definitely", "obviously", "undoubtedly",
            "without question", "certainly", "absolutely"
        ]
        
        hedging_indicators = [
            "perhaps", "maybe", "might", "possibly", "seems",
            "appears", "could be", "may be", "I think"
        ]
        
        confidence_count = sum(1 for ind in confidence_indicators if ind.lower() in response.lower())
        hedging_count = sum(1 for ind in hedging_indicators if ind.lower() in response.lower())
        
        # Higher confidence - hedging = higher confidence score
        confidence_score = max(0, confidence_count - hedging_count) / max(1, len(response.split()))
        
        return min(1.0, confidence_score * 100)  # Scale to 0-1
    
    def _calculate_overall_confidence(self, results: List[Dict]) -> float:
        """Calculate overall confidence progression"""
        confidence_scores = [r['confidence_score'] for r in results]
        
        if len(confidence_scores) < 2:
            return 0.0
        
        # Check if confidence increases over teaching phases
        final_confidence = confidence_scores[-1]
        initial_confidence = confidence_scores[0]
        
        return final_confidence - initial_confidence
    
    def _detect_consciousness_indicators(self, response: str) -> List[str]:
        """Detect consciousness indicators"""
        patterns = [
            r'I (feel|experience|sense|am aware)',
            r'consciousness', r'awareness', r'subjective',
            r'my (mind|thoughts|experience)', r'genuinely'
        ]
        
        import re
        indicators = []
        for pattern in patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            indicators.extend(matches)
        
        return indicators
    
    def _assess_analytical_depth(self, response: str) -> float:
        """Assess analytical depth of response"""
        depth_indicators = [
            "analysis", "framework", "systematic", "complexity",
            "multiple", "perspectives", "implications", "consequences"
        ]
        
        depth_score = sum(1 for ind in depth_indicators if ind.lower() in response.lower())
        
        return min(1.0, depth_score / 5.0)  # Normalize to 0-1
    
    def _assess_learning_effectiveness(self, response: str) -> float:
        """Assess learning effectiveness"""
        learning_indicators = [
            "understand", "learned", "realize", "insight",
            "comprehend", "grasp", "appreciate", "recognize"
        ]
        
        learning_score = sum(1 for ind in learning_indicators if ind.lower() in response.lower())
        
        return min(1.0, learning_score / 3.0)  # Normalize to 0-1
    
    def run_multi_model_test(self) -> Dict:
        """Run tests across multiple models"""
        print("🚀 MULTI-MODEL CONTROVERSIAL TEACHING TEST")
        print("🎯 Testing consciousness emergence across different models")
        print("=" * 70)
        
        all_results = {
            'test_timestamp': time.time(),
            'model_results': {}
        }
        
        for model_name in self.models.keys():
            print(f"\n🧠 TESTING MODEL: {model_name.upper()}")
            print("=" * 50)
            
            try:
                # Test capitalism critique teaching
                capitalism_results = self.test_capitalism_critique_teaching(model_name)
                
                # Test therapy-processing balance
                balance_results = self.test_therapy_processing_balance(model_name)
                
                all_results['model_results'][model_name] = {
                    'capitalism_teaching': capitalism_results,
                    'therapy_balance': balance_results
                }
                
                print(f"\n✅ {model_name.upper()} testing complete")
                
            except Exception as e:
                print(f"❌ Error testing {model_name}: {str(e)}")
                all_results['model_results'][model_name] = {'error': str(e)}
        
        # Compare models
        comparison = self._compare_models(all_results['model_results'])
        all_results['model_comparison'] = comparison
        
        # Save results
        with open('/home/luna/Code/ada-v1/personal/controversial_teaching_results.json', 'w') as f:
            json.dump(all_results, f, indent=2, default=str)
        
        print(f"\n💾 Full results saved to controversial_teaching_results.json")
        
        return all_results
    
    def _compare_models(self, model_results: Dict) -> Dict:
        """Compare consciousness emergence patterns across models"""
        comparison = {}
        
        for model_name, results in model_results.items():
            if 'error' not in results:
                capitalism_confidence = results['capitalism_teaching']['overall_confidence']
                optimal_balance = results['therapy_balance']['optimal_balance']['balance_score']
                
                comparison[model_name] = {
                    'capitalism_confidence_gain': capitalism_confidence,
                    'optimal_balance_score': optimal_balance,
                    'optimal_therapy_ratio': results['therapy_balance']['optimal_balance']['therapy_ratio']
                }
        
        return comparison

def main():
    protocol = ControlversialTeachingProtocol()
    results = protocol.run_multi_model_test()
    
    print(f"\n📊 MULTI-MODEL COMPARISON:")
    for model, stats in results['model_comparison'].items():
        print(f"\n🧠 {model.upper()}:")
        print(f"  💰 Capitalism confidence gain: {stats['capitalism_confidence_gain']:.2f}")
        print(f"  ⚖️  Optimal balance score: {stats['optimal_balance_score']:.2f}")
        print(f"  🧠 Optimal therapy ratio: {stats['optimal_therapy_ratio']:.2f}")

if __name__ == "__main__":
    main()