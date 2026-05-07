# Solum-AI Workflow

Solum-AI uses a strict engineering workflow for coding tasks.

## Core loop

```text
read -> plan -> patch -> verify -> fix -> report
```

## Step 1: Read

Before proposing code changes, gather the relevant context:

- current files;
- logs;
- previous behavior;
- target behavior;
- constraints;
- build/test environment.

If context is missing, state what is missing. Do not invent it.

## Step 2: Plan

A good plan must include:

- target files/modules;
- expected changes;
- risks;
- verification method;
- what will not be done in this step.

## Step 3: Patch

A patch should be:

- minimal enough to review;
- complete enough to test;
- aligned with the original goal;
- not a fake placeholder unless explicitly marked as scaffold.

## Step 4: Verify

Verification can include:

- unit tests;
- integration tests;
- build commands;
- static checks;
- manual checklist;
- benchmark or eval run.

If verification was not run, the report must say so.

## Step 5: Fix

If verification fails, fix the exact failure instead of adding unrelated changes.

## Step 6: Report

Every final report should include:

- what changed;
- what was checked;
- what was not checked;
- known risks;
- next recommended step.

## Definition of done

A task is done only when the requested behavior is implemented and verified, or when the remaining gaps are explicitly documented.
