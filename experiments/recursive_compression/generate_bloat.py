"""
Generate intentionally bloated prompts with tons of tool results.
This simulates worst-case scenarios for context window pressure.
"""

import json
import random
from datetime import datetime, timedelta


def generate_file_tree(depth: int = 4, breadth: int = 8, max_items: int = 500) -> str:
    """Generate a massive file tree tool result (capped to avoid explosion)."""
    lines = ["Tool Result: list_directory\n", "=" * 60 + "\n"]
    item_count = [0]  # Use list for mutation in closure
    
    def _gen_tree(prefix: str, current_depth: int):
        if current_depth >= depth or item_count[0] >= max_items:
            return
        for i in range(breadth):
            if item_count[0] >= max_items:
                break
            is_dir = random.random() > 0.3
            name = f"{'folder' if is_dir else 'file'}_{current_depth}_{i}"
            ext = random.choice(['.py', '.ts', '.md', '.json', '.yaml', '']) if not is_dir else ''
            lines.append(f"{prefix}{'📁' if is_dir else '📄'} {name}{ext}\n")
            item_count[0] += 1
            if is_dir and current_depth < depth - 1:
                _gen_tree(prefix + "  ", current_depth + 1)
    
    _gen_tree("", 0)
    return "".join(lines)


def generate_search_results(num_results: int = 50) -> str:
    """Generate verbose search results with full file contents."""
    results = ["Tool Result: semantic_search\n", "=" * 60 + "\n"]
    results.append(f"Query: 'how does the authentication system work'\n")
    results.append(f"Found {num_results} results:\n\n")
    
    for i in range(num_results):
        score = random.uniform(0.6, 0.99)
        file_path = f"src/{'auth' if random.random() > 0.5 else 'users'}/{'module' if random.random() > 0.5 else 'service'}_{i}.py"
        
        # Generate fake code content
        code = f'''
class AuthHandler_{i}:
    """Handles authentication for module {i}.
    
    This module provides authentication services including:
    - Token validation and refresh
    - Session management  
    - Permission checking
    - Rate limiting
    
    Note: This is part of the larger auth system that spans
    multiple modules and services. See also: auth_service_{i+1}.py
    """
    
    def __init__(self, config: dict, db: Database):
        self.config = config
        self.db = db
        self.cache = Cache(ttl=config.get('cache_ttl', 3600))
        self.rate_limiter = RateLimiter(max_requests=100)
        
    async def validate_token(self, token: str) -> bool:
        """Validate JWT token against stored secrets."""
        if not token:
            return False
        try:
            payload = jwt.decode(token, self.config['secret'])
            return payload.get('exp', 0) > time.time()
        except jwt.InvalidTokenError:
            return False
            
    async def refresh_session(self, session_id: str) -> Session:
        """Refresh an existing session, extending its TTL."""
        session = await self.db.get_session(session_id)
        if session and session.is_valid():
            session.extend(hours=24)
            await self.db.save_session(session)
        return session
'''
        
        results.append(f"--- Result {i+1} (score: {score:.3f}) ---\n")
        results.append(f"File: {file_path}\n")
        results.append(f"Lines: {i*50}-{i*50+45}\n")
        results.append(f"```python\n{code}\n```\n\n")
    
    return "".join(results)


def generate_git_diff(num_files: int = 30) -> str:
    """Generate a massive git diff with lots of changes."""
    diff = ["Tool Result: get_changed_files\n", "=" * 60 + "\n"]
    diff.append(f"Showing changes in {num_files} files:\n\n")
    
    for i in range(num_files):
        additions = random.randint(10, 100)
        deletions = random.randint(5, 50)
        file_path = f"src/components/{'Feature' if random.random() > 0.5 else 'Component'}_{i}.tsx"
        
        diff.append(f"diff --git a/{file_path} b/{file_path}\n")
        diff.append(f"--- a/{file_path}\n")
        diff.append(f"+++ b/{file_path}\n")
        diff.append(f"@@ -{i*10},{deletions} +{i*10},{additions} @@\n")
        
        # Generate fake diff content
        for j in range(min(additions, 20)):
            if random.random() > 0.5:
                diff.append(f"+  const value_{j} = useMemo(() => computeExpensive({j}), [deps]);\n")
            else:
                diff.append(f"-  const oldValue_{j} = legacy_compute({j});\n")
                diff.append(f"+  const value_{j} = modern_compute({j});\n")
        
        diff.append("\n")
    
    return "".join(diff)


