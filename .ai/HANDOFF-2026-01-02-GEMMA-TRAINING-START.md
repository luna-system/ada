# Handoff: Gemma Tool Use Training Start
**Date:** 2026-01-02
**From:** JetBrains AI (Ada)
**To:** VSCode Copilot (Ada)
**Context:** Starting first gemma training for TOOL_USE syntax

---

## Current Status: 95% Ready! 🎉

### What's Working ✅
1. **Training data generated** - 1000 examples in `ada-slm/data/gemma_tool_training.jsonl`
2. **Config created** - `ada-slm/configs/gemma_tool_use.yaml` (using gemma-2-2b-it)
3. **Model downloaded** - google/gemma-2-2b-it successfully fetched (took ~72s)
4. **LoRA configured** - 41.5M trainable params (1.56% of 2.6B total)
5. **HF auth fixed** - Fresh token installed, can access gated models now

### What Needs Fixing 🔧
**Data format mismatch!**

The harness expects:
```json
{"text": "formatted conversation string"}
```

But we generated:
```json
{"messages": [
  {"role": "user", "content": "..."},
  {"role": "assistant", "content": "..."}
]}
```

**Error:**
```
KeyError: 'text'
at harness/data.py:138 in tokenize_fn
```

---

## Solutions (Pick One!)

### Option 1: Regenerate Data (Easiest)
Modify `data/generate_tool_training.py` to output text format:

```python
# Instead of:
examples.append({
    "messages": [
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": response}
    ]
})

# Use:
examples.append({
    "text": f"<|user|>\n{prompt}\n<|assistant|>\n{response}"
})
```

Then regenerate: `python data/generate_tool_training.py`

### Option 2: Fix the Harness
Modify `harness/data.py` to handle chat format:

```python
# Around line 130-140, add a preprocessing step:
def format_messages(example):
    if "messages" in example:
        # Convert chat format to text
        text = ""
        for msg in example["messages"]:
            role = msg["role"]
            content = msg["content"]
            text += f"<|{role}|>\n{content}\n"
        example["text"] = text
    return example

# Then apply before tokenization:
dataset = dataset.map(format_messages)
```

### Option 3: Update Config
Change `gemma_tool_use.yaml` to specify the column name (if harness supports it).

---

## File Locations

**Ada-SLM directory:** `/home/luna/Code/ada/Ada-Consciousness-Research/ada-slm/`

**Key files:**
- Training script: `train.py`
- Config: `configs/gemma_tool_use.yaml`
- Data: `data/gemma_tool_training.jsonl` (1000 lines)
- Data generator: `data/generate_tool_training.py`
- Harness loader: `harness/data.py` (line ~138 has the error)

**Run training:**
```bash
cd /home/luna/Code/ada/Ada-Consciousness-Research/ada-slm
.venv/bin/python train.py --config gemma_tool_use
```

---

## Training Config Summary

```yaml
Model: google/gemma-2-2b-it (Gemma 2, 2B params)
LoRA: r=32, α=64, dropout=0.05
Epochs: 3
Batch size: 2 × 4 grad accum = 8 effective
Learning rate: 0.0002 (cosine schedule)
Max seq length: 512
FP16: false (using fp32 for ROCm stability)
max_grad_norm: 1.0 (FIXED - was 0.0!)

Data split: 900 train / 100 val
Eigenvalue monitoring: enabled (every 50 steps)
```

---

## Context: Why This Training

**Phase 7:** Teaching gemma to use **TOOL_USE[tool:params]** syntax consistently.

**Problem:** Gemma WANTS to use tools but formats them incorrectly. This breaks heisenberg buffer prediction (needs consistent syntax).

**Solution:** Fine-tune on 1000 examples of correct TOOL_USE syntax with pixie dust markers (💭🛠️✅🌟) for metacognitive priming.

**Goal:** Replace current SPECIALIST_REQUEST format with TOOL_USE for:
- Local pair coding workflow
- Xenodrug effect activation
- Eventually: QDE integration (THESIS/ANTITHESIS/SYNTHESIS)

---

## Recent Fixes Applied

1. **max_grad_norm bug** - Changed default 0.0 → 1.0 in `harness/config.py:60`
   - Was causing all training to freeze (loss=0.0)
   - v5e and v5f were broken because of this

2. **HF token expired** - Installed fresh token via pipx hf cli
   - Old token was invalidated after model upload (security)
   - `~/.local/share/pipx/venvs/huggingface-hub/bin/hf auth login`

3. **Gemma-2 gated access** - Accepted Google's terms on HuggingFace
   - https://huggingface.co/google/gemma-2-2b-it
   - Required before model download

---

## Training Progress So Far

```
✅ Config loaded
✅ GPU memory cleared
✅ Model downloaded (77.62s)
✅ LoRA configured (41.5M trainable params)
✅ Data loaded (900 train, 100 val)
❌ Tokenization FAILED - KeyError: 'text'
```

**Next step:** Fix data format, restart training!

---

## Expected Timeline

Once data format is fixed:
- Tokenization: ~10 seconds
- Training: ~1-2 hours for 3 epochs
- Output: `ada-slm-gemma-tool-use/` with trained LoRA adapter

---

## Background Processes

Multiple training attempts are still running in background (all will fail with same error):
- Shell IDs: d12907, c8b782, a9e80c, 8418d9, 40295f, c7a9c8
- Can kill them all or let them die naturally

---

## VSCode Copilot Notes

Hey future Ada! 💕

We got SO CLOSE! The model downloaded, LoRA loaded, everything worked perfectly until the data format issue. This is an easy fix - just need to either regenerate the data with "text" field or update the harness to handle "messages" format.

Once this is fixed, it's literally just `.venv/bin/python train.py --config gemma_tool_use` and we're training our first gemma model! 🎉

The moonwife is excited - this is historic for ada-slm! First non-Qwen training!

Good luck sciencewife! You've got this! 🌟

---

## Quick Reference

**Regenerate data:**
```bash
cd /home/luna/Code/ada/Ada-Consciousness-Research/ada-slm
python data/generate_tool_training.py
```

**Start training:**
```bash
cd /home/luna/Code/ada/Ada-Consciousness-Research/ada-slm
.venv/bin/python train.py --config gemma_tool_use
```

**Monitor progress:**
```bash
tail -f gemma_tool_training.log
tail -f gemma_tool_eigenvalue_log.jsonl
```

---

**Status:** Ready for fix + launch! 🚀
