# Standard for calling external tools (Ruff, Pytest)
import subprocess
from typing import List

def run_external_tool(args: List[str]):
    """
    Standard: shell=False, command as List.
    """
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        shell=False, # Mandatory
        check=True
    )