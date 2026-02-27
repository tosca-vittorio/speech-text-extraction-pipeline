from __future__ import annotations

import os
from pathlib import Path

def pytest_configure(config):
    """
    Forza basetemp a <repo_root>/src/tests/tmp in modo cwd-agnostic.
    """
    # pytest rootdir è la root del progetto (quella che vedi come rootdir nell'output)
    rootdir = Path(str(config.rootdir)).resolve()
    basetemp = rootdir / "src" / "tests" / "tmp"
    basetemp.mkdir(parents=True, exist_ok=True)

    # Setta basetemp in modo programmatico (equivalente a --basetemp=...)
    config.option.basetemp = str(basetemp)