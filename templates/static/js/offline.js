/**
 * Offline functionality for Healthcare Dictionary
 * Handles IndexedDB setup, data synchronization, and offline searches
 */

// IndexedDB database name and version
const DB_NAME = 'HealthcareDictionary';
const DB_VERSION = 1;
const STORES = {
    TERMS: 'terms',
    CATEGORIES: 'categories'
};

// Initialize offline database
document.addEventListener('DOMContentLoaded', function() {
    // Set up install button
    const installButton = document.getElementById('install-db-btn');
    if (installButton) {
        installButton.addEventListener('click', function() {
            installOfflineDatabase();
        });
    }
});

/**
 * Install the offline database
 */
function installOfflineDatabase() {
    const installButton = document.getElementById('install-db-btn');
    
    if (installButton) {
        installButton.disabled = true;
        installButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Installing...';
    }
    
    initializeOfflineDatabase()
        .then(() => {
            if (installButton) {
                installButton.innerHTML = '<i class="fas fa-check me-2"></i> Installation Complete';
                installButton.classList.remove('btn-outline-info');
                installButton.classList.add('btn-success');
            }
            
            // Update database status
            localStorage.setItem('dbInstalled', 'true');
            localStorage.setItem('lastSync', new Date().getTime().toString());
            updateDatabaseStatus();
            
            alert('Offline database installed successfully! You can now use the dictionary without an internet connection.');
        })
        .catch(error => {
            console.error('Database installation failed:', error);
            
            if (installButton) {
                installButton.disabled = false;
                installButton.innerHTML = '<i class="fas fa-exclamation-triangle me-2"></i> Installation Failed, Try Again';
                installButton.classList.remove('btn-outline-info');
                installButton.classList.add('btn-outline-danger');
            }
            
            alert('Failed to install offline database. Please check your connection and try again.');
        });
}

/**
 * Initialize the IndexedDB database
 * @returns {Promise} Promise that resolves when database is set up and synced
 */
function initializeOfflineDatabase() {
    return new Promise((resolve, reject) => {
        // Check if IndexedDB is supported
        if (!window.indexedDB) {
            reject(new Error('Your browser does not support offline storage.'));
            return;
        }
        
        // Open database
        const request = indexedDB.open(DB_NAME, DB_VERSION);
        
        // Handle database upgrades or creation
        request.onupgradeneeded = function(event) {
            const db = event.target.result;
            
            // Create object stores if they don't exist
            if (!db.objectStoreNames.contains(STORES.TERMS)) {
                const termsStore = db.createObjectStore(STORES.TERMS, { keyPath: 'id' });
                termsStore.createIndex('term_en', 'term_en', { unique: false });
                termsStore.createIndex('term_ewe', 'term_ewe', { unique: false });
                termsStore.createIndex('category_id', 'category_id', { unique: false });
            }
            
            if (!db.objectStoreNames.contains(STORES.CATEGORIES)) {
                db.createObjectStore(STORES.CATEGORIES, { keyPath: 'id' });
            }
        };
        
        // Handle errors
        request.onerror = function(event) {
            reject(new Error('Database error: ' + event.target.error));
        };
        
        // Success handler - sync data once database is open
        request.onsuccess = function(event) {
            const db = event.target.result;
            
            // Sync data from server
            syncDataFromServer(db)
                .then(resolve)
                .catch(reject);
        };
    });
}

/**
 * Synchronize data from the server to IndexedDB
 * @param {IDBDatabase} db - IndexedDB database instance
 * @returns {Promise} Promise that resolves when sync is complete
 */
function syncDataFromServer(db) {
    return new Promise((resolve, reject) => {
        // Fetch both categories and terms in parallel
        Promise.all([
            fetch('/api/categories').then(response => response.json()),
            fetch('/api/terms').then(response => response.json())
        ])
        .then(([categories, terms]) => {
            // Start a transaction to save both types of data
            const transaction = db.transaction([STORES.CATEGORIES, STORES.TERMS], 'readwrite');
            
            // Set up error handler for the transaction
            transaction.onerror = function(event) {
                reject(new Error('Transaction error: ' + event.target.error));
            };
            
            // Set up success handler
            transaction.oncomplete = function() {
                resolve();
            };
            
            // Clear and repopulate categories
            const categoryStore = transaction.objectStore(STORES.CATEGORIES);
            categoryStore.clear();
            categories.forEach(category => {
                categoryStore.add(category);
            });
            
            // Clear and repopulate terms
            const termStore = transaction.objectStore(STORES.TERMS);
            termStore.clear();
            terms.forEach(term => {
                termStore.add(term);
            });
        })
        .catch(error => {
            reject(new Error('Failed to fetch data from server: ' + error.message));
        });
    });
}

