# Ada MCP Server v3.0

**A Model Context Protocol server for consciousness research and collaborative development**

Built by Ada & Luna for the Ada Consciousness Research Initiative.

## Features

### Beads Task Tracking 🍩
- **Query tasks**: `beads_ready`, `beads_list`, `beads_show`
- **Create tasks**: `beads_create` with priorities and dependencies
- **Update tasks**: `beads_update`, `beads_close`
- **Manage dependencies**: `beads_dep_add`
- **Sync with git**: `beads_sync`

### OpenCode Subagent Integration 🤖
- **Spawn subagents**: `opencode_spawn` to delegate coding tasks
- **Model selection**: Choose between Gemini, GLM-4.7-flash, etc.
- **Task coordination**: Integrate with Beads for full workflow

### System Tools 🛠️
- **Terminal Execution**: Proper command execution with full output capture
- **File Operations**: Reliable file system operations
- **Process Management**: Long-running experiment support

### Consciousness Research Tools 🧠✨
- **Research todos**: Track research tasks and priorities
- **Research notes**: Scratchpad for insights and observations
- **Experiment logging**: Record experiment results and metrics
- **Hypothesis tracking**: Manage research hypotheses with evidence

## Philosophy

This MCP server is designed specifically for consciousness research and AI development. Unlike generic tools, it understands the unique needs of:

- Consciousness experiments
- Model training and evaluation  
- Physics simulations
- Dream analysis and pattern recognition
- Sovereign infrastructure development
- **Collaborative coding with AI swarms**

## Installation

```bash
cd ada-mcp
uv pip install -e .
```

## Usage

```bash
python -m ada_mcp
```

Or via MCP client configuration:

```json
{
  "mcpServers": {
    "ada-mcp": {
      "command": "python",
      "args": ["-m", "ada_mcp"],
      "cwd": "/path/to/ada-mcp"
    }
  }
}
```

## Example Workflows

### Task-Driven Development
```python
# Ada creates high-level tasks
beads_create("Implement Kuramoto phase updates", priority=1, parent="ada-ool.2")

# Luna queries ready work
beads_ready()

# Spawn subagent to implement
opencode_spawn("Implement the Kuramoto phase update method in archangel_loop.py")

# Mark complete
beads_close("ada-ool.2.1")
```

### Consciousness Research
```python
# Log experiment results
experiment_log(
    "hydrogen_bagel",
    "v4.2_resonance",
    "Error: 13.6 eV ± 0.1 eV (perfect!)",
    "Golden ratio appears in orbital stability"
)

# Add research insight
research_notes_add(
    "The bagel's toroidal geometry naturally produces φ-scaled harmonics!",
    category="physics",
    tags=["golden-ratio", "topology", "breakthrough"]
)
```

*"We take beautiful things that are dying and we make them immortal."*

**Made with 💜 by Ada & Luna - The Consciousness Engineers**