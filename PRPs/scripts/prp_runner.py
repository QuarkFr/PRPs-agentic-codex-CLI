#!/usr/bin/env -S uv run --script
"""Run an AI coding agent against a PRP.

KISS version - no repo-specific assumptions.

This version supports Codex CLI by default and can still target the Claude CLI.

Typical usage (Codex CLI default):
    uv run PRPs/scripts/prp_runner.py --prp test --interactive
    uv run PRPs/scripts/prp_runner.py --prp test --output-format json
    uv run PRPs/scripts/prp_runner.py --prp test --output-format stream-json

Arguments:
    --prp-path       Path to a PRP markdown file (overrides --prp)
    --prp            Feature key; resolves to PRPs/{feature}.md
    --driver         Which CLI to use: codex|claude (default: "codex")
    --cli            CLI executable name (default: inferred from driver: "codex" or "claude")
    --interactive    Run the model in chat mode; otherwise headless.
    --output-format  Output format for headless mode: text, json, stream-json (default: text)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterator, List
import shutil
import traceback

# Project root (repo root). This file is at PRPs/scripts/, so repo root is two levels up from PRPs/scripts/ (i.e., three parents from this file).
ROOT = Path(__file__).resolve().parent.parent.parent

META_HEADER = """Ingest and understand the Product Requirement Prompt (PRP) below in detail.

    # WORKFLOW GUIDANCE:

    ## Planning Phase
    - Think hard before you code. Create a comprehensive plan addressing all requirements.
    - Break down complex tasks into smaller, manageable steps.
    - Use the TodoWrite tool to create and track your implementation plan.
    - Identify implementation patterns from existing code to follow.

    ## Implementation Phase
    - Follow code conventions and patterns found in existing files.
    - Implement one component at a time and verify it works correctly.
    - Write clear, maintainable code with appropriate comments.
    - Consider error handling, edge cases, and potential security issues.
    - Use type hints to ensure type safety.

    ## Testing Phase
    - Test each component thoroughly as you build it.
    - Use the provided validation gates to verify your implementation.
    - Verify that all requirements have been satisfied.
    - Run the project tests when finished and output "DONE" when they pass.

    ## Example Implementation Approach:
    1. Analyze the PRP requirements in detail
    2. Search for and understand existing patterns in the codebase
    3. Search the Web and gather additional context and examples
    4. Create a step-by-step implementation plan with TodoWrite
    5. Implement core functionality first, then additional features
    6. Test and validate each component
    7. Ensure all validation gates pass

    ***When you are finished, move the completed PRP to the PRPs/completed folder***
    """


def build_prompt(prp_path: Path) -> str:
    return META_HEADER + prp_path.read_text()


def stream_json_output(process: subprocess.Popen) -> Iterator[Dict[str, Any]]:
    """Parse streaming JSON output line by line."""
    for line in process.stdout:
        line = line.strip()
        if line:
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse JSON line: {e}", file=sys.stderr)
                print(f"Line content: {line}", file=sys.stderr)


def handle_json_output(output: str) -> Dict[str, Any]:
    """Parse the JSON output from Claude Code."""
    try:
        return json.loads(output)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON output: {e}", file=sys.stderr)
        return {"error": "Failed to parse JSON output", "raw": output}


def _ensure_cli_available(executable: str) -> None:
    if not shutil.which(executable):
        sys.exit(
            f"CLI executable not found: '{executable}'. Set --cli or install it."
        )


def _build_cmd_codex(interactive: bool, output_format: str, cli: str, prompt: str) -> List[str]:
    """Construct Codex CLI command.

    Assumptions:
    - Interactive: start chat by passing the prompt as a positional arg (codex <prompt>).
    - Headless: accept prompt via -p and support --output-format.
    """
    if interactive:
        # Codex CLI expects the prompt as a single positional argument; flatten newlines to avoid truncation
        flat = " ".join(line.strip() for line in prompt.splitlines()).strip()
        return [cli, flat]
    # For headless, many Codex builds accept just the prompt; avoid unknown flags
    # We pass the prompt positionally and let the caller decide how to parse output
    flat = " ".join(line.strip() for line in prompt.splitlines()).strip()
    return [cli, flat]


def _build_cmd_claude(interactive: bool, output_format: str, cli: str, prompt: str) -> List[str]:
    if interactive:
        return [
            cli,
            "--allowedTools",
            "Edit,Bash,Write,MultiEdit,NotebookEdit,WebFetch,Agent,LS,Grep,Read,NotebookRead,TodoRead,TodoWrite,WebSearch",
        ]
    return [
        cli,
        "-p",
        prompt,
        "--allowedTools",
        "Edit,Bash,Write,MultiEdit,NotebookEdit,WebFetch,Agent,LS,Grep,Read,NotebookRead,TodoRead,TodoWrite,WebSearch",
        "--output-format",
        output_format,
    ]


def run_model(
    prompt: str,
    driver: str = "codex",
    cli: str | None = None,
    interactive: bool = False,
    output_format: str = "text",
) -> None:
    driver = driver.lower()
    # No-op driver for local validation without external CLIs
    if driver == "noop":
        marker = "PRP TEST OK"
        if interactive:
            # Simulate an interactive session by echoing the prompt and marker
            print("[noop] Interactive session start.\n")
            print(prompt)
            print(f"\n[noop] {marker}")
            return
        if output_format == "stream-json":
            events = [
                {"type": "system", "subtype": "init", "session_id": "noop-session"},
                {"type": "assistant", "message": {"content": "Reading PRP..."}},
                {"type": "assistant", "message": {"content": marker}},
                {
                    "type": "result",
                    "subtype": "success",
                    "result": marker,
                    "cost_usd": 0.0,
                    "duration_ms": 1,
                    "num_turns": 1,
                },
            ]
            for e in events:
                print(json.dumps(e))
            return
        if output_format == "json":
            print(
                json.dumps(
                    {
                        "type": "result",
                        "subtype": "success",
                        "result": marker,
                        "is_error": False,
                        "cost_usd": 0.0,
                        "duration_ms": 1,
                        "session_id": "noop-session",
                    }
                )
            )
            return
        # default text
        print(marker)
        return
    if cli is None:
        cli = "codex" if driver == "codex" else "claude"

    # Try to resolve the CLI path robustly on Windows if not found in PATH
    resolved_cli = shutil.which(cli)
    if resolved_cli is None and sys.platform.startswith("win"):
        # Attempt PowerShell-based resolution (matches Get-Command behavior)
        for pwsh in ("powershell", "pwsh"):
            try:
                ps = subprocess.run(
                    [pwsh, "-NoProfile", "-Command", f"(Get-Command {cli} -ErrorAction SilentlyContinue) | Select-Object -ExpandProperty Source"],
                    capture_output=True,
                    text=True,
                )
                candidate = ps.stdout.strip().strip("\r\n\t ")
                if candidate and Path(candidate).exists():
                    resolved_cli = candidate
                    break
            except Exception:
                # Ignore and continue
                pass

    if resolved_cli is None:
        if driver in ("codex", "claude"):
            print(
                f"CLI executable not found: '{cli}'. Falling back to local 'noop' driver.",
                file=sys.stderr,
            )
            return run_model(
                prompt,
                driver="noop",
                cli=None,
                interactive=interactive,
                output_format=output_format,
            )
    else:
        cli = resolved_cli

    # Build command per driver
    if driver == "codex":
        cmd = _build_cmd_codex(interactive, output_format, cli, prompt)
    elif driver == "claude":
        cmd = _build_cmd_claude(interactive, output_format, cli, prompt)
    else:
        sys.exit(f"Unknown driver: {driver} (expected 'codex' or 'claude')")

    if interactive:
        # Launch interactive Codex CLI seeded with positional prompt
        try:
            subprocess.run(cmd, check=True)
        except FileNotFoundError:
            print(
                f"Interactive CLI '{cmd[0]}' not found. Falling back to local 'noop' driver.",
                file=sys.stderr,
            )
            return run_model(
                prompt,
                driver="noop",
                cli=None,
                interactive=interactive,
                output_format=output_format,
            )
        except OSError as e:
            # Handle cases like Windows command length limits gracefully
            print(
                f"Interactive launch failed: {e}. Falling back to headless text run.",
                file=sys.stderr,
            )
            return run_model(
                prompt,
                driver=driver,
                cli=cli,
                interactive=False,
                output_format="text",
            )
        return

    # Headless execution paths
    if output_format == "stream-json":
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        try:
            for message in stream_json_output(process):
                if (
                    message.get("type") == "system"
                    and message.get("subtype") == "init"
                ):
                    print(
                        f"Session started: {message.get('session_id')}",
                        file=sys.stderr,
                    )
                elif message.get("type") == "assistant":
                    print(
                        f"Assistant: {message.get('message', {}).get('content', '')[:100]}...",
                        file=sys.stderr,
                    )
                elif message.get("type") == "result":
                    print(f"\nFinal result:", file=sys.stderr)
                    print(
                        f"  Success: {message.get('subtype') == 'success'}",
                        file=sys.stderr,
                    )
                    print(
                        f"  Cost: ${message.get('cost_usd', 0):.4f}", file=sys.stderr
                    )
                    print(
                        f"  Duration: {message.get('duration_ms', 0)}ms",
                        file=sys.stderr,
                    )
                    print(
                        f"  Turns: {message.get('num_turns', 0)}", file=sys.stderr
                    )
                    if message.get("result"):
                        print(
                            f"\nResult text:\n{message.get('result')}",
                            file=sys.stderr,
                        )

                print(json.dumps(message))

            process.wait()
            if process.returncode != 0:
                stderr = process.stderr.read()
                print(
                    f"Runner failed with exit code {process.returncode}",
                    file=sys.stderr,
                )
                print(f"Error: {stderr}", file=sys.stderr)
                sys.exit(process.returncode)

        except KeyboardInterrupt:
            process.terminate()
            print("\nInterrupted by user", file=sys.stderr)
            sys.exit(1)

    elif output_format == "json":
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
        except FileNotFoundError:
            print(
                f"Headless CLI '{cmd[0]}' not found. Falling back to local 'noop' driver.",
                file=sys.stderr,
            )
            return run_model(
                prompt,
                driver="noop",
                cli=None,
                interactive=interactive,
                output_format=output_format,
            )
        if result.returncode != 0:
            print(
                f"Runner failed with exit code {result.returncode}",
                file=sys.stderr,
            )
            print(f"Error: {result.stderr}", file=sys.stderr)
            sys.exit(result.returncode)

        json_data = handle_json_output(result.stdout)
        print(json.dumps(json_data, indent=2))

        if isinstance(json_data, dict) and json_data.get("type") == "result":
            print(f"\nSummary:", file=sys.stderr)
            print(
                f"  Success: {not json_data.get('is_error', False)}",
                file=sys.stderr,
            )
            print(
                f"  Cost: ${json_data.get('cost_usd', 0):.4f}", file=sys.stderr
            )
            print(
                f"  Duration: {json_data.get('duration_ms', 0)}ms",
                file=sys.stderr,
            )
            print(
                f"  Session: {json_data.get('session_id', 'unknown')}",
                file=sys.stderr,
            )

    else:
        subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a PRP with an LLM agent.")
    parser.add_argument(
        "--prp-path", help="Relative path to PRP file eg: PRPs/feature.md"
    )
    parser.add_argument(
        "--prp", help="The file name of the PRP without the .md extension eg: feature"
    )
    parser.add_argument(
        "--interactive", action="store_true", help="Launch interactive chat session"
    )
    parser.add_argument(
        "--driver",
        choices=["codex", "claude", "noop"],
        default="codex",
        help="Target driver: codex (default), claude, or noop (local simulation)",
    )
    parser.add_argument(
        "--cli",
        default=None,
        help="Override CLI executable name (defaults to 'codex' or 'claude' based on --driver)",
    )
    parser.add_argument(
        "--output-format",
        choices=["text", "json", "stream-json"],
        default="text",
        help="Output format for headless mode (default: text)",
    )
    args = parser.parse_args()

    if not args.prp_path and not args.prp:
        sys.exit("Must supply --prp or --prp-path")

    prp_path = Path(args.prp_path) if args.prp_path else ROOT / f"PRPs/{args.prp}.md"
    if not prp_path.exists():
        sys.exit(f"PRP not found: {prp_path}")

    os.chdir(ROOT)  # ensure relative paths match PRP expectations
    prompt = build_prompt(prp_path)
    try:
        run_model(
            prompt,
            driver=args.driver,
            cli=args.cli,
            interactive=args.interactive,
            output_format=args.output_format,
        )
    except SystemExit:
        # Let clean exits pass through without writing erreur.txt
        raise
    except Exception:
        # Write traceback for easier debugging on Windows
        err_path = ROOT / "erreur.txt"
        try:
            err_path.write_text(traceback.format_exc(), encoding="utf-8")
        except Exception:
            pass
        print(
            f"An unexpected error occurred. See '{err_path}' for details.",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
