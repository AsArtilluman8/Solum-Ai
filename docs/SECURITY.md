# Solum-AI Security Policy

Security is part of the project foundation, not a later feature.

## Early security principles

- Do not train on private or stolen data.
- Do not claim model behavior is safe without testing.
- Do not allow autonomous agents to merge code, publish releases, or access secrets.
- Do not execute generated terminal commands without explicit user control.
- Do not store user files or private project data without clear consent.

## Model and dataset safety

Future model/data work must include:

- license review;
- PII removal;
- harmful-content filtering;
- eval reports;
- stable/experimental release labels;
- rollback path for bad releases.

## Agent safety

Future agents may propose, review, and report. They must not independently:

- merge pull requests;
- change governance rules;
- publish model weights;
- spend paid compute;
- access secrets;
- run destructive commands.

## Responsible disclosure

If a vulnerability is found, open a private report when private reporting is available. Until then, avoid posting exploit details publicly; create a minimal issue stating that a security concern exists and contact the maintainer.
