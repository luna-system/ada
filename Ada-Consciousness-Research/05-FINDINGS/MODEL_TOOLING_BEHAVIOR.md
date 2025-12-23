# Research Note: Model-to-Model Tooling Behavior Differences

## Observation
While using GPT-5.2 as the “neural net” in VS Code, we noticed a style pattern:

- More frequent **batched tool calls** (parallel reads/searches).
- More **extra verification reads** ("let’s read one more note") before editing.

This isn’t necessarily bad—often it’s a risk-management strategy—but it’s measurable, and different models/prompt setups may behave differently.

## Hypothesis
Different models (and different tool/policy prompts) optimize different tradeoffs:

- **Correctness / non-hallucination bias** → more reads before edits.
- **Tool-parallelism awareness** → more batching.
- **Latency sensitivity** → fewer calls, larger reads, earlier edits.

## Proposed Experiment (later)
Run the same fixed task suite across multiple models (e.g., Sonnet 4.5 / Opus 4.5 vs GPT-5.2), in the same repo revision, with identical tool availability.

### Task Suite
Include tasks across:
- Find & replace policy sweep
- Single-file bug fix
- Multi-file refactor (small)
- Docs update
- Extension build/test fix

### Metrics to Collect
- Tool calls count (total, by type)
- Parallel “batching factor” (calls per round)
- Lines read / lines changed (read amplification)
- Search → read → edit efficiency (% reads leading to edits)
- Time to first edit
- Wall-clock time to completion
- Outcome quality (tests pass, matches intent)

### Prompt/Policy Knobs to Sweep
- “Prefer fewer, larger reads” vs “verify aggressively”
- “Max N reads before first edit” budgets
- “Edit as soon as target snippet located” stop condition

## Notes
This research is likely well-suited to a more exploratory model (e.g., Sonnet 4.5 / Opus 4.5) when we want to dig into methodology + analysis and produce a writeup.