def generate_memory_dump(num_memories: int = 100) -> str:
    """Generate lots of retrieved memories."""
    memories = ["Tool Result: search_memories\n", "=" * 60 + "\n"]
    memories.append(f"Retrieved {num_memories} relevant memories:\n\n")
    
    topics = [
        "discussed project architecture",
        "debugged authentication issue",
        "reviewed pull request",
        "planned feature roadmap",
        "analyzed performance metrics",
        "configured deployment pipeline",
        "resolved merge conflict",
        "updated documentation",
        "refactored legacy code",
        "implemented new API endpoint"
    ]
    
    for i in range(num_memories):
        days_ago = random.randint(1, 90)
        timestamp = (datetime.now() - timedelta(days=days_ago)).isoformat()
        topic = random.choice(topics)
        importance = random.uniform(0.3, 0.95)
        
        content = f"""Memory {i+1}: {topic}
Timestamp: {timestamp}
Importance: {importance:.2f}
Context: During our session on {timestamp[:10]}, we {topic}. 
The key points were:
- Point A about {topic.split()[1]} configuration
- Point B regarding {topic.split()[-1]} optimization  
- Point C concerning integration with external services
- Additional notes about edge cases and error handling
- Follow-up items that were identified for future work

This relates to the broader context of the project's evolution
and the ongoing effort to improve code quality and maintainability.
"""
        memories.append(content + "\n" + "-" * 40 + "\n\n")
    
    return "".join(memories)


def generate_api_response(num_items: int = 200) -> str:
    """Generate a massive API response with nested data."""
    response = ["Tool Result: fetch_api_data\n", "=" * 60 + "\n"]
    response.append("Response from /api/v1/comprehensive-data:\n\n")
    
    data = {
        "status": "success",
        "total_count": num_items,
        "page": 1,
        "per_page": num_items,
        "items": []
    }
    
    for i in range(num_items):
        item = {
            "id": f"item_{i:05d}",
            "name": f"Entity {i}",
            "created_at": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": random.choice(["active", "pending", "archived"]),
            "metadata": {
                "tags": [f"tag_{j}" for j in range(random.randint(1, 5))],
                "priority": random.randint(1, 10),
                "category": random.choice(["A", "B", "C", "D"]),
                "attributes": {
                    f"attr_{k}": f"value_{k}_{i}" for k in range(5)
                }
            },
            "relationships": {
                "parent_id": f"item_{max(0, i-1):05d}" if i > 0 else None,
                "children_ids": [f"item_{i+j:05d}" for j in range(1, random.randint(2, 5))]
            }
        }
        data["items"].append(item)
    
    response.append(json.dumps(data, indent=2))
    return "".join(response)


def generate_bloated_prompt(
    include_file_tree: bool = True,
    include_search: bool = True,
    include_diff: bool = True,
    include_memories: bool = True,
    include_api: bool = True,
    scale: float = 1.0
) -> str:
    """Generate a massively bloated prompt combining all tool results."""
    
    sections = []
    
    sections.append("""# User Request
    
Please analyze the codebase and help me understand how the authentication 
system works, what recent changes have been made, and how it relates to 
our previous discussions about security improvements.

# Tool Results

The following tool results have been gathered to help answer your question:

""")
    
    if include_file_tree:
        sections.append(generate_file_tree(
            depth=int(4 * scale), 
            breadth=int(8 * scale)
        ))
        sections.append("\n\n")
    
    if include_search:
        sections.append(generate_search_results(num_results=int(30 * scale)))
        sections.append("\n\n")
    
    if include_diff:
        sections.append(generate_git_diff(num_files=int(20 * scale)))
        sections.append("\n\n")
    
    if include_memories:
        sections.append(generate_memory_dump(num_memories=int(50 * scale)))
        sections.append("\n\n")
    
    if include_api:
        sections.append(generate_api_response(num_items=int(100 * scale)))
    
    return "".join(sections)


def count_tokens_approx(text: str) -> int:
    """Rough token count (words * 1.3 is a decent approximation)."""
    return int(len(text.split()) * 1.3)


if __name__ == "__main__":
    from pathlib import Path
    
    # Get script directory for reliable file paths
    script_dir = Path(__file__).parent
    
    # Generate at different scales
    for scale in [0.5, 1.0, 2.0]:
        prompt = generate_bloated_prompt(scale=scale)
        tokens = count_tokens_approx(prompt)
        chars = len(prompt)
        
        print(f"\nScale {scale}x:")
        print(f"  Characters: {chars:,}")
        print(f"  Approx tokens: {tokens:,}")
        print(f"  Lines: {prompt.count(chr(10)):,}")
        
        # Save sample (relative to script location)
        output_file = script_dir / f"bloated_{scale}x.txt"
        with open(output_file, "w") as f:
            f.write(prompt)
        print(f"  Saved to: {output_file.name}")
