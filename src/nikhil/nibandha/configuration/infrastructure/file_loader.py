import yaml
import json
from pathlib import Path
from typing import Type, TypeVar, Union
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class FileConfigLoader:
    """
    Generic loader for Pydantic configuration models from YAML or JSON files.
    """
    
    def load(self, path: Path, model: Type[T]) -> T:
        """
        Load configuration from a file and validate against the provided Pydantic model.
        
        Args:
            path: Path to the configuration file (YAML or JSON).
            model: The Pydantic model class to validate against.
            
        Returns:
            An instance of the specified model.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file format is not supported or invalid.
            ValidationError: If the data does not match the model schema.
        """
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
            
        content = path.read_text(encoding="utf-8")
        
        if path.suffix in (".yaml", ".yml"):
            data = yaml.safe_load(content)
        elif path.suffix == ".json":
            data = json.loads(content)
        else:
            raise ValueError(f"Unsupported configuration format: {path.suffix}")
            
        return model(**(data or {}))

    def save(self, path: Path, config: BaseModel) -> None:
        """
        Save configuration to a file.
        
        Args:
            path: Path to save the configuration to.
            config: The Pydantic model instance to save.
        """
        data = config.model_dump(mode="json")
        
        if path.suffix in (".yaml", ".yml"):
            path.write_text(yaml.dump(data, sort_keys=False), encoding="utf-8")
        elif path.suffix == ".json":
            path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        else:
            raise ValueError(f"Unsupported configuration format: {path.suffix}")
