#!/usr/bin/env python3
"""
Memory Consolidation - Nightly summarization and pattern extraction.

Mimics human sleep consolidation:
- Creates daily meta-summaries from conversation summaries
- Extracts recurring patterns and themes
- Tracks entity mentions and importance
- Gentle memory decay for old, unimportant items

Run this as a nightly cron job or background service.
"""
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from collections import Counter
import re

from brain.rag_store import RagStore
from brain.llm import complete
from brain import config


def consolidate_daily_summaries(rag_store: RagStore, date: datetime) -> Dict[str, Any]:
    """
    Create a daily meta-summary from conversation-level summaries.
    
    Args:
        rag_store: RAG storage instance
        date: Date to consolidate (uses previous 24 hours)
        
    Returns:
        Stats about consolidation (summaries created, patterns found, etc.)
    """
    stats = {
        'date': date.strftime('%Y-%m-%d'),
        'summaries_processed': 0,
        'turns_processed': 0,
        'patterns_found': 0,
        'daily_summary_created': False,
        'entities_tracked': 0
    }
    
    # Get all conversation summaries from the last 24 hours
    end_time = date
    start_time = end_time - timedelta(hours=24)
    
    print(f"[CONSOLIDATION] Processing {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')}")
    
    # Query for conversation-level summaries
    try:
        results = rag_store.col.get(
            where={
                'type': 'summary',
                'timestamp': {
                    '$gte': start_time.isoformat(),
                    '$lt': end_time.isoformat()
                }
            },
            include=['documents', 'metadatas']
        )
        
        summaries = results.get('documents', [])
        metadatas = results.get('metadatas', [])
        
        if not summaries:
            print(f"[CONSOLIDATION] No summaries found for {date.strftime('%Y-%m-%d')}")
            return stats
        
        stats['summaries_processed'] = len(summaries)
        
        # Combine all summaries
        combined_text = "\n\n".join([f"- {s}" for s in summaries])
        
        # Create daily meta-summary using LLM
        prompt = f"""Create a concise daily summary from these conversation summaries:

{combined_text}

Focus on:
1. Main themes and topics discussed
2. Key decisions or conclusions
3. Recurring entities (people, projects, technologies)
4. Important context for future conversations

Keep it brief (3-5 sentences) but informative."""

        try:
            daily_summary = complete(
                prompt,
                model=config.OLLAMA_MODEL,
                max_tokens=300
            )
            
            # Extract entities (simple approach - find capitalized words)
            entities = extract_entities(combined_text)
            themes = extract_themes(combined_text)
            
            # Store daily summary
            scope_key = f"day:{date.strftime('%Y-%m-%d')}"
            rag_store.upsert_doc(
                daily_summary,
                type='summary',
                scope=scope_key,
                source='consolidation',
                importance=7,  # Daily summaries are fairly important
                extra_meta={
                    'summary_level': 'daily',
                    'source_summary_count': len(summaries),
                    'entities': entities[:10],  # Top 10 entities
                    'themes': themes
                }
            )
            
            stats['daily_summary_created'] = True
            stats['entities_tracked'] = len(entities)
            
            print(f"[CONSOLIDATION] Created daily summary: {len(daily_summary)} chars")
            print(f"[CONSOLIDATION] Tracked entities: {', '.join(entities[:5])}")
            
        except Exception as e:
            print(f"[CONSOLIDATION] Failed to create summary: {e}")
            return stats
        
    except Exception as e:
        print(f"[CONSOLIDATION] Error querying summaries: {e}")
        return stats
    
    # Extract and store patterns
    patterns = extract_patterns(combined_text)
    for entity, count in patterns.items():
        if count >= 3:  # Threshold: mentioned 3+ times
            rag_store.upsert_doc(
                f"User has discussed {entity} {count} times on {date.strftime('%Y-%m-%d')}. This is an active interest.",
                type='pattern',
                scope='global',
                importance=min(10, count),
                source='pattern_extraction',
                extra_meta={
                    'entity': entity,
                    'mention_count': count,
                    'extraction_date': date.isoformat()
                }
            )
            stats['patterns_found'] += 1
    
    print(f"[CONSOLIDATION] Extracted {stats['patterns_found']} patterns")
    
    return stats


