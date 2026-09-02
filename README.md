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
| 3 | Generate Test Cases | Executable TCs, requirement gaps, and recommended tests; boundary tests (BTC-xxx) appended |
| 4 | Validate Test Schema | Validate test case structure and fields |
| 5 | Generate Negative Tests | Invalid-input, boundary, and error-handling test cases |
| 6 | Generate Security Tests | Core security suite (~7–8 STC-xxx); conditional tests deferred until architecture confirmed |
| 7 | Coverage/Traceability Validator | Audit coverage and traceability |
| 8 | Remediate Coverage Gaps | Append new scenarios/tests to close gaps from option 7 |
| 9 | Export Report | Export all session artifacts to `./reports/` |
| 10 | Exit | Quit |

### Recommended workflow

```
1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 7 → 9
```

1. **Analyze** the requirement
2. **Generate scenarios**, **test cases**, and **boundary value tests** (option 3 runs both TC and BTC generation)
3. **Validate** test case schema (option 4)
4. **Generate negative and security tests** (options 5–6) as needed
5. **Validate** coverage/traceability (option 7)
6. **Remediate** gaps (option 8; appends new SC/TC; does not overwrite)
7. **Re-validate** until coverage is acceptable
8. **Export** the full test plan

### Export layout

Option 9 creates a timestamped folder:

```
reports/test_plan_YYYYMMDD_HHMMSS/
├── requirement.md
├── analysis.md
├── test_scenarios.md
├── test_cases.md
├── schema_validation.md        # if option 4 was run
├── negative_tests.md           # if option 5 was run
├── security_tests.md           # if option 6 was run
├── coverage_traceability.md
├── remediation_log.md          # if option 8 was run
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
    generate_negative_tests_prompt.txt
    generate_boundary_tests_prompt.txt
    generate_security_tests_prompt.txt
    schema_validation_prompt.txt
    validate_negative_tests_prompt.txt
    validate_security_tests_prompt.txt
```

Edit prompt templates under `prompts/` to change LLM behavior. Wire new menu actions in `prompts.py` and `menu.py`.

## Troubleshooting

**LLM unavailable / CURSOR_API_KEY not set**

- Ensure `.env` is saved with a valid key
- Or `export CURSOR_API_KEY="cursor_..."`

**ModuleNotFoundError: ai_powered_agent**

- Run from the repo root with `PYTHONPATH=src`

**Option 6 says prompt not configured**

- Ensure `generate_security_tests()` exists in `prompts.py` and `generate_security_tests_prompt.txt` is present under `prompts/`
