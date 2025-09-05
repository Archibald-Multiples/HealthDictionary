// Background Slideshow Logic
document.addEventListener('DOMContentLoaded', function() {
    const images = [
        '/static/img/backgrounds/med1.jpg',
        '/static/img/backgrounds/med2.jpg',
        '/static/img/backgrounds/med3.jpg',
        '/static/img/backgrounds/med4.jpg',
        '/static/img/backgrounds/med5.jpg',
        '/static/img/backgrounds/med6.jpg',
        '/static/img/backgrounds/med7.jpg',
        '/static/img/backgrounds/med8.jpg',
        '/static/img/backgrounds/med9.jpg',
        '/static/img/backgrounds/med10.jpg'
    ];
    let idx = 0;
    const bgDiv = document.getElementById('background-slideshow');
    function setBg() {
        bgDiv.style.backgroundImage = `url('${images[idx]}')`;
        idx = (idx + 1) % images.length;
    }
    setBg();
    setInterval(setBg, 30000); // 30 seconds
});
/**
 * Main application JavaScript for Healthcare Dictionary
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize language preference
    initializeLanguage();
    
    // Check online/offline status
    updateConnectionStatus();
    
    // Listen for online/offline events
    window.addEventListener('online', updateConnectionStatus);
    window.addEventListener('offline', updateConnectionStatus);
    
    // Initialize Database Status
    updateDatabaseStatus();
});

/**
 * Initialize language preference from localStorage or default to English
 */
function initializeLanguage() {
    const language = localStorage.getItem('language') || 'en';
    setLanguage(language);
}

/**
 * Set the application language
 * @param {string} lang - Language code (en or ewe)
 */
function setLanguage(lang) {
    // Store preference
    localStorage.setItem('language', lang);
    
    if (lang === 'en') {
        // Show English, hide Ewe
        document.querySelectorAll('.lang-en').forEach(el => el.classList.remove('d-none'));
        document.querySelectorAll('.lang-ewe').forEach(el => el.classList.add('d-none'));
        document.getElementById('lang-en').classList.add('active');
        document.getElementById('lang-ewe').classList.remove('active');
    } else {
        // Show Ewe, hide English
        document.querySelectorAll('.lang-en').forEach(el => el.classList.add('d-none'));
        document.querySelectorAll('.lang-ewe').forEach(el => el.classList.remove('d-none'));
        document.getElementById('lang-en').classList.remove('active');
        document.getElementById('lang-ewe').classList.add('active');
    }
    
    // Toggle radio buttons if they exist
    if (document.getElementById('searchLangEn')) {
        document.getElementById('searchLangEn').checked = (lang === 'en');
        document.getElementById('searchLangEwe').checked = (lang === 'ewe');
    }
}

/**
 * Update the connection status indicators
 */
function updateConnectionStatus() {
    const onlineStatus = document.getElementById('online-status');
    const offlineStatus = document.getElementById('offline-status');
    
    if (navigator.onLine) {
        onlineStatus.classList.remove('d-none');
        offlineStatus.classList.add('d-none');
    } else {
        onlineStatus.classList.add('d-none');
        offlineStatus.classList.remove('d-none');
    }
}

/**
 * Check and update database status
 */
function updateDatabaseStatus() {
    const dbStatus = document.getElementById('db-status');
    
    if (!window.indexedDB) {
        dbStatus.textContent = 'Offline Storage Not Supported';
        dbStatus.classList.remove('bg-info', 'bg-success');
        dbStatus.classList.add('bg-danger');
        return;
    }
    
    // Check if database is installed
    const dbInstalled = localStorage.getItem('dbInstalled') === 'true';
    const lastSync = localStorage.getItem('lastSync');
    
    if (dbInstalled && lastSync) {
        const syncDate = new Date(parseInt(lastSync));
        const formattedDate = syncDate.toLocaleDateString() + ' ' + syncDate.toLocaleTimeString();
        dbStatus.textContent = `Database Installed (Last sync: ${formattedDate})`;
        dbStatus.classList.remove('bg-info', 'bg-danger');
        dbStatus.classList.add('bg-success');
    } else {
        dbStatus.textContent = 'Offline Database Not Installed';
        dbStatus.classList.remove('bg-success', 'bg-danger');
        dbStatus.classList.add('bg-info');
    }
}

/**
 * Synchronize the database with the server
 */
function synchronizeDatabase() {
    const syncButton = document.getElementById('sync-button');
    const dbStatus = document.getElementById('db-status');
    
    // Disable the button during sync
    syncButton.disabled = true;
    syncButton.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i> Syncing...';
    dbStatus.textContent = 'Synchronizing...';
    dbStatus.classList.remove('bg-success', 'bg-danger', 'bg-info');
    dbStatus.classList.add('bg-warning');
    
    // Try to synchronize
    initializeOfflineDatabase()
        .then(() => {
            dbStatus.textContent = 'Database Synchronized Successfully';
            dbStatus.classList.remove('bg-warning', 'bg-danger', 'bg-info');
            dbStatus.classList.add('bg-success');
            
            // Update last sync time
            const now = new Date();
            localStorage.setItem('lastSync', now.getTime().toString());
            localStorage.setItem('dbInstalled', 'true');
            
            // Re-enable the button
            syncButton.disabled = false;
            syncButton.innerHTML = '<i class="fas fa-sync-alt"></i> Sync Database';
            
            // Update the status with timestamp
            setTimeout(() => {
                updateDatabaseStatus();
            }, 2000);
        })
        .catch(error => {
            console.error('Sync failed:', error);
            dbStatus.textContent = 'Synchronization Failed';
            dbStatus.classList.remove('bg-warning', 'bg-success', 'bg-info');
            dbStatus.classList.add('bg-danger');
            
            // Re-enable the button
            syncButton.disabled = false;
            syncButton.innerHTML = '<i class="fas fa-sync-alt"></i> Retry Sync';
        });
}

// Make synchronizeDatabase globally available (for inline onclick)
window.synchronizeDatabase = synchronizeDatabase;