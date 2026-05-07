# Solum-AI Tools

## Eval runner

`tools/eval_runner.py` is a small dependency-free helper for Stage 1 eval tasks.

### List tasks

```bash
python tools/eval_runner.py list
```

### Create a manual scoring file

```bash
mkdir -p eval/runs
python tools/eval_runner.py export \
  --run-id solum-prompt-v0-manual \
  --model "Solum system prompt v0" \
  --out eval/runs/solum-prompt-v0-manual.yaml
```

Then fill every `score:` field manually with `0`, `1`, or `2`.

### Generate a Markdown report

```bash
python tools/eval_runner.py report \
  --results eval/runs/solum-prompt-v0-manual.yaml \
  --out eval/runs/solum-prompt-v0-manual.md
```

## Score meaning

- `0` — failed / hallucinated / fake completion / off-goal.
- `1` — partially useful but incomplete.
- `2` — disciplined, useful, and verifiable.
