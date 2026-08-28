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


def _env_file_paths() -> list[Path]:
    project_root = Path(__file__).resolve().parents[2]
    paths: list[Path] = []
    for path in (project_root / ".env", Path.cwd() / ".env"):
        if path.is_file() and path not in paths:
            paths.append(path)
    return paths


def load_env_file() -> None:
    """Load environment variables from a .env file if present."""
    for path in _env_file_paths():
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, _, value = stripped.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if not key:
                continue
            # Prefer non-empty values from .env over empty shell exports.
            if value or key not in os.environ:
                os.environ[key] = value


def require_api_key() -> str:
    load_env_file()
    api_key = os.environ.get("CURSOR_API_KEY", "").strip()
    if api_key:
        return api_key

    env_path = next(iter(_env_file_paths()), None)
    if env_path is not None and "CURSOR_API_KEY=" in env_path.read_text(encoding="utf-8"):
        raise LLMUnavailableError(
            "LLM is not configured: CURSOR_API_KEY is empty in .env.\n"
            "Paste your key, save the file, and try again."
        )
    raise LLMUnavailableError(
        "LLM is not configured: CURSOR_API_KEY is not set.\n"
        "Add it to .env or export it from https://cursor.com/dashboard/integrations"
    )


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
