"""Form service for handling form operations like save, load, new, etc."""

import json
import os
from pathlib import Path
from typing import Optional
import logging

from ..models.form_model import FormModel, FieldType
from ..models.field_factory import FieldFactory


class FormServiceError(Exception):
    """Base exception for form service errors"""
    pass


class FormValidationError(FormServiceError):
    """Exception for form validation errors"""
    pass


class FormService:
    """Service for managing form operations"""
    
    def __init__(self, forms_directory: Optional[str] = None):
        """Initialize form service with optional forms directory"""
        if forms_directory is None:
            # Default to user's documents directory
            home = Path.home()
            forms_directory = home / "Documents" / "BFB Forms"
        
        self.forms_dir = Path(forms_directory)
        self.forms_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
    def create_new_form(self, title: str = "Untitled Form") -> FormModel:
        """Create a new empty form"""
        if not title or not title.strip():
            title = "Untitled Form"
            
        return FormModel(
            title=title.strip(),
            description="",
            fields=[]
        )
    
    def validate_form(self, form: FormModel) -> list[str]:
        """Validate form and return list of validation errors"""
        errors = []
        
        if not form.title or not form.title.strip():
            errors.append("Form title is required")
            
        if len(form.title.strip()) > 255:
            errors.append("Form title must be 255 characters or less")
            
        # Validate fields
        field_ids = set()
        for i, field in enumerate(form.fields):
            field_prefix = f"Field {i + 1}"
            
            # Check for duplicate IDs
            if field.id is not None:
                if field.id in field_ids:
                    errors.append(f"{field_prefix}: Duplicate field ID {field.id}")
                else:
                    field_ids.add(field.id)
            
            # Validate field properties
            if not field.label or not field.label.strip():
                errors.append(f"{field_prefix}: Field label is required")
                
            if len(field.label) > 255:
                errors.append(f"{field_prefix}: Field label must be 255 characters or less")
                
            # Validate choice fields have choices
            if field.type in [FieldType.SELECT, FieldType.MULTISELECT, FieldType.RADIO, FieldType.CHECKBOX]:
                if not field.choices or len(field.choices) == 0:
                    errors.append(f"{field_prefix}: Choice fields must have at least one choice")
                else:
                    # Validate choices
                    for j, choice in enumerate(field.choices):
                        if not choice.text or not choice.text.strip():
                            errors.append(f"{field_prefix}, Choice {j + 1}: Choice text is required")
                            
            # Validate file upload settings
            if field.type == FieldType.FILEUPLOAD:
                if field.maxFileSize and field.maxFileSize > 100:  # 100MB limit
                    errors.append(f"{field_prefix}: Maximum file size cannot exceed 100MB")
                    
            # Validate HTML content
            if field.type == FieldType.HTML:
                if not field.content or not field.content.strip():
                    errors.append(f"{field_prefix}: HTML fields must have content")
                    
        return errors
    
    def save_form(self, form: FormModel, filename: Optional[str] = None, validate: bool = True) -> str:
        """Save form to JSON file. Returns the filename used."""
        try:
            # Validate form if requested
            if validate:
                errors = self.validate_form(form)
                if errors:
                    raise FormValidationError(f"Form validation failed: {'; '.join(errors)}")
            
            if filename is None:
                # Generate filename from form title
                safe_title = "".join(c for c in form.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_title = safe_title.replace(' ', '_')
                if not safe_title:
                    safe_title = "untitled_form"
                filename = f"{safe_title}.json"
            
            # Ensure .json extension
            if not filename.endswith('.json'):
                filename += '.json'
                
            file_path = self.forms_dir / filename
            
            # Handle duplicate names by adding number
            counter = 1
            original_path = file_path
            while file_path.exists():
                name_part = original_path.stem
                extension = original_path.suffix
                file_path = self.forms_dir / f"{name_part}_{counter}{extension}"
                counter += 1
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(form.model_dump(), f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Form saved successfully: {file_path.name}")
            return file_path.name
            
        except Exception as e:
            self.logger.error(f"Failed to save form: {str(e)}")
            raise FormServiceError(f"Failed to save form: {str(e)}")
    
    def load_form(self, filename: str) -> FormModel:
        """Load form from JSON file"""
        try:
            file_path = self.forms_dir / filename
            
            if not file_path.exists():
                raise FileNotFoundError(f"Form file not found: {filename}")
                
            with open(file_path, 'r', encoding='utf-8') as f:
                form_data = json.load(f)
                
            form = FormModel.model_validate(form_data)
            self.logger.info(f"Form loaded successfully: {filename}")
            return form
            
        except json.JSONDecodeError as e:
            raise FormServiceError(f"Invalid form file format: {str(e)}")
        except Exception as e:
            self.logger.error(f"Failed to load form: {str(e)}")
            raise FormServiceError(f"Failed to load form: {str(e)}")
    
    def list_forms(self) -> list[str]:
        """List all available form files"""
        try:
            return sorted([f.name for f in self.forms_dir.glob('*.json')])
        except Exception as e:
            self.logger.error(f"Failed to list forms: {str(e)}")
            return []
    
    def delete_form(self, filename: str) -> bool:
        """Delete a form file. Returns True if successful."""
        try:
            file_path = self.forms_dir / filename
            
            if file_path.exists():
                file_path.unlink()
                self.logger.info(f"Form deleted successfully: {filename}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to delete form: {str(e)}")
            return False
    
    def get_forms_directory(self) -> str:
        """Get the forms directory path"""
        return str(self.forms_dir)
    
    def export_form(self, form: FormModel, export_path: str, validate: bool = True) -> None:
        """Export form to specific path"""
        try:
            # Validate form if requested
            if validate:
                errors = self.validate_form(form)
                if errors:
                    raise FormValidationError(f"Form validation failed: {'; '.join(errors)}")
                    
            export_path = Path(export_path)
            
            # Ensure parent directory exists
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(form.model_dump(), f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Form exported successfully: {export_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to export form: {str(e)}")
            raise FormServiceError(f"Failed to export form: {str(e)}")
    
    def import_form(self, import_path: str) -> FormModel:
        """Import form from specific path"""
        try:
            import_path = Path(import_path)
            
            if not import_path.exists():
                raise FileNotFoundError(f"Import file not found: {import_path}")
                
            with open(import_path, 'r', encoding='utf-8') as f:
                form_data = json.load(f)
                
            form = FormModel.model_validate(form_data)
            self.logger.info(f"Form imported successfully: {import_path}")
            return form
            
        except json.JSONDecodeError as e:
            raise FormServiceError(f"Invalid form file format: {str(e)}")
        except Exception as e:
            self.logger.error(f"Failed to import form: {str(e)}")
            raise FormServiceError(f"Failed to import form: {str(e)}")
    
    def add_field_to_form(self, form: FormModel, field_type: FieldType, position: Optional[int] = None) -> FormModel:
        """Add a new field to the form at specified position (or end)"""
        try:
            # Get next available field ID
            max_id = 0
            if form.fields:
                max_id = max(field.id or 0 for field in form.fields)
            
            new_field = FieldFactory.create_field(field_type, field_id=max_id + 1)
            
            if position is None or position >= len(form.fields):
                form.fields.append(new_field)
            else:
                form.fields.insert(position, new_field)
                
            self.logger.info(f"Added {field_type} field to form")
            return form
            
        except Exception as e:
            self.logger.error(f"Failed to add field: {str(e)}")
            raise FormServiceError(f"Failed to add field: {str(e)}")
    
    def remove_field_from_form(self, form: FormModel, field_id: int) -> FormModel:
        """Remove a field from the form by ID"""
        try:
            original_count = len(form.fields)
            form.fields = [f for f in form.fields if f.id != field_id]
            
            if len(form.fields) == original_count:
                raise FormServiceError(f"Field with ID {field_id} not found")
                
            self.logger.info(f"Removed field with ID {field_id}")
            return form
            
        except Exception as e:
            self.logger.error(f"Failed to remove field: {str(e)}")
            raise FormServiceError(f"Failed to remove field: {str(e)}")
    
    def duplicate_field_in_form(self, form: FormModel, field_id: int) -> FormModel:
        """Duplicate a field in the form"""
        try:
            field_to_duplicate = None
            field_position = -1
            
            for i, field in enumerate(form.fields):
                if field.id == field_id:
                    field_to_duplicate = field
                    field_position = i
                    break
                    
            if field_to_duplicate is None:
                raise FormServiceError(f"Field with ID {field_id} not found")
                
            # Get next available field ID
            max_id = max(field.id or 0 for field in form.fields)
            
            # Create duplicate with new ID
            duplicate_data = field_to_duplicate.model_dump()
            duplicate_data['id'] = max_id + 1
            duplicate_data['label'] = f"{duplicate_data['label']} (Copy)"
            
            duplicate_field = type(field_to_duplicate).model_validate(duplicate_data)
            
            # Insert after original field
            form.fields.insert(field_position + 1, duplicate_field)
            
            self.logger.info(f"Duplicated field with ID {field_id}")
            return form
            
        except Exception as e:
            self.logger.error(f"Failed to duplicate field: {str(e)}")
            raise FormServiceError(f"Failed to duplicate field: {str(e)}")
    
    def move_field_up(self, form: FormModel, field_id: int) -> FormModel:
        """Move a field up in the form"""
        try:
            for i, field in enumerate(form.fields):
                if field.id == field_id:
                    if i > 0:
                        # Swap with previous field
                        form.fields[i], form.fields[i-1] = form.fields[i-1], form.fields[i]
                        self.logger.info(f"Moved field {field_id} up")
                    else:
                        raise FormServiceError("Field is already at the top")
                    break
            else:
                raise FormServiceError(f"Field with ID {field_id} not found")
                
            return form
            
        except Exception as e:
            self.logger.error(f"Failed to move field up: {str(e)}")
            raise FormServiceError(f"Failed to move field up: {str(e)}")
    
    def move_field_down(self, form: FormModel, field_id: int) -> FormModel:
        """Move a field down in the form"""
        try:
            for i, field in enumerate(form.fields):
                if field.id == field_id:
                    if i < len(form.fields) - 1:
                        # Swap with next field
                        form.fields[i], form.fields[i+1] = form.fields[i+1], form.fields[i]
                        self.logger.info(f"Moved field {field_id} down")
                    else:
                        raise FormServiceError("Field is already at the bottom")
                    break
            else:
                raise FormServiceError(f"Field with ID {field_id} not found")
                
            return form
            
        except Exception as e:
            self.logger.error(f"Failed to move field down: {str(e)}")
            raise FormServiceError(f"Failed to move field down: {str(e)}")