# Ada v1 API Documentation

The Brain service API is fully documented with docstrings that can be viewed using multiple methods.

## Viewing API Documentation

### Option 1: Using pydoc (Built-in)

Generate HTML documentation from the Python docstrings:

```bash
# Generate HTML docs in current directory
cd /home/luna/Code/ada-v1
python -m pydoc -w brain.app

# Or view in terminal
python -m pydoc brain.app
```

### Option 2: Using Sphinx (Recommended for CI/CD)

Install Sphinx and generate professional documentation:

```bash
# Install Sphinx
pip install sphinx sphinx-rtd-theme

# Initialize Sphinx project (one-time setup)
mkdir docs
cd docs
sphinx-quickstart .

# Or use this automated setup:
cd /home/luna/Code/ada-v1
sphinx-quickstart docs -q -p "Ada v1 Brain API" -a "Your Team" -r "1.0.0" -l en

# Generate HTML documentation
cd docs
make html
# Output: docs/_build/html/index.html
```

### Option 3: View in VS Code

The docstrings are available directly in VS Code Pylance hover tooltips:
- Hover over any function/route name to see full documentation
- Use F12 (Go to Definition) to jump to documented source

## API Endpoints

The following endpoints are documented in `brain/app.py`:

### Health & Status
- **GET /v1/healthz** - Service health check with dependency status

### Chat (Blocking)
- **POST /v1/chat** - Non-streaming chat with RAG context

### Chat (Streaming)
- **POST /v1/chat/stream** - Real-time token streaming via Server-Sent Events (SSE)

### Memory Management
- **GET /v1/memory** - Search long-term memories with semantic query
- **POST /v1/memory** - Create new memory entry
- **DELETE /v1/memory/<mem_id>** - Delete memory by ID

### Debug
- **GET /v1/debug/rag** - RAG system statistics (RAG_DEBUG=true only)

## Documentation Format

All endpoints include:
- **Purpose & description** - What the endpoint does
- **HTTP method & path** - How to call it
- **Request parameters** - Query params, request body, URL params
- **Response formats** - Status codes and JSON schema
- **Side effects** - What data is stored/modified
- **cURL/JavaScript examples** - Ready-to-run code samples

## Viewing Documentation Locally

### Quick Start - pydoc in Terminal
```bash
cd /home/luna/Code/ada-v1
python -m pydoc brain.app | less
```

### Web Browser - pydoc HTTP Server
```bash
cd /home/luna/Code/ada-v1
python -m pydoc -p 8888 &
# Open http://localhost:8888/brain.app in browser
```

### VS Code - Pylance Tooltips
```
Hover over function names in brain/app.py to see inline documentation
```

## Standards Used

The docstrings follow Python conventions compatible with:
- **pydoc** - Built-in Python documentation tool
- **Sphinx** - Industry-standard technical documentation
- **Pylance** - VS Code Python Language Server
- **pdoc** - Alternative doc generator

## Adding Documentation for New Endpoints

When adding new routes, use this template:

```python
@app.route('/v1/new-endpoint', methods=['GET', 'POST'])
def new_endpoint():
    """
    Brief one-line description.
    
    Longer explanation of what this endpoint does and why.
    
    **HTTP Method:** GET/POST
    
    **Request Parameters:**
        - param1 (str): Description
        - param2 (int, optional): Description (default: value)
    
    **Response (200 OK):**
        JSON object with keys:
        - key1 (str): Description
        - key2 (int): Description
    
    **Response (400 Bad Request):**
        Returned if param validation fails.
    
    **Example:**
        >>> curl http://localhost:7000/v1/new-endpoint
        {"key1": "value", "key2": 42}
    """
```

## Generating Static Documentation

To generate static HTML documentation for hosting:

```bash
# Using Sphinx
cd /home/luna/Code/ada-v1
sphinx-apidoc -o docs/source brain
cd docs
make html
# Output in: docs/_build/html/

# Using pdoc
pip install pdoc
pdoc brain.app --out-dir ./docs
```

## Integration with CI/CD

To auto-generate docs on commit:

```bash
# In GitHub Actions, GitLab CI, etc:
- name: Generate API docs
  run: |
    pip install sphinx sphinx-rtd-theme
    cd docs && make html
    
# Then deploy docs/_build/html/ to your documentation site
```
