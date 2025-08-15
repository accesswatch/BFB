"""Field Editor Panel for configuring field properties."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QScrollArea,
    QLabel, QLineEdit, QTextEdit, QCheckBox, QComboBox, QSpinBox,
    QGroupBox, QPushButton, QListWidget, QListWidgetItem, QFrame,
    QDoubleSpinBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ..models.form_model import FieldModel, FieldType, Choice, InputItem, ValidationRule


class FieldEditorPanel(QScrollArea):
    """Panel for editing field properties"""
    
    field_updated = Signal(FieldModel)  # Emitted when field is updated
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_field = None
        self.setup_ui()
        self.setup_accessibility()
        
    def setup_ui(self):
        """Setup the user interface"""
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Main widget and layout
        main_widget = QWidget()
        self.layout = QVBoxLayout(main_widget)
        self.layout.setSpacing(10)
        
        # Default message
        self.default_message = QLabel("Select a field to edit its properties")
        self.default_message.setAlignment(Qt.AlignCenter)
        self.default_message.setStyleSheet("QLabel { color: #666; font-style: italic; }")
        self.layout.addWidget(self.default_message)
        
        # Field editor container (initially hidden)
        self.editor_container = QWidget()
        self.editor_layout = QVBoxLayout(self.editor_container)
        self.editor_layout.setSpacing(15)
        self.editor_container.hide()
        self.layout.addWidget(self.editor_container)
        
        self.setup_editor_sections()
        
        self.layout.addStretch()
        self.setWidget(main_widget)
        
    def setup_editor_sections(self):
        """Setup the various editor sections"""
        # General Settings Group
        self.general_group = QGroupBox("General Settings")
        self.general_layout = QFormLayout(self.general_group)
        
        self.label_edit = QLineEdit()
        self.admin_label_edit = QLineEdit()
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.required_check = QCheckBox("This field is required")
        
        self.general_layout.addRow("Field Label:", self.label_edit)
        self.general_layout.addRow("Admin Label:", self.admin_label_edit)
        self.general_layout.addRow("Description:", self.description_edit)
        self.general_layout.addRow("", self.required_check)
        
        self.editor_layout.addWidget(self.general_group)
        
        # Appearance Group
        self.appearance_group = QGroupBox("Appearance")
        self.appearance_layout = QFormLayout(self.appearance_group)
        
        self.size_combo = QComboBox()
        self.size_combo.addItems(["Small", "Medium", "Large"])
        self.css_class_edit = QLineEdit()
        
        self.appearance_layout.addRow("Field Size:", self.size_combo)
        self.appearance_layout.addRow("CSS Class:", self.css_class_edit)
        
        self.editor_layout.addWidget(self.appearance_group)
        
        # Input Settings Group
        self.input_group = QGroupBox("Input Settings")
        self.input_layout = QFormLayout(self.input_group)
        
        self.placeholder_edit = QLineEdit()
        self.default_value_edit = QLineEdit()
        
        self.input_layout.addRow("Placeholder Text:", self.placeholder_edit)
        self.input_layout.addRow("Default Value:", self.default_value_edit)
        
        self.editor_layout.addWidget(self.input_group)
        
        # Choices Group (for choice-based fields)
        self.choices_group = QGroupBox("Choices")
        self.choices_layout = QVBoxLayout(self.choices_group)
        
        self.choices_list = QListWidget()
        self.choices_list.setMaximumHeight(150)
        
        choices_buttons = QHBoxLayout()
        self.add_choice_btn = QPushButton("Add Choice")
        self.edit_choice_btn = QPushButton("Edit Choice")
        self.remove_choice_btn = QPushButton("Remove Choice")
        self.move_up_btn = QPushButton("Move Up")
        self.move_down_btn = QPushButton("Move Down")
        
        choices_buttons.addWidget(self.add_choice_btn)
        choices_buttons.addWidget(self.edit_choice_btn)
        choices_buttons.addWidget(self.remove_choice_btn)
        choices_buttons.addStretch()
        choices_buttons.addWidget(self.move_up_btn)
        choices_buttons.addWidget(self.move_down_btn)
        
        self.choices_layout.addWidget(self.choices_list)
        self.choices_layout.addLayout(choices_buttons)
        
        self.editor_layout.addWidget(self.choices_group)
        self.choices_group.hide()  # Hidden by default
        
        # Validation Group
        self.validation_group = QGroupBox("Validation")
        self.validation_layout = QFormLayout(self.validation_group)
        
        self.max_length_spin = QSpinBox()
        self.max_length_spin.setRange(0, 9999)
        self.max_length_spin.setValue(0)  # 0 means no limit
        
        self.validation_layout.addRow("Maximum Length:", self.max_length_spin)
        
        self.editor_layout.addWidget(self.validation_group)
        
        # File Upload Settings (for file upload fields)
        self.file_group = QGroupBox("File Upload Settings")
        self.file_layout = QFormLayout(self.file_group)
        
        self.max_file_size_spin = QDoubleSpinBox()
        self.max_file_size_spin.setRange(0.1, 100.0)  # MB
        self.max_file_size_spin.setValue(20.0)
        self.max_file_size_spin.setSuffix(" MB")
        
        self.allowed_extensions_edit = QLineEdit()
        self.allowed_extensions_edit.setPlaceholderText("e.g., jpg,png,pdf")
        
        self.multiple_files_check = QCheckBox("Allow multiple files")
        
        self.file_layout.addRow("Max File Size:", self.max_file_size_spin)
        self.file_layout.addRow("Allowed Extensions:", self.allowed_extensions_edit)
        self.file_layout.addRow("", self.multiple_files_check)
        
        self.editor_layout.addWidget(self.file_group)
        self.file_group.hide()  # Hidden by default
        
        # HTML Content Group (for HTML fields)
        self.html_group = QGroupBox("HTML Content")
        self.html_layout = QVBoxLayout(self.html_group)
        
        self.content_edit = QTextEdit()
        self.content_edit.setMaximumHeight(120)
        self.html_layout.addWidget(self.content_edit)
        
        self.editor_layout.addWidget(self.html_group)
        self.html_group.hide()  # Hidden by default
        
        # Connect signals
        self.connect_signals()
        
    def connect_signals(self):
        """Connect UI signals to update handlers"""
        self.label_edit.textChanged.connect(self.update_field)
        self.admin_label_edit.textChanged.connect(self.update_field)
        self.description_edit.textChanged.connect(self.update_field)
        self.required_check.toggled.connect(self.update_field)
        self.size_combo.currentTextChanged.connect(self.update_field)
        self.css_class_edit.textChanged.connect(self.update_field)
        self.placeholder_edit.textChanged.connect(self.update_field)
        self.default_value_edit.textChanged.connect(self.update_field)
        self.max_length_spin.valueChanged.connect(self.update_field)
        self.max_file_size_spin.valueChanged.connect(self.update_field)
        self.allowed_extensions_edit.textChanged.connect(self.update_field)
        self.multiple_files_check.toggled.connect(self.update_field)
        self.content_edit.textChanged.connect(self.update_field)
        
        # Choice management
        self.add_choice_btn.clicked.connect(self.add_choice)
        self.remove_choice_btn.clicked.connect(self.remove_choice)
        self.move_up_btn.clicked.connect(self.move_choice_up)
        self.move_down_btn.clicked.connect(self.move_choice_down)
        
    def setup_accessibility(self):
        """Setup accessibility attributes"""
        self.setAccessibleName("Field Editor Panel")
        self.setAccessibleDescription("Panel for editing the properties of the selected field")
        
        # Set accessible names for major groups
        self.general_group.setAccessibleName("General Settings")
        self.appearance_group.setAccessibleName("Appearance Settings")
        self.input_group.setAccessibleName("Input Settings")
        self.choices_group.setAccessibleName("Choice Settings")
        self.validation_group.setAccessibleName("Validation Settings")
        self.file_group.setAccessibleName("File Upload Settings")
        self.html_group.setAccessibleName("HTML Content Settings")
        
    def set_field(self, field: FieldModel):
        """Set the field to edit"""
        self.current_field = field
        
        if field is None:
            self.show_default_message()
            return
            
        self.show_editor()
        self.populate_field_data(field)
        
    def show_default_message(self):
        """Show the default 'no field selected' message"""
        self.default_message.show()
        self.editor_container.hide()
        
    def show_editor(self):
        """Show the field editor"""
        self.default_message.hide()
        self.editor_container.show()
        
        # Show/hide relevant groups based on field type
        if self.current_field:
            field_type = self.current_field.type
            
            # Show choices for select, radio, checkbox fields
            has_choices = field_type in [FieldType.SELECT, FieldType.MULTISELECT, FieldType.RADIO, FieldType.CHECKBOX]
            self.choices_group.setVisible(has_choices)
            
            # Show file settings for file upload fields
            is_file_field = field_type == FieldType.FILEUPLOAD
            self.file_group.setVisible(is_file_field)
            
            # Show HTML content for HTML fields
            is_html_field = field_type == FieldType.HTML
            self.html_group.setVisible(is_html_field)
            
    def populate_field_data(self, field: FieldModel):
        """Populate UI with field data"""
        # Block signals temporarily to avoid recursive updates
        self.blockSignals(True)
        
        self.label_edit.setText(field.label or "")
        self.admin_label_edit.setText(field.adminLabel or "")
        self.description_edit.setPlainText(field.description or "")
        self.required_check.setChecked(field.isRequired)
        
        # Size
        size_text = field.size.title() if field.size else "Medium"
        index = self.size_combo.findText(size_text)
        if index >= 0:
            self.size_combo.setCurrentIndex(index)
            
        self.css_class_edit.setText(field.cssClass or "")
        self.placeholder_edit.setText(field.placeholder or "")
        self.default_value_edit.setText(field.defaultValue or "")
        
        if field.maxLength:
            self.max_length_spin.setValue(field.maxLength)
        else:
            self.max_length_spin.setValue(0)
            
        # File upload settings
        if field.maxFileSize:
            self.max_file_size_spin.setValue(field.maxFileSize)
        self.allowed_extensions_edit.setText(field.allowedExtensions or "")
        self.multiple_files_check.setChecked(field.multipleFiles)
        
        # HTML content
        self.content_edit.setPlainText(field.content or "")
        
        # Choices
        self.populate_choices(field.choices or [])
        
        self.blockSignals(False)
        
    def populate_choices(self, choices: list[Choice]):
        """Populate the choices list"""
        self.choices_list.clear()
        
        for choice in choices:
            item = QListWidgetItem(choice.text)
            item.setData(Qt.UserRole, choice)
            self.choices_list.addItem(item)
            
    def update_field(self):
        """Update the current field with UI values"""
        if not self.current_field:
            return
            
        self.current_field.label = self.label_edit.text()
        self.current_field.adminLabel = self.admin_label_edit.text()
        self.current_field.description = self.description_edit.toPlainText()
        self.current_field.isRequired = self.required_check.isChecked()
        self.current_field.size = self.size_combo.currentText().lower()
        self.current_field.cssClass = self.css_class_edit.text()
        self.current_field.placeholder = self.placeholder_edit.text()
        self.current_field.defaultValue = self.default_value_edit.text()
        
        max_len = self.max_length_spin.value()
        self.current_field.maxLength = max_len if max_len > 0 else None
        
        # File upload settings
        self.current_field.maxFileSize = self.max_file_size_spin.value()
        self.current_field.allowedExtensions = self.allowed_extensions_edit.text()
        self.current_field.multipleFiles = self.multiple_files_check.isChecked()
        
        # HTML content
        self.current_field.content = self.content_edit.toPlainText()
        
        # Emit update signal
        self.field_updated.emit(self.current_field)
        
    def add_choice(self):
        """Add a new choice"""
        if not self.current_field or not self.current_field.choices:
            return
            
        new_choice = Choice(text=f"Choice {len(self.current_field.choices) + 1}", value="")
        self.current_field.choices.append(new_choice)
        
        item = QListWidgetItem(new_choice.text)
        item.setData(Qt.UserRole, new_choice)
        self.choices_list.addItem(item)
        
        self.field_updated.emit(self.current_field)
        
    def remove_choice(self):
        """Remove the selected choice"""
        current_row = self.choices_list.currentRow()
        if current_row < 0 or not self.current_field or not self.current_field.choices:
            return
            
        self.current_field.choices.pop(current_row)
        self.choices_list.takeItem(current_row)
        
        self.field_updated.emit(self.current_field)
        
    def move_choice_up(self):
        """Move the selected choice up"""
        current_row = self.choices_list.currentRow()
        if current_row <= 0 or not self.current_field or not self.current_field.choices:
            return
            
        # Swap choices
        choices = self.current_field.choices
        choices[current_row], choices[current_row-1] = choices[current_row-1], choices[current_row]
        
        # Update UI
        self.populate_choices(choices)
        self.choices_list.setCurrentRow(current_row - 1)
        
        self.field_updated.emit(self.current_field)
        
    def move_choice_down(self):
        """Move the selected choice down"""
        current_row = self.choices_list.currentRow()
        if current_row < 0 or current_row >= len(self.current_field.choices) - 1:
            return
            
        # Swap choices
        choices = self.current_field.choices
        choices[current_row], choices[current_row+1] = choices[current_row+1], choices[current_row]
        
        # Update UI
        self.populate_choices(choices)
        self.choices_list.setCurrentRow(current_row + 1)
        
        self.field_updated.emit(self.current_field)
        
    def setup_accessibility(self):
        """Setup accessibility attributes"""
        # Set accessible names and descriptions
        self.setAccessibleName("Field Editor Panel")
        self.setAccessibleDescription("Panel for editing properties of the selected field. Use Tab to navigate between controls.")
        
        # Set focus policy for better keyboard navigation
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Enhanced accessibility for form controls
        if hasattr(self, 'label_edit'):
            self.label_edit.setAccessibleName("Field Label")
            self.label_edit.setAccessibleDescription("The display label for this field")
        
        if hasattr(self, 'admin_label_edit'):
            self.admin_label_edit.setAccessibleName("Admin Label")
            self.admin_label_edit.setAccessibleDescription("Administrative label for this field, used in backend")
        
        if hasattr(self, 'description_edit'):
            self.description_edit.setAccessibleName("Field Description")
            self.description_edit.setAccessibleDescription("Help text that appears with the field")
        
        if hasattr(self, 'required_check'):
            self.required_check.setAccessibleName("Required Field")
            self.required_check.setAccessibleDescription("Check this box to make the field required")
        
        if hasattr(self, 'size_combo'):
            self.size_combo.setAccessibleName("Field Size")
            self.size_combo.setAccessibleDescription("Visual size of the field: Small, Medium, or Large")
        
        if hasattr(self, 'css_class_edit'):
            self.css_class_edit.setAccessibleName("CSS Class")
            self.css_class_edit.setAccessibleDescription("Custom CSS class for styling this field")
        
        if hasattr(self, 'placeholder_edit'):
            self.placeholder_edit.setAccessibleName("Placeholder Text")
            self.placeholder_edit.setAccessibleDescription("Placeholder text shown inside empty field")
        
        if hasattr(self, 'default_value_edit'):
            self.default_value_edit.setAccessibleName("Default Value")
            self.default_value_edit.setAccessibleDescription("Default value for this field")