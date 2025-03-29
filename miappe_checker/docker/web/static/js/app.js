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
                const formGroup = element.closest('.form-group');
                const fieldBindings = formGroup.querySelector('.field-bindings');
                if (fieldBindings) {
                    const bindingElement = document.createElement('div');
                    bindingElement.className = 'field-binding';
                    bindingElement.textContent = binding;
                    
                    // Add remove button
                    const removeBtn = document.createElement('button');
                    removeBtn.className = 'remove-binding';
                    removeBtn.textContent = '×';
                    removeBtn.onclick = () => bindingElement.remove();
                    
                    bindingElement.appendChild(removeBtn);
                    fieldBindings.appendChild(bindingElement);
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
                // Get the binding value if it exists
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
    const dropdowns = document.querySelectorAll('.mongo-field-dropdown');
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('change', (event) => {
            const selectedField = event.target.value;
            if (!selectedField) return;
            
            // Get the closest form group
            const formGroup = event.target.closest('.form-group');
            if (!formGroup) return;
            
            // Get the textarea in this form group
            const textarea = formGroup.querySelector('textarea');
            if (!textarea) return;
            
            // Add the binding to the field bindings div
            const fieldBindings = formGroup.querySelector('.field-bindings');
            if (fieldBindings) {
                const binding = document.createElement('div');
                binding.className = 'field-binding';
                binding.textContent = selectedField;
                
                // Add remove button
                const removeBtn = document.createElement('button');
                removeBtn.className = 'remove-binding';
                removeBtn.textContent = '×';
                removeBtn.onclick = () => binding.remove();
                
                binding.appendChild(removeBtn);
                fieldBindings.appendChild(binding);
            }
            
            // Reset dropdown
            event.target.value = '';
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
    // Initialize textareas on page load
    initializeTextareas();
    
    // Check IDs button handler
    const checkIdsButton = document.getElementById('check-ids');
    if (checkIdsButton) {
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
                    const formattedDate = createdAt.toLocaleString();
                    const message = `Existing record found! Created on: ${formattedDate}`;
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
                formData[scope][field] = textarea.value.trim();
                
                // Get MongoDB binding if exists
                const formGroup = textarea.closest('.form-group');
                const fieldBindings = formGroup.querySelector('.field-bindings');
                if (fieldBindings && fieldBindings.children.length > 0) {
                    const binding = fieldBindings.children[0].textContent;
                    formData[scope][`${field}_binding`] = binding;
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
            console.log('Sending save request with data:', requestData);
            
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
            const fieldBindings = document.querySelectorAll('.field-bindings');
            fieldBindings.forEach(bindingsDiv => {
                bindingsDiv.innerHTML = '';
            });
        });
    }
}); 