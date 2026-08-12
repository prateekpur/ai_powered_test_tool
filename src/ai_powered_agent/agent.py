import os
from pathlib import Path


class AgentStartupError(Exception):
    """LLM could not be started (config, install, or connectivity)."""

    def __init__(self, message: str, *, retryable: bool = False) -> None:
        super().__init__(message)
        self.retryable = retryable


class AgentRunError(Exception):
    """LLM run started but failed."""


class LLMUnavailableError(AgentStartupError):
    """LLM is not reachable or not configured."""


def require_api_key() -> str:
    api_key = os.environ.get("CURSOR_API_KEY", "").strip()
    if not api_key:
        raise LLMUnavailableError(
            "LLM is not configured: CURSOR_API_KEY is not set.\n"
            "Export your key from https://cursor.com/dashboard/integrations"
        )
    return api_key


def check_llm_available() -> None:
    """Verify the LLM can be used before sending a prompt."""
    require_api_key()
    try:
        import cursor_sdk  # noqa: F401
    except ImportError as err:
        raise LLMUnavailableError(
            "LLM client is not installed.\n"
            "Install it with: pip install cursor-sdk"
        ) from err


def _startup_error_message(err: Exception) -> LLMUnavailableError:
    message = getattr(err, "message", str(err))
    lower = message.lower()
    retryable = bool(getattr(err, "is_retryable", False))

    if "401" in message or "unauthorized" in lower or "api key" in lower:
        return LLMUnavailableError(
            "LLM authentication failed. Check that CURSOR_API_KEY is valid.",
            retryable=False,
        )
    if any(token in lower for token in ("connection", "network", "timeout", "timed out")):
        return LLMUnavailableError(
            "LLM is unavailable: could not connect to the service.\n"
            "Check your network connection and try again.",
            retryable=True,
        )
    if retryable:
        return LLMUnavailableError(
            f"LLM is temporarily unavailable: {message}\nTry again in a moment.",
            retryable=True,
        )
    return LLMUnavailableError(f"LLM is unavailable: {message}", retryable=False)


def run_agent(prompt: str, cwd: Path | None = None, stream: bool = True) -> str:
    """Send a prompt to the local Cursor agent and return the response."""
    check_llm_available()
    workspace = (cwd or Path.cwd()).resolve()

    try:
        from cursor_sdk import Agent, CursorAgentError, LocalAgentOptions
    except ImportError as err:
        raise LLMUnavailableError(
            "LLM client is not installed.\n"
            "Install it with: pip install cursor-sdk"
        ) from err

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
                raise AgentRunError(
                    f"LLM run failed (run id: {result.id}). "
                    "The service may be unavailable or the prompt could not be completed."
                )

            print()
            return run.text()
    except (ConnectionError, TimeoutError, OSError) as err:
        raise LLMUnavailableError(
            "LLM is unavailable: could not connect to the service.\n"
            f"Details: {err}",
            retryable=True,
        ) from err
    except CursorAgentError as err:
        raise _startup_error_message(err) from err
