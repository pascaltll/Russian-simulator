// static/app.js
/**
 * Main application logic for the Language Simulator.
 * Handles UI interactions, API calls, and data rendering.
 */
document.addEventListener('DOMContentLoaded', () => {

    // --- UI Elements - General ---
    const appContainer = document.getElementById('appContainer');
    const logoutButton = document.getElementById('logoutButton');
    const loggedInUsernameSpan = document.getElementById('loggedInUsername');

    // --- UI Elements - Audio Tools Section ---
    const startButton = document.getElementById('startButton');
    const stopButton = document.getElementById('stopButton');
    const transcribeButton = document.getElementById('transcribeButton');
    const recordingStatus = document.getElementById('recordingStatus');
    const transcriptionResult = document.getElementById('transcriptionResult');
    const audioUploadInput = document.getElementById('audioUploadInput');
    const uploadAndTranscribeButton = document.getElementById('uploadAndTranscribeButton');
    const uploadStatus = document.getElementById('uploadStatus');
    const uploadTranscriptionResult = document.getElementById('uploadTranscriptionResult');

    // --- UI Elements - My Transcriptions Section ---
    const transcriptionList = document.getElementById('transcriptionList');
    const loadAllTranscriptionsButton = document.getElementById('loadAllTranscriptionsButton');

    // --- UI Elements - Auth Section ---
    const authContainer = document.getElementById('authContainer');
    const showLoginButton = document.getElementById('showLoginButton');
    const showRegisterButton = document.getElementById('showRegisterButton');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const loginUsernameInput = document.getElementById('loginUsername');
    const loginPasswordInput = document.getElementById('loginPassword');
    const registerUsernameInput = document.getElementById('registerUsername');
    const registerEmailInput = document.getElementById('registerEmail');
    const registerPasswordInput = document.getElementById('registerPassword');
    const loginMessage = document.getElementById('loginMessage');
    const registerMessage = document.getElementById('registerMessage');

    // --- UI Elements - Grammar Correction Section ---
    const correctGrammarButton = document.getElementById('correctGrammarButton');
    const transcriptionLanguageSelect = document.getElementById('transcriptionLanguage');
    const originalGrammarTextSpan = document.getElementById('originalGrammarText');
    const correctedGrammarTextSpan = document.getElementById('correctedGrammarText');
    const grammarExplanationSpan = document.getElementById('grammarExplanation');
    const grammarErrorsDetailsDiv = document.getElementById('grammarErrorsDetails');
    const grammarCorrectionStatus = document.getElementById('grammarCorrectionStatus');
    const grammarTextInput = document.getElementById('grammarTextInput');

    // --- UI Elements - Vocabulary Section ---
    const suggestDetailsButton = document.getElementById('suggestDetailsButton');
    const targetLanguageSelect = document.getElementById('targetLanguage');
    const russianWordInput = document.getElementById('russianWord');
    const translationInput = document = document.getElementById('translation');
    const exampleSentenceInput = document.getElementById('exampleSentence');
    const vocabForm = document.getElementById('vocabForm');
    const vocabList = document.getElementById('vocabList');
    const clearSuggestionButton = document.getElementById('clearSuggestionButton'); // New clear button

    // --- Main Navigation Tabs ---
    const navTabs = document.querySelectorAll('.nav-tab');
    const contentSections = document.querySelectorAll('.content-section');

    // --- Custom Modal Elements ---
    const customModal = document.getElementById('customModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalMessage = document.getElementById('modalMessage');
    const modalConfirmBtn = document.getElementById('modalConfirmBtn');
    const modalCancelBtn = document.getElementById('modalCancelBtn');

    // Store references to the modal button handlers to remove them later
    let currentConfirmHandler = null;
    let currentCancelHandler = null;


    let mediaRecorder;
    let audioChunks = [];

    // --- Custom Modal Function ---
    /**
     * Displays a custom modal dialog for user confirmation or information.
     * @param {string} title - The title of the modal.
     * @param {string} message - The message content of the modal.
     * @param {boolean} isConfirm - If true, the modal will have a confirm/cancel option.
     * @returns {Promise<boolean>} Resolves to true if confirmed, false if cancelled.
     */
    function showCustomModal(title, message, isConfirm = false) {
        console.log(`[Modal] Showing modal: "${title}" - "${message}" (Confirmation: ${isConfirm})`); // DEBUG
        modalTitle.textContent = title;
        modalMessage.textContent = message;
        customModal.classList.remove('hidden');

        // Remove previous listeners to prevent duplicates
        if (currentConfirmHandler) {
            modalConfirmBtn.removeEventListener('click', currentConfirmHandler);
        }
        if (currentCancelHandler) {
            modalCancelBtn.removeEventListener('click', currentCancelHandler);
        }

        return new Promise(resolve => {
            modalConfirmBtn.textContent = isConfirm ? 'Confirm' : 'OK';
            modalCancelBtn.classList.toggle('hidden', !isConfirm);

            currentConfirmHandler = () => {
                console.log(`[Modal] Confirmed: "${title}"`); // DEBUG
                customModal.classList.add('hidden');
                resolve(true);
            };
            modalConfirmBtn.addEventListener('click', currentConfirmHandler);

            if (isConfirm) {
                currentCancelHandler = () => {
                    console.log(`[Modal] Cancelled: "${title}"`); // DEBUG
                    customModal.classList.add('hidden');
                    resolve(false);
                };
                modalCancelBtn.addEventListener('click', currentCancelHandler);
            }
        });
    }

    // --- Helper for authenticated API calls ---
    /**
     * Fetches data from a given URL with an authentication token.
     * Handles token expiration and redirects to login if unauthorized.
     * @param {string} url - The URL to fetch.
     * @param {Object} options - Fetch options (method, headers, body, etc.).
     * @returns {Promise<Response>} The fetch response.
     * @throws {Error} If the response status is 401 or 403, indicating unauthorized access.
     */
    async function fetchWithAuth(url, options = {}) {
        console.log(`[API] Requesting: ${url} (Method: ${options.method || 'GET'})`); // DEBUG
        const token = localStorage.getItem('token');
        const headers = {
            ...options.headers,
            'Authorization': token ? `Bearer ${token}` : ''
        };

        const response = await fetch(url, { ...options, headers });
        if (response.status === 401 || response.status === 403) {
            console.warn('[API] Unauthorized access, redirecting to login.'); // DEBUG
            await showCustomModal('Session Expired', 'Your session has expired. Please log in again.');
            localStorage.removeItem('token');
            localStorage.removeItem('username');
            checkAuthenticationAndRenderUI();
            throw new Error('Unauthorized'); // Stop further processing
        }
        console.log(`[API] Response from ${url}: HTTP ${response.status}`); // DEBUG
        return response;
    }

    // --- Authentication & UI State Management ---

    /**
     * Shows the specified authentication section (login or register) and hides others.
     * @param {string} sectionId - The ID of the section to show ('loginForm' or 'registerForm').
     */
    function showAuthSection(sectionId) {
        document.querySelectorAll('.auth-section').forEach(section => {
            section.style.display = 'none';
        });
        document.querySelectorAll('.btn-tab').forEach(tab => {
            tab.classList.remove('active');
        });

        if (sectionId === 'loginForm') {
            document.getElementById('loginForm').style.display = 'block';
            document.getElementById('showLoginButton').classList.add('active');
        } else if (sectionId === 'registerForm') {
            document.getElementById('registerForm').style.display = 'block';
            document.getElementById('showRegisterButton').classList.add('active');
        }
    }

    /**
     * Shows the specified main application section and hides others.
     * Activates the corresponding navigation tab.
     * @param {string} sectionId - The ID of the content section to show.
     */
    function showAppSection(sectionId) {
        navTabs.forEach(tab => tab.classList.remove('active'));
        contentSections.forEach(section => {
            section.classList.remove('active');
            section.classList.add('hidden');
        });

        const activeTab = document.querySelector(`.nav-tab[data-target="${sectionId}"]`);
        if (activeTab) {
            activeTab.classList.add('active');
        }

        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.classList.remove('hidden');
            targetSection.classList.add('active');
        }
    }

    /**
     * Checks if a user is authenticated and renders the appropriate UI (auth or app).
     * Loads initial data for the default app section if authenticated.
     */
    async function checkAuthenticationAndRenderUI() {
        const token = localStorage.getItem('token');
        const username = localStorage.getItem('username');

        if (token) {
            authContainer.style.display = 'none';
            appContainer.style.display = 'flex';
            if (username) {
                loggedInUsernameSpan.textContent = `Welcome, ${username}!`;
            }

            showAppSection('audioSection'); // Show audio tools by default
            console.log('[Auth] User authenticated, loading initial data...'); // DEBUG
            await loadTranscriptions(false); // Ensure transcriptions are loaded
            await loadVocabulary(); // Ensure vocabulary is loaded
        } else {
            authContainer.style.display = 'flex';
            appContainer.style.display = 'none';
            showAuthSection('loginForm');
            console.log('[Auth] User not authenticated, showing login screen.'); // DEBUG
        }
    }

    // --- Authentication Event Listeners ---

    // Login Form Submission
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = loginUsernameInput.value;
        const password = loginPasswordInput.value;
        loginMessage.textContent = '';
        console.log('[Auth] Attempting to log in...'); // DEBUG

        try {
            const response = await fetch('/api/auth/token', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
            });
            const result = await response.json();
            if (response.ok) {
                localStorage.setItem('token', result.access_token);
                localStorage.setItem('username', username);
                loginMessage.textContent = 'Login successful!';
                loginMessage.classList.remove('error');
                loginMessage.classList.add('success');
                checkAuthenticationAndRenderUI();
                console.log('[Auth] Login successful.'); // DEBUG
            } else {
                loginMessage.textContent = `Login failed: ${result.detail || 'Invalid credentials. Please try again.'}`;
                loginMessage.classList.remove('success');
                loginMessage.classList.add('error');
                console.error('[Auth] Login failed:', result.detail); // DEBUG
            }
        } catch (error) {
            console.error('[Auth] Network error during login:', error); // DEBUG
            loginMessage.textContent = 'Network error. Could not log in.';
            loginMessage.classList.remove('success');
            loginMessage.classList.add('error');
        }
    });

    // Register Form Submission
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = registerUsernameInput.value;
        const email = registerEmailInput.value.trim() === '' ? null : registerEmailInput.value.trim();
        const password = registerPasswordInput.value;
        registerMessage.textContent = '';
        console.log('[Auth] Attempting to register user...'); // DEBUG

        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });
            const result = await response.json();
            if (response.ok) {
                showCustomModal('Success', 'User registered successfully! Please log in.').then(() => {
                    registerMessage.textContent = ''; // Clear message after modal
                    registerForm.reset();
                    showAuthSection('loginForm');
                });
                console.log('[Auth] Registration successful.'); // DEBUG
            } else {
                const errorMessage = result.detail ?
                                        (Array.isArray(result.detail) ? result.detail.map(d => d.msg).join(', ') : result.detail) :
                                        'Please try again.';
                registerMessage.textContent = `Registration failed: ${errorMessage}`;
                registerMessage.classList.remove('success');
                registerMessage.classList.add('error');
                console.error('[Auth] Registration failed:', result.detail); // DEBUG
            }
        } catch (error) {
            console.error('[Auth] Network error during registration:', error); // DEBUG
            registerMessage.textContent = 'Network error. Could not register user.';
            registerMessage.classList.remove('success');
            registerMessage.classList.add('error');
        }
    });

    // Logout Functionality
    logoutButton.addEventListener('click', async () => {
        console.log('[Logout] Logout button clicked.'); // DEBUG
        const confirmed = await showCustomModal('Confirm Logout', 'Are you sure you want to log out?', true);
        if (confirmed) {
            console.log('[Logout] Logout confirmed by user.'); // DEBUG
            localStorage.removeItem('token');
            localStorage.removeItem('username');
            console.log('[Logout] Token and username removed from localStorage.'); // DEBUG
            
            // Verify localStorage is indeed empty
            console.log('Current token in localStorage:', localStorage.getItem('token')); // DEBUG
            console.log('Current username in localStorage:', localStorage.getItem('username')); // DEBUG

            checkAuthenticationAndRenderUI();
            
            // Clear UI elements explicitly for a clean logout state
            transcriptionResult.innerHTML = '';
            uploadTranscriptionResult.innerHTML = '';
            transcriptionList.innerHTML = '<li>No transcriptions yet.</li>';
            vocabList.innerHTML = '<li>No vocabulary items yet.</li>';
            
            showCustomModal('Logged Out', 'You have been logged out successfully.');
            console.log('[Logout] Session fully closed.'); // DEBUG
        } else {
            console.log('[Logout] Logout cancelled.'); // DEBUG
        }
    });

    // Switch between Login and Register forms
    showLoginButton.addEventListener('click', () => {
        showAuthSection('loginForm');
        console.log('[UI] Switching to login form.'); // DEBUG
    });
    showRegisterButton.addEventListener('click', () => {
        showAuthSection('registerForm');
        console.log('[UI] Switching to registration form.'); // DEBUG
    });

    // --- Main Navigation Tab Logic ---
    navTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetId = tab.dataset.target;
            showAppSection(targetId);
            console.log(`[UI] Switching to section: ${targetId}`); // DEBUG
        });
    });

    // --- Audio Transcription Helper ---
    /**
     * Handles the response from an audio transcription API call and updates the UI.
     * @param {Response} response - The fetch API response.
     * @param {HTMLElement} resultElement - The HTML element to display the transcription result.
     * @param {HTMLElement} [statusElement=null] - Optional HTML element to display status messages.
     */
    async function handleTranscriptionResponse(response, resultElement, statusElement = null) {
        const result = await response.json();
        if (response.ok) {
            console.log('[Audio] Transcription successful, reloading transcriptions...'); // DEBUG
            const detectedLanguage = result.language ? result.language.toUpperCase() : 'Unknown';
            resultElement.innerHTML = `
                <p><strong>Transcription Result</strong></p>
                <p><strong>Detected Language:</strong> ${detectedLanguage}</p>
                <p><code>${result.original_transcript}</code></p>
            `;
            if (statusElement) {
                statusElement.textContent = 'Transcription successful!';
                statusElement.classList.remove('error');
                statusElement.classList.add('success');
            }
            await loadTranscriptions(false); // Ensure this function completes
            console.log('[Audio] Transcriptions reloaded after new transcription.'); // DEBUG
        } else {
            console.error("[Audio] Transcription failed (HTTP status:", response.status, "):", result.detail); // DEBUG
            resultElement.innerHTML = `<p style="color: red;">Error: ${result.detail || 'Unknown error'}</p>`;
            if (statusElement) {
                statusElement.textContent = 'Transcription failed.';
                statusElement.classList.remove('success');
                statusElement.classList.add('error');
            }
        }
    }


    // --- Recording Logic ---

    startButton.addEventListener('click', async () => {
        console.log('[Audio] Starting recording...'); // DEBUG
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            startButton.disabled = true;
            stopButton.disabled = false;
            transcribeButton.style.display = 'none';
            recordingStatus.textContent = 'Recording...';
            recordingStatus.classList.add('recording-indicator');
            transcriptionResult.innerHTML = '';

            mediaRecorder.ondataavailable = e => audioChunks.push(e.data);

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                const formData = new FormData();
                formData.append('audio_file', audioBlob, 'recording.webm');
                console.log('[Audio] Recording stopped. Audio file ready for transcription.'); // DEBUG

                recordingStatus.textContent = 'Recording stopped.';
                recordingStatus.classList.remove('recording-indicator');
                startButton.disabled = false;
                stopButton.disabled = true;
                transcribeButton.style.display = 'inline-block';

                // Assign the transcribe function to the button click
                transcribeButton.onclick = async () => {
                    transcriptionResult.innerHTML = '<p>Transcribing...</p>';
                    console.log('[Audio] Starting transcription of recorded audio...'); // DEBUG
                    try {
                        const response = await fetchWithAuth('/api/audio/transcribe-audio', {
                            method: 'POST',
                            body: formData
                        });
                        await handleTranscriptionResponse(response, transcriptionResult);
                    } catch (error) {
                        transcriptionResult.innerHTML = `<p style="color: red;">Network Error: ${error.message}</p>`;
                        console.error('[Audio] Fetch error during transcription:', error); // DEBUG
                    } finally {
                        transcribeButton.style.display = 'none';
                    }
                };
            };
            mediaRecorder.start();
        } catch (error) {
            console.error('[Audio] Error accessing microphone:', error); // DEBUG
            recordingStatus.textContent = 'Error: Microphone access denied.';
            showCustomModal('Microphone Access Error', 'Error accessing microphone. Please allow microphone access in your browser settings.');
        }
    });

    stopButton.addEventListener('click', () => {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            console.log('[Audio] Stop recording button clicked.'); // DEBUG
        }
    });

    // --- Audio Upload Logic ---
    audioUploadInput.addEventListener('change', () => {
        if (audioUploadInput.files.length > 0) {
            uploadAndTranscribeButton.disabled = false;
            uploadStatus.textContent = `File selected: ${audioUploadInput.files[0].name}`;
            uploadTranscriptionResult.innerHTML = '';
            console.log(`[Audio] File selected for upload: ${audioUploadInput.files[0].name}`); // DEBUG
        } else {
            uploadAndTranscribeButton.disabled = true;
            uploadStatus.textContent = 'No file selected.';
            console.log('[Audio] No file selected for upload.'); // DEBUG
        }
    });

    uploadAndTranscribeButton.addEventListener('click', async () => {
        const file = audioUploadInput.files[0];
        if (!file) {
            uploadStatus.textContent = 'Please select an audio file first.';
            uploadStatus.classList.add('error');
            return;
        }

        uploadStatus.textContent = 'Uploading and transcribing...';
        uploadStatus.classList.remove('error', 'success');
        uploadAndTranscribeButton.disabled = true;
        uploadTranscriptionResult.innerHTML = '';
        console.log('[Audio] Starting audio upload and transcription.'); // DEBUG

        const formData = new FormData();
        formData.append('audio_file', file);

        try {
            const response = await fetchWithAuth('/api/audio/upload-and-transcribe', {
                method: 'POST',
                body: formData
            });
            await handleTranscriptionResponse(response, uploadTranscriptionResult, uploadStatus);
        } catch (error) {
            uploadTranscriptionResult.innerHTML = `<p style="color: red;">Network Error: ${error.message}</p>`;
            uploadStatus.textContent = 'Network error during upload.';
            uploadStatus.classList.remove('success');
            uploadStatus.classList.add('error');
            console.error('[Audio] Fetch error during upload transcription:', error); // DEBUG
        } finally {
            uploadAndTranscribeButton.disabled = false;
            audioUploadInput.value = null; // Clear file input
            console.log('[Audio] Audio upload and transcription finished.'); // DEBUG
        }
    });

    /**
     * Displays a status message within the grammar correction section.
     * @param {string} message - The message to display.
     * @param {boolean} isError - True if the message indicates an error, false for success/info.
     */
    function showGrammarStatus(message, isError = false) {
        if (grammarCorrectionStatus) {
            grammarCorrectionStatus.textContent = message;
            grammarCorrectionStatus.classList.remove('success', 'error', 'hidden');
            if (isError) {
                grammarCorrectionStatus.classList.add('error');
            } else {
                grammarCorrectionStatus.classList.add('success');
            }
        }
    }

    /**
     * Clears all displayed grammar correction results and status messages.
     */
    function clearGrammarResults() {
        if (originalGrammarTextSpan) originalGrammarTextSpan.textContent = '';
        if (correctedGrammarTextSpan) correctedGrammarTextSpan.textContent = '';
        if (grammarExplanationSpan) grammarExplanationSpan.textContent = '';
        if (grammarErrorsDetailsDiv) grammarErrorsDetailsDiv.innerHTML = '';
        if (grammarCorrectionStatus) grammarCorrectionStatus.classList.add('hidden');
    }

    // --- Grammar Correction Logic ---
    if (correctGrammarButton) {
        correctGrammarButton.addEventListener('click', async () => {
            clearGrammarResults();
            showGrammarStatus('Checking grammar...', false);
            console.log('[Grammar] Starting grammar check...'); // DEBUG

            let textToCorrect = grammarTextInput.value.trim();
            console.log(`[Grammar] Initial text in grammarTextInput: "${textToCorrect}"`); // DEBUG

            if (!textToCorrect) {
                // If input field is empty, try to get from last transcription result
                const lastTranscriptionCodeElement = transcriptionResult.querySelector('code');
                if (lastTranscriptionCodeElement) {
                    textToCorrect = lastTranscriptionCodeElement.textContent.trim();
                    console.log(`[Grammar] Text taken from transcriptionResult: "${textToCorrect}"`); // DEBUG
                } else {
                    // If no transcription in audioSection, try from the first item in the transcription list
                    const firstTranscriptionInList = transcriptionList.querySelector('.transcription-item code');
                    if (firstTranscriptionInList) {
                        textToCorrect = firstTranscriptionInList.textContent.trim();
                        console.log(`[Grammar] Text taken from the first transcription in the list: "${textToCorrect}"`); // DEBUG
                    } else {
                        console.log('[Grammar] No text found in transcriptionResult or in the transcription list.'); // DEBUG
                    }
                }
            }

            const language = transcriptionLanguageSelect.value;
            console.log(`[Grammar] Selected language for check: "${language}"`); // DEBUG

            if (!textToCorrect) {
                showGrammarStatus('No text found to check grammar. Please type text, record, or upload audio first.', true);
                console.warn('[Grammar] No text to check grammar. Stopping operation.'); // DEBUG
                return;
            }

            console.log(`[Grammar] Sending text for correction: "${textToCorrect}" with language: "${language}"`); // DEBUG

            try {
                const response = await fetchWithAuth('/api/grammar/check', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ text: textToCorrect, language: language })
                });

                if (response.ok) {
                    const result = await response.json();
                    showGrammarStatus('Grammar check completed!', false);
                    console.log('[Grammar] Grammar check successful. API Result:', result); // DEBUG

                    originalGrammarTextSpan.textContent = result.original_text || 'N/A';
                    correctedGrammarTextSpan.textContent = result.corrected_text || 'N/A';
                    grammarExplanationSpan.textContent = result.explanation || 'No specific explanation provided.';

                    grammarErrorsDetailsDiv.innerHTML = '';
                    if (result.errors && result.errors.length > 0) {
                        console.log('[Grammar] Errors detected:', result.errors); // DEBUG
                        const errorList = document.createElement('ul');
                        result.errors.forEach(error => {
                            const errorLi = document.createElement('li'); // Changed to li for list (Pylint equivalent: C0103)
                            errorLi.innerHTML = `<strong>Error:</strong> ${error.message || 'N/A'}<br>`;
                            errorLi.innerHTML += `<strong>Problematic text:</strong> "${error.bad_word || 'N/A'}"<br>`;
                            if (error.suggestions && error.suggestions.length > 0) {
                                errorLi.innerHTML += `<strong>Suggestions:</strong> ${error.suggestions.join(', ')}<br>`;
                            }
                            errorList.appendChild(errorLi);
                        });
                        grammarErrorsDetailsDiv.appendChild(errorList);
                    } else {
                        grammarErrorsDetailsDiv.textContent = "No specific errors detected or they are minor.";
                        console.log('[Grammar] No specific errors detected.'); // DEBUG
                    }

                } else {
                    const errorResult = await response.json();
                    showGrammarStatus(`Error checking grammar: ${errorResult.detail || 'Could not check grammar.'}`, true);
                    originalGrammarTextSpan.textContent = '';
                    correctedGrammarTextSpan.textContent = '';
                    grammarExplanationSpan.textContent = '';
                    grammarErrorsDetailsDiv.innerHTML = 'Failed to load grammar details.';
                    console.error('[Grammar] API error checking grammar. HTTP Status:', response.status, 'Details:', errorResult); // DEBUG
                }
            } catch (error) {
                console.error('[Grammar] Network or processing error during grammar check:', error); // DEBUG
                showGrammarStatus('Network error. Could not check grammar.', true);
                originalGrammarTextSpan.textContent = '';
                correctedGrammarTextSpan.textContent = '';
                grammarExplanationSpan.innerHTML = '';
                grammarErrorsDetailsDiv.innerHTML = 'Failed to load grammar details.';
            }
        });
    }

    // --- Vocabulary Form ---

    // Event Listener for the Suggest Translation & Comment button
    if (suggestDetailsButton) {
        suggestDetailsButton.addEventListener('click', async () => {
            const russianWord = russianWordInput.value.trim();
            const targetLanguage = targetLanguageSelect.value