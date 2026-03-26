# mirage_parm — documentation

Parameter-card UI for the Ensoniq Mirage (PySide6 + MIDI sysex). This folder holds **mirage_parm-only** docs; the rest of the repo may contain other packages.

## Requirements

- Python **3.12** (matches project `requires-python`; `uv` can install it if missing — see below)
- MIDI output reachable from the machine (interface, virtual MIDI, or synth bridge)

## Tooling: uv only

Use **[uv](https://docs.astral.sh/uv/)** for installs and runs. Do **not** use `python -m venv`, manual virtualenvs, or raw `pip install` outside what `uv` drives — **`uv sync`** creates and updates the project `.venv` for you.

## Install `uv`

### Windows

In **PowerShell** (recommended installer from Astral):

```text
powershell -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
```

Close and reopen the terminal, then check:

```text
uv --version
```

### macOS

**Option A — install script (any shell):**

```text
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Option B — Homebrew:**

```text
brew install uv
```

Then:

```text
uv --version
```

### Python 3.12 (if you do not have it)

From the repo root, uv can fetch the pinned version:

```text
uv python install 3.12
```

## Install project (from repo root)

```text
uv sync
```

## Run

```text
uv run mirage-parm
```

Or:

```text
uv run python -m mirage_parm.main
```

## Diagnostics

In the app: **Help → Diagnostics…** — platform, Python, PySide6, mido versions, `shared.config.MIDI_PORT_NAME`, the **opened** MIDI output name, and a fresh list of MIDI input/output ports from the OS. Use **Refresh** to re-query ports; **Copy to clipboard** when reporting issues.

## MIDI port

Outgoing MIDI uses `shared.config.MIDI_PORT_NAME`. That string must be a **substring** of one of your **MIDI output** port names (see `shared/midi.py`). Put the unique part of the right port into `shared/config.py`.

### Names the app actually uses

This project lists ports with **mido** (same library the GUI uses). From the **repo root**:

```text
uv run python -c "import mido; print(mido.get_output_names())"
```

You should see a Python list of strings. Pick the output that goes to your Mirage, USB–MIDI interface, or virtual MIDI cable, and set `MIDI_PORT_NAME` to a substring that matches **only** that entry (e.g. `Focusrite` or `IAC` on macOS).

### While running mirage_parm

On startup, the app prints **`Available MIDI Output Ports:`** and the same list. If opening fails, fix `MIDI_PORT_NAME` and run again.

### “Play test MIDI (GM)” — no sound

The button sends **General MIDI** (program 0 + short notes) to the output chosen by `MIDI_PORT_NAME`.

- **Software synth** (e.g. **Microsoft GS Wavetable Synth** on Windows — match the name from `mido.get_output_names()`): MIDI turns into audio inside Windows/macOS. That audio is played on the **system default output device** — headphones, built-in speakers, Bluetooth, etc. This app does **not** choose speakers vs headset; change **Settings → Sound → Output** (Windows) or **System Settings → Sound** (macOS).
- **Mirage or USB–MIDI only**: you hear the **instrument** or interface, not the PC’s speakers unless you also route audio back.

Run the app from a **terminal** and click the button again — it prints which port it used and any errors.

### Windows

- Use the **Python one-liner above** (or the app’s printed list). Windows Settings does **not** show the exact strings `mido` uses, so copying from the Python output is the reliable approach.
- If the list is empty, install drivers for your interface, plug it in, and ensure no other app has exclusive access if your driver behaves that way.

### macOS (MacBook)

- Use the **Python one-liner** or the app’s printed list for the exact names.
- **Audio MIDI Setup** (Applications → Utilities) shows connected MIDI devices and is useful to confirm the interface is seen; names there are usually **similar** to Core MIDI names in `mido.get_output_names()`, but always prefer the **Python list** for `config.py`.
- For **IAC Driver** (virtual bus), enable the IAC bus in Audio MIDI Setup if you use it; its name usually appears in the `mido` list as something like `IAC Driver Bus 1`.

## Editing parameters

Card layout and copy live in `mirage_parm/parameter_cards.json`. Reinstall or run from editable checkout so the packaged JSON is not stale.

## Layout code

- `mirage_parm/main.py` — window, scroll area, panel rows
- `mirage_parm/widgets.py` — cards, sliders, envelope layout
- `mirage_parm/parameters.py` — JSON → `CardSpec` / `ParmSpec`