def extract_entities(text: str) -> List[str]:
    """
    Extract named entities (capitalized words/phrases).
    
    Simple heuristic approach - finds technical terms, proper nouns.
    """
    # Find capitalized words (potential entities)
    # Match: FastAPI, Docker, SearxNG, Python, etc.
    entities = re.findall(r'\b[A-Z][a-zA-Z]*(?:[A-Z][a-z]+)*\b', text)
    
    # Count and return most frequent
    entity_counts = Counter(entities)
    
    # Filter out common words
    stopwords = {'I', 'The', 'A', 'An', 'In', 'On', 'At', 'To', 'For', 'And', 'Or', 'But'}
    filtered = [(e, c) for e, c in entity_counts.items() if e not in stopwords and len(e) > 2]
    
    # Return top entities by frequency
    return [e for e, _ in sorted(filtered, key=lambda x: x[1], reverse=True)]


def extract_themes(text: str) -> List[str]:
    """
    Extract high-level themes from text.
    
    Simple keyword matching approach.
    """
    theme_keywords = {
        'architecture': ['architecture', 'design', 'pattern', 'structure'],
        'implementation': ['implement', 'code', 'build', 'create', 'develop'],
        'debugging': ['debug', 'error', 'fix', 'issue', 'problem'],
        'infrastructure': ['docker', 'deploy', 'container', 'service'],
        'data': ['database', 'storage', 'query', 'retrieval'],
        'api': ['api', 'endpoint', 'request', 'response'],
        'search': ['search', 'query', 'retrieve', 'find'],
        'ai_ml': ['model', 'llm', 'embedding', 'specialist', 'rag']
    }
    
    text_lower = text.lower()
    found_themes = []
    
    for theme, keywords in theme_keywords.items():
        if any(kw in text_lower for kw in keywords):
            found_themes.append(theme)
    
    return found_themes


def consolidate_weekly_summaries(rag_store: RagStore, date: datetime) -> Dict[str, Any]:
    """
    Create a weekly meta-summary from daily summaries.
    
    Args:
        rag_store: RAG storage instance
        date: End date of the week to consolidate
        
    Returns:
        Stats about consolidation
    """
    stats = {
        'week_ending': date.strftime('%Y-%m-%d'),
        'daily_summaries_processed': 0,
        'weekly_summary_created': False,
        'key_themes': []
    }
    
    # Get daily summaries from past 7 days
    end_time = date
    start_time = end_time - timedelta(days=7)
    
    print(f"[WEEKLY] Processing week ending {end_time.strftime('%Y-%m-%d')}")
    
    try:
        results = rag_store.col.get(
            where={
                'type': 'summary',
                'summary_level': 'daily',
                'timestamp': {
                    '$gte': start_time.isoformat(),
                    '$lt': end_time.isoformat()
                }
            },
            include=['documents', 'metadatas']
        )
        
        daily_summaries = results.get('documents', [])
        metadatas = results.get('metadatas', [])
        
        if not daily_summaries:
            print(f"[WEEKLY] No daily summaries found for week ending {date.strftime('%Y-%m-%d')}")
            return stats
        
        stats['daily_summaries_processed'] = len(daily_summaries)
        
        # Combine daily summaries
        combined_text = "\n\n".join([f"Day {i+1}: {s}" for i, s in enumerate(daily_summaries)])
        
        # Create weekly meta-summary
        prompt = f"""Create a concise weekly summary from these daily summaries:

{combined_text}

Focus on:
1. Overall progress and major accomplishments
2. Recurring themes and patterns across the week
3. Key technologies, projects, or concepts explored
4. Important decisions or architectural changes

Keep it brief (4-6 sentences) but capture the week's essence."""

        try:
            weekly_summary = complete(
                prompt,
                model=config.OLLAMA_MODEL,
                max_tokens=400
            )
            
            # Extract themes and entities
            themes = extract_themes(combined_text)
            entities = extract_entities(combined_text)
            
            # Store weekly summary
            week_start = start_time.strftime('%Y-%m-%d')
            week_end = end_time.strftime('%Y-%m-%d')
            scope_key = f"week:{week_start}_to_{week_end}"
            
            rag_store.upsert_doc(
                weekly_summary,
                type='summary',
                scope=scope_key,
                source='consolidation',
                importance=8,  # Weekly summaries are quite important
                extra_meta={
                    'summary_level': 'weekly',
                    'week_start': week_start,
                    'week_end': week_end,
                    'daily_summary_count': len(daily_summaries),
                    'key_themes': themes,
                    'key_entities': entities[:10]
                }
            )
            
            stats['weekly_summary_created'] = True
            stats['key_themes'] = themes
            
            print(f"[WEEKLY] Created weekly summary: {len(weekly_summary)} chars")
            print(f"[WEEKLY] Key themes: {', '.join(themes)}")
            
        except Exception as e:
            print(f"[WEEKLY] Failed to create summary: {e}")
            return stats
            
    except Exception as e:
        print(f"[WEEKLY] Error querying daily summaries: {e}")
        return stats
    
    return stats


