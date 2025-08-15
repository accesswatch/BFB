"""Form service for handling form operations like save, load, new, etc."""

import json
import os
from pathlib import Path
from typing import Optional
from ..models.form_model import FormModel, FieldType
from ..models.field_factory import FieldFactory


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
        
    def create_new_form(self, title: str = "Untitled Form") -> FormModel:
        """Create a new empty form"""
        return FormModel(
            title=title,
            description="",
            fields=[]
        )
    
    def save_form(self, form: FormModel, filename: Optional[str] = None) -> str:
        """Save form to JSON file. Returns the filename used."""
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
            
        return file_path.name
    
    def load_form(self, filename: str) -> FormModel:
        """Load form from JSON file"""
        file_path = self.forms_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Form file not found: {filename}")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            form_data = json.load(f)
            
        return FormModel.model_validate(form_data)
    
    def list_forms(self) -> list[str]:
        """List all available form files"""
        return [f.name for f in self.forms_dir.glob('*.json')]
    
    def delete_form(self, filename: str) -> bool:
        """Delete a form file. Returns True if successful."""
        file_path = self.forms_dir / filename
        
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    
    def get_forms_directory(self) -> str:
        """Get the forms directory path"""
        return str(self.forms_dir)
    
    def export_form(self, form: FormModel, export_path: str) -> None:
        """Export form to specific path"""
        export_path = Path(export_path)
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(form.model_dump(), f, indent=2, ensure_ascii=False)
    
    def import_form(self, import_path: str) -> FormModel:
        """Import form from specific path"""
        import_path = Path(import_path)
        
        if not import_path.exists():
            raise FileNotFoundError(f"Import file not found: {import_path}")
            
        with open(import_path, 'r', encoding='utf-8') as f:
            form_data = json.load(f)
            
        return FormModel.model_validate(form_data)
    
    def add_field_to_form(self, form: FormModel, field_type: FieldType, position: Optional[int] = None) -> FormModel:
        """Add a new field to the form at specified position (or end)"""
        # Get next available field ID
        max_id = 0
        if form.fields:
            max_id = max(field.id or 0 for field in form.fields)
        
        new_field = FieldFactory.create_field(field_type, field_id=max_id + 1)
        
        if position is None or position >= len(form.fields):
            form.fields.append(new_field)
        else:
            form.fields.insert(position, new_field)
            
        return form
    
    def remove_field_from_form(self, form: FormModel, field_id: int) -> FormModel:
        """Remove a field from the form by ID"""
        form.fields = [f for f in form.fields if f.id != field_id]
        return form
    
    def duplicate_field_in_form(self, form: FormModel, field_id: int) -> FormModel:
        """Duplicate a field in the form"""
        field_to_duplicate = None
        field_position = -1
        
        for i, field in enumerate(form.fields):
            if field.id == field_id:
                field_to_duplicate = field
                field_position = i
                break
                
        if field_to_duplicate is None:
            raise ValueError(f"Field with ID {field_id} not found")
            
        # Get next available field ID
        max_id = max(field.id or 0 for field in form.fields)
        
        # Create duplicate with new ID
        duplicate_data = field_to_duplicate.model_dump()
        duplicate_data['id'] = max_id + 1
        duplicate_data['label'] = f"{duplicate_data['label']} (Copy)"
        
        duplicate_field = type(field_to_duplicate).model_validate(duplicate_data)
        
        # Insert after original field
        form.fields.insert(field_position + 1, duplicate_field)
        
        return form
    
    def move_field_up(self, form: FormModel, field_id: int) -> FormModel:
        """Move a field up in the form"""
        for i, field in enumerate(form.fields):
            if field.id == field_id and i > 0:
                # Swap with previous field
                form.fields[i], form.fields[i-1] = form.fields[i-1], form.fields[i]
                break
        return form
    
    def move_field_down(self, form: FormModel, field_id: int) -> FormModel:
        """Move a field down in the form"""
        for i, field in enumerate(form.fields):
            if field.id == field_id and i < len(form.fields) - 1:
                # Swap with next field
                form.fields[i], form.fields[i+1] = form.fields[i+1], form.fields[i]
                break
        return form