"""Gradient Compression Test: Real System Logs → Semantic Understanding

This test takes REAL logs (3.5MB, 27K lines) and compresses them using
importance-weighted gradient compression.

The claim: We can compress 100:1 and KEEP THE MEANING.

Weights (from research v2.2):
- Surprise/novelty: 60%
- Temporal decay: 10%
- Relevance: 20%
- Habituation: 10%
"""

import re
import json
import hashlib
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
import math


@dataclass
class LogLine:
    """A single parsed log line."""
    timestamp: datetime
    hostname: str
    service: str
    message: str
    raw: str
    
    # Computed importance signals
    surprise: float = 0.0
    decay: float = 0.0
    relevance: float = 0.0
    habituation: float = 0.0
    importance: float = 0.0
    detail_level: str = "FULL"  # FULL, SUMMARY, DROP


@dataclass 
class SemanticCluster:
    """A cluster of related log lines with semantic meaning."""
    pattern: str
    service: str
    count: int
    first_seen: datetime
    last_seen: datetime
    example_messages: list = field(default_factory=list)
    importance: float = 0.0
    semantic_summary: str = ""


class GradientLogCompressor:
    """Compress logs using importance-weighted gradient compression."""
    
    # Research-validated weights from v2.2
    WEIGHTS = {
        'surprise': 0.60,
        'decay': 0.10,
        'relevance': 0.20,
        'habituation': 0.10
    }
    
    # Detail level thresholds
    THRESHOLDS = {
        'FULL': 0.75,     # Keep full detail
        'SUMMARY': 0.40,  # Summarize
        'DROP': 0.0       # Can be dropped
    }
    
    def __init__(self):
        self.pattern_counts = Counter()
        self.service_counts = Counter()
        self.message_hashes = set()
        self.clusters = {}
        
    def parse_journalctl_line(self, line: str) -> Optional[LogLine]:
        """Parse a journalctl log line."""
        # Format: Dec 22 00:00:03 crane systemd[1]: message
        pattern = r'^(\w{3}\s+\d+\s+\d+:\d+:\d+)\s+(\w+)\s+(\S+?)(?:\[\d+\])?:\s+(.*)$'
        match = re.match(pattern, line.strip())
        
        if not match:
            return None
            
        timestamp_str, hostname, service, message = match.groups()
        
        # Parse timestamp (assume current year)
        try:
            timestamp = datetime.strptime(f"2025 {timestamp_str}", "%Y %b %d %H:%M:%S")
        except ValueError:
            return None
            
        return LogLine(
            timestamp=timestamp,
            hostname=hostname,
            service=service,
            message=message,
            raw=line
        )
    
    def calculate_surprise(self, line: LogLine) -> float:
        """Calculate surprise/novelty signal."""
        # Hash the semantic pattern (service + message type)
        msg_pattern = re.sub(r'[0-9a-f]{8,}', '<ID>', line.message)  # Normalize IDs
        msg_pattern = re.sub(r'\d+', '<N>', msg_pattern)  # Normalize numbers
        pattern_key = f"{line.service}:{msg_pattern[:50]}"
        
        # First occurrence = maximum surprise
        if pattern_key not in self.pattern_counts:
            self.pattern_counts[pattern_key] = 0
            surprise = 1.0
        else:
            # Surprise decreases with repetition (1/log(count+1))
            count = self.pattern_counts[pattern_key]
            surprise = 1.0 / math.log2(count + 2)
        
        self.pattern_counts[pattern_key] += 1
        return surprise
    
    def calculate_decay(self, line: LogLine, now: datetime) -> float:
        """Calculate temporal decay signal."""
        age_seconds = (now - line.timestamp).total_seconds()
        # Half-life of 1 hour
        half_life = 3600
        decay = math.exp(-0.693 * age_seconds / half_life)
        return decay
    
    def calculate_relevance(self, line: LogLine, query: str = "") -> float:
        """Calculate relevance to current query/context."""
        if not query:
            # Default relevance based on service criticality
            critical_services = {'kernel', 'systemd', 'amdgpu', 'ollama'}
            if line.service in critical_services:
                return 0.8
            elif 'error' in line.message.lower() or 'warning' in line.message.lower():
                return 0.9
            elif 'failed' in line.message.lower():
                return 1.0
            return 0.3
        
        # Query-based relevance
        query_lower = query.lower()
        if query_lower in line.message.lower() or query_lower in line.service.lower():
            return 1.0
        return 0.1
    
    def calculate_habituation(self, line: LogLine) -> float:
        """Calculate habituation (repeated pattern penalty)."""
        msg_hash = hashlib.md5(line.message.encode()).hexdigest()[:16]
        
        if msg_hash in self.message_hashes:
            return 0.1  # Low importance for exact duplicates
        
        self.message_hashes.add(msg_hash)
        return 1.0
    
    def calculate_importance(self, line: LogLine, now: datetime, query: str = "") -> float:
        """Calculate overall importance using research-validated weights."""
        line.surprise = self.calculate_surprise(line)
        line.decay = self.calculate_decay(line, now)
        line.relevance = self.calculate_relevance(line, query)
        line.habituation = self.calculate_habituation(line)
        
        importance = (
            self.WEIGHTS['surprise'] * line.surprise +
            self.WEIGHTS['decay'] * line.decay +
            self.WEIGHTS['relevance'] * line.relevance +
            self.WEIGHTS['habituation'] * line.habituation
        )
        
        line.importance = importance
        
        # Assign detail level
        if importance >= self.THRESHOLDS['FULL']:
            line.detail_level = "FULL"
        elif importance >= self.THRESHOLDS['SUMMARY']:
            line.detail_level = "SUMMARY"
        else:
            line.detail_level = "DROP"
            
        return importance
    
    def cluster_by_pattern(self, lines: list[LogLine]) -> dict[str, SemanticCluster]:
        """Cluster log lines by semantic pattern."""
        clusters = defaultdict(lambda: {
            'count': 0,
            'first_seen': None,
            'last_seen': None,
            'examples': [],
            'importance_sum': 0.0,
            'service': None
        })
        
        for line in lines:
            # Create semantic pattern
            msg_pattern = re.sub(r'[0-9a-f]{8,}', '<ID>', line.message)
            msg_pattern = re.sub(r'\d+', '<N>', msg_pattern)
            pattern_key = f"{line.service}:{msg_pattern[:80]}"
            
            cluster = clusters[pattern_key]
            cluster['count'] += 1
            cluster['service'] = line.service
            cluster['importance_sum'] += line.importance
            
            if cluster['first_seen'] is None:
                cluster['first_seen'] = line.timestamp
            cluster['last_seen'] = line.timestamp
            
            if len(cluster['examples']) < 3:
                cluster['examples'].append(line.message[:100])
        
        # Convert to SemanticCluster objects
        result = {}
        for pattern, data in clusters.items():
            result[pattern] = SemanticCluster(
                pattern=pattern,
                service=data['service'],
                count=data['count'],
                first_seen=data['first_seen'],
                last_seen=data['last_seen'],
                example_messages=data['examples'],
                importance=data['importance_sum'] / data['count']
            )
        
        return result
    
    def compress(self, log_text: str, query: str = "") -> dict:
        """Compress logs using gradient compression."""
        lines = log_text.strip().split('\n')
        total_lines = len(lines)
        total_bytes = len(log_text)
        
        # Parse all lines
        parsed_lines = []
        parse_failures = 0
        
        for line in lines:
            parsed = self.parse_journalctl_line(line)
            if parsed:
                parsed_lines.append(parsed)
            else:
                parse_failures += 1
        
        if not parsed_lines:
            return {'error': 'No lines could be parsed'}
        
        # Calculate importance for all lines
        now = datetime.now()
        for line in parsed_lines:
            self.calculate_importance(line, now, query)
        
        # Cluster by pattern
        clusters = self.cluster_by_pattern(parsed_lines)
        
        # Sort clusters by importance
        sorted_clusters = sorted(
            clusters.values(),
            key=lambda c: c.importance,
            reverse=True
        )
        
        # Build compressed output
        full_lines = [l for l in parsed_lines if l.detail_level == "FULL"]
        summary_lines = [l for l in parsed_lines if l.detail_level == "SUMMARY"]
        dropped_lines = [l for l in parsed_lines if l.detail_level == "DROP"]
        
        # Generate semantic summary
        semantic_summary = self._generate_semantic_summary(sorted_clusters, parsed_lines)
        
        # Calculate compression ratio
        compressed_size = len(semantic_summary)
        compression_ratio = total_bytes / compressed_size if compressed_size > 0 else 0
        
        return {
            'input': {
                'total_lines': total_lines,
                'total_bytes': total_bytes,
                'parsed_lines': len(parsed_lines),
                'parse_failures': parse_failures
            },
            'compression': {
                'full_lines': len(full_lines),
                'summary_lines': len(summary_lines),
                'dropped_lines': len(dropped_lines),
                'unique_patterns': len(clusters),
                'compression_ratio': f"{compression_ratio:.1f}:1",
                'compressed_bytes': compressed_size
            },
            'top_clusters': [
                {
                    'pattern': c.pattern[:60],
                    'service': c.service,
                    'count': c.count,
                    'importance': round(c.importance, 3),
                    'example': c.example_messages[0][:80] if c.example_messages else ""
                }
                for c in sorted_clusters[:10]
            ],
            'semantic_summary': semantic_summary,
            'services_seen': dict(self.service_counts.most_common(10))
        }
    
    def _generate_semantic_summary(self, clusters: list[SemanticCluster], lines: list[LogLine]) -> str:
        """Generate a human-readable semantic summary."""
        summary_parts = []
        
        # Time range
        if lines:
            start = min(l.timestamp for l in lines)
            end = max(l.timestamp for l in lines)
            summary_parts.append(f"## Log Analysis: {start.strftime('%Y-%m-%d %H:%M')} to {end.strftime('%H:%M')}")
            summary_parts.append("")
        
        # Service summary
        service_counts = Counter(l.service for l in lines)
        summary_parts.append("### Services Active")
        for service, count in service_counts.most_common(10):
            summary_parts.append(f"- **{service}**: {count} events")
        summary_parts.append("")
        
        # High importance events
        high_importance = [l for l in lines if l.importance >= 0.75]
        if high_importance:
            summary_parts.append("### High Importance Events")
            seen_patterns = set()
            for line in sorted(high_importance, key=lambda l: l.importance, reverse=True)[:10]:
                pattern = f"{line.service}:{line.message[:30]}"
                if pattern not in seen_patterns:
                    seen_patterns.add(pattern)
                    summary_parts.append(f"- [{line.service}] {line.message[:100]}")
            summary_parts.append("")
        
        # Errors and warnings
        errors = [l for l in lines if 'error' in l.message.lower() or 'failed' in l.message.lower()]
        warnings = [l for l in lines if 'warning' in l.message.lower()]
        
        if errors:
            summary_parts.append(f"### Errors ({len(errors)} total)")
            seen = set()
            for line in errors[:5]:
                if line.message[:50] not in seen:
                    seen.add(line.message[:50])
                    summary_parts.append(f"- [{line.service}] {line.message[:100]}")
            summary_parts.append("")
        
        if warnings:
            summary_parts.append(f"### Warnings ({len(warnings)} total)")
            seen = set()
            for line in warnings[:5]:
                if line.message[:50] not in seen:
                    seen.add(line.message[:50])
                    summary_parts.append(f"- [{line.service}] {line.message[:100]}")
            summary_parts.append("")
        
        # Pattern analysis
        summary_parts.append("### Repeated Patterns (potential issues)")
        for cluster in clusters[:5]:
            if cluster.count > 10:
                summary_parts.append(f"- **{cluster.service}**: {cluster.count}x - {cluster.example_messages[0][:60] if cluster.example_messages else 'N/A'}...")
        summary_parts.append("")
        
        # Key semantic insights
        summary_parts.append("### Semantic Insights")
        
        # Detect container restart loop
        container_events = [l for l in lines if 'containerd' in l.service or 'docker' in l.service]
        if len(container_events) > 100:
            summary_parts.append(f"- ⚠️ **Container churn detected**: {len(container_events)} container events (possible restart loop)")
        
        # Detect GPU issues
        gpu_events = [l for l in lines if 'amdgpu' in l.service or 'gpu' in l.message.lower()]
        if gpu_events:
            summary_parts.append(f"- 🎮 **GPU activity**: {len(gpu_events)} events")
        
        # Detect ollama activity
        ollama_events = [l for l in lines if 'ollama' in l.service]
        if ollama_events:
            summary_parts.append(f"- 🤖 **Ollama (LLM)**: {len(ollama_events)} events")
        
        return '\n'.join(summary_parts)