def extract_patterns(text: str) -> Dict[str, int]:
    """
    Extract recurring patterns (frequent entities).
    
    Returns dict of entity -> mention count
    """
    entities = extract_entities(text)
    return dict(Counter(entities).most_common(20))


def prune_old_memories(rag_store: RagStore, days: int = 90) -> int:
    """
    Gentle memory decay - reduce importance of old, low-priority memories.
    
    Args:
        rag_store: RAG storage instance
        days: Age threshold in days
        
    Returns:
        Number of memories pruned
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    try:
        # Find old, low-importance memories
        results = rag_store.col.get(
            where={
                'type': 'memory',
                'importance': {'$lt': 4},
                'timestamp': {'$lt': cutoff.isoformat()}
            },
            include=['metadatas', 'ids']
        )
        
        ids = results.get('ids', [])
        metadatas = results.get('metadatas', [])
        
        pruned = 0
        for mem_id, meta in zip(ids, metadatas):
            current_importance = meta.get('importance', 5)
            new_importance = max(1, current_importance - 1)
            
            # Update importance (decay)
            meta['importance'] = new_importance
            rag_store.col.update(
                ids=[mem_id],
                metadatas=[meta]
            )
            pruned += 1
        
        print(f"[CONSOLIDATION] Decayed {pruned} old memories")
        return pruned
        
    except Exception as e:
        print(f"[CONSOLIDATION] Error pruning memories: {e}")
        return 0


if __name__ == '__main__':
    print("[CONSOLIDATION] Starting nightly consolidation")
    
    # Initialize RAG store
    rag = RagStore()
    
    # Run consolidation for yesterday (completed day)
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    
    stats = consolidate_daily_summaries(rag, yesterday)
    
    print(f"""
[CONSOLIDATION] Daily Summary Completed
  Date: {stats['date']}
  Summaries processed: {stats['summaries_processed']}
  Daily summary created: {stats['daily_summary_created']}
  Patterns found: {stats['patterns_found']}
  Entities tracked: {stats['entities_tracked']}
""")
    
    # Run weekly consolidation and pruning (on Sundays)
    if yesterday.weekday() == 6:  # Sunday
        print("[CONSOLIDATION] Running weekly consolidation")
        
        # Create weekly summary
        weekly_stats = consolidate_weekly_summaries(rag, yesterday)
        print(f"""
[CONSOLIDATION] Weekly Summary Completed
  Week ending: {weekly_stats['week_ending']}
  Daily summaries processed: {weekly_stats['daily_summaries_processed']}
  Weekly summary created: {weekly_stats['weekly_summary_created']}
  Key themes: {', '.join(weekly_stats['key_themes'])}
""")
        
        # Prune old memories
        print("[CONSOLIDATION] Running weekly memory pruning")
        pruned = prune_old_memories(rag, days=90)
        print(f"[CONSOLIDATION] Pruned {pruned} old memories")
    
    print("[CONSOLIDATION] Done")
