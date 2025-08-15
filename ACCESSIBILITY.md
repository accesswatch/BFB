# BFB Accessibility Guide

BFB (BITS Form Builder) is designed to be fully accessible with complete keyboard navigation and screen reader support following WCAG 2.1 Level AA guidelines.

## Keyboard Shortcuts

### File Operations
- **Ctrl+N** - Create new form
- **Ctrl+O** - Open existing form
- **Ctrl+S** - Save current form
- **Ctrl+Shift+S** - Save form as (with new name)
- **Ctrl+Q** - Exit application

### Field Operations
- **Alt+F** - Open Add Field dialog
- **Ctrl+D** - Duplicate selected field
- **Delete** - Delete selected field (with confirmation)
- **Ctrl+Alt+Up** - Move selected field up
- **Ctrl+Alt+Down** - Move selected field down

### Navigation
- **Tab / Shift+Tab** - Navigate between interface elements
- **Arrow Keys** - Navigate within lists (field list, choice lists, etc.)
- **Enter** - Activate buttons or edit selected field
- **Escape** - Close dialogs or cancel operations
- **F6** - Cycle between main interface panels

## Screen Reader Support

### Interface Structure
The main interface is organized into three main areas:
1. **Form Structure Panel (Left)** - Shows form pages and sections
2. **Field List Panel (Center)** - Lists all form fields
3. **Field Editor Panel (Right)** - Properties editor for selected field

### Navigation Tips
- Use **Tab** to move between interface areas
- Use **Arrow Keys** to navigate within lists
- Each interface element has descriptive accessible names
- Status changes are announced via live regions
- All operations provide audio feedback

### Field List Navigation
- Fields are presented as a list with `role="list"`
- Each field item shows: Label, Required indicator (*), Field type
- Use Arrow Keys to select fields
- Enter key opens field for editing
- Required fields are clearly announced

### Add Field Dialog
- Opens with **Alt+F** or Add Field button
- Field types are grouped by category (Standard/Advanced)
- Use Arrow Keys to navigate field types
- Enter key selects and adds the field type
- Each field type includes description when selected

### Field Editor Panel
- Automatically updates when a field is selected
- Properties are grouped in collapsible sections:
  - General Settings
  - Appearance 
  - Input Settings
  - Choices (for select/radio/checkbox fields)
  - Validation
  - File Upload Settings (for file fields)
  - HTML Content (for HTML fields)

## Accessibility Features

### Visual Design
- High contrast focus indicators
- Large click targets (minimum 44px)
- Consistent color scheme
- Scalable text (supports system zoom up to 200%)

### Keyboard-Only Operation
- No drag-and-drop required
- All functionality available via keyboard
- Clear tab order throughout interface
- Skip links for screen readers

### Screen Reader Compatibility
- Tested with NVDA on Windows
- Compatible with Windows Narrator
- Proper heading structure
- Descriptive labels for all controls
- Live regions for status updates

### Form Field Support
All field types are fully accessible:
- **Text Fields** - Standard text input with validation
- **Choice Fields** (Dropdown, Radio, Checkbox) - Accessible choice management
- **Composite Fields** (Name, Address) - Clear sub-field labels
- **File Upload** - Accessible file selection with type/size restrictions
- **Content Fields** (HTML, Section Break) - Proper content structure

## WordPress Publishing

The WordPress publishing dialog includes:
- Secure credential storage
- Connection testing with clear feedback  
- Form conflict detection
- Progress indicators for all operations
- Clear error messages and troubleshooting help

## Getting Help

For accessibility issues or suggestions:
1. Check this guide for keyboard shortcuts
2. Ensure latest version is installed
3. Test with NVDA or Windows Narrator
4. Report issues through project repository

## Technical Standards

BFB conforms to:
- **WCAG 2.1 Level AA** - Web accessibility guidelines
- **Section 508** - US accessibility standards
- **Windows Accessibility Standards** - Platform-specific guidelines
- **Keyboard Navigation Standards** - Standard Windows key combinations

## Customization

### Keyboard Shortcuts
- Most shortcuts follow standard Windows conventions
- Custom shortcuts can be configured in future versions
- All shortcuts are documented in tooltips and menus

### Screen Reader Settings
- Works with default screen reader settings
- No special configuration required
- Verbosity can be controlled through screen reader settings