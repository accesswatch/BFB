"""WordPress connection dialog for configuring publishing settings."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QLabel, QGroupBox, QTextEdit, QCheckBox,
    QProgressBar, QMessageBox, QTabWidget, QWidget
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont

from ..services.wp_client import WPClient, WordPressConnectionError, GravityFormsError


class ConnectionTestWorker(QThread):
    """Worker thread for testing WordPress connection"""
    
    connection_tested = Signal(bool, str)  # success, message
    
    def __init__(self, wp_client):
        super().__init__()
        self.wp_client = wp_client
        
    def run(self):
        """Test the connection in background thread"""
        try:
            success = self.wp_client.test_connection()
            if success:
                info = self.wp_client.get_gravity_forms_info()
                message = f"Connected successfully! Found {info['forms_count']} existing forms."
            else:
                message = "Connection failed"
                
            self.connection_tested.emit(success, message)
            
        except (WordPressConnectionError, GravityFormsError) as e:
            self.connection_tested.emit(False, str(e))
        except Exception as e:
            self.connection_tested.emit(False, f"Unexpected error: {str(e)}")


class WordPressDialog(QDialog):
    """Dialog for configuring WordPress connection and publishing forms"""
    
    form_published = Signal(dict)  # Emitted when form is successfully published
    
    def __init__(self, parent=None, form_model=None):
        super().__init__(parent)
        self.form_model = form_model
        self.wp_client = None
        self.connection_worker = None
        
        self.setup_ui()
        self.setup_accessibility()
        
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("WordPress Publishing")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Tab widget for different sections
        self.tabs = QTabWidget()
        
        # Connection tab
        self.connection_tab = self.create_connection_tab()
        self.tabs.addTab(self.connection_tab, "Connection")
        
        # Publishing tab
        self.publishing_tab = self.create_publishing_tab()
        self.tabs.addTab(self.publishing_tab, "Publish Form")
        
        layout.addWidget(self.tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.test_connection_btn = QPushButton("Test Connection")
        self.publish_btn = QPushButton("Publish Form")
        self.close_btn = QPushButton("Close")
        
        self.publish_btn.setDefault(True)
        self.publish_btn.setEnabled(False)
        
        button_layout.addWidget(self.test_connection_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.publish_btn)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # Connect signals
        self.test_connection_btn.clicked.connect(self.test_connection)
        self.publish_btn.clicked.connect(self.publish_form)
        self.close_btn.clicked.connect(self.reject)
        
    def create_connection_tab(self) -> QWidget:
        """Create the connection settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Connection settings group
        conn_group = QGroupBox("WordPress Site Settings")
        conn_layout = QFormLayout(conn_group)
        
        self.site_url_edit = QLineEdit()
        self.site_url_edit.setPlaceholderText("https://example.com")
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("WordPress username")
        
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Application password or regular password")
        
        conn_layout.addRow("Site URL:", self.site_url_edit)
        conn_layout.addRow("Username:", self.username_edit)
        conn_layout.addRow("Password:", self.password_edit)
        
        layout.addWidget(conn_group)
        
        # Help text
        help_group = QGroupBox("Authentication Help")
        help_layout = QVBoxLayout(help_group)
        
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setMaximumHeight(120)
        help_text.setHtml("""
        <p><b>Application Passwords (Recommended):</b></p>
        <ul>
        <li>Go to WordPress Admin → Users → Your Profile</li>
        <li>Scroll to "Application Passwords" section</li>
        <li>Add new application password for "BFB Form Builder"</li>
        <li>Use the generated password here</li>
        </ul>
        <p><b>Note:</b> Regular passwords also work but are less secure.</p>
        """)
        
        help_layout.addWidget(help_text)
        layout.addWidget(help_group)
        
        # Connection status
        self.status_label = QLabel("Not connected")
        self.status_label.setStyleSheet("QLabel { color: #666; font-style: italic; }")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        return tab
        
    def create_publishing_tab(self) -> QWidget:
        """Create the form publishing tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        if not self.form_model:
            no_form_label = QLabel("No form selected for publishing.")
            no_form_label.setAlignment(Qt.AlignCenter)
            no_form_label.setStyleSheet("QLabel { color: #666; font-style: italic; }")
            layout.addWidget(no_form_label)
            return tab
        
        # Form info group
        form_group = QGroupBox("Form Information")
        form_layout = QFormLayout(form_group)
        
        form_layout.addRow("Title:", QLabel(self.form_model.title))
        form_layout.addRow("Description:", QLabel(self.form_model.description or "No description"))
        form_layout.addRow("Fields:", QLabel(str(len(self.form_model.fields))))
        
        layout.addWidget(form_group)
        
        # Publishing options
        options_group = QGroupBox("Publishing Options")
        options_layout = QVBoxLayout(options_group)
        
        self.update_existing_check = QCheckBox("Update existing form if found (matches by title)")
        options_layout.addWidget(self.update_existing_check)
        
        layout.addWidget(options_group)
        
        # Existing forms (populated after connection test)
        self.existing_forms_group = QGroupBox("Existing Forms on Site")
        self.existing_forms_layout = QVBoxLayout(self.existing_forms_group)
        
        self.existing_forms_text = QTextEdit()
        self.existing_forms_text.setReadOnly(True)
        self.existing_forms_text.setMaximumHeight(100)
        self.existing_forms_text.setPlainText("Connect to see existing forms...")
        
        self.existing_forms_layout.addWidget(self.existing_forms_text)
        layout.addWidget(self.existing_forms_group)
        
        layout.addStretch()
        
        return tab
    
    def setup_accessibility(self):
        """Setup accessibility attributes"""
        self.setAccessibleName("WordPress Publishing Dialog")
        self.setAccessibleDescription("Dialog for configuring WordPress connection and publishing forms")
        
        # Set accessible names for key inputs
        self.site_url_edit.setAccessibleName("WordPress Site URL")
        self.site_url_edit.setAccessibleDescription("Enter the URL of your WordPress site, e.g., https://example.com")
        
        self.username_edit.setAccessibleName("WordPress Username")
        self.username_edit.setAccessibleDescription("Enter your WordPress username")
        
        self.password_edit.setAccessibleName("WordPress Password")
        self.password_edit.setAccessibleDescription("Enter your WordPress password or application password")
        
        # Button accessibility
        self.test_connection_btn.setAccessibleName("Test Connection")
        self.test_connection_btn.setAccessibleDescription("Test the connection to WordPress and Gravity Forms")
        
        self.publish_btn.setAccessibleName("Publish Form")
        self.publish_btn.setAccessibleDescription("Publish the current form to WordPress")
        
        self.close_btn.setAccessibleName("Close Dialog")
        self.close_btn.setAccessibleDescription("Close this dialog without publishing")
        
    def test_connection(self):
        """Test the WordPress connection"""
        site_url = self.site_url_edit.text().strip()
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        
        if not all([site_url, username, password]):
            QMessageBox.warning(self, "Missing Information", 
                               "Please fill in all connection fields.")
            return
            
        # Create WordPress client
        self.wp_client = WPClient(site_url, username, password)
        
        # Start connection test in background
        self.progress_bar.show()
        self.test_connection_btn.setEnabled(False)
        self.status_label.setText("Testing connection...")
        
        self.connection_worker = ConnectionTestWorker(self.wp_client)
        self.connection_worker.connection_tested.connect(self.on_connection_tested)
        self.connection_worker.start()
        
    def on_connection_tested(self, success: bool, message: str):
        """Handle connection test results"""
        self.progress_bar.hide()
        self.test_connection_btn.setEnabled(True)
        
        if success:
            self.status_label.setText("✓ Connected successfully")
            self.status_label.setStyleSheet("QLabel { color: green; }")
            self.publish_btn.setEnabled(True)
            
            # Store credentials securely
            self.wp_client.store_credentials(
                self.username_edit.text().strip(),
                self.password_edit.text().strip()
            )
            
            # Update existing forms list
            self.update_existing_forms_list()
            
            QMessageBox.information(self, "Success", message)
        else:
            self.status_label.setText("✗ Connection failed")
            self.status_label.setStyleSheet("QLabel { color: red; }")
            self.publish_btn.setEnabled(False)
            QMessageBox.critical(self, "Connection Failed", message)
            
    def update_existing_forms_list(self):
        """Update the list of existing forms"""
        if not self.wp_client:
            return
            
        try:
            forms = self.wp_client.list_forms()
            
            if not forms:
                self.existing_forms_text.setPlainText("No existing forms found.")
            else:
                forms_text = "\n".join([
                    f"• {form.get('title', 'Untitled')} (ID: {form.get('id', 'N/A')})"
                    for form in forms
                ])
                self.existing_forms_text.setPlainText(forms_text)
                
        except Exception as e:
            self.existing_forms_text.setPlainText(f"Error loading forms: {str(e)}")
            
    def publish_form(self):
        """Publish the form to WordPress"""
        if not self.wp_client or not self.form_model:
            return
            
        # Show progress
        self.progress_bar.show()
        self.publish_btn.setEnabled(False)
        
        try:
            # Publish the form
            update_existing = self.update_existing_check.isChecked()
            result = self.wp_client.publish_form(self.form_model, update_existing)
            
            self.progress_bar.hide()
            self.publish_btn.setEnabled(True)
            
            # Show success message
            form_id = result.get('id', 'Unknown')
            action = "updated" if update_existing else "created"
            message = f"Form successfully {action}! Form ID: {form_id}"
            
            QMessageBox.information(self, "Publishing Successful", message)
            
            # Emit success signal
            self.form_published.emit(result)
            self.accept()
            
        except Exception as e:
            self.progress_bar.hide()
            self.publish_btn.setEnabled(True)
            QMessageBox.critical(self, "Publishing Failed", f"Failed to publish form: {str(e)}")
            
    def load_saved_connection(self):
        """Load previously saved connection settings"""
        # This would load from settings/keyring
        # For now, we'll leave it empty - user needs to enter credentials
        pass