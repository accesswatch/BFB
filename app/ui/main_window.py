from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QListWidget, QSplitter, QMenuBar, QMenu, QFileDialog, QMessageBox,
    QListWidgetItem, QApplication, QStatusBar, QFrame
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QKeySequence, QAction, QFont, QShortcut

from ..models.form_model import FormModel, FieldModel, FieldType
from ..models.field_factory import FieldFactory
from ..services.form_service import FormService
from ..services.wp_client import WPClient
from .add_field_dialog import AddFieldDialog
from .field_editor_panel import FieldEditorPanel
from .wordpress_dialog import WordPressDialog


class MainWindow(QMainWindow):
    """Main application window for BFB Form Builder"""
    
    def __init__(self):
        super().__init__()
        self.current_form = None
        self.current_filename = None
        self.form_service = FormService()
        self.wp_client = None
        
        # Panel references for F6 cycling
        self.panels = []
        self.current_panel_index = 0
        
        self.setup_ui()
        self.setup_menu()
        self.setup_accessibility()
        self.setup_keyboard_shortcuts()
        self.setup_live_regions()
        
        # Create a new form by default
        self.new_form()
        
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("BFB — BITS Form Builder")
        self.resize(1200, 800)
        
        # Central widget and main layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Toolbar section
        toolbar_frame = QFrame()
        toolbar_frame.setFrameStyle(QFrame.Box)
        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setSpacing(10)
        
        # Form operations buttons
        self.new_btn = QPushButton("New Form")
        self.open_btn = QPushButton("Open")
        self.save_btn = QPushButton("Save")
        self.publish_btn = QPushButton("Publish")
        
        # Field operations buttons
        separator1 = QFrame()
        separator1.setFrameStyle(QFrame.VLine)
        
        self.add_field_btn = QPushButton("Add Field")
        self.duplicate_field_btn = QPushButton("Duplicate")
        self.delete_field_btn = QPushButton("Delete")
        
        separator2 = QFrame()
        separator2.setFrameStyle(QFrame.VLine)
        
        self.move_up_btn = QPushButton("Move Up")
        self.move_down_btn = QPushButton("Move Down")
        
        # Add buttons to toolbar
        toolbar_layout.addWidget(self.new_btn)
        toolbar_layout.addWidget(self.open_btn) 
        toolbar_layout.addWidget(self.save_btn)
        toolbar_layout.addWidget(self.publish_btn)
        toolbar_layout.addWidget(separator1)
        toolbar_layout.addWidget(self.add_field_btn)
        toolbar_layout.addWidget(self.duplicate_field_btn)
        toolbar_layout.addWidget(self.delete_field_btn)
        toolbar_layout.addWidget(separator2)
        toolbar_layout.addWidget(self.move_up_btn)
        toolbar_layout.addWidget(self.move_down_btn)
        toolbar_layout.addStretch()
        
        layout.addWidget(toolbar_frame)
        
        # Main content area with splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Form structure
        self.left_panel = QWidget()
        self.left_panel.setMaximumWidth(200)
        left_layout = QVBoxLayout(self.left_panel)
        
        left_title = QLabel("Form Structure")
        left_title.setFont(QFont("Arial", 10, QFont.Bold))
        left_layout.addWidget(left_title)
        
        self.pages_list = QListWidget()
        self.pages_list.addItem("Page 1")
        self.pages_list.setMaximumHeight(100)
        left_layout.addWidget(self.pages_list)
        
        left_layout.addStretch()
        
        # Center panel - Field list
        self.center_panel = QWidget()
        center_layout = QVBoxLayout(self.center_panel)
        
        # Form title display
        self.form_title_label = QLabel("Untitled Form")
        title_font = QFont("Arial", 14, QFont.Bold)
        self.form_title_label.setFont(title_font)
        self.form_title_label.setStyleSheet("QLabel { padding: 10px; background-color: #f5f5f5; border: 1px solid #ddd; }")
        center_layout.addWidget(self.form_title_label)
        
        center_title = QLabel("Form Fields")
        center_title.setFont(QFont("Arial", 10, QFont.Bold))
        center_layout.addWidget(center_title)
        
        self.fields_list = QListWidget()
        self.fields_list.setAlternatingRowColors(True)
        center_layout.addWidget(self.fields_list)
        
        # Right panel - Field editor
        self.field_editor = FieldEditorPanel()
        
        # Add panels to splitter
        splitter.addWidget(self.left_panel)
        splitter.addWidget(self.center_panel)
        splitter.addWidget(self.field_editor)
        
        # Store panel references for F6 cycling
        self.panels = [self.left_panel, self.center_panel, self.field_editor]
        
        # Set splitter proportions (left: 15%, center: 50%, right: 35%)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        splitter.setSizes([200, 600, 400])
        
        layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Connect signals
        self.connect_signals()
        
    def setup_menu(self):
        """Setup the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New Form", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_form)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open Form...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_form)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save Form", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_form)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save Form As...", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self.save_form_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        publish_action = QAction("Publish to WordPress", self)
        publish_action.triggered.connect(self.publish_form)
        file_menu.addAction(publish_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        add_field_action = QAction("Add Field...", self)
        add_field_action.setShortcut("Alt+F")
        add_field_action.triggered.connect(self.add_field)
        edit_menu.addAction(add_field_action)
        
        edit_menu.addSeparator()
        
        duplicate_action = QAction("Duplicate Field", self)
        duplicate_action.setShortcut("Ctrl+D")
        duplicate_action.triggered.connect(self.duplicate_field)
        edit_menu.addAction(duplicate_action)
        
        delete_action = QAction("Delete Field", self)
        delete_action.setShortcut(QKeySequence.Delete)
        delete_action.triggered.connect(self.delete_field)
        edit_menu.addAction(delete_action)
        
        edit_menu.addSeparator()
        
        move_up_action = QAction("Move Field Up", self)
        move_up_action.setShortcut("Ctrl+Alt+Up")
        move_up_action.triggered.connect(self.move_field_up)
        edit_menu.addAction(move_up_action)
        
        move_down_action = QAction("Move Field Down", self)
        move_down_action.setShortcut("Ctrl+Alt+Down")
        move_down_action.triggered.connect(self.move_field_down)
        edit_menu.addAction(move_down_action)
        
    def setup_accessibility(self):
        """Setup accessibility attributes"""
        self.setAccessibleName("BFB Form Builder Main Window")
        self.setAccessibleDescription("Main window for building accessible forms")
        
        # Set ARIA landmarks for major sections
        self.left_panel.setAccessibleName("Form Structure Panel")
        self.left_panel.setAccessibleDescription("Navigation panel showing form pages and structure")
        self.left_panel.setProperty("aria-label", "Form Structure")
        
        self.center_panel.setAccessibleName("Form Fields Panel") 
        self.center_panel.setAccessibleDescription("Main content panel showing form fields")
        self.center_panel.setProperty("aria-label", "Form Fields")
        
        self.field_editor.setAccessibleName("Field Editor Panel")
        self.field_editor.setAccessibleDescription("Properties panel for editing selected field")
        self.field_editor.setProperty("aria-label", "Field Editor")
        
        # Set accessible names for lists
        self.pages_list.setAccessibleName("Form Pages List")
        self.pages_list.setAccessibleDescription("List of form pages. Currently single page forms are supported.")
        
        self.fields_list.setAccessibleName("Form Fields List")
        self.fields_list.setAccessibleDescription("List of fields in the current form. Use arrow keys to navigate, Enter to edit, Ctrl+Alt+Up/Down to move fields.")
        
        # Enhanced button accessibility with keyboard shortcut information
        self.new_btn.setAccessibleName("New Form")
        self.new_btn.setAccessibleDescription("Create a new form (Ctrl+N)")
        self.new_btn.setToolTip("Create a new form (Ctrl+N)")
        
        self.open_btn.setAccessibleName("Open Form")
        self.open_btn.setAccessibleDescription("Open an existing form file (Ctrl+O)")
        self.open_btn.setToolTip("Open an existing form file (Ctrl+O)")
        
        self.save_btn.setAccessibleName("Save Form")
        self.save_btn.setAccessibleDescription("Save the current form (Ctrl+S)")
        self.save_btn.setToolTip("Save the current form (Ctrl+S)")
        
        self.publish_btn.setAccessibleName("Publish Form")
        self.publish_btn.setAccessibleDescription("Publish the form to WordPress")
        self.publish_btn.setToolTip("Publish the form to WordPress")
        
        self.add_field_btn.setAccessibleName("Add Field")
        self.add_field_btn.setAccessibleDescription("Add a new field to the form (Alt+F)")
        self.add_field_btn.setToolTip("Add a new field to the form (Alt+F)")
        
        self.duplicate_field_btn.setAccessibleName("Duplicate Field")
        self.duplicate_field_btn.setAccessibleDescription("Duplicate the selected field (Ctrl+D)")
        self.duplicate_field_btn.setToolTip("Duplicate the selected field (Ctrl+D)")
        
        self.delete_field_btn.setAccessibleName("Delete Field")
        self.delete_field_btn.setAccessibleDescription("Delete the selected field (Delete key)")
        self.delete_field_btn.setToolTip("Delete the selected field (Delete key)")
        
        self.move_up_btn.setAccessibleName("Move Field Up")
        self.move_up_btn.setAccessibleDescription("Move the selected field up (Ctrl+Alt+Up)")
        self.move_up_btn.setToolTip("Move the selected field up (Ctrl+Alt+Up)")
        
        self.move_down_btn.setAccessibleName("Move Field Down")
        self.move_down_btn.setAccessibleDescription("Move the selected field down (Ctrl+Alt+Down)")
        self.move_down_btn.setToolTip("Move the selected field down (Ctrl+Alt+Down)")
        
        # Form title accessibility
        self.form_title_label.setAccessibleName("Form Title")
        self.form_title_label.setAccessibleDescription("Title of the current form")
        
        # Set better focus policy for keyboard navigation
        self.fields_list.setFocusPolicy(Qt.StrongFocus)
        self.pages_list.setFocusPolicy(Qt.StrongFocus)
        
        # Enable keyboard tracking for better accessibility
        self.fields_list.setKeyboardTracking(True)
        
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for accessibility"""
        # F6 for cycling between panels
        f6_shortcut = QShortcut(QKeySequence("F6"), self)
        f6_shortcut.activated.connect(self.cycle_panels)
        
        # Enhanced keyboard navigation for field list
        self.fields_list.setFocus()  # Set initial focus
        
        # Custom key handling for field list
        self.fields_list.keyPressEvent = self.field_list_key_press_event
        
    def cycle_panels(self):
        """Cycle focus between main panels using F6"""
        if not self.panels:
            return
            
        self.current_panel_index = (self.current_panel_index + 1) % len(self.panels)
        current_panel = self.panels[self.current_panel_index]
        
        # Focus on the first focusable widget in the panel
        if current_panel == self.left_panel:
            self.pages_list.setFocus()
            self.announce_to_screen_reader("Focused on Form Structure panel")
        elif current_panel == self.center_panel:
            self.fields_list.setFocus()
            self.announce_to_screen_reader("Focused on Form Fields panel")
        elif current_panel == self.field_editor:
            self.field_editor.setFocus()
            self.announce_to_screen_reader("Focused on Field Editor panel")
            
    def field_list_key_press_event(self, event):
        """Enhanced key handling for field list"""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Enter key - edit the selected field
            self.edit_field(self.fields_list.currentItem())
            return
        elif event.key() == Qt.Key_Delete:
            # Delete key - delete field with confirmation
            self.delete_field()
            return
        elif event.modifiers() == (Qt.ControlModifier | Qt.AltModifier):
            if event.key() == Qt.Key_Up:
                self.move_field_up()
                return
            elif event.key() == Qt.Key_Down:
                self.move_field_down()
                return
        
        # Default handling for other keys (arrow navigation, etc.)
        QListWidget.keyPressEvent(self.fields_list, event)
        
    def setup_live_regions(self):
        """Setup live regions for screen reader announcements"""
        # Create an invisible label for live announcements
        self.live_region = QLabel()
        self.live_region.setVisible(False)
        self.live_region.setAccessibleName("Status Updates")
        self.live_region.setProperty("aria-live", "polite")
        self.live_region.setProperty("aria-atomic", "true")
        
        # Add to layout but keep invisible
        self.centralWidget().layout().addWidget(self.live_region)
        
    def announce_to_screen_reader(self, message: str):
        """Announce message to screen reader via live region"""
        self.live_region.setText(message)
        self.status_bar.showMessage(message)
        
        # Clear the live region after a short delay to allow for re-announcements
        QTimer.singleShot(100, lambda: self.live_region.setText(""))
        
    def connect_signals(self):
        """Connect UI signals"""
        # Button signals
        self.new_btn.clicked.connect(self.new_form)
        self.open_btn.clicked.connect(self.open_form)
        self.save_btn.clicked.connect(self.save_form)
        self.publish_btn.clicked.connect(self.publish_form)
        
        self.add_field_btn.clicked.connect(self.add_field)
        self.duplicate_field_btn.clicked.connect(self.duplicate_field)
        self.delete_field_btn.clicked.connect(self.delete_field)
        self.move_up_btn.clicked.connect(self.move_field_up)
        self.move_down_btn.clicked.connect(self.move_field_down)
        
        # List signals
        self.fields_list.currentRowChanged.connect(self.on_field_selected)
        self.fields_list.itemDoubleClicked.connect(self.edit_field)
        
        # Field editor signal
        self.field_editor.field_updated.connect(self.on_field_updated)
        
    def new_form(self):
        """Create a new form"""
        if self.check_unsaved_changes():
            self.current_form = self.form_service.create_new_form()
            self.current_filename = None
            self.refresh_ui()
            self.status_bar.showMessage("New form created")
            
    def open_form(self):
        """Open an existing form"""
        if not self.check_unsaved_changes():
            return
            
        forms_dir = self.form_service.get_forms_directory()
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open Form", forms_dir, "JSON Files (*.json)"
        )
        
        if filename:
            try:
                self.current_form = self.form_service.import_form(filename)
                self.current_filename = filename
                self.refresh_ui()
                self.status_bar.showMessage(f"Opened: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open form: {str(e)}")
                
    def save_form(self):
        """Save the current form"""
        if not self.current_form:
            return
            
        try:
            if self.current_filename:
                # Save to existing file
                self.form_service.export_form(self.current_form, self.current_filename)
                self.status_bar.showMessage(f"Saved: {self.current_filename}")
            else:
                # Save as new file
                filename = self.form_service.save_form(self.current_form)
                self.current_filename = self.form_service.forms_dir / filename
                self.status_bar.showMessage(f"Saved: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save form: {str(e)}")
            
    def save_form_as(self):
        """Save form with a new filename"""
        if not self.current_form:
            return
            
        forms_dir = self.form_service.get_forms_directory()
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Form As", forms_dir, "JSON Files (*.json)"
        )
        
        if filename:
            try:
                self.form_service.export_form(self.current_form, filename)
                self.current_filename = filename
                self.status_bar.showMessage(f"Saved as: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save form: {str(e)}")
                
    def publish_form(self):
        """Publish form to WordPress"""
        if not self.current_form:
            QMessageBox.warning(self, "No Form", "Please create or open a form before publishing.")
            return
            
        # Show WordPress dialog
        dialog = WordPressDialog(self, self.current_form)
        dialog.form_published.connect(self.on_form_published)
        dialog.exec()
        
    def on_form_published(self, result: dict):
        """Handle successful form publishing"""
        form_id = result.get('id', 'Unknown')
        self.status_bar.showMessage(f"Form published successfully! WordPress Form ID: {form_id}")
        
        # Optionally update the form ID in our model
        if 'id' in result and isinstance(result['id'], int):
            self.current_form.id = result['id']
        
    def add_field(self):
        """Show add field dialog"""
        dialog = AddFieldDialog(self)
        dialog.field_selected.connect(self.on_field_type_selected)
        dialog.exec()
        
    def on_field_type_selected(self, field_type: str):
        """Handle field type selection from add field dialog"""
        if self.current_form:
            try:
                field_type_enum = FieldType(field_type)
                self.form_service.add_field_to_form(self.current_form, field_type_enum)
                self.refresh_field_list()
                # Select the newly added field
                if self.current_form.fields:
                    new_field_index = len(self.current_form.fields) - 1
                    self.fields_list.setCurrentRow(new_field_index)
                    field_name = self.current_form.fields[new_field_index].label
                    self.announce_to_screen_reader(f"Added {field_type} field: {field_name}")
            except Exception as e:
                error_msg = f"Failed to add field: {str(e)}"
                QMessageBox.critical(self, "Error", error_msg)
                self.announce_to_screen_reader(error_msg)
                
    def duplicate_field(self):
        """Duplicate the selected field"""
        current_row = self.fields_list.currentRow()
        if current_row < 0 or not self.current_form or current_row >= len(self.current_form.fields):
            self.announce_to_screen_reader("No field selected to duplicate")
            return
            
        try:
            field_id = self.current_form.fields[current_row].id
            field_label = self.current_form.fields[current_row].label
            self.form_service.duplicate_field_in_form(self.current_form, field_id)
            self.refresh_field_list()
            self.fields_list.setCurrentRow(current_row + 1)  # Select the duplicate
            self.announce_to_screen_reader(f"Duplicated '{field_label}' field")
        except Exception as e:
            error_msg = f"Failed to duplicate field: {str(e)}"
            QMessageBox.critical(self, "Error", error_msg)
            self.announce_to_screen_reader(error_msg)
            
    def delete_field(self):
        """Delete the selected field"""
        current_row = self.fields_list.currentRow()
        if current_row < 0 or not self.current_form or current_row >= len(self.current_form.fields):
            self.announce_to_screen_reader("No field selected to delete")
            return
            
        field = self.current_form.fields[current_row]
        reply = QMessageBox.question(
            self, "Delete Field", 
            f"Are you sure you want to delete the field '{field.label}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                field_label = field.label
                self.form_service.remove_field_from_form(self.current_form, field.id)
                self.refresh_field_list()
                self.field_editor.set_field(None)
                self.announce_to_screen_reader(f"Deleted '{field_label}' field")
            except Exception as e:
                error_msg = f"Failed to delete field: {str(e)}"
                QMessageBox.critical(self, "Error", error_msg)
                self.announce_to_screen_reader(error_msg)
        else:
            self.announce_to_screen_reader("Field deletion cancelled")
                
    def move_field_up(self):
        """Move the selected field up"""
        current_row = self.fields_list.currentRow()
        if current_row <= 0 or not self.current_form or current_row >= len(self.current_form.fields):
            if current_row == 0:
                self.announce_to_screen_reader("Field is already at the top")
            return
            
        try:
            field_id = self.current_form.fields[current_row].id
            field_label = self.current_form.fields[current_row].label
            self.form_service.move_field_up(self.current_form, field_id)
            self.refresh_field_list()
            self.fields_list.setCurrentRow(current_row - 1)
            self.announce_to_screen_reader(f"Moved '{field_label}' field up")
        except Exception as e:
            error_msg = f"Failed to move field: {str(e)}"
            QMessageBox.critical(self, "Error", error_msg)
            self.announce_to_screen_reader(error_msg)
            
    def move_field_down(self):
        """Move the selected field down"""
        current_row = self.fields_list.currentRow()
        if current_row < 0 or not self.current_form or current_row >= len(self.current_form.fields) - 1:
            if current_row == len(self.current_form.fields) - 1:
                self.announce_to_screen_reader("Field is already at the bottom")
            return
            
        try:
            field_id = self.current_form.fields[current_row].id
            field_label = self.current_form.fields[current_row].label
            self.form_service.move_field_down(self.current_form, field_id)
            self.refresh_field_list()
            self.fields_list.setCurrentRow(current_row + 1)
            self.announce_to_screen_reader(f"Moved '{field_label}' field down")
        except Exception as e:
            error_msg = f"Failed to move field: {str(e)}"
            QMessageBox.critical(self, "Error", error_msg)
            self.announce_to_screen_reader(error_msg)
            
    def on_field_selected(self, current_row: int):
        """Handle field selection"""
        if current_row >= 0 and self.current_form and current_row < len(self.current_form.fields):
            field = self.current_form.fields[current_row]
            self.field_editor.set_field(field)
            # Announce field selection to screen reader
            field_types = FieldFactory.get_field_types()
            type_name = field_types.get(field.type, {}).get("name", str(field.type))
            required_status = "required" if field.isRequired else "optional"
            self.announce_to_screen_reader(f"Selected {field.label}, {type_name} field, {required_status}")
        else:
            self.field_editor.set_field(None)
            
    def edit_field(self, item):
        """Handle field double-click (focus on editor)"""
        self.field_editor.setFocus()
        
    def on_field_updated(self, field: FieldModel):
        """Handle field updates from editor"""
        # Update the field list display
        current_row = self.fields_list.currentRow()
        if current_row >= 0:
            item = self.fields_list.item(current_row)
            if item:
                item.setText(self.format_field_display(field))
        
        # Update form title display
        self.form_title_label.setText(self.current_form.title)
        
    def refresh_ui(self):
        """Refresh the entire UI"""
        self.refresh_field_list()
        self.field_editor.set_field(None)
        
        if self.current_form:
            self.form_title_label.setText(self.current_form.title)
        
    def refresh_field_list(self):
        """Refresh the field list"""
        self.fields_list.clear()
        
        if self.current_form and self.current_form.fields:
            for i, field in enumerate(self.current_form.fields):
                item = QListWidgetItem(self.format_field_display(field))
                item.setData(Qt.UserRole, field)
                
                # Enhanced accessibility for list items
                field_types = FieldFactory.get_field_types()
                type_name = field_types.get(field.type, {}).get("name", str(field.type))
                required_status = "required" if field.isRequired else "optional"
                position_info = f"position {i + 1} of {len(self.current_form.fields)}"
                
                accessible_text = f"{field.label}, {type_name} field, {required_status}, {position_info}"
                item.setAccessibleText(accessible_text)
                item.setToolTip(f"{type_name} field: {field.label}\nRequired: {'Yes' if field.isRequired else 'No'}\nPosition: {i + 1} of {len(self.current_form.fields)}")
                
                self.fields_list.addItem(item)
                
    def format_field_display(self, field: FieldModel) -> str:
        """Format field display text"""
        field_types = FieldFactory.get_field_types()
        type_name = field_types.get(field.type, {}).get("name", str(field.type))
        
        required_indicator = " *" if field.isRequired else ""
        return f"{field.label}{required_indicator} — {type_name}"
        
    def check_unsaved_changes(self) -> bool:
        """Check for unsaved changes. Returns True if it's OK to proceed."""
        # TODO: Implement unsaved changes tracking
        return True
        
    def closeEvent(self, event):
        """Handle window close event"""
        if self.check_unsaved_changes():
            event.accept()
        else:
            event.ignore()
