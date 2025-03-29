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
    
    popup.innerHTML = `
        <div class="popup-content">
            <p>${message}</p>
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
};

const removeBinding = (mongoField, bindingElement) => {
    bindingElement.remove();
    
    // If no more bindings, remove bound class
    const bindingsContainer = mongoField.querySelector('.field-bindings');
    if (bindingsContainer.children.length === 0) {
        mongoField.classList.remove('bound');
    }
};

// Local storage utilities
const saveBindings = () => {
    const bindings = {};
    document.querySelectorAll('.field-binding').forEach(binding => {
        const field = binding.getAttribute('data-field');
        const mongoField = binding.closest('.mongo-field').getAttribute('data-field');
        bindings[field] = mongoField;
    });
    localStorage.setItem('miappeBindings', JSON.stringify(bindings));
};

const restoreBindings = () => {
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