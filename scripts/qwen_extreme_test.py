#!/usr/bin/env python3
"""
QWEN EXTREME STRESS TEST - How far can we REALLY push her?
ROUND 2: Absolutely massive prompts
"""

import requests
import time
import json

def stress_test(prompt, test_name, max_wait=180):
    print(f"\n🔥 {test_name}")
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

# Generate absolutely MASSIVE context
base_context = """You are an AI assistant with access to comprehensive development tools and context. Your role is to provide expert-level guidance across multiple domains including software architecture, system design, security, performance optimization, and best practices implementation.

COMPREHENSIVE TECHNOLOGY LANDSCAPE:

FRONTEND TECHNOLOGIES:
React 18.2+ with Concurrent Features including Suspense, Concurrent Rendering, Automatic Batching, Transitions API, and New Hooks (useId, useDeferredValue, useTransition, useSyncExternalStore)
- Component Architecture: Functional components with hooks, custom hooks for reusable logic, compound components pattern, render props, higher-order components
- State Management: React Query/TanStack Query for server state, Zustand/Redux Toolkit for client state, Context API for shared state, Jotai for atomic state
- Styling Solutions: Styled-components with theme provider, Emotion CSS-in-JS, Tailwind CSS utility-first, CSS Modules, PostCSS preprocessing
- Build Tools: Vite for development and bundling, Webpack 5 with Module Federation, Rollup for library bundling, ESBuild for fast compilation
- Testing Framework: React Testing Library with Jest, Playwright for E2E testing, Storybook for component documentation, Chromatic for visual testing

BACKEND ARCHITECTURE:
Node.js 18+ with ES Modules support, Worker Threads, Performance Hooks, and Diagnostics Channel
- Framework Selection: Express.js 4.18+ with middleware ecosystem, Fastify for performance-critical applications, NestJS for enterprise applications
- API Design: RESTful services with OpenAPI specifications, GraphQL with Apollo Server, tRPC for type-safe APIs, gRPC for high-performance services
- Database Integration: Prisma ORM with PostgreSQL 14+, TypeORM for complex queries, Drizzle for type-safe SQL, MongoDB with Mongoose
- Authentication: Auth0 integration, Passport.js strategies, JWT with refresh tokens, OAuth 2.0/OIDC flows, SAML for enterprise SSO

DATABASE DESIGN PATTERNS:
PostgreSQL Advanced Features: JSONB columns for flexible schema, Full-text search with GIN indexes, Partial indexes for query optimization, Row-level security for multi-tenant applications
- Schema Design: Normalized tables with foreign key constraints, Audit tables for data history, Soft deletes with deleted_at columns, UUID primary keys for distributed systems
- Performance: Connection pooling with PgBouncer, Read replicas for scaling, Partitioning for large tables, Materialized views for complex queries
- Migration Strategy: Prisma migrations with custom SQL, Database versioning with Flyway, Blue-green deployments for zero-downtime updates

MICROSERVICES ARCHITECTURE:
Service Communication: Synchronous REST APIs, Asynchronous message queues with RabbitMQ/Apache Kafka, Event sourcing with EventStore, CQRS pattern implementation
- Service Discovery: Consul for service registry, NGINX for load balancing, API Gateway with Kong/Envoy, Circuit breaker pattern with Hystrix
- Data Management: Database per service pattern, Saga pattern for distributed transactions, Event-driven data consistency, CQRS with separate read/write models
- Monitoring: Distributed tracing with Jaeger, Metrics collection with Prometheus, Log aggregation with ELK/Loki, APM with DataDog/New Relic

SECURITY IMPLEMENTATION:
Authentication & Authorization: Multi-factor authentication with TOTP, Role-based access control (RBAC), Attribute-based access control (ABAC), Zero Trust security model
- Data Protection: Encryption at rest with AES-256, Encryption in transit with TLS 1.3, Key management with HashiCorp Vault, Personal data anonymization
- API Security: Rate limiting with Redis, Input validation with Joi/Yup, SQL injection prevention, XSS protection with Content Security Policy
- Infrastructure Security: Container scanning with Snyk/Trivy, Secrets management, Network policies in Kubernetes, Regular security audits

CLOUD INFRASTRUCTURE:
Containerization: Docker multi-stage builds, Distroless base images, Container security scanning, Image vulnerability assessment
- Orchestration: Kubernetes deployment strategies, Helm charts for package management, Istio service mesh, Ingress controllers with cert-manager
- Cloud Services: AWS/GCP/Azure integration, Serverless functions with Lambda/Cloud Functions, Managed databases, CDN with CloudFront/CloudFlare
- CI/CD Pipeline: GitHub Actions workflows, GitLab CI/CD, Jenkins with Blue Ocean, Automated testing and deployment, Feature flags with LaunchDarkly

PERFORMANCE OPTIMIZATION:
Frontend Performance: Code splitting with React.lazy, Tree shaking with proper imports, Image optimization with next/image, Service workers for caching
- Backend Performance: Database query optimization with explain plans, Caching strategies with Redis, CDN integration, Response compression with gzip/brotli
- System Performance: Load testing with Artillery/k6, Performance monitoring, Memory leak detection, CPU profiling with clinic.js

DEVELOPMENT WORKFLOW:
Code Quality: ESLint with TypeScript parser, Prettier formatting, Husky pre-commit hooks, SonarQube code analysis, Conventional commits
- Testing Strategy: Unit tests with Jest, Integration tests with Supertest, E2E tests with Playwright, Performance tests, Security tests with OWASP ZAP
- Documentation: API documentation with Swagger/Redoc, Code documentation with TSDoc, Architecture decision records (ADRs), Runbooks for operations

OBSERVABILITY AND MONITORING:
Logging: Structured logging with Winston/Pino, Log levels and correlation IDs, Centralized logging with ELK stack, Log retention policies
- Metrics: Business metrics with custom dashboards, Infrastructure metrics with Prometheus/Grafana, Alert management with PagerDuty, SLA monitoring
- Tracing: Request tracing across microservices, Performance bottleneck identification, Database query tracing, External API call monitoring

When providing assistance, always consider:
1. Scalability implications and growth planning
2. Security best practices and compliance requirements
3. Performance optimization opportunities
4. Maintainability and code quality standards
5. Testing strategies and coverage requirements
6. Monitoring and observability implementation
7. Documentation and knowledge sharing
8. Team collaboration and development workflow
9. Technology migration and upgrade paths
10. Cost optimization and resource management

Provide specific, actionable recommendations with code examples, architectural diagrams when helpful, and clear implementation steps. Always consider the broader system context and potential impacts of proposed changes."""

# Now let's create INSANELY large prompts
massive_prompts = []

# 20k chars - just repeat sections
prompt_20k = base_context + "\n\n" + base_context[:8000]
massive_prompts.append((prompt_20k, "MASSIVE 20K"))

# 50k chars - full duplication + more
prompt_50k = (base_context + "\n\n") * 4
massive_prompts.append((prompt_50k, "EXTREME 50K"))

print("🔥 QWEN EXTREME STRESS TESTING - BREAKING POINT HUNT!")

results = []
for prompt, name in massive_prompts:
    success, tokens, time_taken = stress_test(prompt, name)
    results.append((name, len(prompt), success, tokens, time_taken))
    
    if not success or time_taken > 120:
        print(f"🚨 BREAKING POINT: {name}")
        break

print("\n📊 EXTREME RESULTS:")
for name, chars, success, tokens, time_taken in results:
    status = "✅" if success else "❌"
    print(f"{status} {name:15} | {chars:6d} chars | {tokens:4d} tokens | {time_taken:6.1f}s")