# Helper scripts (Windows)

## `add-python-scripts-to-path`

Puts **that Python’s** `Scripts` folder on `PATH` (where `pip` installs `uv.exe`, `pytest.exe`, etc.).

### Important: `.cmd` vs `.ps1`

Running **`add-python-scripts-to-path.cmd`** starts a **new** PowerShell process. A **Session** PATH change applies only to that subprocess, **not** to your current PowerShell window—so `uv` may still be missing where you type commands.

- **To fix PATH in the window you’re using:** run the **`.ps1`** in that same PowerShell session (below).
- **Or** use **`user`** mode (permanent user PATH) and open a **new** terminal.

If `pip` used **`--user`**, `uv.exe` is usually under:

`%APPDATA%\Python\Python314\Scripts` (version folder matches your Python).

The script now resolves that path with **`sysconfig`** and, in **Session** / **User** mode, can append **both** prefix `Scripts` and user `Scripts` so `uv` works after `pip install --user uv`.

**PowerShell — this terminal only**

```powershell
.\scripts\add-python-scripts-to-path.ps1
```

**PowerShell — persist for your user** (open a new terminal after)

```powershell
.\scripts\add-python-scripts-to-path.ps1 -Scope User
```

**PowerShell — use the Python 3.12 launcher**

```powershell
.\scripts\add-python-scripts-to-path.ps1 -Python py -PythonArgs @("-3.12") -Scope User
```

**Command Prompt**

```cmd
scripts\add-python-scripts-to-path.cmd
scripts\add-python-scripts-to-path.cmd user
```

Each Python install has its **own** `Scripts` directory; run the script again after switching which `python` you care about.
