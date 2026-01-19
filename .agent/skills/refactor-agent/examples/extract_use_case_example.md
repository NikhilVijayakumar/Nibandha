# BEFORE: Monolithic Logic (Complexity 15)
class Archiver:
    def process(self):
        # ... validation logic ...
        # ... compression logic ...
        # ... cloud upload logic ...
        pass

# AFTER: Clean Refactor (Complexity 3 each)
# src/nikhil/nibandha/domain/use_cases/validate_path.py
class PathValidator:
    def execute(self, path: Path): ...

# src/nikhil/nibandha/archiver/core.py
class Archiver:
    def __init__(self, validator: PathValidator, uploader: CloudUploader):
        self.validator = validator
        self.uploader = uploader
        
    def process(self):
        # Clean, delegated logic
        self.validator.execute(self.path)
        # ...