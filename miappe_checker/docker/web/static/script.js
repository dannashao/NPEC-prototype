document.addEventListener('DOMContentLoaded', function() {
    const notification = document.getElementById('notification');
    
    function showNotification(message, type = 'success') {
        // Clear any existing notifications
        notification.style.display = 'none';
        notification.textContent = '';
        
        // Set new notification
        notification.textContent = message;
        notification.className = `notification ${type}`;
        notification.style.display = 'block';
        
        // Hide after 5 seconds
        setTimeout(() => {
            notification.style.display = 'none';
        }, 5000);
    }

    // Function to create a binding
    function createBinding(mongoField, scope, field, dropdown) {
        mongoField.classList.add('bound');
        
        const binding = document.createElement('div');
        binding.className = 'field-binding';
        binding.setAttribute('data-field', `${scope}.${field}`);
        binding.innerHTML = `
            ${scope}.${field}
            <button class="unbind-button" title="Remove binding">×</button>
        `;
        
        // Add click handler for unbind button
        const unbindButton = binding.querySelector('.unbind-button');
        unbindButton.addEventListener('click', () => {
            removeBinding(mongoField, binding);
            // Reset the corresponding dropdown
            const fieldName = binding.getAttribute('data-field');
            const [scope, field] = fieldName.split('.');
            const dropdown = document.querySelector(`textarea[name="${scope}.${field}"]`)
                .closest('.form-group')
                .querySelector('.mongo-field-dropdown');
            dropdown.value = '';
        });
        
        // Add to bindings container
        const bindingsContainer = mongoField.querySelector('.field-bindings');
        bindingsContainer.appendChild(binding);
    }

    // Function to remove binding
    function removeBinding(mongoField, bindingElement) {
        bindingElement.remove();
        
        // If no more bindings, remove bound class
        const bindingsContainer = mongoField.querySelector('.field-bindings');
        if (bindingsContainer.children.length === 0) {
            mongoField.classList.remove('bound');
        }
    }

    // Function to restore bindings from localStorage
    function restoreBindings() {
        const bindings = JSON.parse(localStorage.getItem('miappeBindings') || '{}');
        
        Object.entries(bindings).forEach(([field, mongoField]) => {
            const [scope, fieldName] = field.split('.');
            const textarea = document.querySelector(`textarea[name="${field}"]`);
            const dropdown = textarea.closest('.form-group').querySelector('.mongo-field-dropdown');
            const targetMongoField = document.querySelector(`.mongo-field[data-field="${mongoField}"]`);
            
            if (textarea && dropdown && targetMongoField) {
                // Set dropdown value
                dropdown.value = mongoField;
                
                // Set textarea value
                textarea.value = mongoField;
                textarea.dispatchEvent(new Event('input'));
                
                // Create binding
                createBinding(targetMongoField, scope, fieldName, dropdown);
            }
        });
    }

    // Function to save bindings to localStorage
    function saveBindings() {
        const bindings = {};
        document.querySelectorAll('.field-binding').forEach(binding => {
            const field = binding.getAttribute('data-field');
            const mongoField = binding.closest('.mongo-field').getAttribute('data-field');
            bindings[field] = mongoField;
        });
        localStorage.setItem('miappeBindings', JSON.stringify(bindings));
    }

    // Function to reset all bindings
    function resetAllBindings() {
        // Clear all bindings from MongoDB fields
        document.querySelectorAll('.field-binding').forEach(binding => {
            const mongoField = binding.closest('.mongo-field');
            removeBinding(mongoField, binding);
        });

        // Reset all dropdowns
        document.querySelectorAll('.mongo-field-dropdown').forEach(dropdown => {
            dropdown.value = '';
        });

        // Reset all textareas
        document.querySelectorAll('textarea').forEach(textarea => {
            textarea.value = '';
            textarea.dispatchEvent(new Event('input'));
        });

        // Clear localStorage
        localStorage.removeItem('miappeBindings');

        // Show success notification
        showNotification('All bindings have been reset successfully', 'success');
    }

    // Add reset button handler
    document.getElementById('reset-all').addEventListener('click', function() {
        if (confirm('Are you sure you want to reset all bindings? This action cannot be undone.')) {
            resetAllBindings();
        }
    });

    // Restore bindings on page load
    restoreBindings();

    // Auto-expand textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        function adjustHeight() {
            // Store the current scroll position
            const scrollPos = window.pageYOffset;
            
            // Create a temporary div to measure placeholder height
            const tempDiv = document.createElement('div');
            tempDiv.style.cssText = window.getComputedStyle(textarea).cssText;
            tempDiv.style.height = 'auto';
            tempDiv.style.position = 'absolute';
            tempDiv.style.visibility = 'hidden';
            tempDiv.style.whiteSpace = 'pre-wrap';
            tempDiv.style.wordWrap = 'break-word';
            tempDiv.style.width = textarea.offsetWidth + 'px';
            tempDiv.style.padding = window.getComputedStyle(textarea).padding;
            tempDiv.style.boxSizing = window.getComputedStyle(textarea).boxSizing;
            tempDiv.style.fontSize = window.getComputedStyle(textarea).fontSize;
            tempDiv.style.lineHeight = window.getComputedStyle(textarea).lineHeight;
            tempDiv.style.fontFamily = window.getComputedStyle(textarea).fontFamily;
            
            // Set the content to either the placeholder or the actual value
            const content = textarea.value || textarea.placeholder;
            tempDiv.textContent = content;
            
            // Add the temporary div to the document
            document.body.appendChild(tempDiv);
            
            // Get the height
            const height = Math.max(tempDiv.offsetHeight, 38); // Minimum height of 38px
            
            // Remove the temporary div
            document.body.removeChild(tempDiv);
            
            // Set the textarea height
            textarea.style.height = height + 'px';
            
            // Restore scroll position
            window.scrollTo(0, scrollPos);
        }
        
        // Adjust height on input, change, and focus
        textarea.addEventListener('input', adjustHeight);
        textarea.addEventListener('change', adjustHeight);
        textarea.addEventListener('focus', adjustHeight);
        
        // Initial adjustment
        adjustHeight();
    });

    function getUnfinishedMandatoryFields() {
        const unfinishedFields = {};
        const formGroups = document.querySelectorAll('.form-group');
        
        formGroups.forEach(group => {
            const label = group.querySelector('label');
            const textarea = group.querySelector('textarea');
            const isMandatory = label.querySelector('.mandatory') !== null;
            const scope = textarea.name.split('.')[0]; // Get scope from textarea name
            
            // Skip if field is not mandatory
            if (!isMandatory) return;
            
            // For non-mandatory scopes (requirement > 0), check if any field in the scope has input
            const scopeSection = group.closest('.form-section');
            const scopeRequirement = parseInt(scopeSection.classList[1].replace('requirement-', ''));
            
            if (scopeRequirement > 0) {
                const scopeFields = scopeSection.querySelectorAll('textarea');
                let hasAnyInput = false;
                
                scopeFields.forEach(field => {
                    if (field.value.trim() !== '') {
                        hasAnyInput = true;
                    }
                });
                
                // If no fields in scope have input, skip mandatory check
                if (!hasAnyInput) return;
            }
            
            // Check if this field is empty
            if (!textarea.value.trim()) {
                const fieldName = textarea.name.split('.')[1];
                if (!unfinishedFields[scope]) {
                    unfinishedFields[scope] = [];
                }
                unfinishedFields[scope].push(fieldName);
            }
        });
        
        return unfinishedFields;
    }

    document.getElementById('miappe-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        console.log('Form submission started');
        
        const unfinishedFields = getUnfinishedMandatoryFields();
        console.log('Unfinished fields:', unfinishedFields);
        
        // If there are unfinished fields, show popup
        if (Object.keys(unfinishedFields).length > 0) {
            console.log('Showing popup for unfinished fields');
            let message = 'The following mandatory fields are not filled:\n\n';
            
            // Group fields by scope
            Object.entries(unfinishedFields).forEach(([scope, fields]) => {
                // Find the scope section by looking for the h2 with matching text
                const scopeSection = Array.from(document.querySelectorAll('.form-section h2'))
                    .find(h2 => h2.textContent.trim() === scope)
                    ?.closest('.form-section');
                
                if (!scopeSection) {
                    console.error('Could not find section for scope:', scope);
                    return;
                }
                
                const isMandatory = scopeSection.classList.contains('requirement-0');
                const scopeName = scopeSection.querySelector('h2').textContent.trim();
                
                message += `${scopeName}${isMandatory ? ' *' : ''}:\n`;
                fields.forEach(field => {
                    message += `    - ${field}\n`;
                });
                message += '\n';
            });
            
            message += 'Do you want to save anyway?';
            console.log('Popup message:', message);
            
            // Create a custom popup with wider width
            const popup = document.createElement('div');
            popup.className = 'custom-popup';
            popup.innerHTML = `
                <div class="popup-content">
                    <pre>${message}</pre>
                    <div class="popup-buttons">
                        <button class="popup-cancel">Cancel</button>
                        <button class="popup-confirm">Save Anyway</button>
                    </div>
                </div>
            `;
            
            document.body.appendChild(popup);
            console.log('Popup added to DOM');
            
            // Handle button clicks
            try {
                const shouldProceed = await new Promise((resolve) => {
                    console.log('Setting up popup button handlers');
                    popup.querySelector('.popup-cancel').addEventListener('click', () => {
                        console.log('Cancel clicked');
                        document.body.removeChild(popup);
                        resolve(false);
                    });
                    
                    popup.querySelector('.popup-confirm').addEventListener('click', () => {
                        console.log('Save Anyway clicked');
                        document.body.removeChild(popup);
                        resolve(true);
                    });
                });
                console.log('Popup result:', shouldProceed);
                
                if (!shouldProceed) {
                    console.log('User cancelled, stopping submission');
                    return;
                }
            } catch (error) {
                console.error('Error in popup handling:', error);
                return;
            }
        } else {
            console.log('No unfinished fields, proceeding with save');
        }
        
        // Continue with form submission (either no unfinished fields or user confirmed)
        const formData = {};
        const inputs = this.querySelectorAll('textarea');
        console.log('Collecting form data');
        
        // Collect form data
        inputs.forEach(input => {
            const [scope, field] = input.name.split('.');
            if (!formData[scope]) formData[scope] = {};
            
            const value = input.value.trim();
            if (value) {
                formData[scope][field] = value;
            }
        });
        
        console.log('Form data collected:', formData);
        
        // Submit form data
        console.log('Sending data to server');
        fetch('/miappe/save_checklist', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => {
            console.log('Server response received:', response);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Server data:', data);
            if (data.error) {
                showNotification(data.error, 'error');
            } else {
                // Show appropriate notification based on completion status
                if (data.is_complete) {
                    showNotification('Checklist saved successfully! All required fields are complete.', 'success');
                } else {
                    let message = 'Checklist saved successfully! Some fields are still incomplete:\n\n';
                    if (data.incomplete_scopes && Array.isArray(data.incomplete_scopes)) {
                        data.incomplete_scopes.forEach(scope => {
                            message += `- ${scope}\n`;
                        });
                    }
                    showNotification(message, 'warning');
                }
            }
        })
        .catch(error => {
            console.error('Error in form submission:', error);
            showNotification('Error saving checklist: ' + error.message, 'error');
        });
    });
    
    // Handle MongoDB field selection and unbinding
    const dropdowns = document.querySelectorAll('.mongo-field-dropdown');
    const mongoFields = document.querySelectorAll('.mongo-field');
    
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('change', function() {
            const textarea = this.closest('.form-group').querySelector('textarea');
            const [scope, field] = textarea.name.split('.');
            
            // Remove any existing binding for this field
            const existingBinding = document.querySelector(`.field-binding[data-field="${scope}.${field}"]`);
            if (existingBinding) {
                const mongoField = existingBinding.closest('.mongo-field');
                removeBinding(mongoField, existingBinding);
            }
            
            if (this.value) {
                // Update textarea
                textarea.value = this.value;
                textarea.dispatchEvent(new Event('input'));
                
                // Update MongoDB field display
                const mongoField = document.querySelector(`.mongo-field[data-field="${this.value}"]`);
                if (mongoField) {
                    createBinding(mongoField, scope, field, this);
                    // Save bindings after creating new binding
                    saveBindings();
                }
            }
        });
    });
}); 