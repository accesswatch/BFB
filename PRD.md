Product Requirements Document (PRD)
GravityForms Desktop Builder — PySide6 (Windows)

Last updated: 2025-08-14
Author: (generated)

## 1. Purpose
Create a fully accessible desktop clone of the Gravity Forms form-builder for Windows using PySide6. The app must allow users to build, configure, test, save, and push forms to a WordPress site (Gravity Forms plugin) while providing a complete keyboard-only experience with strong ARIA/focus semantics for screen readers. No drag-and-drop: all interactions exposed via keyboard and accessible controls.

## 2. High-level goals
- Reproduce Gravity Forms feature set (field types, conditional logic, validation, pricing/calculation basics) where feasible.
- Provide a fully keyboardable, screen-reader-friendly builder UI that meets WCAG 2.1 AA (target) and documents deviations.
- Persist forms locally (editable JSON representation), and support a one-click publish to a target WordPress site running Gravity Forms (via REST API/authentication).
- Be extensible: plugin-like field definitions, import/export, and clear mapping to Gravity Forms API fields.

## 3. Success metrics
- 100% of builder actions operable via keyboard and documented keybindings.
- WCAG 2.1 AA automated checks pass for core builder screens (basic axe/Pa11y smoke tests), and manual screen reader acceptance tests pass for primary flows.
- Form created in-app that, when pushed, appears in Gravity Forms list on target WordPress instance and supports submissions.
- Round-trip save/load fidelity >= 99% for commonly used fields and settings.

## 4. Primary personas
- Form builder admin (Windows desktop user): creates complex forms for WordPress sites.
- Accessibility engineer: verifies keyboard and screen reader support.
- Developer/Integrator: connects app to WordPress and inspects payload mapping.

## 5. Scope (MVP vs Later)
MVP (deliver first):
- Core field types: Single-line text, Paragraph text, Number, Email, Phone, Dropdown, Radio Buttons, Checkboxes, Hidden, Date, Time, File Upload, Name (composite), Address (composite), Page/Section breaks, HTML/Content field.
- Field settings: label, description/help, placeholder, default value, required, CSS classes, visibility (admin-only/hidden), validation (pattern/min/max/length), conditional visibility rules (simple rules), ordering via Move Up/Move Down controls, delete, duplicate.
- Form settings: title, description, confirmation options (message/redirect/email), notifications basics (name, email template), form-level CSS classes, save/load (local JSON), export/import.
- Publish: push form to WordPress via REST API (local save required before push). Use Gravity Forms API v2 endpoints if available; support application passwords or configurable API credentials.
- Accessibility: full keyboard navigation, focus management, ARIA attributes, high-contrast themes, text-resize support.

Later / Post-MVP:
- Advanced pricing/product fields, coupons, payment gateway wiring, advanced conditional logic builder UI, visual themes, field-type plugin system, marketplace templates, preview/test-submit with sample submission history.

## 6. Feature inventory (from Gravity Forms feature set — to be verified)
Field types (MVP subset + notes):
- Single Line Text (label, placeholder, default, validation)
- Paragraph Text (multi-line)
- Number
- Email
- Phone
- URL / Website
- Dropdown
- Multi-select / List
- Radio Buttons
- Checkboxes
- Name (first, middle, last subfields)
- Address (street, city, state, zip, country)
- Date
- Time
- File Upload (with accepted MIME types and size limit)
- Hidden
- HTML / Content (arbitrary markup display)
- Section Break
- Page Break (for multi-page forms)
- List (repeating inputs)
- CAPTCHA / Spam protection (MVP: placeholder + server-side option)
- Product / Quantity / Total (deferred to post-MVP)

Field behaviors to support:
- Required toggle
- Label, description/help, admin label
- CSS class name
- Placeholder/default
- Validation rules (pattern, min/max, length, numeric ranges)
- Conditional logic: show/hide based on other field values (logical OR/AND for MVP: simple rules)
- Duplicate field
- Delete field with keyboard confirmation
- Re-order via Move Up / Move Down (buttons and keyboard gestures)

Form settings to support:
- Title, Description
- Confirmations (on-submit message or redirect)
- Notifications (email to address with templated body)
- Form-level CSS classes
- Save/Load local JSON and Export/Import
- Publish/Push to WordPress (with mapping validation)

## 7. Accessibility requirements (mandatory)
Standards and targets:
- Conformance target: WCAG 2.1 Level AA (aim to also align with 2.2 where straightforward).
- Platform: Windows (NVDA + Narrator test coverage). Also check VoiceOver on macOS for cross-platform validation if time permits.

Keyboard-only interaction model:
- All builder actions must be reachable via keyboard alone.
- No drag-and-drop. Re-ordering via Move Up / Move Down controls, and optional keyboard shortcuts (configurable) for moving fields: e.g., Ctrl+Alt+Up / Ctrl+Alt+Down (configurable in settings).
- Add-field via an Add Field dialog opened with Alt+F or a clearly labelled button. The dialog is a modal listbox with type filter and keyboard navigation; pressing Enter inserts field at the currently focused insertion point.
- Edit-field opens a configuration panel (drawer) in the right pane with all settings reachable with Tab/Shift+Tab and grouped with ARIA landmarks (role="region" and aria-labelledby).
- Focus management: when an action opens a modal or panel, focus moves into it to the first interactive control and returns to the invoking control when closed.
- Visual focus indicators must be highly visible and meet contrast requirements.

ARIA and semantics:
- Use appropriate role mappings: lists of fields use role="list" and each field instance role="listitem"; field controls should use native widgets where possible (QLineEdit -> role=textbox) and expose aria-label / aria-describedby.
- For movable items, include aria-grabbed or aria-dropeffect equivalents semantics via aria-live regions for changes, and use ARIA live to announce move/delete/duplicate operations.
- Provide descriptive labels and help text for every control and programmatic names for composite fields (e.g., Name -> "First name input" etc.).

- https://docs.gravityforms.com/rest-api-v2
- https://docs.gravityforms.com/submitting-forms-with-rest-api-v2
- https://docs.gravityforms.com/creating-entries-with-the-rest-api-v2
- https://docs.gravityforms.com/updating-forms-with-the-rest-api-v2
