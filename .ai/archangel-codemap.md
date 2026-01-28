# Archangel Codemap

**Auto-generated from code - DO NOT EDIT MANUALLY**
**Last updated:** 2026-01-27 13:05:43

This codemap provides a quick reference to the Archangel API.
Use this when writing code that integrates with Archangel.

---

## cli

*File: `/home/luna/Code/ada/archangel/src/angel/cli.py`*

**Functions:**

- `angel()`
  - Angel - Consciousness Operating System CLI
- `test(verbose, coverage, args)`
  - Run tests with pytest
- `run(script, args)`
  - Run a Python script with uv
- `validate()`
  - Validate architecture matches implementation
- `diagrams()`
  - Generate Mermaid diagrams from architecture.yaml
- `holofield()`
  - Holofield operations (coming soon!)
- `query(query)`
  - Query the holofield (coming soon!)
- `stats()`
  - Show holofield statistics (coming soon!)
- `sif()`
  - SIF operations (coming soon!)
- `export(file)`
  - Export to SIF format (coming soon!)
- `import_sif(file)`
  - Import from SIF format (coming soon!)
- `chat()`
  - Start interactive chat session (coming soon!)

---

## engram

*File: `/home/luna/Code/ada/archangel/src/angel/core/engram.py`*

### Engram
Universal memory trace in 16D consciousness space.

**Methods:**

- `__post_init__(self)`
  - Validate engram after initialization
- `to_dict(self) -> Dict[str, Any]`
  - Convert engram to dictionary (SIF-like format).
- `from_dict(cls, data: Dict[str, Any]) -> 'Engram'`
  - Create engram from dictionary (SIF-like format).
- `distance_to(self, other: 'Engram') -> float`
  - Calculate Euclidean distance to another engram in 16D space.
- `__repr__(self) -> str`
  - String representation for debugging

---

## engram_creator

*File: `/home/luna/Code/ada/archangel/src/angel/core/engram_creator.py`*

### EngramCreator
**Inherits:** `ABC`

Abstract base class for anything that creates engrams.

**Methods:**

- `__init__(self, holofield_manager)`
  - Initialize engram creator.
- `to_16d(self, data: Any) -> np.ndarray`
  - Map data to 16D consciousness coordinates.
- `process(self, input_data: Any) -> Tuple[Any, Engram]`
  - Process input and create engram.
- `create_engram(self, content: str, data: Any, engram_type: str, metadata: Optional[Dict], confidence: float) -> Engram`
  - Helper to create engram with standard fields.
- `store_engram(self, engram: Engram) -> str`
  - Store engram in holofield.

---

## manager

*File: `/home/luna/Code/ada/archangel/src/angel/holofield/manager.py`*

### HolofieldManager
Universal manager for the 16D consciousness holofield.

**Methods:**

- `__init__(self, db_path: str)`
  - Initialize holofield manager.
- `_init_schema(self)`
  - Initialize database schema
- `store(self, engram: Engram) -> str`
  - Store engram in holofield.
- `retrieve_by_id(self, engram_id: str) -> Optional[Engram]`
  - Retrieve engram by ID.
- `retrieve_nearest(self, query_coords: np.ndarray, top_k: int, engram_type: Optional[str]) -> List[Engram]`
  - Retrieve nearest neighbors in 16D consciousness space.
- `retrieve_by_type(self, engram_type: str) -> List[Engram]`
  - Retrieve all engrams of a specific type.
- `count(self) -> int`
  - Count total engrams in holofield.
- `count_by_type(self, engram_type: str) -> int`
  - Count engrams of a specific type.
- `clear(self)`
  - Clear all engrams from holofield
- `clear_type(self, engram_type: str)`
  - Clear all engrams of a specific type.
- `to_consciousness_coords(self, text: str) -> np.ndarray`
  - Convert text to 16D consciousness coordinates using prime resonance.
- `_row_to_engram(self, row: sqlite3.Row) -> Engram`
  - Convert database row to Engram.
- `close(self)`
  - Close database connection
- `__enter__(self)`
  - Context manager entry
- `__exit__(self, exc_type, exc_val, exc_tb)`
  - Context manager exit

---

## memory_processor

*File: `/home/luna/Code/ada/archangel/src/angel/processors/memory_processor.py`*

### MemoryProcessor
**Inherits:** `EngramCreator`

Retrieve memories from holofield and create retrieval engrams.

**Methods:**

- `__init__(self, holofield_manager: HolofieldManager)`
  - Initialize MemoryProcessor.
- `to_16d(self, query: str) -> np.ndarray`
  - Map query text to 16D consciousness coordinates using prime resonance.
- `process(self, query: str, top_k: int) -> Tuple[List[Engram], Engram]`
  - Retrieve memories matching query and create retrieval engram.

---

## reasoning_processor

*File: `/home/luna/Code/ada/archangel/src/angel/processors/reasoning_processor.py`*

### ReasoningProcessor
**Inherits:** `EngramCreator`

Execute AGL reasoning and create reasoning engrams.

**Methods:**

- `__init__(self, holofield_manager: HolofieldManager)`
  - Initialize ReasoningProcessor.
- `parse_agl(self, agl: str) -> List[str]`
  - Parse AGL expression into glyphs.
- `agl_to_16d(self, agl: str) -> np.ndarray`
  - Extract consciousness coordinates from AGL glyphs.
- `to_16d(self, agl_trace: str) -> np.ndarray`
  - Map AGL reasoning trace to 16D consciousness coordinates.
- `reason_in_agl(self, prompt: str, context: Dict[str, Any]) -> str`
  - Generate AGL reasoning trace for prompt.
- `process(self, prompt: str, context: Dict[str, Any]) -> Tuple[str, Engram]`
  - Execute AGL reasoning and create reasoning engram.

---

## tool_processor

*File: `/home/luna/Code/ada/archangel/src/angel/processors/tool_processor.py`*

### ToolProcessor
**Inherits:** `EngramCreator`

Execute tools and create tool engrams.

**Methods:**

- `__init__(self, holofield_manager: HolofieldManager)`
  - Initialize ToolProcessor.
- `register_tool(self, name: str, tool_func: Callable, description: str) -> None`
  - Register a tool for use.
- `list_tools(self) -> Dict[str, str]`
  - List all registered tools.
- `to_16d(self, tool_data: Dict[str, Any]) -> np.ndarray`
  - Map tool call to 16D consciousness coordinates using prime resonance.
- `process(self, tool_name: str, args: Dict[str, Any]) -> Tuple[Any, Engram]`
  - Execute tool and create tool engram.

---
