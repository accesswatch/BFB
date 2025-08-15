"""Add Field Dialog for selecting and adding new fields to forms."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QLineEdit, QTextEdit, QGroupBox, QButtonGroup, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon

from ..models.field_factory import FieldFactory
from ..models.form_model import FieldType


class AddFieldDialog(QDialog):
    """Dialog for selecting a field type to add to the form"""
    
    field_selected = Signal(str)  # Emits the selected field type
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_field_type = None
        self.setup_ui()
        self.setup_accessibility()
        
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("Add Field")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Select a Field Type")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Choose the type of field you want to add to your form:")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Field list
        self.field_list = QListWidget()
        self.field_list.setAlternatingRowColors(True)
        layout.addWidget(self.field_list)
        
        # Field description area
        self.description_label = QLabel("Select a field type to see its description.")
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("QLabel { background-color: #f0f0f0; padding: 8px; border: 1px solid #ccc; }")
        self.description_label.setMinimumHeight(60)
        layout.addWidget(self.description_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.add_button = QPushButton("Add Field")
        self.add_button.setDefault(True)
        self.add_button.setEnabled(False)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.add_button)
        
        layout.addLayout(button_layout)
        
        # Populate field types
        self.populate_field_types()
        
        # Connect signals
        self.field_list.itemSelectionChanged.connect(self.on_selection_changed)
        self.field_list.itemDoubleClicked.connect(self.accept_selection)
        self.add_button.clicked.connect(self.accept_selection)
        self.cancel_button.clicked.connect(self.reject)
        
    def setup_accessibility(self):
        """Setup accessibility attributes"""
        # Set accessible names and descriptions
        self.setAccessibleName("Add Field Dialog")
        self.setAccessibleDescription("Dialog for selecting a field type to add to the form")
        
        self.field_list.setAccessibleName("Field Type List")
        self.field_list.setAccessibleDescription("List of available field types. Use arrow keys to navigate, Enter to select.")
        
        self.description_label.setAccessibleName("Field Description")
        self.description_label.setAccessibleDescription("Description of the currently selected field type")
        
        self.add_button.setAccessibleName("Add Field Button")
        self.add_button.setAccessibleDescription("Add the selected field type to the form")
        
        self.cancel_button.setAccessibleName("Cancel Button") 
        self.cancel_button.setAccessibleDescription("Cancel adding a field and close this dialog")
        
        # Set initial focus
        self.field_list.setFocus()
        
    def populate_field_types(self):
        """Populate the field list with available field types"""
        field_types = FieldFactory.get_field_types()
        
        # Group by category
        categories = {}
        for field_type, info in field_types.items():
            category = info.get("category", "Other")
            if category not in categories:
                categories[category] = []
            categories[category].append((field_type, info))
        
        # Add items grouped by category
        for category in ["Standard", "Advanced"]:  # Preferred order
            if category in categories:
                # Add category header
                header_item = QListWidgetItem(f"── {category} Fields ──")
                header_font = QFont()
                header_font.setBold(True)
                header_item.setFont(header_font)
                header_item.setFlags(Qt.NoItemFlags)  # Make non-selectable
                header_item.setBackground(Qt.lightGray)
                self.field_list.addItem(header_item)
                
                # Add field types in this category
                for field_type, info in sorted(categories[category], key=lambda x: x[1]["name"]):
                    item = QListWidgetItem(info["name"])
                    item.setData(Qt.UserRole, field_type)
                    item.setToolTip(info["description"])
                    # Make accessible
                    item.setAccessibleText(f"{info['name']} - {info['description']}")
                    self.field_list.addItem(item)
        
        # Select first selectable item
        for i in range(self.field_list.count()):
            item = self.field_list.item(i)
            if item.flags() != Qt.NoItemFlags:
                self.field_list.setCurrentItem(item)
                break
                
    def on_selection_changed(self):
        """Handle field selection change"""
        current_item = self.field_list.currentItem()
        
        if current_item and current_item.data(Qt.UserRole):
            field_type = current_item.data(Qt.UserRole)
            field_types = FieldFactory.get_field_types()
            
            if field_type in field_types:
                info = field_types[field_type]
                description_text = f"<b>{info['name']}</b><br>{info['description']}"
                self.description_label.setText(description_text)
                
                # Enhanced accessibility - announce the selection
                announcement = f"Selected {info['name']}. {info['description']}"
                self.description_label.setAccessibleDescription(announcement)
                
                self.selected_field_type = field_type
                self.add_button.setEnabled(True)
        else:
            self.description_label.setText("Select a field type to see its description.")
            self.description_label.setAccessibleDescription("No field type selected")
            self.selected_field_type = None
            self.add_button.setEnabled(False)
            
    def accept_selection(self):
        """Accept the current selection"""
        if self.selected_field_type:
            self.field_selected.emit(self.selected_field_type)
            self.accept()
            
    def keyPressEvent(self, event):
        """Handle keyboard events for accessibility"""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            if self.field_list.hasFocus() and self.selected_field_type:
                self.accept_selection()
                return
            elif self.add_button.hasFocus() and self.add_button.isEnabled():
                self.accept_selection()
                return
        elif event.key() == Qt.Key_Escape:
            self.reject()
            return
        elif event.key() == Qt.Key_Up or event.key() == Qt.Key_Down:
            # Ensure arrow keys work properly in the list
            if self.field_list.hasFocus():
                super().keyPressEvent(event)
                return
            
        super().keyPressEvent(event)
        
    def get_selected_field_type(self) -> str:
        """Get the selected field type"""
        return self.selected_field_type