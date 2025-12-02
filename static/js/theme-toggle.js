/**
 * Theme Toggle Functionality
 * Handles dark/light theme switching with localStorage persistence
 */

// Theme initialization on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeTheme();
    createThemeToggleButton();
});

/**
 * Initialize theme from localStorage or system preference
 */
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme) {
        setTheme(savedTheme);
    } else if (prefersDark) {
        setTheme('dark');
    } else {
        setTheme('light');
    }
}

/**
 * Create and insert theme toggle button
 */
function createThemeToggleButton() {
    // Check if button already exists
    if (document.getElementById('theme-toggle')) {
        return;
    }
    
    const button = document.createElement('button');
    button.id = 'theme-toggle';
    button.className = 'theme-toggle';
    button.setAttribute('aria-label', 'Toggle theme');
    button.setAttribute('title', 'Toggle dark/light theme');
    
    // Set initial icon
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    button.innerHTML = currentTheme === 'dark' 
        ? '<i class="bi bi-sun-fill"></i>' 
        : '<i class="bi bi-moon-stars-fill"></i>';
    
    // Add click event listener
    button.addEventListener('click', toggleTheme);
    
    // Add to body
    document.body.appendChild(button);
}

/**
 * Toggle between dark and light themes
 */
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    setTheme(newTheme);
    
    // Add animation effect
    const button = document.getElementById('theme-toggle');
    button.style.transform = 'scale(0.9) rotate(360deg)';
    setTimeout(() => {
        button.style.transform = 'scale(1) rotate(0deg)';
    }, 300);
}

/**
 * Set theme and update UI
 * @param {string} theme - 'dark' or 'light'
 */
function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    
    // Update button icon
    const button = document.getElementById('theme-toggle');
    if (button) {
        button.innerHTML = theme === 'dark' 
            ? '<i class="bi bi-sun-fill"></i>' 
            : '<i class="bi bi-moon-stars-fill"></i>';
    }
    
    // Update Bootstrap components that need special handling
    updateBootstrapComponents(theme);
    
    // Dispatch custom event for other scripts
    window.dispatchEvent(new CustomEvent('themechange', { detail: { theme } }));
}

/**
 * Update Bootstrap components for theme compatibility
 * @param {string} theme - 'dark' or 'light'
 */
function updateBootstrapComponents(theme) {
    // Update modals
    const modals = document.querySelectorAll('.modal-content');
    modals.forEach(modal => {
        if (theme === 'dark') {
            modal.classList.add('bg-dark', 'text-light');
        } else {
            modal.classList.remove('bg-dark', 'text-light');
        }
    });
    
    // Update badges that shouldn't change
    const badges = document.querySelectorAll('.badge');
    badges.forEach(badge => {
        // Preserve specific badge colors
        if (badge.classList.contains('bg-success') || 
            badge.classList.contains('bg-danger') || 
            badge.classList.contains('bg-warning') ||
            badge.classList.contains('bg-info') ||
            badge.classList.contains('bg-primary')) {
            // Keep their colors
        }
    });
}

/**
 * Listen for system theme changes
 */
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    // Only auto-switch if user hasn't manually set preference
    if (!localStorage.getItem('theme')) {
        setTheme(e.matches ? 'dark' : 'light');
    }
});

/**
 * Keyboard shortcut: Ctrl/Cmd + Shift + D to toggle theme
 */
document.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
        e.preventDefault();
        toggleTheme();
    }
});

// Export functions for potential use in other scripts
window.themeToggle = {
    setTheme,
    toggleTheme,
    getCurrentTheme: () => document.documentElement.getAttribute('data-theme') || 'light'
};
