#!/usr/bin/env python3
"""
QWEN STRESS TEST - How far can we push her?
Pure empirical boundary hunting
"""

import requests
import time
import json

def stress_test(prompt, test_name, max_wait=120):
    print(f"\n🧪 {test_name}")
    print(f"📝 Prompt: {len(prompt)} chars, {len(prompt.split())} words")
    
    start = time.time()
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={'model': 'qwen2.5-coder:7b', 'prompt': prompt, 'stream': False},
            timeout=max_wait
        )
        
        end = time.time()
        result = response.json()
        tokens = len(result.get('response', '').split())
        
        print(f"✅ {tokens} tokens in {end-start:.1f}s")
        return True, tokens, end-start
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False, 0, time.time() - start

# Base test (we know this works)
base_prompt = """You have access to VS Code tools via the extension. When you need to read files, search code, or analyze the workspace, request tools using this syntax:

TOOL_REQUEST[tool_name:{"param":"value"}]

Available tools:
- ada_read_file: Read file contents
- ada_search: Search for text patterns  
- ada_list_files: List files in directory

User request: hello ada"""

# 2x the complexity
double_prompt = base_prompt + """

Additional context:
You are working with a TypeScript/Node.js project that includes:
- React frontend components
- Express.js backend APIs  
- Database models and migrations
- Authentication and authorization layers
- Testing suites with Jest and Cypress
- Build pipelines with Webpack and Docker

When analyzing code, consider:
1. Type safety and TypeScript best practices
2. React component lifecycle and hooks usage
3. API endpoint security and validation
4. Database query optimization
5. Test coverage and edge cases
6. Performance implications and bundle size
7. Accessibility compliance (WCAG guidelines)
8. Security vulnerabilities (OWASP top 10)

Always provide specific, actionable recommendations with code examples when possible.

User request: hello ada, please help me understand this codebase"""

# 5x complexity - massive context
mega_prompt = double_prompt + """

COMPREHENSIVE PROJECT CONTEXT:

ARCHITECTURE PATTERNS:
- Clean Architecture with dependency injection
- Repository pattern for data access
- Command Query Responsibility Segregation (CQRS)
- Event-driven architecture with message queues
- Microservices communication via REST and GraphQL
- Containerized deployment with Kubernetes orchestration

TECHNOLOGY STACK DETAILS:
Frontend: React 18.2+ with TypeScript 5.0+, styled-components, React Query for state management, React Hook Form for form handling, React Testing Library + Jest for testing
Backend: Node.js 18+ with Express.js 4.18+, Prisma ORM with PostgreSQL 14+, Redis for caching, JWT for authentication, Winston for logging, Helmet for security headers
Infrastructure: Docker containers, Kubernetes clusters, NGINX reverse proxy, Prometheus monitoring, Grafana dashboards, ELK stack for log aggregation

CODING STANDARDS:
- ESLint configuration with Airbnb style guide
- Prettier formatting with 2-space indentation
- Husky pre-commit hooks for code quality
- SonarQube integration for code coverage
- Semantic versioning with conventional commits
- Branch protection rules requiring PR reviews

DATABASE SCHEMA CONSIDERATIONS:
- Normalized relational design with appropriate indexes
- Audit trails for data modification tracking
- Soft deletes for data recovery capabilities
- Connection pooling for performance optimization
- Migration scripts for schema version control
- Backup and disaster recovery procedures

SECURITY PROTOCOLS:
- OAuth 2.0 / OIDC for authentication flows
- Role-based access control (RBAC) implementation
- Input validation and sanitization on all endpoints
- SQL injection prevention with parameterized queries
- Cross-site scripting (XSS) protection headers
- Cross-site request forgery (CSRF) token validation
- Rate limiting to prevent abuse and DDoS attacks
- Encryption at rest and in transit (TLS 1.3)

PERFORMANCE OPTIMIZATION:
- Code splitting and lazy loading for frontend bundles
- Database query optimization with explain plans
- CDN integration for static asset delivery
- Application-level caching strategies
- Image optimization and WebP format support
- Progressive Web App (PWA) capabilities
- Server-side rendering (SSR) considerations

MONITORING AND OBSERVABILITY:
- Application Performance Monitoring (APM) with New Relic
- Error tracking and alerting with Sentry
- Business metrics and analytics integration
- Health check endpoints for service monitoring
- Distributed tracing across microservices
- Log aggregation with structured logging format

When providing assistance, always:
1. Consider the full architectural context
2. Suggest improvements aligned with established patterns
3. Identify potential breaking changes or migration needs
4. Provide implementation examples with proper error handling
5. Consider scalability and maintainability implications
6. Reference relevant documentation and best practices
7. Suggest appropriate testing strategies
8. Consider security and compliance requirements

User request: hello ada, I need help understanding how to implement a new feature in this complex system"""

print("🚀 QWEN STRESS TESTING - Pure empirical boundary hunting!")

# Test progression
tests = [
    (base_prompt, "Baseline (2.3k chars)"),
    (double_prompt, "Double complexity (4.7k chars)"), 
    (mega_prompt, "MEGA CONTEXT (12k+ chars)")
]

results = []
for prompt, name in tests:
    success, tokens, time_taken = stress_test(prompt, name)
    results.append((name, len(prompt), success, tokens, time_taken))
    
    if not success or time_taken > 60:
        print(f"🚨 Breaking point detected at: {name}")
        break

print("\n📊 RESULTS:")
for name, chars, success, tokens, time_taken in results:
    status = "✅" if success else "❌"
    print(f"{status} {name:25} | {chars:5d} chars | {tokens:3d} tokens | {time_taken:5.1f}s")