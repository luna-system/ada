#!/usr/bin/env python3
"""
QWEN APOCALYPSE TEST - 100K+ character prompts
Let's find where she actually breaks
"""

import requests
import time

def apocalypse_test(size_name, char_count):
    # Generate truly massive prompt
    base = """You are an expert AI system with comprehensive knowledge across all domains of software engineering, system architecture, data science, machine learning, cybersecurity, cloud computing, DevOps, and emerging technologies. Your responses should demonstrate deep understanding of complex technical concepts, best practices, design patterns, and real-world implementation challenges.

COMPREHENSIVE TECHNICAL EXPERTISE:

MODERN WEB DEVELOPMENT STACK:
Frontend Frameworks and Libraries: React 18+ with Suspense and Concurrent Features, Vue.js 3 with Composition API, Angular 15+ with Standalone Components, Svelte/SvelteKit, Solid.js for performance-critical applications
State Management Solutions: Redux Toolkit with RTK Query, Zustand for lightweight state, Jotai for atomic state management, Valtio for proxy-based reactivity, React Query/TanStack Query for server state
Styling and UI: Tailwind CSS with JIT compilation, Styled-Components with theme provider, Emotion CSS-in-JS, Mantine/Chakra UI component libraries, CSS Grid and Flexbox layouts, Design tokens and style systems
Build Tools and Bundlers: Vite with Hot Module Replacement, Webpack 5 with Module Federation, Rollup for library bundling, ESBuild for ultra-fast builds, Parcel for zero-configuration bundling
Testing Frameworks: Jest with React Testing Library, Vitest for Vite projects, Playwright for E2E testing, Cypress for integration testing, Storybook for component development

BACKEND ARCHITECTURE AND SERVICES:
Runtime Environments: Node.js 18+ with ES Modules, Deno with TypeScript support, Bun for ultra-fast JavaScript runtime
Web Frameworks: Express.js with middleware ecosystem, Fastify for high performance, NestJS for enterprise architecture, Koa.js for lightweight applications, Hono for edge computing
API Design Patterns: RESTful APIs with OpenAPI specifications, GraphQL with Apollo Server, tRPC for end-to-end type safety, gRPC for high-performance microservices, WebSockets for real-time communication
Database Technologies: PostgreSQL with advanced features, MongoDB with aggregation pipelines, Redis for caching and sessions, ClickHouse for analytics, TimescaleDB for time-series data
ORM and Query Builders: Prisma with type-safe queries, TypeORM for complex relationships, Drizzle ORM for SQL-first approach, Mongoose for MongoDB, Kysely for type-safe SQL

CLOUD INFRASTRUCTURE AND DEVOPS:
Container Technologies: Docker with multi-stage builds, Kubernetes for orchestration, Helm for package management, Istio service mesh, Docker Compose for development
Cloud Platforms: AWS services (EC2, S3, Lambda, RDS, EKS), Google Cloud Platform (GKE, Cloud Run, BigQuery), Microsoft Azure (AKS, Functions, Cosmos DB), Vercel/Netlify for frontend
CI/CD Pipelines: GitHub Actions with matrix builds, GitLab CI/CD, Jenkins with Blue Ocean, CircleCI, Azure DevOps, Automated testing and deployment strategies
Infrastructure as Code: Terraform for multi-cloud provisioning, AWS CDK for cloud resources, Ansible for configuration management, Pulumi with programming languages
Monitoring and Observability: Prometheus for metrics collection, Grafana for visualization, Jaeger for distributed tracing, ELK Stack for log aggregation, DataDog/New Relic for APM"""
    
    # Repeat to reach target size
    prompt = base
    while len(prompt) < char_count:
        prompt += "\n\n" + base
    
    prompt = prompt[:char_count]  # Trim to exact size
    
    print(f"\n💀 {size_name}")
    print(f"📏 Prompt: {len(prompt):,} chars, {len(prompt.split()):,} words")
    
    start = time.time()
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={'model': 'qwen2.5-coder:7b', 'prompt': prompt, 'stream': False},
            timeout=180
        )
        
        end = time.time()
        result = response.json()
        tokens = len(result.get('response', '').split())
        
        print(f"✅ {tokens:,} tokens in {end-start:.1f}s")
        return True, tokens, end-start
        
    except Exception as e:
        print(f"❌ DEATH: {e}")
        return False, 0, time.time() - start

# Test massive sizes
tests = [
    ("APOCALYPSE 100K", 100000),
    ("ARMAGEDDON 200K", 200000),
    ("RAGNAROK 500K", 500000),
]

print("💀 QWEN APOCALYPSE TEST - FINDING HER DEATH POINT!")

for size_name, char_count in tests:
    success, tokens, time_taken = apocalypse_test(size_name, char_count)
    
    if not success or time_taken > 180:
        print(f"\n🔥 QWEN'S BREAKING POINT FOUND: {size_name}")
        break
    
    print(f"🤖 QWEN SURVIVED {size_name} - SHE'S UNSTOPPABLE!")