def test_gradient_compression():
    """Test gradient compression on real system logs."""
    print("🔬 GRADIENT COMPRESSION TEST")
    print("=" * 60)
    
    # Load test logs
    log_path = Path("/tmp/test_logs.txt")
    if not log_path.exists():
        print("❌ No test logs found. Run: journalctl --since '2025-12-22' > /tmp/test_logs.txt")
        return
    
    log_text = log_path.read_text()
    print(f"📂 Input: {len(log_text):,} bytes, {len(log_text.splitlines()):,} lines")
    
    # Compress
    compressor = GradientLogCompressor()
    result = compressor.compress(log_text)
    
    print(f"\n📊 COMPRESSION RESULTS")
    print("-" * 40)
    print(f"Input lines:     {result['input']['total_lines']:,}")
    print(f"Input bytes:     {result['input']['total_bytes']:,}")
    print(f"Parsed lines:    {result['input']['parsed_lines']:,}")
    print(f"Parse failures:  {result['input']['parse_failures']:,}")
    
    print(f"\n📦 GRADIENT DISTRIBUTION")
    print("-" * 40)
    print(f"FULL (≥0.75):    {result['compression']['full_lines']:,} lines")
    print(f"SUMMARY (≥0.40): {result['compression']['summary_lines']:,} lines")
    print(f"DROP (<0.40):    {result['compression']['dropped_lines']:,} lines")
    print(f"Unique patterns: {result['compression']['unique_patterns']:,}")
    print(f"Compression:     {result['compression']['compression_ratio']}")
    print(f"Output bytes:    {result['compression']['compressed_bytes']:,}")
    
    print(f"\n🔝 TOP CLUSTERS BY IMPORTANCE")
    print("-" * 40)
    for i, cluster in enumerate(result['top_clusters'][:5], 1):
        print(f"{i}. [{cluster['service']}] importance={cluster['importance']:.3f}, count={cluster['count']}")
        print(f"   {cluster['example'][:70]}...")
    
    print(f"\n📝 SEMANTIC SUMMARY")
    print("=" * 60)
    print(result['semantic_summary'])
    
    # Save results
    output_path = Path("/tmp/gradient_compression_result.json")
    with open(output_path, 'w') as f:
        # Can't serialize datetime directly
        result_serializable = {
            k: v for k, v in result.items() 
            if k != 'semantic_summary'
        }
        result_serializable['semantic_summary_preview'] = result['semantic_summary'][:500]
        json.dump(result_serializable, f, indent=2, default=str)
    
    print(f"\n✅ Results saved to {output_path}")
    
    return result


if __name__ == "__main__":
    test_gradient_compression()
