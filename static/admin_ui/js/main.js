/**
 * Django API Hub - Admin UI JavaScript
 * 
 * This file contains the JavaScript code for the custom admin UI.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize HTMX events
    setupHtmxEvents();
    
    // Initialize any interactive components
    initializeComponents();
});

/**
 * Set up HTMX event handlers
 */
function setupHtmxEvents() {
    // Handle HTMX after swap event
    document.body.addEventListener('htmx:afterSwap', function(event) {
        // Reinitialize components after HTMX content swap
        initializeComponents();
    });
    
    // Handle HTMX before request event
    document.body.addEventListener('htmx:beforeRequest', function(event) {
        // Show loading indicator if needed
        const target = event.detail.target;
        if (target.dataset.showLoading) {
            const loadingEl = document.createElement('div');
            loadingEl.className = 'htmx-loading';
            loadingEl.innerHTML = `
                <div class="flex items-center justify-center p-4">
                    <svg class="animate-spin h-5 w-5 text-blue-500 mr-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Loading...</span>
                </div>
            `;
            target.appendChild(loadingEl);
        }
    });
    
    // Handle HTMX after request event
    document.body.addEventListener('htmx:afterRequest', function(event) {
        // Remove loading indicator
        const target = event.detail.target;
        const loadingEl = target.querySelector('.htmx-loading');
        if (loadingEl) {
            loadingEl.remove();
        }
    });
    
    // Handle HTMX response error
    document.body.addEventListener('htmx:responseError', function(event) {
        console.error('HTMX Response Error:', event.detail);
        
        // Show error notification
        showNotification('An error occurred while processing your request.', 'error');
    });
}

/**
 * Initialize interactive components
 */
function initializeComponents() {
    // Initialize dropdowns
    initializeDropdowns();
    
    // Initialize modals
    initializeModals();
    
    // Initialize tabs
    initializeTabs();
    
    // Initialize code editors (if any)
    initializeCodeEditors();
}

/**
 * Initialize dropdown components
 */
function initializeDropdowns() {
    document.querySelectorAll('[data-dropdown]').forEach(function(dropdown) {
        const button = dropdown.querySelector('[data-dropdown-toggle]');
        const menu = dropdown.querySelector('[data-dropdown-menu]');
        
        if (button && menu) {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                menu.classList.toggle('hidden');
            });
            
            // Close dropdown when clicking outside
            document.addEventListener('click', function(e) {
                if (!dropdown.contains(e.target)) {
                    menu.classList.add('hidden');
                }
            });
        }
    });
}

/**
 * Initialize modal components
 */
function initializeModals() {
    // Open modal buttons
    document.querySelectorAll('[data-modal-open]').forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const modalId = button.dataset.modalOpen;
            openModal(modalId);
        });
    });
    
    // Close modal buttons
    document.querySelectorAll('[data-modal-close]').forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const modal = button.closest('[data-modal]');
            if (modal) {
                closeModal(modal.id);
            }
        });
    });
}

/**
 * Open a modal by ID
 */
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        // Dispatch custom event for Alpine.js to handle
        window.dispatchEvent(new CustomEvent('open-modal'));
        
        // Load content if needed
        const contentUrl = modal.dataset.modalContent;
        if (contentUrl) {
            const contentContainer = document.getElementById('modal-content');
            if (contentContainer) {
                // Use HTMX to load content
                contentContainer.setAttribute('hx-get', contentUrl);
                contentContainer.setAttribute('hx-trigger', 'load');
            }
        }
    }
}

/**
 * Close a modal by ID
 */
function closeModal(modalId) {
    // Dispatch custom event for Alpine.js to handle
    window.dispatchEvent(new CustomEvent('close-modal'));
}

/**
 * Initialize tab components
 */
function initializeTabs() {
    document.querySelectorAll('[data-tabs]').forEach(function(tabContainer) {
        const tabs = tabContainer.querySelectorAll('[data-tab]');
        const panels = tabContainer.querySelectorAll('[data-tab-panel]');
        
        tabs.forEach(function(tab) {
            tab.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Deactivate all tabs
                tabs.forEach(t => t.classList.remove('active-tab'));
                
                // Activate clicked tab
                tab.classList.add('active-tab');
                
                // Hide all panels
                panels.forEach(p => p.classList.add('hidden'));
                
                // Show corresponding panel
                const panelId = tab.dataset.tab;
                const panel = tabContainer.querySelector(`[data-tab-panel="${panelId}"]`);
                if (panel) {
                    panel.classList.remove('hidden');
                }
            });
        });
    });
}

/**
 * Initialize code editors
 */
function initializeCodeEditors() {
    // This is a placeholder for code editor initialization
    // In a real implementation, you might use a library like CodeMirror or Monaco Editor
}

/**
 * Show a notification message
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `max-w-sm w-full bg-white shadow-lg rounded-lg pointer-events-auto ring-1 ring-black ring-opacity-5 overflow-hidden`;
    
    // Set icon based on type
    let icon = '';
    if (type === 'success') {
        icon = `<svg class="h-6 w-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>`;
    } else if (type === 'error') {
        icon = `<svg class="h-6 w-6 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>`;
    } else if (type === 'warning') {
        icon = `<svg class="h-6 w-6 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
        </svg>`;
    } else {
        icon = `<svg class="h-6 w-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>`;
    }
    
    // Set notification content
    notification.innerHTML = `
        <div class="p-4">
            <div class="flex items-start">
                <div class="flex-shrink-0">
                    ${icon}
                </div>
                <div class="ml-3 w-0 flex-1 pt-0.5">
                    <p class="text-sm font-medium text-gray-900">
                        ${message}
                    </p>
                </div>
                <div class="ml-4 flex-shrink-0 flex">
                    <button class="bg-white rounded-md inline-flex text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                        <span class="sr-only">Close</span>
                        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Add notification to the notifications container
    const notificationsContainer = document.getElementById('notifications');
    if (notificationsContainer) {
        notificationsContainer.appendChild(notification);
        
        // Add animation classes
        notification.classList.add('transform', 'ease-out', 'duration-300', 'transition');
        notification.classList.add('translate-y-2', 'opacity-0', 'sm:translate-y-0', 'sm:translate-x-2');
        
        // Trigger animation
        setTimeout(() => {
            notification.classList.remove('translate-y-2', 'opacity-0', 'sm:translate-y-0', 'sm:translate-x-2');
            notification.classList.add('translate-y-0', 'opacity-100', 'sm:translate-x-0');
        }, 10);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.classList.add('transition', 'ease-in', 'duration-100');
            notification.classList.add('opacity-0');
            setTimeout(() => {
                notification.remove();
            }, 100);
        }, 5000);
        
        // Add click handler to close button
        const closeButton = notification.querySelector('button');
        if (closeButton) {
            closeButton.addEventListener('click', function() {
                notification.classList.add('transition', 'ease-in', 'duration-100');
                notification.classList.add('opacity-0');
                setTimeout(() => {
                    notification.remove();
                }, 100);
            });
        }
    }
}
