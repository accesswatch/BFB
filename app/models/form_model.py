from pydantic import BaseModel, Field
from typing import List, Optional, Any, Union
from enum import Enum


class FieldType(str, Enum):
    """Supported field types in the MVP"""
    TEXT = "text"
    TEXTAREA = "textarea" 
    NUMBER = "number"
    EMAIL = "email"
    PHONE = "phone"
    WEBSITE = "website"
    SELECT = "select"
    MULTISELECT = "multiselect"
    RADIO = "radio"
    CHECKBOX = "checkbox"
    NAME = "name"
    ADDRESS = "address"
    DATE = "date"
    TIME = "time"
    FILEUPLOAD = "fileupload"
    HIDDEN = "hidden"
    HTML = "html"
    SECTION = "section"
    PAGE = "page"


class Choice(BaseModel):
    text: str
    value: Optional[str] = None
    isSelected: bool = False


class InputItem(BaseModel):
    id: str
    label: Optional[str] = None
    name: Optional[str] = None
    placeholder: Optional[str] = None


class ValidationRule(BaseModel):
    type: str
    value: Optional[Union[str, int, float]] = None
    message: Optional[str] = None


class ConditionalLogic(BaseModel):
    actionType: str  # "show" or "hide"
    logicType: str   # "all" or "any"
    rules: List[dict] = Field(default_factory=list)


class FieldModel(BaseModel):
    id: Optional[int] = None
    type: FieldType
    label: str
    adminLabel: Optional[str] = ""
    description: Optional[str] = ""
    isRequired: bool = False
    placeholder: Optional[str] = ""
    defaultValue: Optional[str] = ""
    inputs: Optional[List[InputItem]] = None
    choices: Optional[List[Choice]] = None
    cssClass: Optional[str] = ""
    size: Optional[str] = "medium"  # small, medium, large
    maxLength: Optional[int] = None
    visibility: str = "visible"  # visible, hidden, admin_only
    allowsPrepopulate: bool = False
    inputName: Optional[str] = None
    content: Optional[str] = ""  # for HTML fields
    displayOnly: bool = False
    conditionalLogic: Optional[ConditionalLogic] = None
    validation: Optional[List[ValidationRule]] = None
    # File upload specific
    maxFileSize: Optional[int] = None
    allowedExtensions: Optional[str] = None
    multipleFiles: bool = False


class NotificationSettings(BaseModel):
    id: Optional[str] = None
    name: str = "Admin Notification"
    event: str = "form_submission"
    to: str = "{admin_email}"
    subject: str = "New submission from {form_title}"
    message: str = "{all_fields}"
    from_name: str = "{site_title}"
    from_email: str = "{admin_email}"
    replyTo: Optional[str] = None
    bcc: Optional[str] = None
    isActive: bool = True


class ConfirmationSettings(BaseModel):
    id: Optional[str] = None
    name: str = "Default Confirmation"
    type: str = "message"  # message, page, redirect
    message: Optional[str] = "Thanks for contacting us! We will get in touch with you shortly."
    url: Optional[str] = None
    pageId: Optional[int] = None
    queryString: Optional[str] = None
    isActive: bool = True
    isDefault: bool = True


class FormModel(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = ""
    version: str = "1.0"
    fields: List[FieldModel] = Field(default_factory=list)
    button: dict = Field(default_factory=lambda: {"type": "text", "text": "Submit"})
    labelPlacement: str = "top_label"  # top_label, left_label, right_label
    descriptionPlacement: str = "below"  # below, above
    requiredIndicator: str = "text"  # text, asterisk
    cssClass: Optional[str] = ""
    enableHoneypot: bool = True
    enableAnimation: bool = False
    save: bool = False
    limitEntries: bool = False
    limitEntriesCount: Optional[int] = None
    limitEntriesMessage: Optional[str] = ""
    scheduleForm: bool = False
    scheduleStart: Optional[str] = None
    scheduleEnd: Optional[str] = None
    scheduleMessage: Optional[str] = ""
    notifications: List[NotificationSettings] = Field(default_factory=list)
    confirmations: List[ConfirmationSettings] = Field(default_factory=list)
    
    def model_post_init(self, __context):
        """Initialize default notification and confirmation if none exist"""
        if not self.notifications:
            self.notifications = [NotificationSettings()]
        if not self.confirmations:
            self.confirmations = [ConfirmationSettings()]
