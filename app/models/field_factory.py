"""Field factory for creating different field types with proper defaults"""

from typing import Dict, List
from .form_model import FieldModel, FieldType, Choice, InputItem


class FieldFactory:
    """Factory class for creating form fields with proper defaults"""
    
    @staticmethod
    def get_field_types() -> Dict[str, Dict]:
        """Get available field types with their display names and descriptions"""
        return {
            FieldType.TEXT: {
                "name": "Single Line Text",
                "description": "A single line of text input",
                "category": "Standard"
            },
            FieldType.TEXTAREA: {
                "name": "Paragraph Text", 
                "description": "A multi-line text area",
                "category": "Standard"
            },
            FieldType.NUMBER: {
                "name": "Number",
                "description": "Numeric input with validation",
                "category": "Standard"
            },
            FieldType.EMAIL: {
                "name": "Email",
                "description": "Email address with validation",
                "category": "Standard"
            },
            FieldType.PHONE: {
                "name": "Phone",
                "description": "Phone number input",
                "category": "Standard"
            },
            FieldType.WEBSITE: {
                "name": "Website",
                "description": "URL/Website input with validation",
                "category": "Standard"
            },
            FieldType.SELECT: {
                "name": "Dropdown",
                "description": "Single selection dropdown",
                "category": "Standard"
            },
            FieldType.MULTISELECT: {
                "name": "Multi Select",
                "description": "Multiple selection list",
                "category": "Standard"
            },
            FieldType.RADIO: {
                "name": "Radio Buttons",
                "description": "Single selection from radio buttons",
                "category": "Standard"
            },
            FieldType.CHECKBOX: {
                "name": "Checkboxes",
                "description": "Multiple selection checkboxes",
                "category": "Standard"
            },
            FieldType.NAME: {
                "name": "Name",
                "description": "Composite name field (first, last, etc.)",
                "category": "Advanced"
            },
            FieldType.ADDRESS: {
                "name": "Address",
                "description": "Composite address field",
                "category": "Advanced"
            },
            FieldType.DATE: {
                "name": "Date",
                "description": "Date picker input",
                "category": "Advanced"
            },
            FieldType.TIME: {
                "name": "Time",
                "description": "Time picker input",
                "category": "Advanced"
            },
            FieldType.FILEUPLOAD: {
                "name": "File Upload",
                "description": "File upload with type restrictions",
                "category": "Advanced"
            },
            FieldType.HIDDEN: {
                "name": "Hidden",
                "description": "Hidden field for storing values",
                "category": "Advanced"
            },
            FieldType.HTML: {
                "name": "HTML",
                "description": "Display HTML content",
                "category": "Advanced"
            },
            FieldType.SECTION: {
                "name": "Section Break",
                "description": "Visual section divider",
                "category": "Advanced"
            },
            FieldType.PAGE: {
                "name": "Page Break",
                "description": "Break form into multiple pages",
                "category": "Advanced"
            }
        }
    
    @classmethod
    def create_field(cls, field_type: FieldType, field_id: int = None) -> FieldModel:
        """Create a new field with appropriate defaults for the given type"""
        
        base_field = FieldModel(
            id=field_id,
            type=field_type,
            label=cls._get_default_label(field_type)
        )
        
        # Apply type-specific configurations
        if field_type == FieldType.TEXT:
            base_field.placeholder = "Enter text here"
            
        elif field_type == FieldType.TEXTAREA:
            base_field.placeholder = "Enter your message here"
            
        elif field_type == FieldType.EMAIL:
            base_field.placeholder = "Enter your email address"
            
        elif field_type == FieldType.PHONE:
            base_field.placeholder = "Enter your phone number"
            
        elif field_type == FieldType.WEBSITE:
            base_field.placeholder = "https://example.com"
            
        elif field_type in [FieldType.SELECT, FieldType.MULTISELECT]:
            base_field.choices = [
                Choice(text="First Choice", value="first"),
                Choice(text="Second Choice", value="second"),
                Choice(text="Third Choice", value="third")
            ]
            base_field.placeholder = "Select an option"
            
        elif field_type == FieldType.RADIO:
            base_field.choices = [
                Choice(text="First Choice", value="first"),
                Choice(text="Second Choice", value="second"),
                Choice(text="Third Choice", value="third")
            ]
            
        elif field_type == FieldType.CHECKBOX:
            base_field.choices = [
                Choice(text="First Choice", value="first"),
                Choice(text="Second Choice", value="second"),
                Choice(text="Third Choice", value="third")
            ]
            
        elif field_type == FieldType.NAME:
            base_field.inputs = [
                InputItem(id="3.1", label="First", name="first", placeholder="First"),
                InputItem(id="3.2", label="Last", name="last", placeholder="Last")
            ]
            
        elif field_type == FieldType.ADDRESS:
            base_field.inputs = [
                InputItem(id="1.1", label="Street Address", name="street", placeholder="Street Address"),
                InputItem(id="1.2", label="Address Line 2", name="street2", placeholder="Address Line 2"),
                InputItem(id="1.3", label="City", name="city", placeholder="City"),
                InputItem(id="1.4", label="State / Province", name="state", placeholder="State / Province"),
                InputItem(id="1.5", label="ZIP / Postal Code", name="zip", placeholder="ZIP / Postal Code"),
                InputItem(id="1.6", label="Country", name="country", placeholder="Country")
            ]
            
        elif field_type == FieldType.FILEUPLOAD:
            base_field.allowedExtensions = "jpg,jpeg,png,gif,pdf,doc,docx,txt"
            base_field.maxFileSize = 20  # MB
            
        elif field_type == FieldType.HIDDEN:
            base_field.visibility = "hidden"
            base_field.label = "Hidden Field"
            
        elif field_type == FieldType.HTML:
            base_field.content = "<p>Add your HTML content here</p>"
            base_field.displayOnly = True
            
        elif field_type == FieldType.SECTION:
            base_field.displayOnly = True
            base_field.description = "This is a section break"
            
        elif field_type == FieldType.PAGE:
            base_field.displayOnly = True
            base_field.label = "Page Break"
            base_field.description = "This will create a new page"
            
        return base_field
    
    @staticmethod
    def _get_default_label(field_type: FieldType) -> str:
        """Get default label for field type"""
        labels = {
            FieldType.TEXT: "Untitled",
            FieldType.TEXTAREA: "Message",
            FieldType.NUMBER: "Number",
            FieldType.EMAIL: "Email",
            FieldType.PHONE: "Phone",
            FieldType.WEBSITE: "Website",
            FieldType.SELECT: "Dropdown",
            FieldType.MULTISELECT: "Multi Select",
            FieldType.RADIO: "Radio Buttons",
            FieldType.CHECKBOX: "Checkboxes",
            FieldType.NAME: "Name",
            FieldType.ADDRESS: "Address",
            FieldType.DATE: "Date",
            FieldType.TIME: "Time",
            FieldType.FILEUPLOAD: "File Upload",
            FieldType.HIDDEN: "Hidden Field",
            FieldType.HTML: "HTML Block",
            FieldType.SECTION: "Section Break",
            FieldType.PAGE: "Page Break"
        }
        return labels.get(field_type, "Field")