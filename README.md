# PRP (Product Requirement Prompts) — Codex CLI Edition

- A curated set of prompts and PRP assets optimized for OpenAI Codex CLI

> Note: This repository is dedicated to Codex CLI usage only. If you are looking for the open-source Codex CLI, see: https://github.com/openai/codex/

---

Acknowledgement and provenance
- This repository was duplicated and adapted from: https://github.com/Wirasm/PRPs-agentic-eng
- All credit to the original author for the methodology and materials; this fork adapts usage and tooling for Codex CLI.

## Video Walkthrough

👉 https://www.youtube.com/watch?v=KVOZ9s1S9Gk&lc=UgzfwxvFjo6pKEyPo1R4AaABAg

### ☕ Support This Work

**Found value in these resources?**

👉 **Buy him a coffee:** https://coff.ee/wirasm

He spent a considerable amount of time creating these resources and prompts. If you find value in this project, please consider buying him a coffee to support his work.

That will help him maintain and improve the resources available for free

# AI Engineering Resources for Codex CLI

A comprehensive library of assets and context engineering for Agentic Engineering, optimized for OpenAI Codex CLI. This repository provides the Product Requirement Prompt (PRP) methodology, pre-configured command prompts, and documentation to enable AI-assisted development that delivers production-ready code on the first pass.

## What is PRP?

Product Requirement Prompt (PRP)

## In short

A PRP is PRD + curated codebase intelligence + agent/runbook—the minimum viable packet an AI needs to plausibly ship production-ready code on the first pass.

Product Requirement Prompt (PRP) is a structured prompt methodology first established in summer 2024 with context engineering at heart. A PRP supplies an AI coding agent with everything it needs to deliver a vertical slice of working software—no more, no less.

### How PRP Differs from Traditional PRD

A traditional PRD clarifies what the product must do and why customers need it, but deliberately avoids how it will be built.

A PRP keeps the goal and justification sections of a PRD yet adds three AI-critical layers:

### Context

Precise file paths and content, library versions and library context, code snippets examples. LLMs generate higher-quality code when given direct, in-prompt references instead of broad descriptions. Usage of a ai_docs/ directory to pipe in library and other docs.

## Getting Started

### Install Codex CLI

- Codex CLI repository: https://github.com/openai/codex/
- Quick install examples (see repo for latest):
  - `npm install -g @openai/codex`
  - or `brew install codex`

Then verify installation:

```bash
codex --version
```

### Using pre-configured prompts with `cx` / `cx.ps1`

This repo ships helper launchers that feed prompts from `.codex/commands/**` into Codex CLI.

- Linux/macOS:
  - List available prompts: `./cx --list`
  - Run a prompt: `./cx prp-base-create "Your feature idea"`
- Windows (PowerShell):
  - List prompts: `./cx.ps1 --list`
  - Run a prompt: `./cx.ps1 prp-base-create "Your feature idea"`

Notes
- The leading slash in the command name maps to files under `.codex/commands` or `%USERPROFILE%/.codex/commands`.
- Arguments after the command are passed to the prompt and can be referenced via `$ARGUMENTS` in the prompt files.
- The scripts will launch `codex` with a suggested approval mode.

## Using Codex Commands

The `.codex/commands/` directory contains pre-configured prompt files organized by topic (PRPs, reviews, Git, utilities). Use the `cx` launchers to run them from your terminal.

Examples

- Generate a comprehensive PRP:
  - macOS/Linux: `./cx prp-base-create "User authentication with OAuth2"`
  - Windows: `./cx.ps1 prp-base-create "User authentication with OAuth2"`
- Execute a PRP against the codebase:
  - macOS/Linux: `./cx prp-base-execute PRPs/my-feature.md`
  - Windows: `./cx.ps1 prp-base-execute PRPs/my-feature.md`
-
List all available prompts:

```bash
./cx --list   # or on Windows: ./cx.ps1 --list
```

## Using PRPs

### Creating a PRP

1. **Use the template** as a starting point:

   ```bash
   cp PRPs/templates/prp_base.md PRPs/my-feature.md
   ```

2. **Fill in the sections**:
   - Goal: What needs to be built
   - Why: Business value and user impact
   - Context: Documentation, code examples, gotchas
   - Implementation Blueprint: Tasks and pseudocode
   - Validation Loop: Executable tests

3. **Or use Codex via `cx` to generate one**:
   ```bash
   ./cx prp-base-create "Implement user authentication with JWT tokens"
   # Windows: ./cx.ps1 prp-base-create "Implement user authentication with JWT tokens"
   ```

### Executing a PRP

1. **Using Codex commands via `cx`/`cx.ps1`**:
   ```bash
   ./cx prp-base-execute PRPs/my-feature.md
   # Windows: ./cx.ps1 prp-base-execute PRPs/my-feature.md
   ```

### PRP Best Practices

1. **Context is King**: Include ALL necessary documentation, examples, and caveats
2. **Validation Loops**: Provide executable tests/lints the AI can run and fix
3. **Information Dense**: Use keywords and patterns from the codebase
4. **Progressive Success**: Start simple, validate, then enhance

### Example PRP Structure

