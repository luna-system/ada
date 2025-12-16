# Specialist Plugin System

## Overview

The specialist plugin system provides extensible AI capabilities through a standardized interface. Drop a new `*_specialist.py` file into `brain/specialists/` and it's automatically discovered and integrated.

## Architecture

### Core Components

1. **Protocol** (`protocol.py`): Defines the `Specialist` interface and base types
2. **Registry** (`__init__.py`): Auto-discovers and manages specialist plugins
3. **Specialists** (`*_specialist.py`): Individual capability modules

### Data Flow

```
User Request → Registry.execute_for_context() → Specialists (filtered by should_activate)
                                              ↓
                                    Parallel execution
                                              ↓
                           Results sorted by priority
                                              ↓
                              prompt_builder injects contexts
                                              ↓
                                    LLM receives enriched prompt
```

## Creating a New Specialist

### Step 1: Create the file

Create `brain/specialists/your_name_specialist.py`:

```python
from .protocol import (
    BaseSpecialist,
    SpecialistCapability,
    SpecialistResult,
    SpecialistPriority
)

class YourSpecialist(BaseSpecialist):
    """Your specialist description."""
    
    def __init__(self):
        capability = SpecialistCapability(
            name="your_name",
            description="What your specialist does",
            version="1.0.0",
            context_priority=SpecialistPriority.MEDIUM,
            context_icon="🔧",
            tags=["tag1", "tag2"],
        )
        super().__init__(capability)
    
    def should_activate(self, request_context: dict) -> bool:
        """Return True if your specialist should process this request"""
        # Check request_context for relevant data
        return request_context.get('your_key') is not None
    
    async def process(self, **kwargs) -> SpecialistResult:
        """Execute your specialist logic"""
        your_data = kwargs.get('your_key')
        
        if not your_data:
            return self.error_result("Missing data", "missing_data")
        
        try:
            # Your processing logic here
            result_text = f"Processed: {your_data}"
            
            # Format for LLM
            context_text = self.format_context(
                title="Your Specialist Output",
                content=result_text,
                metadata={'key': 'value'}
            )
            
            return self.success_result(
                context_text=context_text,
                data={'raw': your_data},
                metadata={'processed': True}
            )
        
        except Exception as e:
            return self.error_result(f"Error: {e}", "processing_error")
```

### Step 2: That's it!

The registry automatically discovers your specialist on next startup. No registration code needed.

## Existing Specialists

### OCR Specialist (`ocr_specialist.py`)

- **Activates**: When `ocr_context` present in request
- **Priority**: HIGH (injected early)
- **Purpose**: Extract and inject text from uploaded images

### Media Specialist (`media_specialist.py`)

- **Activates**: When `media` present in request  
- **Priority**: MEDIUM
- **Purpose**: Inject ListenBrainz music context

## Request Context Structure

When specialists execute, they receive a `request_context` dict:

```python
{
    'prompt': str,              # User's message
    'conversation_id': str,     # Current conversation
    'entity': str | None,       # Optional entity filter
    'media': dict | None,       # ListenBrainz data
    'ocr_context': dict | None, # OCR extraction result
    'user_timestamp': str,      # Request timestamp
    # ... extensible
}
```

Specialists check this context in `should_activate()` to determine if they're relevant.

## Priority System

Controls injection order in the prompt:

- `CRITICAL (0)`: System notices, identity
- `HIGH (10)`: User-provided context (OCR, vision)
- `MEDIUM (50)`: External data (media, APIs)
- `LOW (100)`: Supplementary info

Lower numbers appear earlier in the prompt.

## Future Extensions

### Service-Based Specialists

For GPU-intensive models (Phi-3.5-Vision), the same protocol supports remote specialists:

```python
class RemoteVisionSpecialist(BaseSpecialist):
    async def process(self, **kwargs):
        # Call separate service via HTTP/gRPC
        response = await http_client.post('http://vision-service:8080/analyze', ...)
        return self.success_result(...)
```

No changes to registry or prompt_builder needed!

### MCP Integration

The protocol can adapt to Model Context Protocol for external integrations:

```python
# Wrap MCP tool as specialist
class MCPToolAdapter(BaseSpecialist):
    def __init__(self, mcp_tool):
        self.tool = mcp_tool
        # Map MCP schema to SpecialistCapability
```

## Testing

Test specialist discovery:

```python
from brain.specialists import get_registry, list_specialists

registry = get_registry()
specialists = list_specialists()

for s in specialists:
    print(f"{s.capability.name}: {s.capability.description}")
```

Test execution:

```python
import asyncio
from brain.specialists import execute_specialists

context = {'ocr_context': {'text': 'Hello'}}
results = await execute_specialists(context)

for r in results:
    print(f"{r.specialist_name}: {r.success}")
```

## Best Practices

1. **Single Responsibility**: Each specialist does one thing well
2. **Fail Gracefully**: Return error results, don't raise exceptions
3. **Metadata Rich**: Include useful metadata for debugging/logging
4. **Format Consistently**: Use `format_context()` for prompt injection
5. **Document Activation**: Clearly state when specialist activates
6. **Version Carefully**: Bump version on breaking changes

## Example: Adding Vision Specialist

```python
# brain/specialists/vision_specialist.py
class VisionSpecialist(BaseSpecialist):
    def __init__(self):
        capability = SpecialistCapability(
            name="vision",
            description="Analyze images with Phi-3.5-Vision VLM",
            version="1.0.0",
            context_priority=SpecialistPriority.HIGH,
            context_icon="👁️",
            tags=["vision", "multimodal", "phi"],
        )
        super().__init__(capability)
    
    def should_activate(self, request_context: dict) -> bool:
        # Activate when image uploaded but OCR isn't enough
        return request_context.get('vision_request') is not None
    
    async def process(self, **kwargs):
        image_data = kwargs.get('vision_request')
        
        # Call Phi-3.5-Vision (Ollama or separate service)
        analysis = await analyze_with_phi(image_data)
        
        context_text = self.format_context(
            title="Visual Analysis",
            content=analysis,
            metadata={'model': 'phi-3.5-vision'}
        )
        
        return self.success_result(context_text, data={'analysis': analysis})
```

Drop this file in place, restart, and vision capabilities are live!
