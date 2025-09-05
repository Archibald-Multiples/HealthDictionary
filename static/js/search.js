/**
 * Search functionality for Healthcare Dictionary
 * Handles both online and offline search capabilities
 */

document.addEventListener('DOMContentLoaded', function() {
    // Handle search form submission
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(event) {
            // If offline, use IndexedDB for search
            if (!navigator.onLine) {
                event.preventDefault();
                performOfflineSearch();
            }
        });
    }
    
    // Handle language selection in search
    const searchLangEn = document.getElementById('searchLangEn');
    const searchLangEwe = document.getElementById('searchLangEwe');
    
    if (searchLangEn && searchLangEwe) {
        // Set initial state based on current language
        const currentLang = localStorage.getItem('language') || 'en';
        searchLangEn.checked = (currentLang === 'en');
        searchLangEwe.checked = (currentLang === 'ewe');
        
        // Update language preference when changed
        searchLangEn.addEventListener('change', function() {
            if (this.checked) {
                localStorage.setItem('language', 'en');
            }
        });
        
        searchLangEwe.addEventListener('change', function() {
            if (this.checked) {
                localStorage.setItem('language', 'ewe');
            }
        });
    }
});

/**
 * Perform search using offline IndexedDB when no internet connection
 */
function performOfflineSearch() {
    const query = document.getElementById('search-input').value;
    const categoryId = document.getElementById('category-filter').value;
    const language = document.querySelector('input[name="lang"]:checked').value || 'en';
    
    // Check if database is installed
    checkOfflineDatabaseReady()
        .then(isReady => {
            if (!isReady) {
                showOfflineSearchError('The offline database has not been installed yet. Please connect to the internet and install it first.');
                return;
            }
            
            // Perform the search
            return searchOfflineTerms(query, categoryId, language);
        })
        .then(results => {
            if (!results) return; // Error was already shown
            
            // Display results
            displayOfflineSearchResults(results, query);
        })
        .catch(error => {
            console.error('Offline search error:', error);
            showOfflineSearchError('An error occurred during the offline search. ' + error.message);
        });
}

/**
 * Display offline search results 
 * @param {Array} results - Array of term objects
 * @param {string} query - Search query
 */
