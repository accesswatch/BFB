from app.models.form_model import FormModel, FieldModel, FieldType
from app.models.field_factory import FieldFactory


def test_form_roundtrip():
    f = FormModel(id=None, title="Test", fields=[FieldModel(id=1, type=FieldType.TEXT, label="Name")])
    s = f.model_dump_json()
    f2 = FormModel.model_validate_json(s)
    assert f2.title == "Test"
    assert len(f2.fields) == 1
    assert f2.fields[0].type == FieldType.TEXT


def test_field_factory():
    """Test field factory creates proper field defaults"""
    text_field = FieldFactory.create_field(FieldType.TEXT, field_id=1)
    assert text_field.type == FieldType.TEXT
    assert text_field.label == "Untitled"
    assert text_field.placeholder == "Enter text here"
    
    email_field = FieldFactory.create_field(FieldType.EMAIL)
    assert email_field.type == FieldType.EMAIL
    assert "email" in email_field.placeholder.lower()
    
    select_field = FieldFactory.create_field(FieldType.SELECT)
    assert select_field.type == FieldType.SELECT
    assert len(select_field.choices) == 3
    
    name_field = FieldFactory.create_field(FieldType.NAME)
    assert name_field.type == FieldType.NAME
    assert len(name_field.inputs) == 2  # First and Last


def test_get_field_types():
    """Test getting field type definitions"""
    field_types = FieldFactory.get_field_types()
    assert FieldType.TEXT in field_types
    assert FieldType.EMAIL in field_types
    assert field_types[FieldType.TEXT]["name"] == "Single Line Text"
