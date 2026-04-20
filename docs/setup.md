# Setup

## Install

```bash
cd browser-agent
pip install -e .
playwright install chromium
```

## Environment

Copy `.env.example` to `.env` and set your API key:

```bash
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY
```

Or export it directly:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

## Prerequisites

- Python 3.11+
- `gh` CLI — authenticated (`gh auth login`) for PR creation
- Chromium — installed via `playwright install chromium`

## Quick Start

```bash
# Free-form browser task
python -m src.cli run "Go to github.com and check my notifications"

# Fix vulnerabilities from Slack
python -m src.cli fix-vulns --repos-dir ~/Code
```
