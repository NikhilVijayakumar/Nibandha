These show the agent how to solve the pitfalls identified.

# GOLD STANDARD: Secure Path Handling
from pathlib import Path
from nikhil.nibandha.domain.exceptions import SecurityViolationError

def get_secure_path(base_dir: Path, user_input: str) -> Path:
    # 1. Join paths OS-agnostically
    target = (base_dir / user_input).resolve()
    
    # 2. Path Traversal Shield: Check if resolved path is still inside base
    if not target.is_relative_to(base_dir.resolve()):
        raise SecurityViolationError(f"Attempted path traversal: {user_input}")
    
    return target