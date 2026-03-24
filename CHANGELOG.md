# Changelog

## 0.2.2 — 2026-03-19

### Added
- **`mirage_parm/`** — parameter-**card** UI (`mirage_parm/parameters.py`, `widgets.py`, `main.py`) aligned with **`Mirage-docs/mirage-parameter-cards.pdf`**: full **Filter** card (14 params); placeholder cards **Program**, **Wavesample**, **Sampling** to fill from the PDF.
- Console script **`mirage-parm`** → `mirage_parm.main:main`.
- **`shared/sysex.py`** — `send_mirage_parameter()`; **`mirage_orig.mirage_slider`** uses it for SysEx sends.

## 0.2.1 — 2026-03-19

### Changed
- Split **shared** vs **original UI** packages: **`shared/`** (config + `open_midi_output_port`), **`mirage_orig/`** (main window + `MirageSlider`). **`ensoniq/`** remains a thin compatibility layer (`mirage_main.py`, `mirage_slider.py`, `config.py` re-exports).

## 0.2.0 — 2026-03-19

### Added
- **`pyproject.toml`** — project metadata, runtime + optional `dev` deps, console script **`mirage-gui`**.
- **`readme-windows.md`** — PowerShell, `uv`, venv, and PATH notes (including user `Scripts` / `python -m uv`).
- **`scripts/`** — `add-python-scripts-to-path.ps1` / `.cmd` to put prefix + user `Scripts` on PATH.
- **`.python-version`** — default interpreter hint for `uv` / pyenv (`3.12`).

### Changed
- **`ensoniq/requirements.txt`** — `python-rtmidi` from PyPI (`==1.5.8`) instead of a local wheel path.
- **PySide6 stack** pinned to **6.10.2** (works with current Qt for Python releases on supported Pythons).
- **`ensoniq/mirage_main.py`** — removed duplicate **`MirageSlider`** class that shadowed `mirage_slider.py` when imported (fixes empty window for **`uv run mirage-gui`**).

### Fixed
- **`mirage-gui`** entry point now builds the same UI as **`python ensoniq/mirage_main.py`**.

## 0.1.0

- Initial packaged layout: `ensoniq` module, sliders + MIDI, `qt/` tutorials, docs under `Mirage-docs/`.
