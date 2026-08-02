import argparse
import sys
from pathlib import Path

from ai_powered_agent.agent import AgentRunError, AgentStartupError, run_agent
from ai_powered_agent.menu import run_menu


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI test planning agent powered by the Cursor SDK.",
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        help="Send a one-off prompt instead of opening the interactive menu",
    )
    parser.add_argument(
        "--file",
        "-f",
        type=Path,
        help="Read a one-off prompt from a text file",
    )
    parser.add_argument(
        "--cwd",
        type=Path,
        default=Path.cwd(),
        help="Workspace directory for the local agent (default: current directory)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports"),
        help="Directory for exported reports (default: ./reports)",
    )
    parser.add_argument(
        "--no-stream",
        action="store_true",
        help="Wait for the full response instead of streaming output",
    )
    args = parser.parse_args()

    if args.prompt or args.file or not sys.stdin.isatty():
        if args.file:
            prompt = args.file.read_text(encoding="utf-8")
        elif args.prompt:
            prompt = args.prompt
        else:
            prompt = sys.stdin.read()

        if not prompt.strip():
            parser.error("Provide a prompt via argument, --file, or stdin.")

        try:
            run_agent(prompt, cwd=args.cwd, stream=not args.no_stream)
        except AgentStartupError as err:
            print(err, file=sys.stderr)
            sys.exit(1)
        except AgentRunError as err:
            print(err, file=sys.stderr)
            sys.exit(2)
        return

    try:
        run_menu(cwd=args.cwd.resolve(), output_dir=args.output_dir.resolve())
    except KeyboardInterrupt:
        print("\nGoodbye.")
        sys.exit(0)
