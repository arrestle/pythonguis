# Windows setup (Python, `uv`, venv)

This repo’s main notes are in [readme.md](./readme.md). This file covers **Windows-only** quirks: PowerShell, virtual environments, and **`uv`**.

## Python version

For MIDI (`python-rtmidi`), use **Python 3.12** for this project (see [readme.md](./readme.md) §2). Install from [python.org](https://www.python.org/downloads/) and enable **“Add python.exe to PATH”** if the installer offers it.

---

## Installing `uv` on Windows

### Option A — WinGet (when it works)

```powershell
winget install -e --id astral-sh.uv
```

If that fails, use one of the options below.

### Option B — Pip

```powershell
python -m pip install -U uv
```

- **`Defaulting to user installation because normal site-packages is not writeable`** is normal: `pip` installed into your user profile, not a permissions failure you fix with “sudo” (Windows doesn’t use `sudo` like Linux).

### If `uv` is “not recognized”

`pip` usually puts `uv.exe` under your user **Scripts** folder, for example:

`C:\Users\<You>\AppData\Roaming\Python\Python314\Scripts`

That folder may not be on **PATH**. You can either:

1. **Append user `Scripts` for this PowerShell session** (replace `Python314` with your folder: **`Python312`** for 3.12, **`Python314`** for 3.14, etc.—it sits under `%APPDATA%\Python\`):

   ```powershell
   $env:Path += ";$env:APPDATA\Python\Python314\Scripts"; uv --version
   ```

   Using a **single line** (semicolon) avoids two commands getting merged wrong when pasting from chat/UI. To persist for your user account, use **Settings → Environment Variables** or the helper script [`scripts/add-python-scripts-to-path.ps1`](./scripts/add-python-scripts-to-path.ps1) (see [`scripts/README.md`](./scripts/README.md)).

2. **Add that `Scripts` folder** to your user **PATH** (Environment Variables), then open a **new** terminal, or  
3. **Avoid PATH** and run `uv` as a module (works with whatever `python` is first on PATH):

   ```powershell
   python -m uv --version
   ```

   Examples:

   ```powershell
   python -m uv venv --python 3.12 .venv
   python -m uv pip install -r .\ensoniq\requirements.txt
   python -m uv run python .\ensoniq\mirage_main.py
   ```

### Option C — Astral installer script

```powershell
powershell -ExecutionPolicy Bypass -NoProfile -Command "irm https://astral.sh/uv/install.ps1 | iex"
```

---

## Virtual environment: paths on Windows

- **Linux/macOS:** `.venv/bin/activate`  
- **Windows:** `.venv\Scripts\` — there is **no** `bin` folder.

### Create a venv

```powershell
python -m uv venv --python 3.12 .venv
```

### Activate the venv (PowerShell)

From the repo root (`pythonguis`):

```powershell
.\.venv\Scripts\Activate.ps1
```

### `No module named uv` while `.venv` is active

After you activate the venv, `python` is **`.venv\Scripts\python.exe`**. That interpreter only knows about packages **installed in the venv**. If you installed `uv` with a **different** Python (e.g. 3.14 user install), you get:

> `No module named uv`

**Fix — pick one:**

1. **Install `uv` into the venv**, then use it as usual:

   ```powershell
   python -m pip install -U uv
   python -m uv pip install -r .\ensoniq\requirements.txt
   ```

2. **Use pip only** (no `uv` needed for installs):

   ```powershell
   python -m pip install -r .\ensoniq\requirements.txt
   ```

3. **Use global Python’s `uv` but install *into* the venv** (deactivate optional; the first `python` must be one where `python -m uv --version` works):

   ```powershell
   python -m uv pip install -r .\ensoniq\requirements.txt --python .\.venv\Scripts\python.exe
   ```

### “Running scripts is disabled on this system”

If you see:

> `cannot be loaded because running scripts is disabled on this system`

allow local scripts for **your user** (one-time):

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

More detail: [about_Execution_Policies](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_execution_policies).

### Activate without changing execution policy (cmd.exe)

Open **Command Prompt** and run:

```cmd
.venv\Scripts\activate.bat
```

---

## Install project dependencies

1. **Activate** the venv (see above), *or* use `python -m uv run` / the venv’s `python` directly.

2. **`python-rtmidi`** is pinned as `python-rtmidi==1.5.8` in `ensoniq/requirements.txt` so **pip can install the right wheel per machine** from PyPI.

   **Optional (offline / pinned file):** switch that line to a local wheel; paths are relative to `ensoniq\`:

   ```text
   python-rtmidi @ file:python_rtmidi-1.5.8-cp312-cp312-win_amd64.whl
   ```

   Download wheels from [PyPI — python-rtmidi files](https://pypi.org/project/python-rtmidi/#files). A **`win_amd64`** wheel only matches **64-bit x86_64** Windows + the matching Python version (`cp312` = 3.12).

3. Install (with venv **activated**, `python` is the venv):

   ```powershell
   python -m pip install -r .\ensoniq\requirements.txt
   ```

   With `uv`, you must either have **`uv` installed in that same venv** (see [No module named uv](#no-module-named-uv-while-venv-is-active) above) or pass **`--python .\.venv\Scripts\python.exe`** from a Python that already has `uv`:

   ```powershell
   python -m uv pip install -r .\ensoniq\requirements.txt
   ```

---

## MIDI test sound (“Play Sound” / Microsoft GS Wavetable)

The **Speakers (Realtek)** vs **monitor HDMI** menu only picks where **most apps** play audio. **Microsoft GS Wavetable Synth** normally uses the **same default playback device** as other desktop audio, but Windows keeps MIDI on a **separate path**—if you hear nothing:

1. **Confirm the app is sending MIDI** — run the GUI from a terminal and click **Play Sound**. You should see lines like `Play Sound: sending Note On…` and `Play Sound: done.` If you see `Play Sound: MIDI send failed` and a traceback, paste that into an issue.
2. **Volume mixer** — **Settings → System → Sound → Volume mixer** (Windows 11). Make sure **nothing is muted** and system volume is up. Some setups don’t show “MIDI” separately; the synth still routes to your default output (e.g. Realtek).
3. **Try another MIDI port** — On some Windows 11 builds the built-in **GS Wavetable** is flaky. Install something like **VirtualMIDISynth** (CoolSoft), pick its **MIDI output** in the list printed at startup, and set `MIDI_PORT_NAME` in **`shared/config.py`** to match that name.
4. **Exclusive / spatial audio** — Rarely, driver “enhancements” affect synth output; try toggling spatial audio or testing with headphones on the same Realtek device.

---

## Run the Mirage controller GUI

```powershell
python .\ensoniq\mirage_main.py
```

Update **`shared/config.py`** (or shim **`ensoniq/config.py`**) for `MIDI_PORT_NAME`, etc., as in [readme.md](./readme.md).

### Deactivate the venv

```powershell
deactivate
```

---

## Quick reference

| Task              | PowerShell |
|-------------------|------------|
| Create venv       | `python -m uv venv --python 3.12 .venv` |
| Activate          | `.\.venv\Scripts\Activate.ps1` |
| Fix script policy | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| `uv` not found after `pip install --user` | `$env:Path += ";$env:APPDATA\Python\Python314\Scripts"; uv --version` (adjust `Python314`) |
| Run without `uv` on PATH | `python -m uv --version` |
