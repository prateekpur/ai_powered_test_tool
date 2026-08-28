# AI Powered Agent

AI-assisted test planning tool. Uses the [Cursor SDK](https://cursor.com/docs/sdk/python) to analyze requirements, generate scenarios and test cases, validate coverage/traceability, remediate gaps, and export artifacts.

## Prerequisites

- Python 3.10+
- [Cursor API key](https://cursor.com/dashboard/integrations)
- `cursor-sdk` (`pip install cursor-sdk`)

## Setup

```bash
cd ai_powered_agent
python3 -m venv .venv
source .venv/bin/activate
pip install cursor-sdk
```

Configure your API key:

```bash
cp .env.example .env
# Edit .env and set CURSOR_API_KEY=cursor_...
```

The app loads `.env` from the project root automatically.

## Usage

Launch the interactive menu:

```bash
PYTHONPATH=src python3 -m ai_powered_agent
```

If installed as a package (`pip install -e .` when `pyproject.toml` is present):

```bash
ai-agent
```

### Menu options

| # | Option | Description |
|---|--------|-------------|
| 1 | Analyze Requirement | Capture requirement details and run analysis |
| 2 | Generate Test Scenarios | High-level scenarios from requirement + analysis |
| 3 | Generate Test Cases | Detailed test cases from scenarios |
| 4 | Generate Negative Tests | Negative test cases *(prompt not wired yet)* |
| 5 | Generate Security Tests | Security test cases *(prompt not wired yet)* |
| 6 | Coverage/Traceability Validator | Audit coverage and traceability |
| 7 | Remediate Coverage Gaps | Append new scenarios/tests to close gaps from option 6 |
| 8 | Export Report | Export all session artifacts to `./reports/` |
| 9 | Exit | Quit |

### Recommended workflow

```
1 → 2 → 3 → 6 → 7 → 6 → 8
```

1. **Analyze** the requirement
2. **Generate scenarios** and **test cases**
3. **Validate** coverage/traceability
4. **Remediate** gaps (appends new SC/TC; does not overwrite)
5. **Re-validate** until coverage is acceptable
6. **Export** the full test plan

### Export layout

Option 8 creates a timestamped folder:

```
reports/test_plan_YYYYMMDD_HHMMSS/
├── requirement.md
├── analysis.md
├── test_scenarios.md
├── test_cases.md
├── coverage_traceability.md
├── remediation_log.md          # if option 7 was run
├── test_report.md              # combined report
└── manifest.json
```

Only artifacts present in the session are written.

### One-off prompts (no menu)

```bash
PYTHONPATH=src python3 -m ai_powered_agent "Your prompt here"
PYTHONPATH=src python3 -m ai_powered_agent --file path/to/prompt.txt
```

## Project layout

```
src/ai_powered_agent/
  agent.py          # LLM wrapper, .env loading, error handling
  cli.py            # Command-line entry point
  menu.py           # Interactive menu
  models.py         # Requirement and RequirementAnalysis models
  prompts.py        # Prompt builders
  session.py        # Session state, remediation append, export
  prompts/
    analyse_prompt.txt
    generate_scenarios_prompt.txt
    generate_test_cases_prompt.txt
    coverage_traceability_validator_prompt.txt
    remediate_gaps_prompt.txt
```

Edit prompt templates under `prompts/` to change LLM behavior. Wire new menu actions in `prompts.py` and `menu.py`.

## Troubleshooting

**LLM unavailable / CURSOR_API_KEY not set**

- Ensure `.env` is saved with a valid key
- Or `export CURSOR_API_KEY="cursor_..."`

**ModuleNotFoundError: ai_powered_agent**

- Run from the repo root with `PYTHONPATH=src`

**Option 4 or 5 says prompt not configured**

- Add `generate_negative_tests()` / `generate_security_tests()` in `prompts.py` and matching `.txt` templates
