"""Contextual Router - Route requests to optimal processing paths.

Research foundation: v2.3.0 contextual malleability framework.
"Context-matching (r=0.924) beats universal approaches (r=0.726)"

The router analyzes request context to select:
- Optimal model (qwen2.5-coder vs deepseek-r1)
- Format (FIM vs chat)
- Processing path (direct Ollama vs full brain)
- Cache strategy
"""
# @ai-indexable: core-functionality
# @ai-purpose: Intelligent request routing based on context analysis
# @ai-dependencies: brain.config
# @ai-related: brain/app.py, ada-mcp/tools/complete_code.py

import hashlib
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any


class RequestType(Enum):
    """Types of requests the router can classify."""
    CODE_COMPLETION = "code_completion"
    CHAT = "chat"
    REASONING = "reasoning"
    QUICK_QUERY = "quick_query"
    UNKNOWN = "unknown"


@dataclass
class RequestContext:
    """Context information for routing decisions."""
    message: str
    has_code_before: bool = False
    has_code_after: bool = False
    code_before: Optional[str] = None
    code_after: Optional[str] = None
    language: Optional[str] = None
    is_completion: bool = False
    requires_reasoning: bool = False
    is_simple_query: bool = False
    is_simple: bool = False
    unknown_flag: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResponsePath:
    """Configuration for processing a request."""
    model: str
    format: str  # "fim" or "chat"
    use_rag: bool = False
    use_specialists: bool = False
    use_cache: bool = False
    cache_ttl: int = 0  # seconds
    stream: bool = True
    enable_thinking: bool = False
    timeout: int = 30
    temperature: float = 0.7
    top_p: float = 0.95
    max_tokens: int = 150
    routing_time_ms: float = 0.0


