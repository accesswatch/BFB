from pydantic import BaseModel, Field
from typing import List, Optional, Any


class Choice(BaseModel):
    text: str
    value: Optional[str] = None


class InputItem(BaseModel):
    id: str
    label: Optional[str] = None


class FieldModel(BaseModel):
    id: Optional[int]
    type: str
    label: str
    adminLabel: Optional[str] = ""
    isRequired: bool = False
    inputs: Optional[List[InputItem]] = None
    choices: Optional[List[Choice]] = None
    cssClass: Optional[str] = ""
    conditionalLogic: Optional[Any] = None


class FormModel(BaseModel):
    id: Optional[int]
    title: str
    description: Optional[str] = ""
    version: str = "1.0"
    fields: List[FieldModel] = Field(default_factory=list)
    notifications: Optional[List[Any]] = None
    confirmations: Optional[List[Any]] = None
