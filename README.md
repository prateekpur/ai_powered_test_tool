# AI Powered Agent

Local [Cursor SDK](https://cursor.com/docs/sdk/python) agent for AI-assisted test planning.

## Prerequisites

- Python 3.10+
- [Cursor API key](https://cursor.com/dashboard/integrations)

## Setup

```bash
cd ai_powered_agent
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Copy the example env file and add your API key:

```bash
cp .env.example .env
export CURSOR_API_KEY="cursor_..."
```

## Usage

Launch the interactive menu:

```bash
ai-agent
```

Menu options:

1. Analyze Requirement
2. Generate Test Scenarios
3. Generate Test Cases
4. Generate Negative Tests
5. Generate Security Tests
6. Export Report
7. Exit

Exported reports are saved as Markdown files in `./reports/`.

Send a one-off prompt without the menu:

```bash
ai-agent "Summarize what this repository does"
ai-agent --file prompts/my-prompt.txt
```

## Project layout

```
src/ai_powered_agent/
  agent.py      # Cursor SDK wrapper
  cli.py        # Command-line entry point
  menu.py       # Interactive menu
  models.py     # Requirement and RequirementAnalysis models
  prompts.py    # Prompt builders (add your own)
  session.py    # In-memory session and report export
```
