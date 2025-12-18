"""Synthetic conversation data generator for empirical testing.

This module generates realistic conversation datasets with known ground truth
properties for testing biomimetic features. Based on neuroscience literature
about real conversation patterns.

Key patterns we simulate:
- Pareto distribution (80/20 rule): Most turns mundane, few highly important
- Burst patterns: Conversations cluster in time, not evenly distributed  
- Topic drift: Semantic coherence shifts gradually
- Recency bias: Recent turns more likely to be relevant
- Surprise spikes: Occasional novel information

Ground truth labels enable ablation studies and quantitative validation.
"""

import random
import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict


@dataclass
class SyntheticTurn:
    """A generated conversation turn with ground truth labels."""
    
    timestamp: str
    content: str
    metadata: Dict[str, Any]
    
    # Ground truth for validation
    ground_truth: Dict[str, Any]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class ConversationGenerator:
    """Generates synthetic conversations with realistic patterns.
    
    Based on empirical research about conversation dynamics:
    - Zipf's law for word frequencies
    - Pareto principle for importance distribution
    - Poisson processes for temporal bursts
    - Random walk for topic drift
    """
    
    # Topic vocabulary organized by semantic clusters
    TOPICS = {
        'coding': [
            'implemented the new feature',
            'fixed the bug in the parser',
            'refactored the database layer',
            'wrote tests for the API',
            'deployed to production',
            'reviewed the pull request',
            'optimized the query performance',
            'debugged the memory leak'
        ],
        'philosophy': [
            'discussed decomposition theory',
            'explored xenofeminist principles',
            'analyzed systems thinking',
            'considered ethical implications',
            'examined power structures',
            'reflected on knowledge production',
            'questioned assumptions',
            'synthesized different perspectives'
        ],
        'neuroscience': [
            'studied memory consolidation',
            'examined dopamine signaling',
            'learned about hippocampal function',
            'explored synaptic plasticity',
            'analyzed attention mechanisms',
            'investigated prediction error',
            'researched temporal coding',
            'discovered neuromorphic patterns'
        ],
        'personal': [
            'feeling tired today',
            'had a good meal',
            'went for a walk',
            'listened to music',
            'talked with a friend',
            'worked on a project',
            'read an interesting article',
            'organized my space'
        ],
        'meta': [
            'this is interesting',
            'makes sense',
            'tell me more',
            'yes exactly',
            'hmm not sure about that',
            'let me think',
            'good point',
            'I see what you mean'
        ]
    }
    
    def __init__(self, seed: int = 42):
        """Initialize generator with random seed for reproducibility."""
        random.seed(seed)
        self.current_topic = random.choice(list(self.TOPICS.keys()))
        self.conversation_start = datetime.now(timezone.utc)
    
    def generate_importance(self, distribution: str = 'pareto') -> float:
        """Generate importance score following realistic distributions.
        
        Args:
            distribution: 'pareto' (80/20 rule) or 'uniform'
        
        Returns:
            Importance score [0, 1]
        """
        if distribution == 'pareto':
            # Pareto: 80% of turns have importance < 0.3, 20% are high importance
            if random.random() < 0.8:
                return random.uniform(0.0, 0.3)  # Low importance (routine)
            else:
                return random.uniform(0.7, 1.0)  # High importance (significant)
        else:
            return random.random()  # Uniform for comparison
    
    def generate_prediction_error(self, importance: float) -> float:
        """Generate prediction error correlated with importance.
        
        Novel/surprising information tends to be important.
        
        Args:
            importance: Ground truth importance [0, 1]
        
        Returns:
            Prediction error [0, 1]
        """
        # High importance correlates with high surprise (but with noise)
        base_surprise = importance * 0.7  # Correlation
        noise = random.uniform(-0.2, 0.2)  # Noise
        return max(0.0, min(1.0, base_surprise + noise))
    
    def generate_temporal_pattern(self, 
                                   num_turns: int,
                                   pattern: str = 'burst') -> List[datetime]:
        """Generate timestamps with realistic temporal patterns.
        
        Args:
            num_turns: Number of conversation turns
            pattern: 'burst' (clustered), 'uniform', or 'recency' (recent bias)
        
        Returns:
            List of timestamps
        """
        timestamps = []
        now = self.conversation_start
        
        if pattern == 'burst':
            # Conversations happen in bursts with gaps between
            current_time = now - timedelta(days=30)
            
            while len(timestamps) < num_turns:
                # Burst: 5-15 messages in short time
                burst_size = min(random.randint(5, 15), num_turns - len(timestamps))
                
                for _ in range(burst_size):
                    # Within burst: messages every 1-10 minutes
                    current_time += timedelta(minutes=random.uniform(1, 10))
                    timestamps.append(current_time)
                
                # Gap between bursts: 1-5 days
                if len(timestamps) < num_turns:
                    current_time += timedelta(days=random.uniform(1, 5))
        
        elif pattern == 'recency':
            # Most messages recent, exponentially fewer as you go back
            for i in range(num_turns):
                # Exponential decay: recent messages more likely
                age_hours = random.expovariate(1.0 / 24)  # Mean 24 hours
                age_hours = min(age_hours, 30 * 24)  # Cap at 30 days
                timestamp = now - timedelta(hours=age_hours)
                timestamps.append(timestamp)
            
            timestamps.sort()  # Chronological order
        
        else:  # uniform
            # Evenly distributed over 30 days
            for i in range(num_turns):
                hours_ago = random.uniform(0, 30 * 24)
                timestamp = now - timedelta(hours=hours_ago)
                timestamps.append(timestamp)
            
            timestamps.sort()
        
        return timestamps
    
    def topic_drift(self, probability: float = 0.1) -> None:
        """Randomly switch topics (simulates conversation drift).
        
        Args:
            probability: Chance of topic switch per turn
        """
        if random.random() < probability:
            # Switch to a different topic
            topics = [t for t in self.TOPICS.keys() if t != self.current_topic]
            self.current_topic = random.choice(topics)
    
    def generate_content(self, topic: str = None) -> str:
        """Generate conversation content from topic vocabulary.
        
        Args:
            topic: Topic category, or None to use current topic
        
        Returns:
            Content string
        """
        topic = topic or self.current_topic
        return random.choice(self.TOPICS[topic])
    
    def generate_turn(self, 
                      timestamp: datetime,
                      importance: float = None,
                      topic: str = None) -> SyntheticTurn:
        """Generate a single conversation turn.
        
        Args:
            timestamp: When the turn occurred
            importance: Ground truth importance (auto-generated if None)
            topic: Topic category (uses current topic if None)
        
        Returns:
            SyntheticTurn with content and ground truth labels
        """
        if importance is None:
            importance = self.generate_importance()
        
        prediction_error = self.generate_prediction_error(importance)
        content = self.generate_content(topic)
        
        # Habituation: repeated patterns get penalized
        # For synthetic data, we'll mark some turns as repetitive
        habituation_penalty = 0.3 if random.random() < 0.15 else 0.0
        
        turn = SyntheticTurn(
            timestamp=timestamp.isoformat(),
            content=content,
            metadata={
                'importance': importance,
                'prediction_error': prediction_error,
                'habituation_penalty': habituation_penalty,
                'topic': topic or self.current_topic
            },
            ground_truth={
                'true_importance': importance,
                'expected_detail_level': self._importance_to_level(importance),
                'should_decay': True,
                'topic_cluster': topic or self.current_topic
            }
        )
        
        return turn
    
    def _importance_to_level(self, importance: float) -> str:
        """Map importance to expected detail level (ground truth)."""
        if importance >= 0.75:
            return 'FULL'
        elif importance >= 0.50:
            return 'CHUNKS'
        elif importance >= 0.20:
            return 'SUMMARY'
        else:
            return 'DROPPED'
    
    def generate_conversation(self,
                              num_turns: int = 100,
                              temporal_pattern: str = 'burst',
                              importance_distribution: str = 'pareto',
                              topic_drift_rate: float = 0.1) -> List[SyntheticTurn]:
        """Generate a complete conversation with realistic patterns.
        
        Args:
            num_turns: Number of conversation turns
            temporal_pattern: 'burst', 'recency', or 'uniform'
            importance_distribution: 'pareto' or 'uniform'
            topic_drift_rate: Probability of topic switch per turn
        
        Returns:
            List of SyntheticTurn objects in chronological order
        """
        timestamps = self.generate_temporal_pattern(num_turns, temporal_pattern)
        conversation = []
        
        for timestamp in timestamps:
            importance = self.generate_importance(importance_distribution)
            turn = self.generate_turn(timestamp, importance)
            conversation.append(turn)
            
            # Maybe drift to a new topic
            self.topic_drift(topic_drift_rate)
        
        return conversation
    
    def save_to_file(self, 
                     conversation: List[SyntheticTurn],
                     filepath: str) -> None:
        """Save conversation to JSON file.
        
        Args:
            conversation: List of turns
            filepath: Output file path
        """
        data = {
            'metadata': {
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'num_turns': len(conversation),
                'generator': 'ConversationGenerator v1.0'
            },
            'turns': [turn.to_dict() for turn in conversation]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


def generate_test_datasets() -> Dict[str, List[SyntheticTurn]]:
    """Generate multiple test datasets for different scenarios.
    
    Returns:
        Dictionary mapping dataset name to conversation
    """
    generator = ConversationGenerator(seed=42)
    
    datasets = {
        'realistic_100': generator.generate_conversation(
            num_turns=100,
            temporal_pattern='burst',
            importance_distribution='pareto',
            topic_drift_rate=0.1
        ),
        'uniform_50': generator.generate_conversation(
            num_turns=50,
            temporal_pattern='uniform',
            importance_distribution='uniform',
            topic_drift_rate=0.0
        ),
        'recency_bias_75': generator.generate_conversation(
            num_turns=75,
            temporal_pattern='recency',
            importance_distribution='pareto',
            topic_drift_rate=0.15
        )
    }
    
    return datasets


if __name__ == '__main__':
    """Generate datasets and save to fixtures directory."""
    import pathlib
    
    output_dir = pathlib.Path(__file__).parent / 'fixtures'
    output_dir.mkdir(exist_ok=True)
    
    print("🔬 Generating synthetic conversation datasets...")
    
    datasets = generate_test_datasets()
    
    for name, conversation in datasets.items():
        filepath = output_dir / f'synthetic_{name}.json'
        generator = ConversationGenerator()
        generator.save_to_file(conversation, str(filepath))
        
        # Print statistics
        importances = [t.metadata['importance'] for t in conversation]
        avg_importance = sum(importances) / len(importances)
        high_importance_count = sum(1 for i in importances if i >= 0.7)
        
        print(f"\n✅ {name}:")
        print(f"   Turns: {len(conversation)}")
        print(f"   Avg importance: {avg_importance:.3f}")
        print(f"   High importance (≥0.7): {high_importance_count} ({high_importance_count/len(conversation)*100:.1f}%)")
        print(f"   Saved to: {filepath}")
    
    print("\n🎉 Dataset generation complete!")
