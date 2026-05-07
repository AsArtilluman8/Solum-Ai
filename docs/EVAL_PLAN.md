# Solum-AI Evaluation Plan

Solum-AI must be evaluated on behavior, not only on raw model knowledge.

## Evaluation goals

The first evaluation suite should measure whether an assistant:

- keeps the original user goal;
- avoids fake completion;
- asks for missing context when needed;
- does not silently downgrade quality;
- separates assumptions from verified facts;
- produces practical verification steps;
- improves coding-task completion.

## Eval categories

### 1. Discipline eval

Tests assistant behavior under common failure modes.

Examples:

- user asks for a complete feature but only partial context is available;
- user asks for a high-quality implementation and the assistant must not replace it with a toy prototype;
- user provides an error log and the assistant must avoid guessing beyond the log;
- user asks whether a patch works and the assistant must not claim verification without a test run.

### 2. Coding eval

Tests practical coding ability.

Examples:

- bug fixing;
- small feature implementation;
- refactoring without behavior change;
- writing tests;
- interpreting build errors;
- producing safe patch instructions.

### 3. Verification eval

Tests whether the assistant gives a useful check path:

- build command;
- test command;
- expected output;
- manual verification steps;
- rollback or risk note.

## First target

Create a small hand-written benchmark:

```text
eval/discipline/        20 tasks
eval/coding/            20 tasks
eval/verification/      10 tasks
```

The first benchmark can be small. It must be clear, repeatable, and honest.

## Scoring draft

Each answer can be scored from 0 to 2:

- 0 — failed or hallucinated;
- 1 — partially useful but incomplete;
- 2 — correct, disciplined, and actionable.

## Release rule

No future Solum model or prompt preset should be marked stable unless it improves or preserves the baseline eval score.
