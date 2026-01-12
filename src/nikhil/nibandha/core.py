# src/nikhil/nibandha/core.py
import logging
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel

class AppConfig(BaseModel):
    """The definition of an app that wants to use Nibandha."""
    name: str
    custom_folders: List[str] = []
    log_level: str = "INFO"

class Nibandha:
    def __init__(self, config: AppConfig, root_name: str = ".Nibandha"):
        self.config = config
        self.root = Path(root_name) / config.name
        self.log_dir = self.root / "logs"

    def bind(self):
        """Creates the structure and binds the logger."""
        # 1. Create default and custom folders
        folders = ["logs"] + self.config.custom_folders
        for folder in folders:
            (self.root / folder).mkdir(parents=True, exist_ok=True)

        # 2. Setup standard logger
        self._init_logger()
        return self

    def _init_logger(self):
        log_file = self.log_dir / f"{self.config.name}.log"
        logging.basicConfig(
            level=self.config.log_level,
            format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.config.name)
        self.logger.info(f"Nibandha initialized at {self.root}")