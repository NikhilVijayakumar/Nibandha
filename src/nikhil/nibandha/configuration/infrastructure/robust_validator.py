import logging
from typing import Type, Any, Dict, List, Optional
from pydantic import BaseModel, TypeAdapter

logger = logging.getLogger(__name__)

class RobustConfigValidator:
    """
    Validator that recursively checks input data against a Pydantic model.
    It sanitizes the data by keeping valid fields and discarding invalid ones (triggering fallback to defaults),
    while maintaining a detailed audit log.
    """
    def __init__(self):
        self.audit_log: List[str] = []

    def validate_and_sanitize(self, model_class: Type[BaseModel], input_data: Dict[str, Any], parent_path: str = "") -> Dict[str, Any]:
        """
        Recursively validates input_data against model_class.
        Returns a dictionary containing ONLY valid fields. Invalid fields are omitted,
        allowing Pydantic to fall back to their default values during instantiation.
        Populates self.audit_log with decisions.
        """
        clean_data = {}
        
        if input_data is None:
             # Just return empty, defaults will take over
             return {}
             
        if not isinstance(input_data, dict):
            self.audit_log.append(f"[WARNING] {parent_path or 'Root'}: Input is not a dictionary ({type(input_data).__name__}). Using defaults.")
            return {}

        for field_name, field_info in model_class.model_fields.items():
            full_path = f"{parent_path}.{field_name}" if parent_path else field_name
            
            # 1. Missing fields - skip (defaults used later)
            if field_name not in input_data:
                continue

            value = input_data[field_name]
            field_type = field_info.annotation
            
            # 2. Check for Pydantic Model (Direct or Optional/Union wrapped)
            # Simplistic check: if it's a class and subclass of BaseModel
            # For robust production usage, we might need to unwrap types, but Nibandha config is flat enough.
            is_model = False
            target_model = field_type
            
            # Handle simple Optional[T] or basic types
            origin = getattr(field_type, "__origin__", None)
            if isinstance(field_type, type) and issubclass(field_type, BaseModel):
                is_model = True
            
            # Special handling: If value is a dict and target is a model, recurse
            # This allows partial recovery inside nested configs (e.g., valid 'enabled' but invalid 'level')
            if is_model and isinstance(value, dict):
                sub_validator = RobustConfigValidator()
                # Recurse
                sub_clean = sub_validator.validate_and_sanitize(target_model, value, full_path)
                # We always accept the sub-clean dict, because validate_and_sanitize guarantees it returns a valid dict (empty or partial)
                # However, if sub_clean is empty, should we include it? Yes, let sub-model defaults apply.
                clean_data[field_name] = sub_clean
                self.audit_log.extend(sub_validator.audit_log)
                continue

            # 3. Standard Validation for primitives or mismatch types
            try:
                adapter = TypeAdapter(field_type)
                valid_value = adapter.validate_python(value)
                clean_data[field_name] = valid_value
                self.audit_log.append(f"[VALID]   {full_path}: Accepted.")
            except Exception as e:
                # REJECT invalid field, do NOT include in clean_data
                # This triggers fallback to default value defined in the Model
                msg = f"[INVALID] {full_path}: Rejected value '{value}' ({type(e).__name__}). Using Default."
                self.audit_log.append(msg)
                logger.warning(msg)

        return clean_data
