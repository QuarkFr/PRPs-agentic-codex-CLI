# AGENTS.md

Guidance for Codex CLI (open‑source) agents working in this repository. This project is a PRP (Product Requirement Prompt) Framework optimized for agentic engineering with validation-first execution.

## Project Nature

- Purpose: Enable one-pass implementation by combining PRD scope with rich, concrete context and executable validation.
- Mantra: Context is King • Validation First • Keep it simple • Avoid novelty when patterns exist.

## How Codex CLI Should Work Here

- Tools: Use `apply_patch` to edit files, `shell` to run read/build/test commands, and `update_plan` to keep a concise plan with one in-progress step.
- Preambles: Before tool calls, send a short 1–2 sentence note describing what you’ll do next.
- Progress: Share brief status updates for larger tasks; keep messages concise and actionable.
- Scope: Make focused, minimal changes; don’t fix unrelated issues unless explicitly requested.
- Approvals/Sandbox: Some environments restrict writes/network; request escalations only when necessary and explain why.

## Core Methodology (PRP)

PRP = PRD + curated codebase intelligence + agent/runbook + executable validation gates.

Each PRP should include:
- Goal/Why/What: Clear outcomes, business value, user-visible behavior.
- All Needed Context: Precise file paths, code snippets, library versions, URLs, known gotchas.
- Implementation Blueprint: Dependency-ordered tasks, naming/placement guidance, pseudocode.
- Validation Loop: Concrete commands for syntax/style, unit, and integration checks.

## Repository Components

- `PRPs/templates/`: Base/spec/planning/task templates for drafting PRPs.
- `PRPs/ai_docs/`: Curated reference docs to inject exact external knowledge.
- `PRPs/scripts/prp_runner.py`: Minimal runner that feeds a PRP into a CLI LLM. Note: It targets the `claude` CLI; use as a reference when operating purely inside Codex CLI.
- `.claude/commands/`: Slash-command prompts for Claude Code. In Codex CLI, treat these as reusable prompt content rather than invokable commands.
- `claude_md_files/`: Example framework-specific CLAUDE.md files (Astro, Node, Python, React, Java) for inspiration.

## Standard Workflow (Codex CLI)

1) Plan
- Read the relevant PRP or create one from `PRPs/templates/`.
- Use `update_plan` to list meaningful steps (keep one in progress).

2) Implement
- Identify existing patterns in the repo; match structure, naming, and style.
- Edit files with `apply_patch`; keep diffs minimal and localized.

3) Validate
- Run validation gates defined in the PRP (e.g., lint/type/test/integration). If tools aren’t configured here, propose commands and add tests only when requested.

4) Document
- Update PRP status, add short usage notes or README deltas when relevant.

5) Handoff
- Summarize what changed, where, and how to validate locally.

## Validation Gates (Examples)

- Level 1: Syntax & Style (example)
  - `ruff check --fix` and `mypy .` (Python projects)
- Level 2: Unit Tests
  - `uv run pytest tests/ -v`
- Level 3: Integration Checks
  - `uv run <app>` and `curl` scripted flows

Only run commands that exist/configured in the target repo. When missing, recommend setups succinctly instead of inventing them.

## Anti‑Patterns

- Skipping validation or adding generic, non-executable guidance.
- Vague references instead of exact files/paths/URLs.
- Creating new patterns when templates/conventions exist.
- Broad refactors outside the requested scope.
- Adding dependencies/config without explicit user approval.

## Working With `.claude/commands/`

- Treat these markdown files as high-quality prompt snippets and process guides.
- When the repo references a Claude slash command, translate it into Codex CLI steps: author a PRP, then implement/validate directly.

## Using `PRPs/scripts/prp_runner.py`

- The runner is designed for the `claude` CLI. In Codex CLI contexts without that binary, you can:
  - Author/curate PRPs and implement changes directly.
  - Mirror the PRP’s Validation Loop using available local tools.
  - If users have `claude` locally, provide the exact commands to run.

## Coding Guidelines (Codex CLI)

- Minimal, focused diffs; preserve existing style; avoid one-letter names.
- No unsolicited license headers or sweeping rewrites.
- Don’t commit or branch unless explicitly asked.
- If adding tests/docs is logical and consistent with repo patterns, do so; otherwise propose them.

## Quickstart (Agent)

1. Skim `README.md` and the relevant PRP/template.
2. Create or refine a PRP, ensuring “No Prior Knowledge” completeness.
3. Plan with `update_plan` and implement with `apply_patch`.
4. Run the PRP’s validation gates (or propose equivalents if missing).
5. Summarize changes and remaining follow-ups succinctly.

Remember: Optimize for one-pass success via dense, actionable context and executable validation.

