import os
from pathlib import Path

from cursor_sdk import Agent, CursorAgentError, LocalAgentOptions


class AgentStartupError(Exception):
    pass


class AgentRunError(Exception):
    pass


def require_api_key() -> str:
    api_key = os.environ.get("CURSOR_API_KEY", "").strip()
    if not api_key:
        raise AgentStartupError(
            "CURSOR_API_KEY is not set. Export your key from "
            "https://cursor.com/dashboard/integrations"
        )
    return api_key


def run_agent(prompt: str, cwd: Path | None = None, stream: bool = True) -> str:
    """Send a prompt to the local Cursor agent and return the response."""
    workspace = (cwd or Path.cwd()).resolve()

    try:
        with Agent.create(
            model="composer-2.5",
            api_key=require_api_key(),
            local=LocalAgentOptions(cwd=str(workspace)),
        ) as agent:
            run = agent.send(prompt.strip())
            print(f"\nAgent: {agent.agent_id}  Run: {run.id}\n", flush=True)

            if stream:
                for message in run.messages():
                    if message.type == "assistant":
                        for block in message.message.content:
                            if block.type == "text":
                                print(block.text, end="", flush=True)

            result = run.wait()
            if result.status == "error":
                raise AgentRunError(f"Run failed: {result.id}")

            print()
            return run.text()
    except CursorAgentError as err:
        raise AgentStartupError(
            f"Agent startup failed: {err.message} (retryable={err.is_retryable})"
        ) from err
