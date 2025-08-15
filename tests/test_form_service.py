"""Test form service operations"""

import tempfile
import shutil
from pathlib import Path
import pytest

from app.models.form_model import FormModel, FieldModel, FieldType
from app.models.field_factory import FieldFactory
from app.services.form_service import FormService


@pytest.fixture
def temp_forms_dir():
    """Create a temporary directory for forms"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture  
def form_service(temp_forms_dir):
    """Create form service with temporary directory"""
    return FormService(temp_forms_dir)


def test_create_new_form(form_service):
    """Test creating a new form"""
    form = form_service.create_new_form("Test Form")
    assert form.title == "Test Form"
    assert len(form.fields) == 0
    assert form.notifications is not None
    assert form.confirmations is not None


def test_save_and_load_form(form_service):
    """Test saving and loading forms"""
    # Create form with fields
    form = FormModel(
        title="Test Form",
        description="A test form",
        fields=[
            FieldFactory.create_field(FieldType.TEXT, 1),
            FieldFactory.create_field(FieldType.EMAIL, 2)
        ]
    )
    
    # Save form
    filename = form_service.save_form(form)
    assert filename.endswith('.json')
    
    # Load form
    loaded_form = form_service.load_form(filename)
    assert loaded_form.title == "Test Form"
    assert loaded_form.description == "A test form" 
    assert len(loaded_form.fields) == 2
    assert loaded_form.fields[0].type == FieldType.TEXT
    assert loaded_form.fields[1].type == FieldType.EMAIL


def test_add_field_to_form(form_service):
    """Test adding fields to a form"""
    form = form_service.create_new_form("Test Form")
    
    # Add text field
    form_service.add_field_to_form(form, FieldType.TEXT)
    assert len(form.fields) == 1
    assert form.fields[0].type == FieldType.TEXT
    
    # Add email field at beginning
    form_service.add_field_to_form(form, FieldType.EMAIL, 0)
    assert len(form.fields) == 2
    assert form.fields[0].type == FieldType.EMAIL
    assert form.fields[1].type == FieldType.TEXT


def test_remove_field_from_form(form_service):
    """Test removing fields from a form"""
    form = FormModel(
        title="Test Form",
        fields=[
            FieldModel(id=1, type=FieldType.TEXT, label="Name"),
            FieldModel(id=2, type=FieldType.EMAIL, label="Email")
        ]
    )
    
    # Remove first field
    form_service.remove_field_from_form(form, 1)
    assert len(form.fields) == 1
    assert form.fields[0].id == 2


def test_duplicate_field_in_form(form_service):
    """Test duplicating a field"""
    form = FormModel(
        title="Test Form",
        fields=[
            FieldModel(id=1, type=FieldType.TEXT, label="Name")
        ]
    )
    
    # Duplicate field
    form_service.duplicate_field_in_form(form, 1)
    assert len(form.fields) == 2
    assert form.fields[1].label == "Name (Copy)"
    assert form.fields[1].id != form.fields[0].id


def test_move_field_operations(form_service):
    """Test moving fields up and down"""
    form = FormModel(
        title="Test Form",
        fields=[
            FieldModel(id=1, type=FieldType.TEXT, label="Field 1"),
            FieldModel(id=2, type=FieldType.EMAIL, label="Field 2"),
            FieldModel(id=3, type=FieldType.PHONE, label="Field 3")
        ]
    )
    
    # Move middle field up
    form_service.move_field_up(form, 2)
    assert form.fields[0].label == "Field 2"
    assert form.fields[1].label == "Field 1"
    assert form.fields[2].label == "Field 3"
    
    # Move first field down
    form_service.move_field_down(form, 2)
    assert form.fields[0].label == "Field 1"
    assert form.fields[1].label == "Field 2"
    assert form.fields[2].label == "Field 3"


def test_list_forms(form_service):
    """Test listing available forms"""
    # Initially empty
    forms = form_service.list_forms()
    assert len(forms) == 0
    
    # Save some forms
    form1 = form_service.create_new_form("Form 1")
    form2 = form_service.create_new_form("Form 2")
    
    form_service.save_form(form1)
    form_service.save_form(form2)
    
    # Check list
    forms = form_service.list_forms()
    assert len(forms) == 2
    assert any("Form_1" in name for name in forms)
    assert any("Form_2" in name for name in forms)


def test_export_import_form(form_service, temp_forms_dir):
    """Test exporting and importing forms"""
    form = FormModel(
        title="Export Test",
        fields=[FieldFactory.create_field(FieldType.TEXT, 1)]
    )
    
    export_path = Path(temp_forms_dir) / "export_test.json"
    
    # Export form
    form_service.export_form(form, str(export_path))
    assert export_path.exists()
    
    # Import form
    imported_form = form_service.import_form(str(export_path))
    assert imported_form.title == "Export Test"
    assert len(imported_form.fields) == 1
    assert imported_form.fields[0].type == FieldType.TEXT