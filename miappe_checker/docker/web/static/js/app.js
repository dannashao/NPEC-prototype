/**
 * Main application logic for MIAPPE metadata checker.
 * This file contains the core functionality for handling form interactions and API calls.
 */

// Global state
let currentInvestigationId = null;
let currentStudyId = null;
let currentData = null;

// API endpoints
const API_BASE_URL = '/miappe/api';

// Form initialization
const initializeForm = async (data) => {
    currentData = data;
    
    // Hide stage 1 and show stage 2
    document.getElementById('stage1').style.display = 'none';
    document.getElementById('stage2').style.display = 'block';
    
    // Initialize form fields based on MIAPPE schema
    Object.entries(data).forEach(([key, value]) => {
        const kebabKey = convertCamelToKebab(key);
        const element = document.querySelector(`[name="${kebabKey}"]`);
        if (element) {
            if (element.tagName === 'TEXTAREA') {
                element.value = value || '';
                element.dispatchEvent(new Event('input'));
            } else {
                element.value = value || '';
            }
        }
    });
    
    // Initialize textareas with auto-resize
    initializeTextareas();
    
    // Initialize MongoDB field dropdowns
    initializeMongoFieldDropdowns();
};

const initializeFormWithData = (data) => {
    console.log('Starting form initialization with data:', data);
    
    // Hide stage 1 and show stage 2
    document.getElementById('stage1').style.display = 'none';
    document.getElementById('stage2').style.display = 'block';
    
    // Initialize MongoDB field dropdowns after stage 2 is visible
    console.log('Stage 2 is now visible, initializing dropdowns...');
    initializeMongoFieldDropdowns();
    
    // Store the IDs globally
    window.currentInvestigationId = data.investigation?.investigation_id;
    window.currentStudyId = data.study?.study_id;
    
    // Helper function to set form field value and binding
    const setFieldValue = (scope, field, value, binding) => {
        const element = document.querySelector(`textarea[name="${scope}.${field}"]`);
        if (element) {
            // Handle array values
            const displayValue = Array.isArray(value) ? value.join(', ') : (value || '');
            element.value = displayValue;
            element.dispatchEvent(new Event('input'));
            console.log(`Set ${scope}.${field} to:`, displayValue);
            
            // Set MongoDB binding if exists
            if (binding) {
                // Find the dropdown for this field
                const formGroup = element.closest('.form-group');
                const dropdown = formGroup.querySelector('.mongo-field-dropdown');
                if (dropdown) {
                    dropdown.value = binding;
                    dropdown.dataset.selectedValue = binding;
                    dropdown.dataset.selectedScope = scope;
                    dropdown.dataset.selectedField = field;
                }
                
                // Update MongoDB field display
                const mongoField = document.querySelector(`.mongo-field[data-field="${binding}"]`);
                if (mongoField) {
                    // Add bound class to the MongoDB field itself
                    mongoField.classList.add('bound');
                    
                    // Create or update bindings container
                    let bindingsContainer = mongoField.querySelector('.field-bindings');
                    if (!bindingsContainer) {
                        bindingsContainer = document.createElement('div');
                        bindingsContainer.className = 'field-bindings';
                        mongoField.appendChild(bindingsContainer);
                    }
                    
                    // Clear existing bindings
                    bindingsContainer.innerHTML = '';
                    
                    // Create binding element
                    const bindingElement = document.createElement('div');
                    bindingElement.className = 'field-binding';
                    bindingElement.setAttribute('data-scope', scope);
                    bindingElement.setAttribute('data-field-name', field);
                    
                    // Create binding text
                    const bindingText = document.createElement('span');
                    bindingText.className = 'binding-text';
                    bindingText.textContent = `${field} (${scope})`;
                    
                    // Create remove button
                    const removeBtn = document.createElement('button');
                    removeBtn.className = 'remove-binding';
                    removeBtn.textContent = '×';
                    removeBtn.onclick = (e) => {
                        e.stopPropagation();
                        removeBinding(mongoField, bindingElement);
                        
                        // Reset the corresponding dropdown
                        if (dropdown) {
                            dropdown.value = '';
                            delete dropdown.dataset.selectedValue;
                            delete dropdown.dataset.selectedScope;
                            delete dropdown.dataset.selectedField;
                        }
                    };
                    
                    bindingElement.appendChild(bindingText);
                    bindingElement.appendChild(removeBtn);
                    bindingsContainer.appendChild(bindingElement);
                }
            }
        } else {
            console.warn(`Element not found: textarea[name="${scope}.${field}"]`);
        }
    };

    // Helper function to process scope data
    const processScopeData = (scope, data) => {
        if (!data) return;
        
        // Skip metadata fields
        const skipFields = ['is_new_record', 'created_at'];
        
        Object.entries(data).forEach(([dbField, value]) => {
            if (skipFields.includes(dbField)) return;
            
            // Convert snake_case to UPPER_SNAKE_CASE for mapping lookup
            const upperField = dbField.toUpperCase();
            // Get the frontend field name from the mapping
            const frontendField = DB_TO_FRONTEND[upperField];
            
            if (frontendField) {
                console.log(`Mapping ${dbField} to ${frontendField} for scope ${scope}`);
                // Check if there's a binding for this field
                const bindingField = `${dbField}_binding`;
                const binding = data[bindingField];
                setFieldValue(scope, frontendField, value, binding);
            } else {
                console.warn(`No mapping found for field ${dbField} in scope ${scope}`);
            }
        });
    };

    // Process investigation data
    if (data.investigation) {
        console.log('Processing investigation data:', data.investigation);
        processScopeData('INVESTIGATION', data.investigation);
    }

    // Process study data
    if (data.study) {
        console.log('Processing study data:', data.study);
        processScopeData('STUDY', data.study);
    }

    // Process other scopes
    const otherScopes = [
        { key: 'person', name: 'PERSON' },
        { key: 'data_file', name: 'DATA_FILE' },
        { key: 'biological_material', name: 'BIOLOGICAL_MATERIAL' },
        { key: 'environment', name: 'ENVIRONMENT' },
        { key: 'experimental_factor', name: 'EXPERIMENTAL_FACTOR' },
        { key: 'event', name: 'EVENT' },
        { key: 'observation_unit', name: 'OBSERVATION_UNIT' },
        { key: 'sample', name: 'SAMPLE' },
        { key: 'observed_variable', name: 'OBSERVED_VARIABLE' }
    ];

    otherScopes.forEach(scope => {
        const scopeData = data[scope.key];
        if (scopeData) {
            console.log(`Processing ${scope.name} data:`, scopeData);
            // Handle both array and single object data
            const dataArray = Array.isArray(scopeData) ? scopeData : [scopeData];
            dataArray.forEach(item => {
                if (item) {
                    processScopeData(scope.name, item);
                }
            });
        }
    });
    
    // Initialize textareas with auto-resize
    initializeTextareas();
};

