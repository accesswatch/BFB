import httpx
from typing import Optional, Dict, List
import json
import keyring
from ..models.form_model import FormModel


class WordPressConnectionError(Exception):
    """Exception for WordPress connection issues"""
    pass


class GravityFormsError(Exception):
    """Exception for Gravity Forms API issues"""
    pass


class WPClient:
    """WordPress client for publishing forms to Gravity Forms plugin"""
    
    def __init__(self, base_url: str, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize WordPress client
        
        Args:
            base_url: WordPress site URL (e.g., https://example.com)
            username: WordPress username (optional, will use keyring if not provided)
            password: WordPress password or application password (optional, will use keyring if not provided)
        """
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.client = httpx.Client(timeout=30.0)
        
    def get_credentials(self) -> tuple[str, str]:
        """Get stored credentials from keyring or return provided ones"""
        username = self.username
        password = self.password
        
        if not username:
            username = keyring.get_password("BFB_WordPress", f"{self.base_url}_username")
            
        if not password and username:
            password = keyring.get_password("BFB_WordPress", f"{self.base_url}_{username}")
            
        if not username or not password:
            raise WordPressConnectionError("WordPress credentials not found. Please configure them first.")
            
        return username, password
    
    def store_credentials(self, username: str, password: str):
        """Store credentials securely using keyring"""
        keyring.set_password("BFB_WordPress", f"{self.base_url}_username", username)
        keyring.set_password("BFB_WordPress", f"{self.base_url}_{username}", password)
        self.username = username
        self.password = password
    
    def test_connection(self) -> bool:
        """Test connection to WordPress and Gravity Forms"""
        try:
            username, password = self.get_credentials()
            
            # Test WordPress REST API
            wp_response = self.client.get(
                f"{self.base_url}/wp-json/wp/v2/users/me",
                auth=(username, password)
            )
            wp_response.raise_for_status()
            
            # Test Gravity Forms API
            gf_response = self.client.get(
                f"{self.base_url}/wp-json/gf/v2/forms",
                auth=(username, password)
            )
            gf_response.raise_for_status()
            
            return True
            
        except httpx.HTTPError as e:
            raise WordPressConnectionError(f"Connection failed: {str(e)}")
        except Exception as e:
            raise WordPressConnectionError(f"Unexpected error: {str(e)}")
    
    def get_gravity_forms_info(self) -> dict:
        """Get Gravity Forms plugin information"""
        try:
            username, password = self.get_credentials()
            
            response = self.client.get(
                f"{self.base_url}/wp-json/gf/v2/forms",
                auth=(username, password)
            )
            response.raise_for_status()
            
            forms_data = response.json()
            return {
                "status": "connected",
                "forms_count": len(forms_data),
                "api_version": "v2"
            }
            
        except httpx.HTTPError as e:
            if e.response.status_code == 404:
                raise GravityFormsError("Gravity Forms plugin not found or not activated")
            elif e.response.status_code == 401:
                raise GravityFormsError("Authentication failed - check credentials")
            else:
                raise GravityFormsError(f"API error: {e.response.status_code}")
                
    def list_forms(self) -> List[dict]:
        """List existing forms on WordPress site"""
        try:
            username, password = self.get_credentials()
            
            response = self.client.get(
                f"{self.base_url}/wp-json/gf/v2/forms",
                auth=(username, password)
            )
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPError as e:
            raise GravityFormsError(f"Failed to list forms: {str(e)}")
    
    def publish_form(self, form: FormModel, update_existing: bool = False) -> dict:
        """
        Publish a form to Gravity Forms
        
        Args:
            form: The FormModel to publish
            update_existing: Whether to update if form already exists (by title)
        
        Returns:
            dict: Response from Gravity Forms API
        """
        try:
            username, password = self.get_credentials()
            
            # Convert form to Gravity Forms format
            gf_form = self._convert_to_gravity_forms_format(form)
            
            # Check if form already exists (if update_existing is True)
            existing_form_id = None
            if update_existing:
                existing_forms = self.list_forms()
                for existing in existing_forms:
                    if existing.get('title') == form.title:
                        existing_form_id = existing.get('id')
                        break
            
            if existing_form_id:
                # Update existing form
                response = self.client.put(
                    f"{self.base_url}/wp-json/gf/v2/forms/{existing_form_id}",
                    json=gf_form,
                    auth=(username, password)
                )
            else:
                # Create new form
                response = self.client.post(
                    f"{self.base_url}/wp-json/gf/v2/forms",
                    json=gf_form,
                    auth=(username, password)
                )
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            error_details = ""
            try:
                error_data = e.response.json()
                error_details = error_data.get('message', str(e))
            except:
                error_details = str(e)
                
            raise GravityFormsError(f"Failed to publish form: {error_details}")
    
    def _convert_to_gravity_forms_format(self, form: FormModel) -> dict:
        """Convert BFB FormModel to Gravity Forms API format"""
        gf_form = {
            "title": form.title,
            "description": form.description or "",
            "labelPlacement": form.labelPlacement,
            "descriptionPlacement": form.descriptionPlacement,
            "button": form.button,
            "fields": [],
            "version": form.version,
            "cssClass": form.cssClass or "",
            "enableHoneypot": form.enableHoneypot,
            "enableAnimation": form.enableAnimation,
            "save": form.save,
            "limitEntries": form.limitEntries,
            "limitEntriesCount": form.limitEntriesCount,
            "limitEntriesMessage": form.limitEntriesMessage,
            "scheduleForm": form.scheduleForm,
            "scheduleStart": form.scheduleStart,
            "scheduleEnd": form.scheduleEnd,
            "scheduleMessage": form.scheduleMessage,
            "confirmations": [self._convert_confirmation(conf) for conf in form.confirmations],
            "notifications": [self._convert_notification(notif) for notif in form.notifications]
        }
        
        # Convert fields
        for field in form.fields:
            gf_field = self._convert_field_to_gravity_forms(field)
            if gf_field:  # Only add if conversion was successful
                gf_form["fields"].append(gf_field)
        
        return gf_form
    
    def _convert_field_to_gravity_forms(self, field) -> Optional[dict]:
        """Convert a BFB field to Gravity Forms field format"""
        # Map BFB field types to Gravity Forms types
        type_mapping = {
            "text": "text",
            "textarea": "textarea", 
            "number": "number",
            "email": "email",
            "phone": "phone",
            "website": "website",
            "select": "select",
            "multiselect": "multiselect",
            "radio": "radio",
            "checkbox": "checkbox",
            "name": "name",
            "address": "address",
            "date": "date",
            "time": "time",
            "fileupload": "fileupload",
            "hidden": "hidden",
            "html": "html",
            "section": "section",
            "page": "page"
        }
        
        gf_type = type_mapping.get(field.type)
        if not gf_type:
            return None  # Skip unsupported field types
        
        gf_field = {
            "id": field.id,
            "type": gf_type,
            "label": field.label,
            "adminLabel": field.adminLabel or "",
            "description": field.description or "",
            "isRequired": field.isRequired,
            "size": field.size or "medium",
            "cssClass": field.cssClass or "",
            "placeholder": field.placeholder or "",
            "defaultValue": field.defaultValue or ""
        }
        
        # Add field-specific properties
        if field.choices:
            gf_field["choices"] = [
                {
                    "text": choice.text,
                    "value": choice.value or choice.text,
                    "isSelected": choice.isSelected
                }
                for choice in field.choices
            ]
        
        if field.inputs:
            gf_field["inputs"] = [
                {
                    "id": inp.id,
                    "label": inp.label or "",
                    "name": inp.name or "",
                    "placeholder": inp.placeholder or ""
                }
                for inp in field.inputs
            ]
        
        # File upload specific
        if field.type == "fileupload":
            if field.maxFileSize:
                gf_field["maxFileSize"] = field.maxFileSize
            if field.allowedExtensions:
                gf_field["allowedExtensions"] = field.allowedExtensions
            gf_field["multipleFiles"] = field.multipleFiles
        
        # HTML field specific
        if field.type == "html":
            gf_field["content"] = field.content or ""
        
        # Validation
        if field.maxLength:
            gf_field["maxLength"] = field.maxLength
            
        if field.conditionalLogic:
            gf_field["conditionalLogic"] = {
                "actionType": field.conditionalLogic.actionType,
                "logicType": field.conditionalLogic.logicType,
                "rules": field.conditionalLogic.rules
            }
        
        return gf_field
    
    def _convert_confirmation(self, conf) -> dict:
        """Convert BFB confirmation to Gravity Forms format"""
        return {
            "id": conf.id,
            "name": conf.name,
            "type": conf.type,
            "message": conf.message,
            "url": conf.url,
            "pageId": conf.pageId,
            "queryString": conf.queryString,
            "isActive": conf.isActive,
            "isDefault": conf.isDefault
        }
    
    def _convert_notification(self, notif) -> dict:
        """Convert BFB notification to Gravity Forms format"""
        return {
            "id": notif.id,
            "name": notif.name,
            "event": notif.event,
            "to": notif.to,
            "subject": notif.subject,
            "message": notif.message,
            "from": notif.from_email,
            "fromName": notif.from_name,
            "replyTo": notif.replyTo,
            "bcc": notif.bcc,
            "isActive": notif.isActive
        }