class ContextualRouter:
    """Route requests to optimal paths based on context analysis.
    
    Implements research-validated context-matching approach:
    - Analyzes request context (code, language, complexity)
    - Classifies request type
    - Routes to optimal model + format + processing path
    - Manages caching strategy
    
    Performance target: <10ms routing time
    """

    def __init__(self):
        """Initialize router with patterns and cache."""
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'total': 0,
        }
        
        # Language detection patterns (order matters - most specific first!)
        self.language_patterns = {
            'python': [r'\bdef\b', r'\bclass\b', r'\bimport\b', r':\s*$'],
            'rust': [r'\bfn\s+\w+\(', r'\blet\s+mut\b', r'\bimpl\b', r'::'],  # More specific Rust patterns
            'javascript': [r'\bfunction\b', r'\bconst\b', r'\blet\b', r'=>'],
            'typescript': [r'\binterface\b', r'\btype\b', r':\s*\w+(\[\])?'],
            'go': [r'\bfunc\b', r':=', r'\bpackage\b'],
        }
        
        # Reasoning keywords
        self.reasoning_keywords = [
            'analyze', 'compare', 'evaluate', 'trade-off', 'trade-offs',
            'pros and cons', 'explain why', 'justify', 'reason about',
            'consider', 'weigh', 'assess',
        ]
        
        # Simple query patterns
        self.simple_patterns = [
            r'^what is \d+',  # "what is 2+2"
            r'^how many',  # "how many bytes"
            r"^what'?s? the",  # "what's the capital"
            r'^\d+\s*[\+\-\*/]\s*\d+',  # "2+2"
        ]

    def classify(self, context: RequestContext) -> RequestType:
        """Classify request type based on context.
        
        Args:
            context: Request context with message and metadata
            
        Returns:
            RequestType enum indicating optimal processing path
        """
        start_time = time.time()
        
        # Explicit flags take precedence
        if context.is_completion:
            return RequestType.CODE_COMPLETION
        
        if context.requires_reasoning:
            return RequestType.REASONING
        
        if context.is_simple_query or self.is_simple_query(context):
            return RequestType.QUICK_QUERY
        
        # Detect code completion from context
        if context.has_code_before or context.code_before:
            if not context.message or len(context.message.strip()) < 10:
                return RequestType.CODE_COMPLETION
        
        # Detect reasoning from message
        if self.requires_reasoning(context):
            return RequestType.REASONING
        
        # Default to chat
        return RequestType.CHAT

    def route(self, request_type: RequestType, context: RequestContext) -> ResponsePath:
        """Route request to optimal processing path.
        
        Args:
            request_type: Classified request type
            context: Request context
            
        Returns:
            ResponsePath with model, format, and configuration
        """
        start_time = time.time()
        
        if request_type == RequestType.CODE_COMPLETION:
            path = self._route_code_completion(context)
        elif request_type == RequestType.REASONING:
            path = self._route_reasoning(context)
        elif request_type == RequestType.QUICK_QUERY:
            path = self._route_quick_query(context)
        elif request_type == RequestType.CHAT:
            path = self._route_chat(context)
        else:
            # Fallback to chat for unknown types
            path = self._route_chat(context)
        
        # Add routing time metric
        path.routing_time_ms = (time.time() - start_time) * 1000
        
        return path

    def _route_code_completion(self, context: RequestContext) -> ResponsePath:
        """Route code completion to qwen2.5-coder with FIM format."""
        # Detect language if not provided
        if not context.language:
            context.language = self.detect_language(context)
        
        # Simple completions use fewer tokens
        max_tokens = 50 if context.is_simple else 150
        
        return ResponsePath(
            model="qwen2.5-coder:7b",
            format="fim",
            use_rag=False,
            use_specialists=False,
            use_cache=True,
            cache_ttl=3600,  # 1 hour
            stream=True,
            temperature=0.2,  # Low temp for focused completions
            top_p=0.95,
            max_tokens=max_tokens,
        )

    def _route_chat(self, context: RequestContext) -> ResponsePath:
        """Route chat to deepseek-r1 with full RAG."""
        return ResponsePath(
            model="deepseek-r1:latest",
            format="chat",
            use_rag=True,
            use_specialists=True,
            use_cache=False,
            stream=True,
            temperature=0.7,
            top_p=0.95,
            max_tokens=2048,
            timeout=30,
        )

    def _route_reasoning(self, context: RequestContext) -> ResponsePath:
        """Route reasoning to deepseek-r1 with thinking enabled."""
        return ResponsePath(
            model="deepseek-r1:latest",
            format="chat",
            use_rag=True,
            use_specialists=True,
            use_cache=False,
            stream=True,
            enable_thinking=True,
            temperature=0.7,
            top_p=0.95,
            max_tokens=4096,
            timeout=60,  # Longer timeout for complex reasoning
        )

    def _route_quick_query(self, context: RequestContext) -> ResponsePath:
        """Route simple queries with caching."""
        return ResponsePath(
            model="deepseek-r1:latest",
            format="chat",
            use_rag=False,  # Don't need full context for simple queries
            use_specialists=False,
            use_cache=True,
            cache_ttl=86400,  # 24 hours
            stream=True,
            temperature=0.3,
            top_p=0.9,
            max_tokens=512,
            timeout=15,
        )

    def has_code_context(self, context: RequestContext) -> bool:
        """Check if context includes code."""
        if context.has_code_before or context.has_code_after:
            return True
        
        if context.code_before or context.code_after:
            return True
        
        # Check message for code-like content
        message = context.message.lower()
        code_indicators = ['def ', 'function ', 'class ', '{', '}', 'import ', 'fn ']
        return any(indicator in message for indicator in code_indicators)

    def detect_language(self, context: RequestContext) -> Optional[str]:
        """Detect programming language from context.
        
        Args:
            context: Request context with code
            
        Returns:
            Language name or None if not detected
        """
        # Check explicit language field
        if context.language:
            return context.language
        
        # Analyze code content
        code = context.code_before or context.message or ""
        
        # Try each language pattern
        for language, patterns in self.language_patterns.items():
            for pattern in patterns:
                if re.search(pattern, code):
                    return language
        
        return None

    def requires_reasoning(self, context: RequestContext) -> bool:
        """Check if request requires complex reasoning.
        
        Args:
            context: Request context
            
        Returns:
            True if reasoning indicators detected
        """
        if context.requires_reasoning:
            return True
        
        message_lower = context.message.lower()
        return any(keyword in message_lower for keyword in self.reasoning_keywords)

    def is_simple_query(self, context: RequestContext) -> bool:
        """Check if request is a simple factual query.
        
        Args:
            context: Request context
            
        Returns:
            True if simple query pattern detected
        """
        if context.is_simple_query:
            return True
        
        message = context.message.lower().strip()
        
        # Check simple patterns
        for pattern in self.simple_patterns:
            if re.match(pattern, message):
                return True
        
        # Simple if very short and starts with common question words
        if len(message.split()) <= 6:
            if message.startswith(('what', 'how', 'when', 'where', 'who')):
                return True
        
        return False

    def generate_cache_key(self, request_type: RequestType, context: RequestContext) -> str:
        """Generate cache key for request.
        
        Args:
            request_type: Type of request
            context: Request context
            
        Returns:
            Hash-based cache key
        """
        if request_type == RequestType.CODE_COMPLETION:
            # Include code context and language
            content = f"{context.code_before}|{context.language}"
        elif request_type == RequestType.QUICK_QUERY:
            # Normalize the question
            content = context.message.lower().strip()
            # Remove punctuation variations
            content = re.sub(r'[?!.,;]+$', '', content)
            # Normalize whitespace
            content = re.sub(r'\s+', ' ', content)
        else:
            # For chat/reasoning, include full message
            content = context.message
        
        # Generate hash
        return hashlib.sha256(content.encode()).hexdigest()[:16]
