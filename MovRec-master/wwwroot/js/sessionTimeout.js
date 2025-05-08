// Session timeout handling
document.addEventListener('DOMContentLoaded', function () {
    let sessionTimeout;
    const timeoutMinutes = 45; // Match this with your session timeout in Program.cs
    let isSessionExpired = false;

    // Create modal HTML
    const modalHTML = `
        <div class="session-modal-overlay">
            <div class="session-modal">
                <div class="session-modal-title">Session Timeout</div>
                <div class="session-modal-message"></div>
                <div class="session-modal-buttons"></div>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHTML);

    const modalOverlay = document.querySelector('.session-modal-overlay');
    const modalMessage = document.querySelector('.session-modal-message');
    const modalButtons = document.querySelector('.session-modal-buttons');

    function showModal(message, buttons) {
        modalMessage.textContent = message;
        modalButtons.innerHTML = '';

        buttons.forEach(button => {
            const buttonElement = document.createElement('button');
            buttonElement.className = `session-modal-button ${button.class || 'secondary'}`;
            buttonElement.textContent = button.text;
            buttonElement.onclick = button.onClick;
            modalButtons.appendChild(buttonElement);
        });

        modalOverlay.style.display = 'flex';
    }

    function hideModal() {
        modalOverlay.style.display = 'none';
    }

    function resetSessionTimer() {
        clearTimeout(sessionTimeout);

        // Set session timeout (45 minutes)
        sessionTimeout = setTimeout(() => {
            isSessionExpired = true;
            showModal('Your session has expired. Please log in again.', [
                {
                    text: 'OK',
                    class: 'primary',
                    onClick: () => {
                        hideModal();
                        window.location.href = '/Account/Login';
                    }
                }
            ]);
        }, timeoutMinutes * 60 * 1000);
    }

    function refreshSession() {
        fetch('/Account/RefreshSession', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin'
        })
            .then(response => {
                if (response.ok) {
                    resetSessionTimer();
                } else {
                    isSessionExpired = true;
                    showModal('Your session has expired. Please log in again.', [
                        {
                            text: 'OK',
                            class: 'primary',
                            onClick: () => {
                                hideModal();
                                window.location.href = '/Home/Index';
                            }
                        }
                    ]);
                }
            })
            .catch((error) => {
                isSessionExpired = true;
                showModal('Your session has expired. Please log in again.', [
                    {
                        text: 'OK',
                        class: 'primary',
                        onClick: () => {
                            hideModal();
                            window.location.href = '/Account/Login';
                        }
                    }
                ]);
            });
    }

    function handleUserInteraction() {
        if (isSessionExpired) {
            showModal('Your session has expired. Please log in again.', [
                {
                    text: 'OK',
                    class: 'primary',
                    onClick: () => {
                        hideModal();
                        window.location.href = '/Account/Login';
                    }
                }
            ]);
        } else {
            refreshSession();
        }
    }

    // Add event listeners for user interaction
    ['click', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
        document.addEventListener(event, handleUserInteraction);
    });

    // Initial session timer setup
    resetSessionTimer();
}); 