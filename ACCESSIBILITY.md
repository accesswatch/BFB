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
- **F6** - Cycle between main interface panels (Form Structure → Form Fields → Field Editor)

## Screen Reader Support

### Interface Structure
The main interface is organized into three main areas accessible via F6:
1. **Form Structure Panel (Left)** - Shows form pages and sections
2. **Form Fields Panel (Center)** - Lists all form fields
3. **Field Editor Panel (Right)** - Properties editor for selected field

### Enhanced Accessibility Features

#### Live Region Announcements
- Field addition: "Added Text field: First Name"
- Field movement: "Moved 'Email' field up" / "Field is already at the top"
- Field deletion: "Deleted 'Phone Number' field"
- Field selection: "Selected Email, Text field, required"
- Panel navigation: "Focused on Form Fields panel"

#### Field List Navigation
- Fields are presented as a list with proper ARIA markup
- Each field item shows: Label, Required indicator (*), Field type, Position
- Accessible text includes: "Email, Text field, required, position 2 of 5"
- Use Arrow Keys to select fields, Enter to edit
- Tooltips provide additional context

#### Enhanced Keyboard Navigation
- **F6 Panel Cycling**: Seamlessly move between the three main panels
- **Comprehensive Key Handling**: All field operations available via keyboard
- **Focus Management**: Proper focus indicators and logical tab order
- **Movement Feedback**: Clear audio feedback for field reordering operations

### Navigation Tips
- Use **F6** to cycle between interface panels efficiently
- Use **Arrow Keys** within panels to navigate lists
- All operations provide immediate screen reader feedback
- Status changes are announced via live regions
- Error conditions are clearly announced with helpful messages

### Add Field Dialog Enhancements
- Opens with **Alt+F** or Add Field button
- Field types are grouped by category with clear navigation
- Arrow keys navigate field types with immediate description updates
- Enter key selects field type, Escape cancels
- Rich descriptions announced when field types are selected

### Field Editor Panel Improvements  
- Automatically updates when a field is selected
- Enhanced tab order for logical navigation
- Comprehensive accessible names and descriptions for all controls
- Properties grouped in logical sections with clear labels

## Accessibility Features

### Visual Design
- High contrast focus indicators with enhanced visibility
- Large click targets (minimum 44px)
- Consistent color scheme with accessibility considerations
- Scalable text (supports system zoom up to 200%)
- Clear visual feedback for field movement operations

### Keyboard-Only Operation
- No drag-and-drop required - all operations keyboard accessible
- F6 panel cycling for efficient navigation
- Comprehensive keyboard shortcuts for all functions
- Clear tab order throughout interface
- Enhanced field movement with boundary detection

### Screen Reader Compatibility
- Tested with NVDA on Windows
- Compatible with Windows Narrator
- ARIA landmarks for major interface sections
- Live regions for dynamic status updates
- Descriptive labels for all controls with context
- Position information for list items

### Enhanced Form Field Support
All field types are fully accessible with rich descriptions:
- **Text Fields** - Standard text input with validation
- **Choice Fields** (Dropdown, Radio, Checkbox) - Accessible choice management
- **Composite Fields** (Name, Address) - Clear sub-field labels
- **File Upload** - Accessible file selection with type/size restrictions
- **Content Fields** (HTML, Section Break) - Proper content structure

## Field Movement User Experience

### Keyboard Field Movement
- **Ctrl+Alt+Up** / **Ctrl+Alt+Down** - Move fields with immediate feedback
- **Visual Feedback** - Selection moves with field for clear orientation
- **Boundary Detection** - Clear announcements when movement isn't possible
- **Position Updates** - Screen reader announces new field positions
- **Error Handling** - Helpful messages for invalid operations

### Enhanced Movement Features
- Real-time position announcements: "Moved 'Email' field up"
- Boundary feedback: "Field is already at the top"
- Focus preservation during movement operations
- Clear visual indicators during field reordering

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

## Recent Accessibility Enhancements

### Live Regions
- Dynamic content updates announced to screen readers
- Status messages for all field operations
- Error announcements with helpful context

### Panel Navigation
- F6 cycling between all major interface areas
- Clear focus management and announcements
- Logical navigation flow

### Enhanced Field Operations
- Rich screen reader feedback for all operations
- Position-aware field movement
- Comprehensive keyboard operation support
- Better error handling and user guidance

### Improved Focus Management
- Enhanced focus indicators throughout interface
- Logical tab order in all dialogs and panels
- Consistent focus behavior across all components

## Customization

### Keyboard Shortcuts
- Most shortcuts follow standard Windows conventions
- Custom shortcuts can be configured in future versions
- All shortcuts are documented in tooltips and menus

### Screen Reader Settings
- Works with default screen reader settings
- No special configuration required
- Verbosity can be controlled through screen reader settings