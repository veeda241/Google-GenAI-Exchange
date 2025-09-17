document.addEventListener('DOMContentLoaded', () => {
    const enterButton = document.getElementById('enter-button');
    const themeToggle = document.getElementById('theme-toggle');
    const secretCodeInput = document.getElementById('secret-code');
    const gatekeeper = document.getElementById('gatekeeper');
    const exclusiveContent = document.getElementById('exclusive-content');
    const errorMessage = document.getElementById('error-message');

    // This is your secret password. Change it to whatever you like!
    const SECRET_PASSWORD = 'gemini';

    // --- Theme Toggling Logic ---
    const htmlElement = document.documentElement;

    const setTheme = (theme) => {
        htmlElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        if (themeToggle) {
            themeToggle.textContent = theme === 'light' ? '🌙' : '☀️';
        }
    };

    const initTheme = () => {
        const savedTheme = localStorage.getItem('theme');
        const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;

        if (savedTheme) {
            setTheme(savedTheme);
        } else if (prefersDark) {
            setTheme('dark');
        } else {
            setTheme('light');
        }
    };

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = htmlElement.getAttribute('data-theme');
            setTheme(currentTheme === 'light' ? 'dark' : 'light');
        });
    }

    initTheme();

    const checkPassword = () => {
        errorMessage.classList.add('hidden'); // Hide message on new attempt
        if (secretCodeInput.value === SECRET_PASSWORD) {
            // Correct password: Start the fade-out process
            gatekeeper.classList.add('fade-out');

            // After the animation, hide the gatekeeper and show the content
            gatekeeper.addEventListener('animationend', () => {
                gatekeeper.classList.add('hidden');
                exclusiveContent.classList.remove('hidden');
            }, { once: true }); // The listener removes itself after running once

        } else {
            // Incorrect password
            errorMessage.classList.remove('hidden');
            gatekeeper.classList.add('shake'); // Add shake animation
            secretCodeInput.value = ''; // Clear the input
            secretCodeInput.focus(); // Set focus back to input

            // Remove the shake class after the animation completes
            setTimeout(() => {
                gatekeeper.classList.remove('shake');
            }, 500); // Must match the animation duration in CSS
        }
    };

    // Listen for click on the enter button
    enterButton.addEventListener('click', checkPassword);

    // Also listen for 'Enter' key press in the input field
    secretCodeInput.addEventListener('keyup', (event) => {
        if (event.key === 'Enter') {
            checkPassword();
        }
    });
});