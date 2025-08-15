from app.models.form_model import FormModel, FieldModel


def test_form_roundtrip():
    f = FormModel(id=None, title="Test", fields=[FieldModel(id=1, type="text", label="Name")])
    s = f.json()
    f2 = FormModel.parse_raw(s)
    assert f2.title == "Test"
    assert len(f2.fields) == 1
