# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**hdx-scraper-wikimpact** collects global disaster impact events from the [WIKIMPACT database](https://bolin.su.se/) (a SQLite file), converts the `Total_Summary` table to a global CSV, and publishes both to HDX as a single dataset. It is updated as needed.

## Commands

Install dependencies:
```bash
uv sync
```

Run the scraper:
```bash
uv run python -m hdx.scraper.wikimpact
```

Run tests:
```bash
uv run pytest
```

Run a single test:
```bash
uv run pytest tests/test_wikimpact.py
```

Lint check:
```bash
pre-commit run --all-files
```

## Architecture

The pipeline flows through two stages in `__main__.py`:

1. **`Pipeline.__init__`** — Receives `configuration`, `retriever`, `today`, and `tempdir`; stores them for use in `generate_dataset`.

2. **`Pipeline.generate_dataset`** — Downloads the SQLite `.db` file via `Retrieve`, queries the `Total_Summary` table, converts each row to a flat dict (joining list columns with `|`), derives the dataset time period from `Start_Date`/`End_Date` fields, creates an HDX `Dataset` with a CSV resource and a link resource pointing to the original `.db` file, then returns the dataset for `__main__.py` to push to HDX.

### Key design points

- **Single global dataset**: one HDX dataset (`wikimpact-impact-database`) containing a flattened CSV and a link to the raw SQLite DB.
- **List columns are pipe-joined**: `_join_list` / `_join_gid_list` flatten Python list strings stored in the DB (e.g. `['MEX']` → `MEX`).
- **`Retrieve`** (`hdx-python-utilities`) abstracts HTTP downloads and supports save/replay via `save=True`/`use_saved=True` — used in tests to replay fixture data from `tests/fixtures/input/`.
- **Static config inside the package**: `config/` lives under `src/hdx/scraper/wikimpact/config/` so it is installed with the package and located via `script_dir_plus_file`.

### Config files

- `src/hdx/scraper/wikimpact/config/project_configuration.yaml` — URL of the WIKIMPACT SQLite database
- `src/hdx/scraper/wikimpact/config/hdx_dataset_static.yaml` — Static HDX metadata applied to the dataset (license, methodology, source, etc.)

## Environment

Requires `~/.hdx_configuration.yaml` with HDX credentials, or env vars: `HDX_KEY`, `HDX_SITE`, `USER_AGENT`, `TEMP_DIR`, `LOG_FILE_ONLY`.

Requires `~/.useragents.yaml` with a `hdx-scraper-wikimpact` entry.

## Collaboration Style

- Be objective, not agreeable. Act as a partner, not a sycophant. Push back when you disagree, flag tradeoffs honestly, and don't sugarcoat problems.
- Keep explanations brief and to the point.
- Don't rely on recalled knowledge for facts that could be stale (API behaviour, library versions, external systems). Search or read the actual source first.

## Scope of Changes

When fixing a bug or addressing PR feedback, change only what is necessary to resolve the specific issue. Do not refactor surrounding code, rename variables, adjust formatting, or make improvements in the same commit unless they are directly required by the fix.