// MongoDB field handling
const initializeMongoFieldDropdowns = () => {
    console.log('Initializing MongoDB field dropdowns...');
    
    // Check if we're in stage 2
    const stage2 = document.getElementById('stage2');
    if (!stage2 || stage2.style.display === 'none') {
        console.log('Stage 2 not visible, skipping dropdown initialization');
        return;
    }
    
    const dropdowns = document.querySelectorAll('.mongo-field-dropdown');
    console.log(`Found ${dropdowns.length} dropdowns to initialize`);
    
    if (dropdowns.length === 0) {
        console.warn('No MongoDB field dropdowns found in the DOM');
        return;
    }
    
    dropdowns.forEach((dropdown, index) => {
        console.log(`Setting up dropdown ${index + 1}:`, dropdown);
        
        // Remove any existing event listeners
        const newDropdown = dropdown.cloneNode(true);
        dropdown.parentNode.replaceChild(newDropdown, dropdown);
        
        newDropdown.addEventListener('change', (event) => {
            console.log('Dropdown change event triggered');
            const selectedField = event.target.value;
            console.log('Selected field:', selectedField);
            
            if (!selectedField) {
                console.log('No field selected, returning');
                return;
            }
            
            // Get the closest form group
            const formGroup = event.target.closest('.form-group');
            if (!formGroup) {
                console.error('Could not find parent form-group');
                return;
            }
            console.log('Found form group:', formGroup);
            
            // Get the scope and field from the textarea name
            const textarea = formGroup.querySelector('textarea');
            if (!textarea) {
                console.error('Could not find textarea in form group');
                return;
            }
            const [scope, field] = textarea.name.split('.');
            console.log('Parsed scope and field:', { scope, field });
            
            // Find the MongoDB field element
            const mongoField = document.querySelector(`.mongo-field[data-field="${selectedField}"]`);
            if (!mongoField) {
                console.error(`Could not find MongoDB field element for: ${selectedField}`);
                return;
            }
            console.log('Found MongoDB field element:', mongoField);
            
            try {
                // Create binding in MongoDB field
                console.log('Creating binding in MongoDB field...');
                createBinding(mongoField, scope, field, newDropdown);
                
                // Add bound class to form group
                formGroup.classList.add('bound');
                console.log('Added bound class to form group');
                
                // Store the selected value in the dropdown
                newDropdown.dataset.selectedValue = selectedField;
                newDropdown.dataset.selectedScope = scope;
                newDropdown.dataset.selectedField = field;
                
                console.log(`Successfully added binding for ${scope}.${field}:`, selectedField);
            } catch (error) {
                console.error('Error during binding process:', error);
            }
        });
    });
};

