/**
 * Frontend utility functions for MIAPPE metadata checker.
 * This file contains helper functions for handling field name conversions and UI interactions.
 */

// Field name conversion utilities
const convertKebabToCamel = (str) => {
    return str.replace(/-([a-z])/g, (g) => g[1].toUpperCase());
};

const convertCamelToKebab = (str) => {
    return str.replace(/([a-z0-9])([A-Z])/g, '$1-$2').toLowerCase();
};

// UI utility functions
const showNotification = (message, type = 'success') => {
    const notification = document.getElementById('notification');
    
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
};

const showPopup = async (message, buttons = ['OK']) => {
    const popup = document.createElement('div');
    popup.className = 'custom-popup';
    
    const buttonHtml = buttons.map(btn => 
        `<button class="popup-${btn.toLowerCase().replace(/\s+/g, '-')}">${btn}</button>`
    ).join('');
    
    // Convert newlines to <br> tags and preserve whitespace
    const formattedMessage = message
        .split('\n')
        .map(line => line.trim())
        .join('<br>');
    
    popup.innerHTML = `
        <div class="popup-content">
            <p style="white-space: pre-line;">${formattedMessage}</p>
            <div class="popup-buttons">
                ${buttonHtml}
            </div>
        </div>
    `;
    
    document.body.appendChild(popup);
    
    // Handle button clicks
    return new Promise((resolve) => {
        buttons.forEach(btn => {
            const buttonClass = `popup-${btn.toLowerCase().replace(/\s+/g, '-')}`;
            popup.querySelector(`.${buttonClass}`).addEventListener('click', () => {
                document.body.removeChild(popup);
                resolve(btn);
            });
        });
    });
};

// Form utility functions
const adjustTextareaHeight = (textarea) => {
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
};

const initializeTextareas = () => {
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        // Adjust height on input, change, and focus
        textarea.addEventListener('input', () => adjustTextareaHeight(textarea));
        textarea.addEventListener('change', () => adjustTextareaHeight(textarea));
        textarea.addEventListener('focus', () => adjustTextareaHeight(textarea));
        
        // Initial adjustment
        adjustTextareaHeight(textarea);
    });
};

// MongoDB field binding utilities
const createBinding = (mongoField, scope, field, dropdown) => {
    console.log('Creating binding:', { mongoField, scope, field, dropdown });
    
    try {
        // Check if binding already exists
        const existingBinding = mongoField.querySelector(`.field-binding[data-field="${scope}.${field}"]`);
        if (existingBinding) {
            console.log('Binding already exists, removing it first');
            removeBinding(mongoField, existingBinding);
        }
        
        // Get or create bindings container
        let bindingsContainer = mongoField.querySelector('.field-bindings');
        if (!bindingsContainer) {
            bindingsContainer = document.createElement('div');
            bindingsContainer.className = 'field-bindings';
            mongoField.appendChild(bindingsContainer);
        }
        
        // Create binding element
        const binding = document.createElement('div');
        binding.className = 'field-binding';
        binding.setAttribute('data-field', `${scope}.${field}`);
        binding.setAttribute('data-scope', scope);
        binding.setAttribute('data-field-name', field);
        
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
            console.log('Remove button clicked for binding:', binding);
            removeBinding(mongoField, binding);
            
            // Reset the corresponding dropdown
            const dropdowns = document.querySelectorAll('.mongo-field-dropdown');
            dropdowns.forEach(d => {
                if (d.dataset.selectedScope === scope && d.dataset.selectedField === field) {
                    d.value = '';
                    delete d.dataset.selectedValue;
                    delete d.dataset.selectedScope;
                    delete d.dataset.selectedField;
                }
            });
            
            // Remove bound class from form group
            const formGroup = document.querySelector(`textarea[name="${scope}.${field}"]`)?.closest('.form-group');
            if (formGroup) {
                formGroup.classList.remove('bound');
            }
        };
        
        binding.appendChild(bindingText);
        binding.appendChild(removeBtn);
        bindingsContainer.appendChild(binding);
        
        // Add bound class to MongoDB field
        mongoField.classList.add('bound');
        
        // Save bindings to localStorage
        saveBindings();
        
        console.log('Binding created successfully');
    } catch (error) {
        console.error('Error in createBinding:', error);
        throw error;
    }
};

const removeBinding = (mongoField, bindingElement) => {
    console.log('Removing binding:', bindingElement);
    
    try {
        // Remove the binding element
        bindingElement.remove();
        
        // Remove bound class if no bindings remain
        const bindingsContainer = mongoField.querySelector('.field-bindings');
        if (!bindingsContainer || bindingsContainer.children.length === 0) {
            mongoField.classList.remove('bound');
        }
        
        // Save bindings to localStorage
        saveBindings();
        
        console.log('Binding removed successfully');
    } catch (error) {
        console.error('Error in removeBinding:', error);
        throw error;
    }
};

const saveBindings = () => {
    console.log('Saving bindings to localStorage');
    
    try {
        const bindings = [];
        document.querySelectorAll('.field-binding').forEach(binding => {
            bindings.push({
                field: binding.getAttribute('data-field'),
                scope: binding.getAttribute('data-scope'),
                fieldName: binding.getAttribute('data-field-name')
            });
        });
        
        localStorage.setItem('miappeBindings', JSON.stringify(bindings));
        console.log('Bindings saved successfully:', bindings);
    } catch (error) {
        console.error('Error saving bindings:', error);
        throw error;
    }
};

const restoreBindings = () => {
    console.log('Restoring bindings from localStorage');
    
    try {
        const savedBindings = localStorage.getItem('miappeBindings');
        if (!savedBindings) {
            console.log('No saved bindings found');
            return;
        }
        
        const bindings = JSON.parse(savedBindings);
        console.log('Restoring bindings:', bindings);
        
        bindings.forEach(binding => {
            const mongoField = document.querySelector(`.mongo-field[data-field="${binding.field}"]`);
            if (mongoField) {
                createBinding(mongoField, binding.scope, binding.fieldName);
                
                // Update dropdown
                const dropdowns = document.querySelectorAll('.mongo-field-dropdown');
                dropdowns.forEach(d => {
                    if (d.dataset.selectedScope === binding.scope && d.dataset.selectedField === binding.fieldName) {
                        d.value = binding.field;
                        d.dataset.selectedValue = binding.field;
                        d.dataset.selectedScope = binding.scope;
                        d.dataset.selectedField = binding.fieldName;
                    }
                });
            }
        });
        
        console.log('Bindings restored successfully');
    } catch (error) {
        console.error('Error restoring bindings:', error);
        throw error;
    }
};

const resetAllBindings = () => {
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
}; 