```markdown
## Goal

Implement user authentication with JWT tokens

## Why

- Enable secure user sessions
- Support API authentication
- Replace basic auth with industry standard

## What

JWT-based authentication system with login, logout, and token refresh

### Success Criteria

- [ ] Users can login with email/password
- [ ] JWT tokens expire after 24 hours
- [ ] Refresh tokens work correctly
- [ ] All endpoints properly secured

## All Needed Context

### Documentation & References

- url: https://jwt.io/introduction/
  why: JWT structure and best practices

- file: src/auth/basic_auth.py
  why: Current auth pattern to replace

- doc: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
  section: OAuth2 with Password and JWT

### Known Gotchas

# CRITICAL: Use RS256 algorithm for production

# CRITICAL: Store refresh tokens in httpOnly cookies

# CRITICAL: Implement token blacklist for logout

## Implementation Blueprint

[... detailed implementation plan ...]

## Validation Loop

### Level 1: Syntax & Style

ruff check src/ --fix
mypy src/

### Level 2: Unit Tests

uv run pytest tests/test_auth.py -v

### Level 3: Integration Test

curl -X POST http://localhost:8000/auth/login \
 -H "Content-Type: application/json" \
 -d '{"email": "test@example.com", "password": "testpass"}'
```

## Project Structure Recommendations

```
your-project/
|-- .codex/
|   `-- commands/          # Codex CLI prompt files
|-- PRPs/
|   |-- templates/         # PRP templates
|   |-- ai_docs/           # Curated documentation for agents
|   |-- completed/         # Finished PRPs
|   `-- *.md               # Active PRPs
|-- AGENTS.md (optional)    # Project-specific Codex guidance
|-- src/                   # Your source code
`-- tests/                 # Your tests
```

## Setting Up AGENTS.md

Create a `AGENTS.md` file in your project root with:

1. **Core Principles**: KISS, YAGNI, etc.
2. **Code Structure**: File size limits, function length
3. **Architecture**: How your project is organized
4. **Testing**: Test patterns and requirements
5. **Style Conventions**: Language-specific guidelines
6. **Development Commands**: How to run tests, lint, etc.

See the example AGENTS.md in this repository for a comprehensive template.

## Advanced Usage

### Running Multiple Codex Sessions

Use Git worktrees for parallel development:

```bash
git worktree add -b feature-auth ../project-auth
git worktree add -b feature-api ../project-api

# Run Codex in each worktree
cd ../project-auth && codex
cd ../project-auth && codex
```

### CI/CD Integration

For non-interactive or CI usage, consult Codex CLI’s “Non-interactive / CI mode” documentation and adapt your workflow accordingly. A common approach is to call Codex with a specific prompt file from `.codex/commands/` and set the desired approval/sandbox flags per your CI needs. See `PRPs/ai_docs/codex_cli_readme.md` for details.

### Custom Commands

Create your own commands in `.codex/commands/`:

```markdown
# .codex/commands/my-command.md

# My Custom Command

Do something specific to my project.

## Arguments: $ARGUMENTS

[Your command implementation]
```

## Resources Included

## Documentation (PRPs/ai_docs/)

Purpose
- Central place for curated, high-signal documentation that Codex can read directly from your workspace.
- Includes Codex CLI quickstart and reference, plus framework- or language-specific docs you want agents to consult.

What’s inside
- `PRPs/ai_docs/codex_cli_readme.md`: Upstream Codex CLI README content for local reference.
- `PRPs/ai_docs/codex_cli_help.md`: Codex CLI usage tips and examples.
- `PRPs/ai_docs/codex_documentation.md`: Additional operational notes and scenarios.

How to use with PRPs
- In your PRP’s “All Needed Context”, reference files explicitly so Codex prioritizes them:

  ```markdown
  ## All Needed Context
  - file: PRPs/ai_docs/codex_cli_readme.md
    why: Exact Codex CLI behavior and flags
  - file: PRPs/ai_docs/codex_cli_help.md
    why: Quick usage reminders while executing tasks
  - file: PRPs/ai_docs/codex_documentation.md
    why: Known gotchas and environment considerations
  ```

Notes
- The `cx`/`cx.ps1` scripts do not auto-inject file contents; listing files in PRPs prompts Codex to open and use them during execution.
- Keep docs concise and scoped; prefer exact file paths and short excerpts over broad links.

---

Additional references
- Codex CLI repository: https://github.com/openai/codex/
- Source repository this work adapts: https://github.com/Wirasm/PRPs-agentic-eng

### Templates (PRPs/templates/)

- `prp_base.md`: Comprehensive base PRP with Goal/Why/What, All Needed Context, Implementation Blueprint, and Validation Loop.
- `prp_base_typescript.md`: Base PRP adapted for TypeScript/Node projects with TS-centric patterns.
- `prp_planning.md`: Planning-focused template covering scope, milestones, dependencies, and deliverables.
- `prp_spec.md`: Specification template for APIs/contracts with acceptance criteria.
- `prp_task.md`: Lightweight task template for small, well-bounded changes.

### Example PRP

- `example-from-workshop-mcp-crawl4ai-refactor-1.md` - Real-world refactoring example

## License

MIT License

## Support

He spent a considerable amount of time creating these resources and prompts. If you find value in this project, please consider buying him a coffee to support his work.

👉 **Buy him a coffee:** https://coff.ee/wirasm

---

Remember: The goal is one-pass implementation success through comprehensive context. Happy coding with Codex!