// Utility functions
const getUnfinishedMandatoryFields = () => {
    const unfinishedFields = {};
    const textareas = document.querySelectorAll('textarea[data-requirement="0"]');
    
    textareas.forEach(textarea => {
        if (!textarea.value.trim()) {
            const [scope, field] = textarea.name.split('.');
            if (!unfinishedFields[scope]) {
                unfinishedFields[scope] = [];
            }
            unfinishedFields[scope].push(field);
        }
    });
    
    return unfinishedFields;
};

// Event handlers
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM Content Loaded - Initializing application...');
    
    // Initialize textareas on page load
    initializeTextareas();
    
    // Check IDs button handler
    const checkIdsButton = document.getElementById('check-ids');
    if (checkIdsButton) {
        console.log('Found check-ids button, setting up click handler');
        checkIdsButton.addEventListener('click', async () => {
            const investigationId = document.getElementById('investigation_id').value;
            const studyId = document.getElementById('study_id').value;
            
            console.log('Check IDs button clicked');
            console.log('Input values:', { investigationId, studyId });
            
            if (!investigationId || !studyId) {
                showNotification('Please enter both Investigation ID and Study ID', 'error');
                return;
            }
            
            try {
                console.log('Sending request to /miappe/api/check_investigation');
                const response = await fetch(`${API_BASE_URL}/check_investigation`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        investigation_id: investigationId,
                        study_id: studyId
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                console.log('Response data:', data);
                
                // Show appropriate notification based on record status
                if (data.is_new_record) {
                    const message = `New record created for Investigation ID: ${investigationId} and Study ID: ${studyId}`;
                    await showPopup(message, ['Continue']);
                } else {
                    const createdAt = new Date(data.created_at);
                    const updatedAt = new Date(data.updated_at);
                    const formattedCreatedDate = createdAt.toLocaleString();
                    const formattedUpdatedDate = updatedAt.toLocaleString();
                    const message = `Existing record found!\nCreated on: ${formattedCreatedDate}\nModified on: ${formattedUpdatedDate}`;
                    await showPopup(message, ['Continue']);
                }
                
                // Initialize form with data
                await initializeFormWithData(data);
                
            } catch (error) {
                console.error('Error in check IDs:', error);
                showNotification('Error checking IDs: ' + error.message, 'error');
            }
        });
    }
    
    // Save button handler
    const form = document.getElementById('miappe-form');
    if (form) {
        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            
            // Check for unfinished mandatory fields
            const unfinishedFields = getUnfinishedMandatoryFields();
            if (Object.keys(unfinishedFields).length > 0) {
                let message = 'The following mandatory fields are not filled:\n\n';
                Object.entries(unfinishedFields).forEach(([scope, fields]) => {
                    message += `${scope}:\n`;
                    fields.forEach(field => {
                        message += `    - ${field}\n`;
                    });
                    message += '\n';
                });
                message += 'Do you want to save anyway?';
                
                const shouldProceed = await showPopup(message, ['Cancel', 'Save Anyway']);
                if (shouldProceed !== 'Save Anyway') {
                    return;
                }
            }
            
            // Collect and format form data
            const formData = {};
            form.querySelectorAll('textarea').forEach(textarea => {
                const [scope, field] = textarea.name.split('.');
                if (!formData[scope]) {
                    formData[scope] = {};
                }
                
                // Get the field value
                formData[scope][field] = textarea.value.trim();
            });
            
            // Collect bindings from MongoDB fields
            document.querySelectorAll('.mongo-field').forEach(mongoField => {
                const bindingsContainer = mongoField.querySelector('.field-bindings');
                if (bindingsContainer) {
                    bindingsContainer.querySelectorAll('.field-binding').forEach(binding => {
                        const scope = binding.getAttribute('data-scope');
                        const field = binding.getAttribute('data-field-name');
                        const mongoFieldValue = mongoField.getAttribute('data-field');
                        
                        if (scope && field && mongoFieldValue) {
                            if (!formData[scope]) {
                                formData[scope] = {};
                            }
                            // Add the binding with the correct field name
                            formData[scope][`${field}_binding`] = mongoFieldValue;
                            console.log(`Found binding for ${scope}.${field}:`, mongoFieldValue);
                        }
                    });
                }
            });
            
            // Get IDs from the form data
            const investigation_id = formData.INVESTIGATION?.investigationId;
            const study_id = formData.STUDY?.studyId;
            
            if (!investigation_id || !study_id) {
                showNotification('Missing investigation or study ID in form data', 'error');
                return;
            }
            
            // Debug log the request data
            const requestData = {
                investigation_id,
                study_id,
                form_data: formData
            };
            console.log('Sending save request with data:', JSON.stringify(requestData, null, 2));
            
            try {
                const response = await fetch(`${API_BASE_URL}/save_checklist`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(requestData)
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(`HTTP error! status: ${response.status}, message: ${errorData.error || 'Unknown error'}`);
                }
                
                const data = await response.json();
                showNotification('Checklist saved successfully', 'success');
            } catch (error) {
                console.error('Error saving form:', error);
                showNotification('Error saving checklist: ' + error.message, 'error');
            }
        });
    }
    
    // Reset bindings button handler
    const resetBindingsButton = document.getElementById('reset-all');
    if (resetBindingsButton) {
        resetBindingsButton.addEventListener('click', () => {
            console.log('Reset bindings button clicked');
            // Clear all bindings from MongoDB fields
            document.querySelectorAll('.mongo-field').forEach(field => {
                const bindingsContainer = field.querySelector('.field-bindings');
                if (bindingsContainer) {
                    bindingsContainer.innerHTML = '';
                }
                field.classList.remove('bound');
            });
            
            // Reset all dropdowns
            document.querySelectorAll('.mongo-field-dropdown').forEach(dropdown => {
                dropdown.value = '';
                delete dropdown.dataset.selectedValue;
                delete dropdown.dataset.selectedScope;
                delete dropdown.dataset.selectedField;
            });
            
            // Remove bound class from all form groups
            document.querySelectorAll('.form-group.bound').forEach(group => {
                group.classList.remove('bound');
            });
            
            // Clear localStorage
            localStorage.removeItem('miappeBindings');
            
            showNotification('All bindings have been reset successfully', 'success');
        });
    }

    // Add form submission handler
    const checklistForm = document.getElementById('checklistForm');
    if (checklistForm) {
        checklistForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            try {
                // Collect form data
                const formData = {};
                
                // First, collect all MongoDB field bindings
                const mongoFields = document.querySelectorAll('.mongo-field');
                mongoFields.forEach(mongoField => {
                    const scope = mongoField.getAttribute('data-scope');
                    const fieldName = mongoField.getAttribute('data-field-name');
                    const mongoFieldValue = mongoField.getAttribute('data-field');
                    
                    if (!formData[scope]) {
                        formData[scope] = {};
                    }
                    
                    // Convert field name to match backend format
                    const backendField = FRONTEND_TO_BACKEND[fieldName];
                    if (backendField) {
                        // Add the binding with the correct field name format
                        formData[scope][`${fieldName}_binding`] = mongoFieldValue;
                        console.log(`Added binding for ${scope}.${fieldName}: ${mongoFieldValue}`);
                    } else {
                        console.warn(`No backend mapping found for field: ${fieldName}`);
                    }
                });
                
                // Then collect all form field values
                const formGroups = document.querySelectorAll('.form-group');
                formGroups.forEach(group => {
                    const scope = group.getAttribute('data-scope');
                    const fieldName = group.getAttribute('data-field-name');
                    const input = group.querySelector('input, select, textarea');
                    
                    if (!input) return;
                    
                    if (!formData[scope]) {
                        formData[scope] = {};
                    }
                    
                    // Convert field name to match backend format
                    const backendField = FRONTEND_TO_BACKEND[fieldName];
                    if (backendField) {
                        formData[scope][fieldName] = input.value;
                    } else {
                        console.warn(`No backend mapping found for field: ${fieldName}`);
                    }
                });
                
                // Get investigation_id and study_id
                const investigationId = formData.investigation?.investigation_id;
                const studyId = formData.study?.study_id;
                
                if (!investigationId || !studyId) {
                    showNotification('Error: Missing investigation_id or study_id', 'error');
                    return;
                }
                
                // Debug log the request data
                console.log('Sending request data:', {
                    investigation_id: investigationId,
                    study_id: studyId,
                    form_data: formData
                });
                
                // Send data to backend
                const response = await fetch('/miappe/api/save_checklist', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        investigation_id: investigationId,
                        study_id: studyId,
                        form_data: formData
                    })
                });
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'Failed to save checklist');
                }
                
                showNotification('Checklist saved successfully', 'success');
            } catch (error) {
                console.error('Error saving checklist:', error);
                showNotification(error.message || 'Error saving checklist', 'error');
            }
        });
    }
}); 