function displayOfflineSearchResults(results, query) {
    const resultsContainer = document.getElementById('search-results');
    
    if (!resultsContainer) {
        alert('Search results: ' + results.length + ' terms found');
        return;
    }
    
    // Clear existing results
    resultsContainer.innerHTML = '';
    
    // Update results count
    const countElement = document.querySelector('h2.h5 .badge');
    if (countElement) {
        countElement.textContent = results.length;
    }
    
    if (results.length === 0) {
        resultsContainer.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                <span class="lang-en">No results found for "${query}". Try a different search term or category.</span>
                <span class="lang-ewe d-none">Nyagbɔgblɔ aɖeke medo ɖe "${query}" ŋu o. Di nyagbɔgblɔ bubu alo ɖoƒe bubu.</span>
            </div>
        `;
        return;
    }
    
    // Build HTML for each result
    results.forEach(term => {
        const resultItem = document.createElement('a');
        resultItem.href = `/term/${term.id}`;
        resultItem.className = 'list-group-item list-group-item-action term-item';
        resultItem.setAttribute('data-term-id', term.id);
        
        resultItem.innerHTML = `
            <div class="d-flex w-100 justify-content-between">
                <h5 class="mb-1">
                    <span class="lang-en">${escapeHtml(term.term_en)}</span>
                    <span class="lang-ewe d-none">${escapeHtml(term.term_ewe)}</span>
                </h5>
                <small>
                    <span class="badge bg-primary">
                        <span class="lang-en">${escapeHtml(term.category_name_en)}</span>
                        <span class="lang-ewe d-none">${escapeHtml(term.category_name_ewe)}</span>
                    </span>
                </small>
            </div>
            <div class="row">
                <div class="col-md-6">
                    <p class="mb-1">
                        <span class="lang-en"><strong>English:</strong> ${truncateText(escapeHtml(term.definition_en), 100)}</span>
                        <span class="lang-ewe d-none"><strong>Yevugbe:</strong> ${truncateText(escapeHtml(term.definition_en), 100)}</span>
                    </p>
                </div>
                <div class="col-md-6">
                    <p class="mb-1">
                        <span class="lang-en"><strong>Ewe:</strong> ${truncateText(escapeHtml(term.definition_ewe), 100)}</span>
                        <span class="lang-ewe d-none"><strong>Eʋegbe:</strong> ${truncateText(escapeHtml(term.definition_ewe), 100)}</span>
                    </p>
                </div>
            </div>
        `;
        
        resultsContainer.appendChild(resultItem);
    });
    
    // Apply current language selection
    const currentLang = localStorage.getItem('language') || 'en';
    if (currentLang === 'ewe') {
        document.querySelectorAll('.lang-en').forEach(el => el.classList.add('d-none'));
        document.querySelectorAll('.lang-ewe').forEach(el => el.classList.remove('d-none'));
    }
    
    // Highlight search terms
    if (query && query.length > 2) {
        highlightOfflineSearchTerms(query);
    }
}

/**
 * Show error message for offline search
 * @param {string} message - Error message to display
 */
function showOfflineSearchError(message) {
    const resultsContainer = document.getElementById('search-results');
    
    if (!resultsContainer) {
        alert('Error: ' + message);
        return;
    }
    
    resultsContainer.innerHTML = `
        <div class="alert alert-danger">
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${message}
        </div>
        <div class="text-center mt-3">
            <button class="btn btn-primary" id="install-offline-db">
                <i class="fas fa-download me-2"></i>
                <span class="lang-en">Install Offline Database</span>
                <span class="lang-ewe d-none">Ɖe Nuŋlɔɖia Ɖe Wò Mɔ̀ Dzi</span>
            </button>
        </div>
    `;
    
    // Setup install button
    const installButton = document.getElementById('install-offline-db');
    if (installButton) {
        installButton.addEventListener('click', function() {
            if (navigator.onLine) {
                installOfflineDatabase();
            } else {
                alert('You need to be online to install the offline database.');
            }
        });
    }
}

/**
 * Highlight search terms in the results
 * @param {string} query - Search query to highlight
 */
function highlightOfflineSearchTerms(query) {
    const terms = document.querySelectorAll('.term-item');
    if (!query || query.length < 3) return;
    
    const regex = new RegExp(escapeRegExp(query), 'gi');
    terms.forEach(term => {
        const textNodes = getTextNodes(term);
        textNodes.forEach(node => {
            const text = node.nodeValue;
            if (regex.test(text)) {
                const newNode = document.createElement('span');
                newNode.innerHTML = text.replace(regex, match => <mark>${match}</mark>);
                node.parentNode.replaceChild(newNode, node);
            }
        });
    });
}

/**
 * Get all text nodes within an element
 * @param {Element} element - Element to search within
 * @returns {Array} Array of text nodes
 */
function getTextNodes(element) {
    const nodes = [];
    const walker = document.createTreeWalker(
        element,
        NodeFilter.SHOW_TEXT,
        null,
        false
    );
    
    let node;
    while(node = walker.nextNode()) {
        nodes.push(node);
    }
    
    return nodes;
}

/**
 * Escape string for use in regular expression
 * @param {string} string - String to escape
 * @returns {string} Escaped string
 */
function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * Escape HTML special characters
 * @param {string} text - String to escape
 * @returns {string} HTML escaped string
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Truncate text to a specified length with ellipsis
 * @param {string} text - Text to truncate
 * @param {number} length - Maximum length
 * @returns {string} Truncated text
 */
function truncateText(text, length) {
    if (!text) return '';
    return text.length > length ? text.substring(0, length) + '...' : text;
}