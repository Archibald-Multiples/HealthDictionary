/**
 * Feedback functionality for Healthcare Dictionary
 * Handles form submission and offline feedback storage
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize feedback form
    initializeFeedbackForm();
    
    // Auto-dismiss flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.classList.add('fade');
            setTimeout(() => {
                message.remove();
            }, 150);
        }, 5000);
    });
});

/**
 * Initialize the feedback form with event listeners
 */
function initializeFeedbackForm() {
    const feedbackForm = document.getElementById('feedback-form');
    if (!feedbackForm) return;
    
    // Handle offline form submission
    feedbackForm.addEventListener('submit', function(event) {
        if (!navigator.onLine) {
            event.preventDefault();
            handleOfflineFeedback(this);
        }
    });
}

/**
 * Handle feedback submission when offline
 * @param {HTMLFormElement} form - The feedback form
 */
function handleOfflineFeedback(form) {
    // Get form data
    const formData = new FormData(form);
    const feedbackData = {};
    
    for (const [key, value] of formData.entries()) {
        feedbackData[key] = value;
    }
    
    // Add timestamp
    feedbackData.timestamp = new Date().toISOString();
    
    // Store feedback in localStorage for later submission
    storeFeedbackForLater(feedbackData);
    
    // Show success message
    alert('Feedback saved offline. Will submit when online.');
    
    // Reset form
    form.reset();
    
    // Redirect to home page
    window.location.href = '/';
}

/**
 * Store feedback in localStorage for later submission
 * @param {Object} feedbackData - The feedback data to store
 */
function storeFeedbackForLater(feedbackData) {
    // Get existing pending feedback items
    let pendingFeedback = JSON.parse(localStorage.getItem('pendingFeedback') || '[]');
    
    // Add new feedback
    pendingFeedback.push(feedbackData);
    
    // Save back to localStorage
    localStorage.setItem('pendingFeedback', JSON.stringify(pendingFeedback));
    
    // Register sync event if supported
    if ('serviceWorker' in navigator && 'SyncManager' in window) {
        navigator.serviceWorker.ready
            .then(registration => {
                registration.sync.register('sync-feedback');
            })
            .catch(err => {
                console.error('Failed to register sync event:', err);
            });
    }
}

/**
 * Submit pending feedback when online
 * Called by the service worker or when online status changes
 * @returns {Promise} Promise that resolves when all feedback is submitted
 */
function submitPendingFeedback() {
    return new Promise((resolve, reject) => {
        // Get pending feedback
        const pendingFeedback = JSON.parse(localStorage.getItem('pendingFeedback') || '[]');
        if (pendingFeedback.length === 0) {
            resolve('No pending feedback');
            return;
        }
        
        // Keep track of successful submissions
        const successfulSubmissions = [];
        
        // Process each feedback item
        const promises = pendingFeedback.map((feedback, index) => {
            return fetch('/api/feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(feedback)
            })
            .then(response => {
                if (response.ok) {
                    successfulSubmissions.push(index);
                    return true;
                } else {
                    return false;
                }
            })
            .catch(() => false);
        });
        
        // After all submissions are attempted
        Promise.all(promises)
            .then(() => {
                // Remove successfully submitted feedback
                const remainingFeedback = pendingFeedback.filter(
                    (_, index) => !successfulSubmissions.includes(index)
                );
                
                // Update localStorage
                localStorage.setItem('pendingFeedback', JSON.stringify(remainingFeedback));
                
                // Resolve with result
                resolve(`Submitted ${successfulSubmissions.length} of ${pendingFeedback.length} pending feedback items.`);
            })
            .catch(error => {
                reject(new Error(`Error submitting feedback: ${error.message}`));
            });
    });
}

// Check if we're back online and submit any pending feedback
window.addEventListener('online', function() {
    submitPendingFeedback()
        .then(result => {
            console.log(result);
            if (result.includes('Submitted') && !result.includes('0 of')) {
                alert('Your saved feedback has been submitted successfully.');
            }
        })
        .catch(error => {
            console.error('Failed to submit pending feedback:', error);
        });
});