"""Test WordPress client functionality"""

import pytest
from unittest.mock import Mock, patch
import httpx

from app.services.wp_client import WPClient, WordPressConnectionError, GravityFormsError
from app.models.form_model import FormModel, FieldModel, FieldType
from app.models.field_factory import FieldFactory


@pytest.fixture
def wp_client():
    """Create a WordPress client for testing"""
    return WPClient("https://test.com", "user", "pass")


@pytest.fixture
def sample_form():
    """Create a sample form for testing"""
    form = FormModel(
        title="Test Form",
        description="A test form",
        fields=[
            FieldFactory.create_field(FieldType.TEXT, 1),
            FieldFactory.create_field(FieldType.EMAIL, 2),
            FieldFactory.create_field(FieldType.SELECT, 3)
        ]
    )
    return form


def test_wp_client_initialization():
    """Test WordPress client initialization"""
    client = WPClient("https://example.com", "user", "pass")
    assert client.base_url == "https://example.com"
    assert client.username == "user" 
    assert client.password == "pass"


def test_wp_client_url_normalization():
    """Test URL normalization (trailing slash removal)"""
    client = WPClient("https://example.com/", "user", "pass")
    assert client.base_url == "https://example.com"


@patch('app.services.wp_client.keyring')
def test_credentials_storage(mock_keyring, wp_client):
    """Test credential storage and retrieval"""
    wp_client.store_credentials("testuser", "testpass")
    
    # Verify keyring calls
    assert mock_keyring.set_password.call_count == 2
    mock_keyring.set_password.assert_any_call("BFB_WordPress", "https://test.com_username", "testuser")
    mock_keyring.set_password.assert_any_call("BFB_WordPress", "https://test.com_testuser", "testpass")


def test_convert_field_to_gravity_forms(wp_client, sample_form):
    """Test conversion of BFB field to Gravity Forms format"""
    text_field = sample_form.fields[0]  # Text field
    gf_field = wp_client._convert_field_to_gravity_forms(text_field)
    
    assert gf_field is not None
    assert gf_field["type"] == "text"
    assert gf_field["label"] == text_field.label
    assert gf_field["id"] == text_field.id
    assert gf_field["isRequired"] == text_field.isRequired


def test_convert_select_field_to_gravity_forms(wp_client, sample_form):
    """Test conversion of select field with choices"""
    select_field = sample_form.fields[2]  # Select field
    gf_field = wp_client._convert_field_to_gravity_forms(select_field)
    
    assert gf_field is not None
    assert gf_field["type"] == "select"
    assert "choices" in gf_field
    assert len(gf_field["choices"]) == len(select_field.choices)
    
    # Check choice conversion
    for i, choice in enumerate(select_field.choices):
        gf_choice = gf_field["choices"][i]
        assert gf_choice["text"] == choice.text
        assert gf_choice["value"] == choice.value or choice.text


def test_convert_form_to_gravity_forms(wp_client, sample_form):
    """Test conversion of complete form to Gravity Forms format"""
    gf_form = wp_client._convert_to_gravity_forms_format(sample_form)
    
    assert gf_form["title"] == sample_form.title
    assert gf_form["description"] == sample_form.description
    assert len(gf_form["fields"]) == len(sample_form.fields)
    
    # Check field conversion
    for i, field in enumerate(sample_form.fields):
        gf_field = gf_form["fields"][i]
        assert gf_field["id"] == field.id
        assert gf_field["label"] == field.label


@patch('app.services.wp_client.httpx.Client')
def test_test_connection_success(mock_client_class, wp_client):
    """Test successful connection test"""
    # Mock successful responses
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    
    # Create new client instance with mocked httpx.Client
    wp_client.client = mock_client
    
    # Mock WordPress API response
    wp_response = Mock()
    wp_response.raise_for_status.return_value = None
    
    # Mock Gravity Forms API response
    gf_response = Mock()
    gf_response.raise_for_status.return_value = None
    gf_response.json.return_value = [{"id": 1, "title": "Test Form"}]
    
    mock_client.get.side_effect = [wp_response, gf_response]
    
    # Set up client with credentials
    wp_client.username = "testuser"
    wp_client.password = "testpass"
    
    result = wp_client.test_connection()
    assert result is True


@patch('app.services.wp_client.httpx.Client')
def test_list_forms(mock_client_class, wp_client):
    """Test listing existing forms"""
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    
    # Replace the client instance
    wp_client.client = mock_client
    
    # Mock response with forms data
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = [
        {"id": 1, "title": "Form 1"},
        {"id": 2, "title": "Form 2"}
    ]
    mock_client.get.return_value = response
    
    # Set up client with credentials
    wp_client.username = "testuser"
    wp_client.password = "testpass"
    
    forms = wp_client.list_forms()
    assert len(forms) == 2
    assert forms[0]["title"] == "Form 1"
    assert forms[1]["title"] == "Form 2"


@patch('app.services.wp_client.httpx.Client')
def test_publish_form_new(mock_client_class, wp_client, sample_form):
    """Test publishing a new form"""
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    
    # Replace the client instance
    wp_client.client = mock_client
    
    # Mock successful publish response
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"id": 123, "title": "Test Form"}
    
    # Mock list forms response (empty)
    list_response = Mock()
    list_response.raise_for_status.return_value = None
    list_response.json.return_value = []
    
    mock_client.get.return_value = list_response
    mock_client.post.return_value = response
    
    # Set up client with credentials
    wp_client.username = "testuser"
    wp_client.password = "testpass"
    
    result = wp_client.publish_form(sample_form)
    assert result["id"] == 123
    assert result["title"] == "Test Form"


@patch('app.services.wp_client.httpx.Client')
def test_publish_form_update_existing(mock_client_class, wp_client, sample_form):
    """Test updating an existing form"""
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    
    # Replace the client instance
    wp_client.client = mock_client
    
    # Mock successful update response
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"id": 123, "title": "Test Form"}
    
    # Mock list forms response (with existing form)
    list_response = Mock()
    list_response.raise_for_status.return_value = None
    list_response.json.return_value = [{"id": 123, "title": "Test Form"}]
    
    mock_client.get.return_value = list_response
    mock_client.put.return_value = response
    
    # Set up client with credentials
    wp_client.username = "testuser"
    wp_client.password = "testpass"
    
    result = wp_client.publish_form(sample_form, update_existing=True)
    assert result["id"] == 123
    
    # Verify PUT was called instead of POST
    mock_client.put.assert_called_once()
    mock_client.post.assert_not_called()


def test_convert_confirmation(wp_client):
    """Test confirmation conversion"""
    from app.models.form_model import ConfirmationSettings
    
    conf = ConfirmationSettings(
        name="Test Confirmation",
        type="message",
        message="Thank you!",
        isActive=True
    )
    
    gf_conf = wp_client._convert_confirmation(conf)
    assert gf_conf["name"] == "Test Confirmation"
    assert gf_conf["type"] == "message"
    assert gf_conf["message"] == "Thank you!"
    assert gf_conf["isActive"] is True


def test_convert_notification(wp_client):
    """Test notification conversion"""
    from app.models.form_model import NotificationSettings
    
    notif = NotificationSettings(
        name="Admin Notification",
        event="form_submission",
        to="admin@example.com",
        subject="New submission",
        message="Form submitted"
    )
    
    gf_notif = wp_client._convert_notification(notif)
    assert gf_notif["name"] == "Admin Notification"
    assert gf_notif["event"] == "form_submission"
    assert gf_notif["to"] == "admin@example.com"
    assert gf_notif["subject"] == "New submission"