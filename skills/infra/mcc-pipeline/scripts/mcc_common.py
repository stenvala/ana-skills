"""Shared utilities for MCC build and deploy scripts."""

import subprocess
import sys


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Run a command, print it, and fail immediately on non-zero exit code."""
    print("Running command:", " ".join(cmd), flush=True)
    sys.stdout.flush()
    sys.stderr.flush()
    check = kwargs.pop("check", True)
    result = subprocess.run(cmd, check=check, **kwargs)
    return result
