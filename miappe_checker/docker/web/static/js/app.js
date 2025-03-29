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
    
    // Populate form fields
    Object.entries(data).forEach(([key, value]) => {
        const element = document.querySelector(`[name="${key}"]`);
        if (element) {
            if (element.tagName === 'TEXTAREA') {
                element.value = value || '';
                element.dispatchEvent(new Event('input'));
            } else {
                element.value = value || '';
            }
        }
    });
    
    // Initialize textareas
    initializeTextareas();
    
    // Restore saved bindings
    restoreBindings();
};

const initializeFormWithData = (data) => {
    console.log('Starting form initialization with data:', data);
    
    // Get the form container
    const formContainer = document.getElementById('form-container');
    if (!formContainer) {
        console.error('Form container not found');
        return;
    }
    
    // Show the form container
    formContainer.style.display = 'block';
    
    // Initialize investigation data
    if (data.investigation) {
        console.log('Initializing investigation data:', data.investigation);
        Object.entries(data.investigation).forEach(([key, value]) => {
            const element = document.querySelector(`textarea[name="investigation.${key}"]`);
            if (element) {
                element.value = Array.isArray(value) ? value.join(', ') : (value || '');
                element.dispatchEvent(new Event('input'));
            }
        });
    }

    // Initialize study data
    if (data.study) {
        console.log('Initializing study data:', data.study);
        Object.entries(data.study).forEach(([key, value]) => {
            const element = document.querySelector(`textarea[name="study.${key}"]`);
            if (element) {
                element.value = Array.isArray(value) ? value.join(', ') : (value || '');
                element.dispatchEvent(new Event('input'));
            }
        });
    }

    // Initialize related data (person, data file, etc.)
    const relatedDataTypes = [
        'person', 'dataFile', 'biologicalMaterial', 'environment',
        'experimentalFactor', 'event', 'observationUnit', 'sample',
        'observedVariable'
    ];

    relatedDataTypes.forEach(type => {
        if (data[type]) {
            console.log(`Initializing ${type} data:`, data[type]);
            data[type].forEach(item => {
                Object.entries(item).forEach(([key, value]) => {
                    const element = document.querySelector(`textarea[name="${type}.${key}"]`);
                    if (element) {
                        element.value = Array.isArray(value) ? value.join(', ') : (value || '');
                        element.dispatchEvent(new Event('input'));
                    }
                });
            });
        }
    });
};

const getUnfinishedMandatoryFields = () => {
    const unfinishedFields = {};
    const formGroups = document.querySelectorAll('.form-group');
    
    formGroups.forEach(group => {
        const label = group.querySelector('label');
        const textarea = group.querySelector('textarea');
        
        if (!label || !textarea) return;
        
        const isMandatory = label.querySelector('.mandatory') !== null;
        const scope = textarea.name.split('.')[0];
        
        if (!isMandatory) return;
        
        const scopeSection = group.closest('.form-section');
        if (!scopeSection) return;
        
        const scopeRequirement = parseInt(scopeSection.classList[1].replace('requirement-', ''));
        
        if (scopeRequirement > 0) {
            const scopeFields = scopeSection.querySelectorAll('textarea');
            let hasAnyInput = false;
            
            scopeFields.forEach(field => {
                if (field.value.trim() !== '') {
                    hasAnyInput = true;
                }
            });
            
            if (!hasAnyInput) return;
        }
        
        if (!textarea.value.trim()) {
            const fieldName = textarea.name.split('.')[1];
            if (!unfinishedFields[scope]) {
                unfinishedFields[scope] = [];
            }
            unfinishedFields[scope].push(fieldName);
        }
    });
    
    return unfinishedFields;
};

// API calls
const checkInvestigation = async (investigationId, studyId) => {
    try {
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
        
        // Check if this is a new record
        const isNewRecord = data.studyTitle === 'New Study' && 
                          data.studyDescription === 'Please provide study description' &&
                          data.contactInstitution === 'Please provide contact institution';
        
        if (isNewRecord) {
            await showPopup(
                'No existing record found. A new form has been created for you to fill out.',
                ['Continue']
            );
        }
        
        currentInvestigationId = investigationId;
        currentStudyId = studyId;
        
        await initializeFormWithData(data);
        return data;
    } catch (error) {
        console.error('Error checking investigation:', error);
        showNotification('Error checking investigation: ' + error.message, 'error');
        throw error;
    }
};

const saveChecklist = async (formData) => {
    try {
        const response = await fetch(`${API_BASE_URL}/save_checklist`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                investigation_id: currentInvestigationId,
                study_id: currentStudyId,
                data: formData
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        showNotification('Checklist saved successfully', 'success');
        return data;
    } catch (error) {
        console.error('Error saving checklist:', error);
        showNotification('Error saving checklist: ' + error.message, 'error');
        throw error;
    }
};

// Event handlers
document.addEventListener('DOMContentLoaded', () => {
    // Check IDs button handler
    const checkIdsButton = document.getElementById('check-ids-button');
    if (checkIdsButton) {
        checkIdsButton.addEventListener('click', async () => {
            const investigationId = document.getElementById('investigation-id').value;
            const studyId = document.getElementById('study-id').value;
            
            if (!investigationId || !studyId) {
                showNotification('Please enter both Investigation ID and Study ID', 'error');
                return;
            }
            
            try {
                await checkInvestigation(investigationId, studyId);
            } catch (error) {
                console.error('Error in check IDs:', error);
            }
        });
    }
    
    // Save button handler
    const saveButton = document.getElementById('save-button');
    if (saveButton) {
        saveButton.addEventListener('click', async () => {
            const formData = {};
            const form = document.getElementById('miappe-form');
            
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
            
            // Collect form data
            form.querySelectorAll('textarea').forEach(textarea => {
                formData[textarea.name] = textarea.value;
            });
            
            try {
                await saveChecklist(formData);
            } catch (error) {
                console.error('Error saving form:', error);
            }
        });
    }
    
    // Reset bindings button handler
    const resetBindingsButton = document.getElementById('reset-bindings-button');
    if (resetBindingsButton) {
        resetBindingsButton.addEventListener('click', () => {
            resetAllBindings();
        });
    }
    
    // MongoDB field dropdown handlers
    document.querySelectorAll('.mongo-field-dropdown').forEach(dropdown => {
        dropdown.addEventListener('change', (event) => {
            const mongoField = event.target.value;
            const textarea = event.target.closest('.form-group').querySelector('textarea');
            const scope = textarea.name.split('.')[0];
            const field = textarea.name.split('.')[1];
            
            if (mongoField) {
                const targetMongoField = document.querySelector(`.mongo-field[data-field="${mongoField}"]`);
                if (targetMongoField) {
                    createBinding(targetMongoField, scope, field, dropdown);
                    textarea.value = mongoField;
                    textarea.dispatchEvent(new Event('input'));
                    saveBindings();
                }
            }
        });
    });
}); 