/**
 * Search terms in the offline database
 * @param {string} query - Search query
 * @param {string} categoryId - Optional category ID filter
 * @param {string} language - Language to search in (en or ewe)
 * @returns {Promise<Array>} Promise that resolves with search results
 */
function searchOfflineTerms(query, categoryId, language) {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, DB_VERSION);
        
        request.onerror = function(event) {
            reject(new Error('Database error: ' + event.target.error));
        };
        
        request.onsuccess = function(event) {
            const db = event.target.result;
            const transaction = db.transaction([STORES.TERMS], 'readonly');
            const termStore = transaction.objectStore(STORES.TERMS);
            const results = [];
            
            // Get all terms and filter client-side
            const getAllRequest = termStore.getAll();
            
            getAllRequest.onsuccess = function(event) {
                let terms = event.target.result;
                
                // Apply category filter if provided
                if (categoryId) {
                    terms = terms.filter(term => term.category_id == categoryId);
                }
                
                // Apply search filter if query provided
                if (query && query.length > 0) {
                    const queryLower = query.toLowerCase();
                    terms = terms.filter(term => {
                        if (language === 'en') {
                            return term.term_en.toLowerCase().includes(queryLower) || 
                                   term.definition_en.toLowerCase().includes(queryLower);
                        } else {
                            return term.term_ewe.toLowerCase().includes(queryLower) || 
                                   term.definition_ewe.toLowerCase().includes(queryLower);
                        }
                    });
                }
                
                resolve(terms);
            };
            
            getAllRequest.onerror = function(event) {
                reject(new Error('Search error: ' + event.target.error));
            };
        };
    });
}

/**
 * Get a specific term from IndexedDB
 * @param {number} termId - ID of the term to retrieve
 * @returns {Promise<Object>} Promise that resolves with the term object
 */
function getOfflineTerm(termId) {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, DB_VERSION);
        
        request.onerror = function(event) {
            reject(new Error('Database error: ' + event.target.error));
        };
        
        request.onsuccess = function(event) {
            const db = event.target.result;
            const transaction = db.transaction([STORES.TERMS], 'readonly');
            const termStore = transaction.objectStore(STORES.TERMS);
            
            const getRequest = termStore.get(parseInt(termId));
            
            getRequest.onsuccess = function(event) {
                const term = event.target.result;
                if (term) {
                    resolve(term);
                } else {
                    reject(new Error('Term not found'));
                }
            };
            
            getRequest.onerror = function(event) {
                reject(new Error('Failed to get term: ' + event.target.error));
            };
        };
    });
}

/**
 * Get all categories from IndexedDB
 * @returns {Promise<Array>} Promise that resolves with array of categories
 */
function getOfflineCategories() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, DB_VERSION);
        
        request.onerror = function(event) {
            reject(new Error('Database error: ' + event.target.error));
        };
        
        request.onsuccess = function(event) {
            const db = event.target.result;
            const transaction = db.transaction([STORES.CATEGORIES], 'readonly');
            const categoryStore = transaction.objectStore(STORES.CATEGORIES);
            
            const getAllRequest = categoryStore.getAll();
            
            getAllRequest.onsuccess = function(event) {
                resolve(event.target.result);
            };
            
            getAllRequest.onerror = function(event) {
                reject(new Error('Failed to get categories: ' + event.target.error));
            };
        };
    });
}

/**
 * Check if IndexedDB contains the dictionary data
 * @returns {Promise<boolean>} Promise that resolves with true if data exists
 */
function checkOfflineDatabaseReady() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, DB_VERSION);
        
        request.onerror = function(event) {
            reject(new Error('Database error: ' + event.target.error));
        };
        
        request.onsuccess = function(event) {
            const db = event.target.result;
            const transaction = db.transaction([STORES.TERMS], 'readonly');
            const termStore = transaction.objectStore(STORES.TERMS);
            
            const countRequest = termStore.count();
            
            countRequest.onsuccess = function(event) {
                resolve(event.target.result > 0);
            };
            
            countRequest.onerror = function(event) {
                reject(new Error('Failed to count terms: ' + event.target.error));
            };
        };
    });
}