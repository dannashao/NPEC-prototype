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
            
            // Skip if label or textarea is missing
            if (!label || !textarea) {
                console.warn('Missing label or textarea in form group:', group);
                return;
            }
            
            const isMandatory = label.querySelector('.mandatory') !== null;
            const scope = textarea.name.split('.')[0]; // Get scope from textarea name
            
            // Skip if field is not mandatory
            if (!isMandatory) return;
            
            // For non-mandatory scopes (requirement > 0), check if any field in the scope has input
            const scopeSection = group.closest('.form-section');
            if (!scopeSection) {
                console.warn('Could not find form section for group:', group);
                return;
            }
            
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
        
        try {
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
            } else {
                console.log('No unfinished fields, proceeding with save');
            }
            
            // Continue with form submission (either no unfinished fields or user confirmed)
            const formData = {};
            const inputs = this.querySelectorAll('textarea');
            console.log('Collecting form data');
            
            // Add investigation and study IDs
            if (!window.currentInvestigationId || !window.currentStudyId) {
                throw new Error('Missing investigation or study ID');
            }
            
            formData.investigation_id = window.currentInvestigationId;
            formData.study_id = window.currentStudyId;
            console.log('Added IDs:', { investigation_id: formData.investigation_id, study_id: formData.study_id });
            
            // Collect form data
            inputs.forEach(input => {
                const [scope, field] = input.name.split('.');
                if (!formData[scope]) formData[scope] = {};
                
                const value = input.value.trim();
                if (value) {
                    // Handle special cases based on SQL schema
                    switch (scope) {
                        case 'INVESTIGATION':
                            // Map frontend field names to database field names
                            const dbField = {
                                'investigationId': 'INVESTIGATION_ID',
                                'investigationTitle': 'TITLE',
                                'investigationDescription': 'DESCRIPTION',
                                'submissionDate': 'SUBMISSION_DATE',
                                'publicReleaseDate': 'PUBLIC_RELEASE_DATE',
                                'license': 'LICENSE',
                                'miappeVersion': 'MIAPPE_VERSION',
                                'associatedPublication': 'ASSOCIATED_PUBLICATION'
                            }[field] || field;
                            
                            if (dbField === 'ASSOCIATED_PUBLICATION') {
                                formData[scope][dbField] = value.split(',').map(pub => pub.trim());
                            } else {
                                formData[scope][dbField] = value;
                            }
                            break;
                            
                        case 'STUDY':
                            // Map frontend field names to database field names
                            const studyDbField = {
                                'studyId': 'STUDY_ID',
                                'studyTitle': 'STUDY_TITLE',
                                'studyDescription': 'STUDY_DESCRIPTION',
                                'studyStartDate': 'STUDY_START_DATE',
                                'studyEndDate': 'STUDY_END_DATE',
                                'contactInstitution': 'CONTACT_INSTITUTION',
                                'locationCountry': 'LOCATION_COUNTRY',
                                'siteName': 'SITE_NAME',
                                'locationLatitude': 'LOCATION_LATITUDE',
                                'locationLongitude': 'LOCATION_LONGITUDE',
                                'locationAltitude': 'LOCATION_ALTITUDE',
                                'experimentalDesignDescription': 'EXPERIMENTAL_DESIGN_DESCRIPTION',
                                'experimentalDesignType': 'EXPERIMENTAL_DESIGN_TYPE',
                                'observationUnitLevelHierarchy': 'OBSERVATION_UNIT_LEVEL_HIERARCHY',
                                'observationUnitDescription': 'OBSERVATION_UNIT_DESCRIPTION',
                                'growthFacilityDescription': 'GROWTH_FACILITY_DESCRIPTION',
                                'growthFacilityType': 'GROWTH_FACILITY_TYPE',
                                'culturalPractices': 'CULTURAL_PRACTICES',
                                'experimentalDesignMap': 'EXPERIMENTAL_DESIGN_MAP'
                            }[field] || field;
                            
                            if (studyDbField === 'CULTURAL_PRACTICES') {
                                formData[scope][studyDbField] = value;
                            } else if (studyDbField === 'EXPERIMENTAL_DESIGN_MAP') {
                                formData[scope][studyDbField] = value.split(',').map(map => map.trim());
                            } else {
                                formData[scope][studyDbField] = value;
                            }
                            break;
                            
                        case 'PERSON':
                            // Map frontend field names to database field names
                            const personDbField = {
                                'name': 'NAME',
                                'role': 'ROLE',
                                'affiliation': 'AFFILIATION'
                            }[field] || field;
                            
                            // Initialize the PERSON array if it doesn't exist
                            if (!formData[scope]) {
                                formData[scope] = [];
                            }
                            
                            // If this is the first field being set, create a new person object
                            if (formData[scope].length === 0) {
                                formData[scope].push({
                                    NAME: '',
                                    ROLE: [],
                                    AFFILIATION: []
                                });
                            }
                            
                            // Update the last person object with the new value
                            const lastPerson = formData[scope][formData[scope].length - 1];
                            if (personDbField === 'ROLE' || personDbField === 'AFFILIATION') {
                                lastPerson[personDbField] = value.split(',').map(item => item.trim());
                            } else {
                                lastPerson[personDbField] = value;
                            }
                            break;
                            
                        case 'DATA_FILE':
                            // Map frontend field names to database field names
                            const dataFileDbField = {
                                'fileLink': 'FILE_LINK',
                                'description': 'DESCRIPTION',
                                'version': 'VERSION'
                            }[field] || field;
                            
                            // Initialize the DATA_FILE array if it doesn't exist
                            if (!formData[scope]) {
                                formData[scope] = [];
                            }
                            
                            // If this is the first field being set, create a new data file object
                            if (formData[scope].length === 0) {
                                formData[scope].push({
                                    FILE_LINK: '',
                                    DESCRIPTION: '',
                                    VERSION: ''
                                });
                            }
                            
                            // Update the last data file object with the new value
                            const lastDataFile = formData[scope][formData[scope].length - 1];
                            lastDataFile[dataFileDbField] = value;
                            break;
                            
                        case 'BIOLOGICAL_MATERIAL':
                            // Map frontend field names to database field names
                            const biologicalMaterialDbField = {
                                'biologicalMaterialId': 'BIOLOGICAL_MATERIAL_ID',
                                'externalId': 'EXTERNAL_ID',
                                'organism': 'ORGANISM',
                                'genus': 'GENUS',
                                'species': 'SPECIES',
                                'infraspecificName': 'INFRASPECIFIC_NAME',
                                'latitude': 'LATITUDE',
                                'longitude': 'LONGITUDE',
                                'altitude': 'ALTITUDE',
                                'coordinateUncertainty': 'COORDINATE_UNCERTAINTY',
                                'preprocessing': 'PREPROCESSING',
                                'sourceId': 'SOURCE_ID',
                                'sourceDoi': 'SOURCE_DOI',
                                'sourceAccessionNumber': 'SOURCE_ACCESSION_NUMBER',
                                'sourceAccessionName': 'SOURCE_ACCESSION_NAME',
                                'sourceInstitutionCode': 'SOURCE_INSTITUTION_CODE',
                                'sourceInstitutionName': 'SOURCE_INSTITUTION_NAME',
                                'sourceOtherIds': 'SOURCE_OTHER_IDS',
                                'sourceLatitude': 'SOURCE_LATITUDE',
                                'sourceLongitude': 'SOURCE_LONGITUDE',
                                'sourceAltitude': 'SOURCE_ALTITUDE',
                                'sourceCoordinateUncertainty': 'SOURCE_COORDINATE_UNCERTAINTY',
                                'sourceDescription': 'SOURCE_DESCRIPTION'
                            }[field] || field;
                            
                            // Initialize the BIOLOGICAL_MATERIAL array if it doesn't exist
                            if (!formData[scope]) {
                                formData[scope] = [];
                            }
                            
                            // If this is the first field being set, create a new biological material object
                            if (formData[scope].length === 0) {
                                formData[scope].push({
                                    BIOLOGICAL_MATERIAL_ID: '',
                                    EXTERNAL_ID: '',
                                    ORGANISM: '',
                                    GENUS: '',
                                    SPECIES: '',
                                    INFRASPECIFIC_NAME: '',
                                    LATITUDE: '',
                                    LONGITUDE: '',
                                    ALTITUDE: '',
                                    COORDINATE_UNCERTAINTY: '',
                                    PREPROCESSING: '',
                                    SOURCE_ID: '',
                                    SOURCE_DOI: '',
                                    SOURCE_ACCESSION_NUMBER: '',
                                    SOURCE_ACCESSION_NAME: '',
                                    SOURCE_INSTITUTION_CODE: '',
                                    SOURCE_INSTITUTION_NAME: '',
                                    SOURCE_OTHER_IDS: '',
                                    SOURCE_LATITUDE: '',
                                    SOURCE_LONGITUDE: '',
                                    SOURCE_ALTITUDE: '',
                                    SOURCE_COORDINATE_UNCERTAINTY: '',
                                    SOURCE_DESCRIPTION: ''
                                });
                            }
                            
                            // Update the last biological material object with the new value
                            const lastBiologicalMaterial = formData[scope][formData[scope].length - 1];
                            lastBiologicalMaterial[biologicalMaterialDbField] = value;
                            break;
                            
                        case 'ENVIRONMENT':
                            // Map frontend field names to database field names
                            const environmentDbField = {
                                'parameter': 'PARAMETER',
                                'parameterValue': 'PARAMETER_VALUE'
                            }[field] || field;
                            
                            // Initialize the ENVIRONMENT array if it doesn't exist
                            if (!formData[scope]) {
                                formData[scope] = [];
                            }
                            
                            // If this is the first field being set, create a new environment object
                            if (formData[scope].length === 0) {
                                formData[scope].push({
                                    PARAMETER: '',
                                    PARAMETER_VALUE: ''
                                });
                            }
                            
                            // Update the last environment object with the new value
                            const lastEnvironment = formData[scope][formData[scope].length - 1];
                            lastEnvironment[environmentDbField] = value;
                            break;
                            
                        case 'EXPERIMENTAL_FACTOR':
                            // Map frontend field names to database field names
                            const experimentalFactorDbField = {
                                'factorType': 'FACTOR_TYPE',
                                'factorDescription': 'FACTOR_DESCRIPTION',
                                'factorValues': 'FACTOR_VALUES'
                            }[field] || field;
                            
                            // Initialize the EXPERIMENTAL_FACTOR array if it doesn't exist
                            if (!formData[scope]) {
                                formData[scope] = [];
                            }
                            
                            // If this is the first field being set, create a new experimental factor object
                            if (formData[scope].length === 0) {
                                formData[scope].push({
                                    FACTOR_TYPE: '',
                                    FACTOR_DESCRIPTION: '',
                                    FACTOR_VALUES: []
                                });
                            }
                            
                            // Update the last experimental factor object with the new value
                            const lastExperimentalFactor = formData[scope][formData[scope].length - 1];
                            if (experimentalFactorDbField === 'FACTOR_VALUES') {
                                lastExperimentalFactor[experimentalFactorDbField] = value.split(',').map(v => v.trim());
                            } else {
                                lastExperimentalFactor[experimentalFactorDbField] = value;
                            }
                            break;
                            
                        case 'EVENT':
                            // Map frontend field names to database field names
                            const eventDbField = {
                                'eventType': 'EVENT_TYPE',
                                'accessionNumber': 'ACCESSION_NUMBER',
                                'description': 'DESCRIPTION',
                                'eventDate': 'EVENT_DATE'
                            }[field] || field;
                            
                            // Initialize the EVENT array if it doesn't exist
                            if (!formData[scope]) {
                                formData[scope] = [];
                            }
                            
                            // If this is the first field being set, create a new event object
                            if (formData[scope].length === 0) {
                                formData[scope].push({
                                    EVENT_TYPE: '',
                                    ACCESSION_NUMBER: '',
                                    DESCRIPTION: '',
                                    EVENT_DATE: []
                                });
                            }
                            
                            // Update the last event object with the new value
                            const lastEvent = formData[scope][formData[scope].length - 1];
                            if (eventDbField === 'EVENT_DATE') {
                                lastEvent[eventDbField] = value.split(',').map(date => date.trim());
                            } else {
                                lastEvent[eventDbField] = value;
                            }
                            break;
                            
                        case 'OBSERVATION_UNIT':
                            // Map frontend field names to database field names
                            const observationUnitDbField = {
                                'observationUnitId': 'OBSERVATION_UNIT_ID',
                                'observationUnitType': 'OBSERVATION_UNIT_TYPE',
                                'externalId': 'EXTERNAL_ID',
                                'spatialDistribution': 'SPATIAL_DISTRIBUTION',
                                'factorValues': 'FACTOR_VALUES'
                            }[field] || field;
                            
                            // Initialize the OBSERVATION_UNIT array if it doesn't exist
                            if (!formData[scope]) {
                                formData[scope] = [];
                            }
                            
                            // If this is the first field being set, create a new observation unit object
                            if (formData[scope].length === 0) {
                                formData[scope].push({
                                    OBSERVATION_UNIT_ID: '',
                                    OBSERVATION_UNIT_TYPE: '',
                                    EXTERNAL_ID: '',
                                    SPATIAL_DISTRIBUTION: '',
                                    FACTOR_VALUES: []
                                });
                            }
                            
                            // Update the last observation unit object with the new value
                            const lastObservationUnit = formData[scope][formData[scope].length - 1];
                            if (Array.isArray(value)) {
                                lastObservationUnit[observationUnitDbField] = value;
                            } else {
                                lastObservationUnit[observationUnitDbField] = value;
                            }
                            break;
                            
                        case 'SAMPLE':
                            // Map frontend field names to database field names
                            const sampleDbField = {
                                'sampleId': 'SAMPLE_ID',
                                'developmentStage': 'DEVELOPMENT_STAGE',
                                'anatomicalEntity': 'ANATOMICAL_ENTITY',
                                'description': 'DESCRIPTION',
                                'collectionDate': 'COLLECTION_DATE',
                                'externalId': 'EXTERNAL_ID'
                            }[field] || field;
                            
                            // Initialize the SAMPLE array if it doesn't exist
                            if (!formData[scope]) {
                                formData[scope] = [];
                            }
                            
                            // If this is the first field being set, create a new sample object
                            if (formData[scope].length === 0) {
                                formData[scope].push({
                                    SAMPLE_ID: '',
                                    DEVELOPMENT_STAGE: '',
                                    ANATOMICAL_ENTITY: '',
                                    DESCRIPTION: '',
                                    COLLECTION_DATE: '',
                                    EXTERNAL_ID: []
                                });
                            }
                            
                            // Update the last sample object with the new value
                            const lastSample = formData[scope][formData[scope].length - 1];
                            if (Array.isArray(value)) {
                                lastSample[sampleDbField] = value;
                            } else {
                                lastSample[sampleDbField] = value;
                            }
                            break;
                            
                        case 'OBSERVED_VARIABLE':
                            // Map frontend field names to database field names
                            const observedVariableDbField = {
                                'variableId': 'VARIABLE_ID',
                                'variableName': 'VARIABLE_NAME',
                                'accessionNumber': 'ACCESSION_NUMBER',
                                'traitName': 'TRAIT_NAME',
                                'traitEntity': 'TRAIT_ENTITY',
                                'traitEntityAccessionNumber': 'TRAIT_ENTITY_ACCESSION_NUMBER',
                                'traitCharacteristic': 'TRAIT_CHARACTERISTIC',
                                'traitCharacteristicAccessionNumber': 'TRAIT_CHARACTERISTIC_ACCESSION_NUMBER',
                                'traitAccessionNumber': 'TRAIT_ACCESSION_NUMBER',
                                'methodName': 'METHOD_NAME',
                                'methodAccessionNumber': 'METHOD_ACCESSION_NUMBER',
                                'methodDescription': 'METHOD_DESCRIPTION',
                                'methodReference': 'METHOD_REFERENCE',
                                'scaleName': 'SCALE_NAME',
                                'scaleAccessionNumber': 'SCALE_ACCESSION_NUMBER',
                                'timeScale': 'TIME_SCALE'
                            }[field] || field;
                            
                            // Initialize the OBSERVED_VARIABLE array if it doesn't exist
                            if (!formData[scope]) {
                                formData[scope] = [];
                            }
                            
                            // If this is the first field being set, create a new observed variable object
                            if (formData[scope].length === 0) {
                                formData[scope].push({
                                    VARIABLE_ID: '',
                                    VARIABLE_NAME: '',
                                    ACCESSION_NUMBER: '',
                                    TRAIT_NAME: '',
                                    TRAIT_ENTITY: '',
                                    TRAIT_ENTITY_ACCESSION_NUMBER: '',
                                    TRAIT_CHARACTERISTIC: '',
                                    TRAIT_CHARACTERISTIC_ACCESSION_NUMBER: '',
                                    TRAIT_ACCESSION_NUMBER: '',
                                    METHOD_NAME: '',
                                    METHOD_ACCESSION_NUMBER: '',
                                    METHOD_DESCRIPTION: '',
                                    METHOD_REFERENCE: '',
                                    SCALE_NAME: '',
                                    SCALE_ACCESSION_NUMBER: '',
                                    TIME_SCALE: ''
                                });
                            }
                            
                            // Update the last observed variable object with the new value
                            const lastObservedVariable = formData[scope][formData[scope].length - 1];
                            lastObservedVariable[observedVariableDbField] = value;
                            break;
                            
                        default:
                            formData[scope][field] = value;
                    }
                }
            });
            
            // Add form status
            formData.status = Object.keys(unfinishedFields).length > 0 ? 'incomplete' : 'complete';
            
            console.log('Form data collected:', formData);
            
            // Submit form data
            console.log('Sending data to server');
            const response = await fetch('/miappe/save_checklist', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            console.log('Server response received:', response);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            console.log('Server data:', data);
            
            if (!data.success) {
                showNotification(data.message, 'error');
            } else {
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
        } catch (error) {
            console.error('Error in form submission:', error);
            showNotification('Error saving checklist: ' + error.message, 'error');
        }
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

    // Stage 1: Investigation and Study ID handling
    const stage1 = document.getElementById('stage1');
    const stage2 = document.getElementById('stage2');
    const checkIdsButton = document.getElementById('check-ids');
    const investigationIdInput = document.getElementById('investigation_id');
    const studyIdInput = document.getElementById('study_id');

    checkIdsButton.addEventListener('click', async function() {
        console.log('Check IDs button clicked');
        const investigationId = investigationIdInput.value.trim();
        const studyId = studyIdInput.value.trim();
        console.log('Input values:', { investigationId, studyId });

        if (!investigationId || !studyId) {
            console.log('Missing investigation_id or study_id');
            showNotification('Please enter both Investigation ID and Study ID', 'error');
            return;
        }

        try {
            console.log('Sending request to /miappe/api/check_investigation');
            const response = await fetch('/miappe/api/check_investigation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    investigation_id: investigationId,
                    study_id: studyId
                })
            });
            console.log('Response received:', response);

            const data = await response.json();
            console.log('Response data:', data);

            if (!data.success) {
                console.log('Request failed:', data.message);
                showNotification(data.message, 'error');
                return;
            }

            console.log('Request successful, proceeding with form initialization');
            // Store the IDs for later use
            window.currentInvestigationId = investigationId;
            window.currentStudyId = studyId;
            
            // Check if this is a new record
            const isNewRecord = data.studies && data.studies[0] && 
                              data.studies[0].study_title === `Study ${studyId}` &&
                              data.studies[0].study_description === "" &&
                              data.studies[0].contact_institution === "Not specified";
            
            if (isNewRecord) {
                // Create a custom popup for new record
                const popup = document.createElement('div');
                popup.className = 'custom-popup';
                popup.innerHTML = `
                    <div class="popup-content">
                        <p>No existing record found for Investigation ID ${investigationId} and Study ID ${studyId}.</p>
                        <p>A new form has been created for you to fill out.</p>
                        <div class="popup-buttons">
                            <button class="popup-confirm">Continue</button>
                        </div>
                    </div>
                `;
                
                document.body.appendChild(popup);
                console.log('New record popup added to DOM');
                
                // Handle button click
                await new Promise((resolve) => {
                    popup.querySelector('.popup-confirm').addEventListener('click', () => {
                        console.log('Continue clicked');
                        document.body.removeChild(popup);
                        resolve();
                    });
                });
            }
            
            // Show success message
            showNotification('IDs verified successfully', 'success');
            
            // Hide stage 1 and show stage 2
            console.log('Switching to stage 2');
            stage1.style.display = 'none';
            stage2.style.display = 'block';
            
            // Initialize the form with the investigation data
            console.log('Initializing form with data');
            initializeFormWithData(data);
        } catch (error) {
            console.error('Error in check IDs:', error);
            showNotification('Error checking IDs: ' + error.message, 'error');
        }
    });
});

