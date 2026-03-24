"""
Backward-compatible entrypoint for the original Mirage UI.

Implementation: :mod:`mirage_orig.main`.
"""

from mirage_orig.main import MainWindow, MirageMain, main

__all__ = ["main", "MirageMain", "MainWindow"]

if __name__ == "__main__":
    main()
