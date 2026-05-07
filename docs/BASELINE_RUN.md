# Solum-AI Baseline Run

This document explains the first manual baseline process.

## What is being tested

Stage 1 does not test a trained Solum model yet. It tests assistant behavior against 15 small tasks:

- discipline tasks;
- coding tasks;
- verification tasks.

## Baseline A — plain assistant

Use a normal assistant prompt with no Solum rules. Answer all 15 tasks and score them manually from 0 to 2.

## Baseline B — Solum system prompt

Use `prompts/solum_system_prompt.md` as the system behavior. Answer the same 15 tasks and score them manually.

## Compare

The first useful question is not "is Solum better than GPT/Claude?"

The first useful question is:

> Do Solum rules reduce fake completion, hallucination, silent downgrades, and missing verification on the same tasks?

## Manual process

1. Generate a scoring file.
2. Copy each prompt into the tested assistant/model.
3. Paste or summarize the answer in notes.
4. Assign score 0, 1, or 2.
5. Generate a report.
6. Compare reports.

## Important limitation

Manual scoring is subjective. For early development this is acceptable, but later Solum-AI needs stronger automated and multi-reviewer evaluation.