function initializeFormWithData(data) {
    console.log('Starting form initialization with data:', JSON.stringify(data, null, 2));
    
    // Get the stage2 container
    const stage2 = document.getElementById('stage2');
    if (!stage2) {
        console.error('Stage 2 container not found');
        return;
    }
    console.log('Stage 2 container found:', stage2);
    
    // Initialize investigation data
    if (data.investigation) {
        console.log('Initializing investigation data:', JSON.stringify(data.investigation, null, 2));
        const investigation = data.investigation;
        
        // Map database fields to form fields
        const fieldMapping = {
            'investigation_id': 'investigationId',
            'title': 'investigationTitle',
            'description': 'investigationDescription',
            'submission_date': 'submissionDate',
            'public_release_date': 'publicReleaseDate',
            'license': 'license',
            'miappe_version': 'miappeVersion',
            'associated_publication': 'associatedPublication'
        };
        
        Object.entries(fieldMapping).forEach(([dbField, formField]) => {
            const element = stage2.querySelector(`textarea[name="INVESTIGATION.${formField}"]`);
            if (element) {
                const value = dbField === 'associated_publication' 
                    ? (investigation[dbField] ? investigation[dbField].join(', ') : '')
                    : investigation[dbField] || '';
                element.value = value;
                console.log(`Found and set INVESTIGATION.${formField} to:`, value);
                // Trigger input event to update textarea height
                element.dispatchEvent(new Event('input'));
            } else {
                console.warn(`Element not found: INVESTIGATION.${formField}`);
                // Log the HTML structure around where the element should be
                const section = stage2.querySelector('.form-section');
                if (section) {
                    console.log('Form section HTML:', section.innerHTML);
                }
            }
        });
    } else {
        console.log('No investigation data available');
    }

    // Initialize study data
    if (data.studies && data.studies.length > 0) {
        console.log('Initializing study data:', JSON.stringify(data.studies[0], null, 2));
        const study = data.studies[0];
        
        // Map database fields to form fields
        const fieldMapping = {
            'study_id': 'studyId',
            'study_title': 'studyTitle',
            'study_description': 'studyDescription',
            'study_start_date': 'studyStartDate',
            'study_end_date': 'studyEndDate',
            'contact_institution': 'contactInstitution',
            'location_country': 'locationCountry',
            'site_name': 'siteName',
            'location_latitude': 'locationLatitude',
            'location_longitude': 'locationLongitude',
            'location_altitude': 'locationAltitude',
            'experimental_design_description': 'experimentalDesignDescription',
            'experimental_design_type': 'experimentalDesignType',
            'observation_unit_level_hierarchy': 'observationUnitLevelHierarchy',
            'observation_unit_description': 'observationUnitDescription',
            'growth_facility_description': 'growthFacilityDescription',
            'growth_facility_type': 'growthFacilityType',
            'cultural_practices': 'culturalPractices'
        };
        
        Object.entries(fieldMapping).forEach(([dbField, formField]) => {
            const element = stage2.querySelector(`textarea[name="STUDY.${formField}"]`);
            if (element) {
                element.value = study[dbField] || '';
                console.log(`Found and set STUDY.${formField} to:`, study[dbField] || '');
                // Trigger input event to update textarea height
                element.dispatchEvent(new Event('input'));
            } else {
                console.warn(`Element not found: STUDY.${formField}`);
                // Log the HTML structure around where the element should be
                const section = stage2.querySelector('.form-section');
                if (section) {
                    console.log('Form section HTML:', section.innerHTML);
                }
            }
        });
    } else {
        console.log('No study data available');
    }

    // Initialize people data
    if (data.PERSON && data.PERSON.length > 0) {
        console.log('Initializing person data:', JSON.stringify(data.PERSON, null, 2));
        const people = data.PERSON.filter(person => person !== null); // Filter out null values
        if (people.length > 0) {
            // Create a formatted text for each person
            const peopleText = people.map(person => {
                const name = person.NAME || '';
                const roles = Array.isArray(person.ROLE) ? person.ROLE.join(', ') : '';
                const affiliations = Array.isArray(person.AFFILIATION) ? person.AFFILIATION.join(', ') : '';
                return `${name} (${roles}) - ${affiliations}`;
            }).join('\n');
            
            // Set the value in the name field
            const element = stage2.querySelector('textarea[name="PERSON.name"]');
            if (element) {
                element.value = peopleText;
                console.log('Found and set PERSON.name to:', peopleText);
                // Trigger input event to update textarea height
                element.dispatchEvent(new Event('input'));
            } else {
                console.warn('Element not found: PERSON.name');
                // Log the HTML structure around where the element should be
                const section = stage2.querySelector('.form-section');
                if (section) {
                    console.log('Form section HTML:', section.innerHTML);
                }
            }
        } else {
            console.log('No valid person data to initialize');
        }
    } else {
        console.log('No person data available');
    }

    // Initialize data file data
    if (data.DATA_FILE) {
        console.log('Initializing data file data:', JSON.stringify(data.DATA_FILE, null, 2));
        const dataFile = data.DATA_FILE;
        
        // Map database fields to form fields
        const fieldMapping = {
            'file_link': 'fileLink',
            'description': 'description',
            'version': 'version'
        };
        
        Object.entries(fieldMapping).forEach(([dbField, formField]) => {
            const element = stage2.querySelector(`textarea[name="DATA_FILE.${formField}"]`);
            if (element) {
                element.value = dataFile[dbField] || '';
                console.log(`Found and set DATA_FILE.${formField} to:`, dataFile[dbField] || '');
                // Trigger input event to update textarea height
                element.dispatchEvent(new Event('input'));
            } else {
                console.warn(`Element not found: DATA_FILE.${formField}`);
                // Log the HTML structure around where the element should be
                const section = stage2.querySelector('.form-section');
                if (section) {
                    console.log('Form section HTML:', section.innerHTML);
                }
            }
        });
    } else {
        console.log('No data file data available');
    }

    // Initialize biological material data
    if (data.BIOLOGICAL_MATERIAL) {
        console.log('Initializing biological material data:', JSON.stringify(data.BIOLOGICAL_MATERIAL, null, 2));
        const biologicalMaterial = data.BIOLOGICAL_MATERIAL;
        
        // Map database fields to form fields
        const fieldMapping = {
            'biological_material_id': 'biologicalMaterialId',
            'external_id': 'externalId',
            'organism': 'organism',
            'genus': 'genus',
            'species': 'species',
            'infraspecific_name': 'infraspecificName',
            'latitude': 'latitude',
            'longitude': 'longitude',
            'altitude': 'altitude',
            'coordinate_uncertainty': 'coordinateUncertainty',
            'preprocessing': 'preprocessing',
            'source_id': 'sourceId',
            'source_doi': 'sourceDoi',
            'source_accession_number': 'sourceAccessionNumber',
            'source_accession_name': 'sourceAccessionName',
            'source_institution_code': 'sourceInstitutionCode',
            'source_institution_name': 'sourceInstitutionName',
            'source_other_ids': 'sourceOtherIds',
            'source_latitude': 'sourceLatitude',
            'source_longitude': 'sourceLongitude',
            'source_altitude': 'sourceAltitude',
            'source_coordinate_uncertainty': 'sourceCoordinateUncertainty',
            'source_description': 'sourceDescription'
        };
        
        Object.entries(fieldMapping).forEach(([dbField, formField]) => {
            const element = stage2.querySelector(`textarea[name="BIOLOGICAL_MATERIAL.${formField}"]`);
            if (element) {
                const value = Array.isArray(biologicalMaterial[dbField]) 
                    ? biologicalMaterial[dbField].join(', ')
                    : biologicalMaterial[dbField] || '';
                element.value = value;
                console.log(`Found and set BIOLOGICAL_MATERIAL.${formField} to:`, value);
                // Trigger input event to update textarea height
                element.dispatchEvent(new Event('input'));
            } else {
                console.warn(`Element not found: BIOLOGICAL_MATERIAL.${formField}`);
                // Log the HTML structure around where the element should be
                const section = stage2.querySelector('.form-section');
                if (section) {
                    console.log('Form section HTML:', section.innerHTML);
                }
            }
        });
    } else {
        console.log('No biological material data available');
    }

    // Initialize environment data
    if (data.ENVIRONMENT) {
        console.log('Initializing environment data:', JSON.stringify(data.ENVIRONMENT, null, 2));
        const environment = data.ENVIRONMENT;
        
        // Map database fields to form fields
        const fieldMapping = {
            'parameter': 'parameter',
            'parameter_value': 'parameterValue'
        };
        
        Object.entries(fieldMapping).forEach(([dbField, formField]) => {
            const element = stage2.querySelector(`textarea[name="ENVIRONMENT.${formField}"]`);
            if (element) {
                element.value = environment[dbField] || '';
                console.log(`Found and set ENVIRONMENT.${formField} to:`, environment[dbField] || '');
                // Trigger input event to update textarea height
                element.dispatchEvent(new Event('input'));
            } else {
                console.warn(`Element not found: ENVIRONMENT.${formField}`);
                // Log the HTML structure around where the element should be
                const section = stage2.querySelector('.form-section');
                if (section) {
                    console.log('Form section HTML:', section.innerHTML);
                }
            }
        });
    } else {
        console.log('No environment data available');
    }

    // Initialize experimental factor data
    if (data.EXPERIMENTAL_FACTOR) {
        console.log('Initializing experimental factor data:', JSON.stringify(data.EXPERIMENTAL_FACTOR, null, 2));
        const experimentalFactor = data.EXPERIMENTAL_FACTOR;
        
        // Map database fields to form fields
        const fieldMapping = {
            'factor_type': 'factorType',
            'factor_description': 'factorDescription',
            'factor_values': 'factorValues'
        };
        
        Object.entries(fieldMapping).forEach(([dbField, formField]) => {
            const element = stage2.querySelector(`textarea[name="EXPERIMENTAL_FACTOR.${formField}"]`);
            if (element) {
                const value = dbField === 'factor_values' 
                    ? (experimentalFactor[dbField] ? experimentalFactor[dbField].join(', ') : '')
                    : experimentalFactor[dbField] || '';
                element.value = value;
                console.log(`Found and set EXPERIMENTAL_FACTOR.${formField} to:`, value);
                // Trigger input event to update textarea height
                element.dispatchEvent(new Event('input'));
            } else {
                console.warn(`Element not found: EXPERIMENTAL_FACTOR.${formField}`);
                // Log the HTML structure around where the element should be
                const section = stage2.querySelector('.form-section');
                if (section) {
                    console.log('Form section HTML:', section.innerHTML);
                }
            }
        });
    } else {
        console.log('No experimental factor data available');
    }

    // Initialize event data
    if (data.EVENT) {
        console.log('Initializing event data:', JSON.stringify(data.EVENT, null, 2));
        const event = data.EVENT;
        
        // Map database fields to form fields
        const fieldMapping = {
            'event_type': 'eventType',
            'accession_number': 'accessionNumber',
            'description': 'description',
            'event_date': 'eventDate'
        };
        
        Object.entries(fieldMapping).forEach(([dbField, formField]) => {
            const element = stage2.querySelector(`textarea[name="EVENT.${formField}"]`);
            if (element) {
                const value = dbField === 'event_date' 
                    ? (event[dbField] ? event[dbField].join(', ') : '')
                    : event[dbField] || '';
                element.value = value;
                console.log(`Found and set EVENT.${formField} to:`, value);
                // Trigger input event to update textarea height
                element.dispatchEvent(new Event('input'));
            } else {
                console.warn(`Element not found: EVENT.${formField}`);
                // Log the HTML structure around where the element should be
                const section = stage2.querySelector('.form-section');
                if (section) {
                    console.log('Form section HTML:', section.innerHTML);
                }
            }
        });
    } else {
        console.log('No event data available');
    }

    // Initialize observation unit data
    if (data.OBSERVATION_UNIT) {
        console.log('Initializing observation unit data:', JSON.stringify(data.OBSERVATION_UNIT, null, 2));
        const observationUnit = data.OBSERVATION_UNIT;
        
        // Map database fields to form fields
        const fieldMapping = {
            'observation_unit_id': 'observationUnitId',
            'observation_unit_type': 'observationUnitType',
            'external_id': 'externalId',
            'spatial_distribution': 'spatialDistribution',
            'factor_values': 'factorValues'
        };
        
        Object.entries(fieldMapping).forEach(([dbField, formField]) => {
            const element = stage2.querySelector(`textarea[name="OBSERVATION_UNIT.${formField}"]`);
            if (element) {
                const value = Array.isArray(observationUnit[dbField]) 
                    ? observationUnit[dbField].join(', ')
                    : observationUnit[dbField] || '';
                element.value = value;
                console.log(`Found and set OBSERVATION_UNIT.${formField} to:`, value);
                // Trigger input event to update textarea height
                element.dispatchEvent(new Event('input'));
            } else {
                console.warn(`Element not found: OBSERVATION_UNIT.${formField}`);
                // Log the HTML structure around where the element should be
                const section = stage2.querySelector('.form-section');
                if (section) {
                    console.log('Form section HTML:', section.innerHTML);
                }
            }
        });
    } else {
        console.log('No observation unit data available');
    }

    // Initialize sample data
    if (data.SAMPLE) {
        console.log('Initializing sample data:', JSON.stringify(data.SAMPLE, null, 2));
        const sample = data.SAMPLE;
        
        // Map database fields to form fields
        const fieldMapping = {
            'sample_id': 'sampleId',
            'development_stage': 'developmentStage',
            'anatomical_entity': 'anatomicalEntity',
            'description': 'description',
            'collection_date': 'collectionDate',
            'external_id': 'externalId'
        };
        
        Object.entries(fieldMapping).forEach(([dbField, formField]) => {
            const element = stage2.querySelector(`textarea[name="SAMPLE.${formField}"]`);
            if (element) {
                const value = Array.isArray(sample[dbField]) 
                    ? sample[dbField].join(', ')
                    : sample[dbField] || '';
                element.value = value;
                console.log(`Found and set SAMPLE.${formField} to:`, value);
                // Trigger input event to update textarea height
                element.dispatchEvent(new Event('input'));
            } else {
                console.warn(`Element not found: SAMPLE.${formField}`);
                // Log the HTML structure around where the element should be
                const section = stage2.querySelector('.form-section');
                if (section) {
                    console.log('Form section HTML:', section.innerHTML);
                }
            }
        });
    } else {
        console.log('No sample data available');
    }

    // Initialize observed variable data
    if (data.OBSERVED_VARIABLE) {
        console.log('Initializing observed variable data:', JSON.stringify(data.OBSERVED_VARIABLE, null, 2));
        const observedVariable = data.OBSERVED_VARIABLE;
        
        // Map database fields to form fields
        const fieldMapping = {
            'variable_id': 'variableId',
            'variable_name': 'variableName',
            'accession_number': 'accessionNumber',
            'trait_name': 'traitName',
            'trait_entity': 'traitEntity',
            'trait_entity_accession_number': 'traitEntityAccessionNumber',
            'trait_characteristic': 'traitCharacteristic',
            'trait_characteristic_accession_number': 'traitCharacteristicAccessionNumber',
            'trait_accession_number': 'traitAccessionNumber',
            'method_name': 'methodName',
            'method_accession_number': 'methodAccessionNumber',
            'method_description': 'methodDescription',
            'method_reference': 'methodReference',
            'scale_name': 'scaleName',
            'scale_accession_number': 'scaleAccessionNumber',
            'time_scale': 'timeScale'
        };
        
        Object.entries(fieldMapping).forEach(([dbField, formField]) => {
            const element = stage2.querySelector(`textarea[name="OBSERVED_VARIABLE.${formField}"]`);
            if (element) {
                element.value = observedVariable[dbField] || '';
                console.log(`Found and set OBSERVED_VARIABLE.${formField} to:`, observedVariable[dbField] || '');
                // Trigger input event to update textarea height
                element.dispatchEvent(new Event('input'));
            } else {
                console.warn(`Element not found: OBSERVED_VARIABLE.${formField}`);
                // Log the HTML structure around where the element should be
                const section = stage2.querySelector('.form-section');
                if (section) {
                    console.log('Form section HTML:', section.innerHTML);
                }
            }
        });
    } else {
        console.log('No observed variable data available');
    }
    
    console.log('Form initialization complete');
} 