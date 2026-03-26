# CI, uv, and GitHub Actions — reference

This document describes how continuous integration is set up for this repo, how it relates to local development, and **why we use [uv](https://docs.astral.sh/uv/) instead of plain pip** in CI.

## Why uv instead of pip

| Aspect | uv | pip alone |
|--------|----|-----------|
| **Lockfile** | `uv.lock` pins exact versions of every dependency (including transitive). CI installs the same graph every run. | `pip install -e ".[dev]"` resolves from PyPI at install time; versions can drift unless you pin everything manually. |
| **Speed** | Fast resolver and installs; optional caching via `setup-uv` keeps CI quick. | Slower on cold installs; caching is possible but separate from dependency resolution. |
| **Local ↔ CI parity** | The main readme already standardizes on `uv sync` / `uv run`. CI runs the same commands, so “works on my machine” matches what GitHub runs. | You’d maintain two stories: uv locally vs pip in CI, or pip everywhere with weaker reproducibility. |
| **Build** | `uv build` uses the project’s `[build-system]` (setuptools) without an extra `pip install build` step. | Typical pattern is `pip install build` then `python -m build`. |

Nothing stops you from using pip in a one-off environment; **the project’s intended workflow is uv + `uv.lock`**, so CI follows that.

## Where the workflow lives

- **File:** [`.github/workflows/ci.yml`](../.github/workflows/ci.yml)

## When it runs

- **Push** and **pull requests** targeting `main` or `master`
- **Manual runs:** *Actions* → *CI* → *Run workflow* (`workflow_dispatch`)

## What it does (overview)

1. Checks out the repository.
2. Installs **uv** and **Python 3.12** via [`astral-sh/setup-uv`](https://github.com/astral-sh/setup-uv) (with caching enabled).
3. Installs dependencies with **`uv sync --extra dev`** (same as local dev + tests).
4. Builds **sdist and wheel** with **`uv build`** (output under `dist/`).
5. Runs tests with **`uv run pytest -v`**.
6. Uploads **`dist/`** as a workflow artifact named `dist-<runner-os>` (e.g. `dist-macos-latest`, `dist-windows-latest`).

## OS matrix

Jobs run on **`macos-latest`** and **`windows-latest`** in parallel. `fail-fast: false` means if one OS fails, the other still finishes, which helps tell platform-specific issues apart.

## Headless Qt / PySide6

The workflow sets:

```text
QT_QPA_PLATFORM=offscreen
```

PySide6 tests need a Qt platform plugin. On GitHub-hosted runners there is no real display; **`offscreen`** uses Qt’s offscreen backend so widgets can be created and exercised without a GUI session.

## Matching CI locally

From the repo root (after [installing uv](https://docs.astral.sh/uv/getting-started/installation/)):

```bash
uv sync --extra dev
uv build
uv run pytest -v
```

To approximate the headless Qt environment (especially on Linux or in SSH sessions):

```bash
export QT_QPA_PLATFORM=offscreen   # Unix
set QT_QPA_PLATFORM=offscreen      # Windows cmd
$env:QT_QPA_PLATFORM="offscreen"   # PowerShell
```

## Artifacts

Each successful job uploads the contents of **`dist/`** (wheel + sdist). Download them from the workflow run page: *Summary* → *Artifacts*. They are convenient for smoke-testing installs; release publishing, if you add it later, would typically use tagged releases or trusted publishing instead of relying on PR artifacts alone.

## Further reading

- [uv documentation](https://docs.astral.sh/uv/)
- [Pytest-Qt](https://pytest-qt.readthedocs.io/) (Qt fixtures used by the test suite)
