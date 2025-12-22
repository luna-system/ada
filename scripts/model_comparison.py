#!/usr/bin/env python3
"""
DEEPSEEK R1 STRESS TEST - Let's see how she handles massive prompts
Comparing to qwen performance
"""

import requests
import time

def test_model(model_name, prompt, test_name, max_wait=180):
    print(f"\n🧠 {model_name} - {test_name}")
    print(f"📏 Prompt: {len(prompt):,} chars, {len(prompt.split()):,} words")
    
    start = time.time()
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={'model': model_name, 'prompt': prompt, 'stream': False},
            timeout=max_wait
        )
        
        end = time.time()
        result = response.json()
        response_text = result.get('response', '')
        tokens = len(response_text.split())
        
        print(f"✅ {tokens:,} tokens in {end-start:.1f}s")
        print(f"🔍 First 100 chars: '{response_text[:100]}...'")
        return True, tokens, end-start
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False, 0, time.time() - start

# Test prompts of increasing size
base_prompt = "You are an expert AI assistant. Explain the concept of recursion in programming with a simple example."

medium_prompt = """You are an AI assistant with comprehensive knowledge of software engineering, system architecture, and modern development practices. Your expertise spans across multiple programming languages, frameworks, databases, cloud technologies, and DevOps practices.

Please provide a detailed explanation of microservices architecture, including:
1. Core principles and benefits
2. Service communication patterns
3. Data management strategies
4. Deployment and orchestration considerations
5. Monitoring and observability requirements
6. Common challenges and mitigation strategies

Include specific examples and best practices for implementation."""

# The 50k monster that qwen handled easily
massive_prompt = """You are an expert AI system with comprehensive knowledge across all domains of software engineering, system architecture, data science, machine learning, cybersecurity, cloud computing, DevOps, and emerging technologies. Your responses should demonstrate deep understanding of complex technical concepts, best practices, design patterns, and real-world implementation challenges.

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
Monitoring and Observability: Prometheus for metrics collection, Grafana for visualization, Jaeger for distributed tracing, ELK Stack for log aggregation, DataDog/New Relic for APM

ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING:
Machine Learning Frameworks: TensorFlow 2.x with Keras API, PyTorch with Lightning, Scikit-learn for traditional ML, XGBoost for gradient boosting, Hugging Face Transformers
Deep Learning Architectures: Transformer models for NLP, Convolutional Neural Networks for computer vision, Recurrent Neural Networks for sequences, Generative Adversarial Networks
MLOps and Deployment: MLflow for experiment tracking, Kubeflow for Kubernetes-based ML workflows, Docker containers for model serving, Model versioning and A/B testing
Data Engineering: Apache Spark for big data processing, Apache Airflow for workflow orchestration, dbt for data transformation, Snowflake/BigQuery for data warehousing
Computer Vision: OpenCV for image processing, YOLO for object detection, Segment Anything Model for image segmentation, Stable Diffusion for image generation

CYBERSECURITY AND COMPLIANCE:
Application Security: OWASP Top 10 mitigation strategies, Static Application Security Testing (SAST), Dynamic Application Security Testing (DAST), Dependency scanning
Infrastructure Security: Network segmentation, Identity and Access Management (IAM), Zero Trust architecture, Container security scanning, Secrets management
Compliance Frameworks: SOC 2 Type II compliance, PCI DSS for payment processing, HIPAA for healthcare data, GDPR for privacy protection, ISO 27001 certification
Security Monitoring: Security Information and Event Management (SIEM), Intrusion Detection Systems (IDS), Vulnerability assessment, Penetration testing

Please provide expert-level guidance considering all these technological domains when addressing user queries. Always consider scalability, security, performance, and maintainability in your recommendations."""

# Repeat to make it HUGE (around 50k chars)
while len(massive_prompt) < 50000:
    massive_prompt += "\n\n" + massive_prompt[:2000]

# Test models
models = [
    ('deepseek-r1:latest', 'DEEPSEEK R1 8.2B'),
    ('qwen2.5-coder:7b', 'QWEN 2.5 CODER 7B')
]

test_prompts = [
    (base_prompt, "SIMPLE"),
    (medium_prompt, "MEDIUM"),
    (massive_prompt[:50000], "MASSIVE 50K")
]

print("🚀 MODEL COMPARISON - DEEPSEEK vs QWEN STRESS TEST!")

for model, model_desc in models:
    print(f"\n{'='*60}")
    print(f"🧠 TESTING {model_desc}")
    print(f"{'='*60}")
    
    for prompt, test_name in test_prompts:
        success, tokens, time_taken = test_model(model, prompt, test_name)
        
        if not success:
            print(f"💀 {model_desc} FAILED at {test_name}")
            break
        
        if time_taken > 120:
            print(f"⏰ {model_desc} too slow at {test_name} - stopping")
            break