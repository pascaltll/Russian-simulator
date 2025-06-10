// static/app.js
document.addEventListener('DOMContentLoaded', () => {

    // UI Elements - Main App
    const appContainer = document.getElementById('appContainer');
    const startButton = document.getElementById('startButton');
    const stopButton = document.getElementById('stopButton');
    const transcribeButton = document.getElementById('transcribeButton');
    const recordingStatus = document.getElementById('recordingStatus');
    const transcriptionResult = document.getElementById('transcriptionResult');
    const transcriptionList = document.getElementById('transcriptionList');
    const vocabForm = document.getElementById('vocabForm');
    const vocabList = document.getElementById('vocabList');
    const logoutButton = document.getElementById('logoutButton');
    const loggedInUsernameSpan = document.getElementById('loggedInUsername');

    // Botón para cargar todos los audios
    const loadAllTranscriptionsButton = document.getElementById('loadAllTranscriptionsButton');

    // UI Elements - Upload Audio
    const audioUploadInput = document.getElementById('audioUploadInput');
    const uploadAndTranscribeButton = document.getElementById('uploadAndTranscribeButton');
    const uploadStatus = document.getElementById('uploadStatus');
    const uploadTranscriptionResult = document.getElementById('uploadTranscriptionResult');

    // UI Elements - Auth Section
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

    // UI Elements for Grammar Correction
    const correctGrammarButton = document.getElementById('correctGrammarButton');
    const transcriptionLanguageSelect = document.getElementById('transcriptionLanguage'); 
    const originalGrammarTextSpan = document.getElementById('originalGrammarText');
    const correctedGrammarTextSpan = document.getElementById('correctedGrammarText');
    const grammarExplanationSpan = document.getElementById('grammarExplanation');
    const grammarErrorsDetailsDiv = document.getElementById('grammarErrorsDetails');
    const grammarCorrectionStatus = document.getElementById('grammarCorrectionStatus'); // New status element
    const grammarSection = document.getElementById('grammarSection'); // The section that displays grammar results
    const grammarTextInput = document.getElementById('grammarTextInput'); // NUEVO: Elemento para la entrada de texto



    // UI Elements for Vocabulary 
    const suggestDetailsButton = document.getElementById('suggestDetailsButton');
    const targetLanguageSelect = document.getElementById('targetLanguage');
    const russianWordInput = document.getElementById('russianWord');
    const translationInput = document.getElementById('translation');
    const exampleSentenceInput = document.getElementById('exampleSentence');

    // Main Navigation Tabs
    const navTabs = document.querySelectorAll('.nav-tab');
    const contentSections = document.querySelectorAll('.content-section');

    // Custom Modal Elements
    const customModal = document.getElementById('customModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalMessage = document.getElementById('modalMessage');
    const modalConfirmBtn = document.getElementById('modalConfirmBtn');
    const modalCancelBtn = document.getElementById('modalCancelBtn');

    let mediaRecorder;
    let audioChunks = [];

    // --- Custom Modal Function ---
    /**
     * Displays a custom modal dialog.
     * @param {string} title - The title of the modal.
     * @param {string} message - The message content of the modal.
     * @param {boolean} isConfirm - If true, the modal will have a confirm/cancel option.
     * @returns {Promise<boolean>} Resolves to true if confirmed, false if cancelled.
     */
    function showCustomModal(title, message, isConfirm = false) {
        modalTitle.textContent = title;
        modalMessage.textContent = message;
        customModal.classList.remove('hidden');

        return new Promise(resolve => {
            modalConfirmBtn.textContent = isConfirm ? 'Confirm' : 'OK';
            modalCancelBtn.classList.toggle('hidden', !isConfirm); // Show/hide cancel button

            // Remove existing event listeners to prevent multiple bindings
            const oldConfirmHandler = modalConfirmBtn.onclick;
            const oldCancelHandler = modalCancelBtn.onclick;
            if (oldConfirmHandler) modalConfirmBtn.removeEventListener('click', oldConfirmHandler);
            if (oldCancelHandler) modalCancelBtn.removeEventListener('click', oldCancelHandler);


            const confirmHandler = () => {
                customModal.classList.add('hidden');
                resolve(true);
            };

            const cancelHandler = () => {
                customModal.classList.add('hidden');
                resolve(false);
            };

            modalConfirmBtn.addEventListener('click', confirmHandler, { once: true }); // Use { once: true } for auto-cleanup
            modalCancelBtn.addEventListener('click', cancelHandler, { once: true });
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
        const token = localStorage.getItem('token');
        const headers = {
            ...options.headers,
            'Authorization': token ? `Bearer ${token}` : ''
        };

        const response = await fetch(url, { ...options, headers });
        if (response.status === 401 || response.status === 403) {
            // Token expired or unauthorized, redirect to login
            showCustomModal('Session Expired', 'Your session has expired. Please log in again.').then(() => {
                localStorage.removeItem('token');
                localStorage.removeItem('username');
                checkAuthenticationAndRenderUI();
            });
            throw new Error('Unauthorized'); // Stop further processing
        }
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
        // Deactivate all navigation tabs
        navTabs.forEach(tab => tab.classList.remove('active'));
        // Hide all content sections
        contentSections.forEach(section => section.classList.remove('active'));
        contentSections.forEach(section => section.classList.add('hidden'));

        // Activate the clicked tab
        const activeTab = document.querySelector(`.nav-tab[data-target="${sectionId}"]`);
        if (activeTab) {
            activeTab.classList.add('active');
        }

        // Show the target content section
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
        console.log("checkAuthenticationAndRenderUI called.");
        const token = localStorage.getItem('token');
        const username = localStorage.getItem('username'); // Retrieve username
        console.log("Token from localStorage:", token ? "Token found (length: " + token.length + ")" : "No token found.");

        if (token) {
            console.log("Token found. Hiding authContainer, showing appContainer.");
            authContainer.style.display = 'none';
            appContainer.style.display = 'flex'; // Use flex for app-container
            if (username) {
                loggedInUsernameSpan.textContent = `Welcome, ${username}!`; // Display username
            }

            // Load initial data for the first visible section
            showAppSection('audioSection'); // Show audio tools by default
            await loadTranscriptions(false);
            await loadVocabulary();
        } else {
            console.log("No token found. Showing authContainer, hiding appContainer.");
            authContainer.style.display = 'flex'; // Use flex for auth-container
            appContainer.style.display = 'none';
            showAuthSection('loginForm');
        }
    }

    // Login Form Submission
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = loginUsernameInput.value;
        const password = loginPasswordInput.value;
        loginMessage.textContent = '';
        console.log("Attempting login for user:", username);

        try {
            const response = await fetch('/api/auth/token', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
            });
            const result = await response.json();
            if (response.ok) {
                console.log("Login successful! Received token (first 20 chars):", result.access_token ? result.access_token.substring(0, 20) + "..." : "No token in response.");
                localStorage.setItem('token', result.access_token);
                localStorage.setItem('username', username); // Store username
                loginMessage.textContent = 'Login successful!';
                loginMessage.classList.remove('error');
                loginMessage.classList.add('success');
                checkAuthenticationAndRenderUI();
            } else {
                console.error("Login failed (HTTP status:", response.status, "):", result.detail);
                loginMessage.textContent = `Login failed: ${result.detail || 'Invalid credentials. Please try again.'}`;
                loginMessage.classList.remove('success');
                loginMessage.classList.add('error');
            }
        } catch (error) {
            console.error('Network error during login:', error);
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
        console.log("Attempting registration for user:", username, "Email:", email);

        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });
            const result = await response.json();
            if (response.ok) {
                console.log("Registration successful for user:", username);
                registerMessage.textContent = 'User registered successfully! Please log in.';
                registerMessage.classList.remove('error');
                registerMessage.classList.add('success');
                showAuthSection('loginForm');
                registerForm.reset();
            } else {
                console.error("Registration failed (HTTP status:", response.status, "):", result.detail);
                const errorMessage = result.detail ?
                                        (Array.isArray(result.detail) ? result.detail.map(d => d.msg).join(', ') : result.detail) :
                                        'Please try again.';
                registerMessage.textContent = `Registration failed: ${errorMessage}`;
                registerMessage.classList.remove('success');
                registerMessage.classList.add('error');
            }
        } catch (error) {
            console.error('Network error during registration:', error);
            registerMessage.textContent = 'Network error. Could not register user.';
            registerMessage.classList.remove('success');
            registerMessage.classList.add('error');
        }
    });

    // Logout Functionality
    logoutButton.addEventListener('click', async () => {
        console.log("Logout button clicked.");
        const confirmed = await showCustomModal('Logout Confirmation', 'Are you sure you want to log out?', true);
        if (confirmed) {
            localStorage.removeItem('token');
            localStorage.removeItem('username'); // Clear username on logout
            checkAuthenticationAndRenderUI();
            transcriptionResult.innerHTML = '';
            uploadTranscriptionResult.innerHTML = '';
            transcriptionList.innerHTML = '<li>No transcriptions yet.</li>';
            vocabList.innerHTML = '<li>No vocabulary items yet.</li>';
            showCustomModal('Logged Out', 'You have been successfully logged out.');
        }
    });

    // Switch between Login and Register forms
    showLoginButton.addEventListener('click', () => {
        console.log("Show Login button clicked.");
        showAuthSection('loginForm');
    });
    showRegisterButton.addEventListener('click', () => {
        console.log("Show Register button clicked.");
        showAuthSection('registerForm');
    });

    // --- Main Navigation Tab Logic ---
    navTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetId = tab.dataset.target;
            showAppSection(targetId);
        });
    });

    // --- Recording Logic ---

    startButton.addEventListener('click', async () => {
        console.log("Start recording button clicked.");
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

                recordingStatus.textContent = 'Recording stopped.';
                recordingStatus.classList.remove('recording-indicator');
                startButton.disabled = false;
                stopButton.disabled = true;
                transcribeButton.style.display = 'inline-block';

                transcribeButton.onclick = async () => {
                    console.log("Transcribe recorded audio button clicked.");
                    transcriptionResult.innerHTML = '<p>Transcribing...</p>';
                    try {
                        const response = await fetchWithAuth('/api/audio/transcribe-audio', {
                            method: 'POST',
                            body: formData
                        });
                        const result = await response.json();
                        if (response.ok) {
                            const detectedLanguage = result.language ? result.language.toUpperCase() : 'Unknown';
                            transcriptionResult.innerHTML = `
                                <p><strong>Transcription Result</strong></p>
                                <p><strong>Detected Language:</strong> ${detectedLanguage}</p>
                                <p><code>${result.original_transcript}</code></p>
                            `;
                            loadTranscriptions(false);
                        } else {
                            console.error("Transcription failed (HTTP status:", response.status, "):", result.detail);
                            transcriptionResult.innerHTML = `<p style="color: red;">Error: ${result.detail || 'Unknown error'}</p>`;
                        }
                    } catch (error) {
                        transcriptionResult.innerHTML = `<p style="color: red;">Network Error: ${error.message}</p>`;
                        console.error('Fetch error during transcription:', error);
                    } finally {
                        transcribeButton.style.display = 'none';
                    }
                };
            };
            mediaRecorder.start();
        } catch (error) {
            console.error('Error accessing microphone:', error);
            recordingStatus.textContent = 'Error: Microphone access denied.';
            showCustomModal('Microphone Access Error', 'Error accessing microphone. Please allow microphone access in your browser settings.');
        }
    });

    stopButton.addEventListener('click', () => {
        console.log("Stop recording button clicked.");
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
        }
    });

    // --- Audio Upload Logic ---
    audioUploadInput.addEventListener('change', () => {
        console.log("Audio file selected for upload.");
        if (audioUploadInput.files.length > 0) {
            uploadAndTranscribeButton.disabled = false;
            uploadStatus.textContent = `File selected: ${audioUploadInput.files[0].name}`;
            uploadTranscriptionResult.innerHTML = '';
        } else {
            uploadAndTranscribeButton.disabled = true;
            uploadStatus.textContent = 'No file selected.';
        }
    });

    uploadAndTranscribeButton.addEventListener('click', async () => {
        const file = audioUploadInput.files[0];
        console.log("Upload and Transcribe button clicked.");
        if (!file) {
            uploadStatus.textContent = 'Please select an audio file first.';
            uploadStatus.classList.add('error');
            return;
        }

        uploadStatus.textContent = 'Uploading and transcribing...';
        uploadStatus.classList.remove('error', 'success');
        uploadAndTranscribeButton.disabled = true;
        uploadTranscriptionResult.innerHTML = '';

        const formData = new FormData();
        formData.append('audio_file', file);

        try {
            const response = await fetchWithAuth('/api/audio/upload-and-transcribe', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            if (response.ok) {
                const detectedLanguage = result.language ? result.language.toUpperCase() : 'Unknown';
                uploadTranscriptionResult.innerHTML = `
                    <p><strong>Transcription Result (Upload)</strong></p>
                    <p><strong>Detected Language:</strong> ${detectedLanguage}</p>
                    <p><code>${result.original_transcript}</code></p>
                `;
                uploadStatus.textContent = 'Transcription successful!';
                uploadStatus.classList.remove('error');
                uploadStatus.classList.add('success');
                loadTranscriptions(false);
            } else {
                console.error("Upload transcription failed (HTTP status:", response.status, "):", result.detail);
                uploadTranscriptionResult.innerHTML = `<p style="color: red;">Error: ${result.detail || 'Unknown error'}</p>`;
                uploadStatus.textContent = 'Transcription failed.';
                uploadStatus.classList.remove('success');
                uploadStatus.classList.add('error');
            }
        } catch (error) {
            uploadTranscriptionResult.innerHTML = `<p style="color: red;">Network Error: ${error.message}</p>`;
            uploadStatus.textContent = 'Network error during upload.';
            uploadStatus.classList.remove('success');
            uploadStatus.classList.add('error');
            console.error('Fetch error during upload transcription:', error);
        } finally {
            uploadAndTranscribeButton.disabled = false;
            audioUploadInput.value = null; // Clear file input
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
            // Apply appropriate styling based on whether it's an error or success message
            grammarCorrectionStatus.classList.remove('success', 'error');
            if (isError) {
                grammarCorrectionStatus.classList.add('error');
            } else {
                grammarCorrectionStatus.classList.add('success'); // Use 'success' class for general info too
            }
            grammarCorrectionStatus.classList.remove('hidden'); // Ensure it's visible
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
        if (grammarCorrectionStatus) grammarCorrectionStatus.textContent = '';
        if (grammarCorrectionStatus) grammarCorrectionStatus.classList.add('hidden'); // Hide it when cleared
    }

    // --- Grammar Correction Logic ---
    if (correctGrammarButton) {
        correctGrammarButton.addEventListener('click', async () => {
            clearGrammarResults(); // Clear previous results
            showGrammarStatus('Checking grammar...', false);

            let textToCorrect = grammarTextInput.value.trim(); // INTENTA OBTENER EL TEXTO DEL CAMPO DE ENTRADA

            // Si el campo de entrada está vacío, intenta obtenerlo de la última transcripción
            if (!textToCorrect) {
                const lastTranscriptionElement = document.getElementById('transcriptionResult');
                if (lastTranscriptionElement && lastTranscriptionElement.querySelector('code')) {
                    textToCorrect = lastTranscriptionElement.querySelector('code').textContent.trim();
                } else {
                    // Si no hay transcripción en audioSection, intenta obtener de la última en la lista de transcripciones
                    if (transcriptionList.firstElementChild && transcriptionList.firstElementChild.querySelector('code')) {
                        textToCorrect = transcriptionList.firstElementChild.querySelector('code').textContent.trim();
                    }
                }
            }
            
            const language = transcriptionLanguageSelect.value;
            console.log("Grammar check button clicked. Text:", textToCorrect, "Language:", language);

            if (!textToCorrect) {
                showGrammarStatus('No text found to check grammar. Please type text, record, or upload audio first.', true);
                return;
            }

            try {
                // Use fetchWithAuth for authenticated request
                const response = await fetchWithAuth('/api/grammar/check', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ text: textToCorrect, language: language })
                });

                if (response.ok) {
                    const result = await response.json();
                    console.log("Grammar check successful:", result);
                    showGrammarStatus('Grammar check completed!', false);

                    originalGrammarTextSpan.textContent = result.original_text || 'N/A';
                    correctedGrammarTextSpan.textContent = result.corrected_text || 'N/A';
                    grammarExplanationSpan.textContent = result.explanation || 'No specific explanation provided.';

                    grammarErrorsDetailsDiv.innerHTML = '';
                    if (result.errors && result.errors.length > 0) {
                        const errorList = document.createElement('ul');
                        result.errors.forEach(error => {
                            const errorP = document.createElement('li'); // Changed to li for list
                            errorP.innerHTML = `<strong>Error:</strong> ${error.message || 'N/A'}<br>`;
                            errorP.innerHTML += `<strong>Problematic text:</strong> "${error.bad_word || 'N/A'}"<br>`;
                            if (error.suggestions && error.suggestions.length > 0) {
                                errorP.innerHTML += `<strong>Suggestions:</strong> ${error.suggestions.join(', ')}<br>`;
                            }
                            errorList.appendChild(errorP);
                        });
                        grammarErrorsDetailsDiv.appendChild(errorList);
                    } else {
                        grammarErrorsDetailsDiv.textContent = "No specific errors detected or they are minor.";
                    }

                } else {
                    const errorResult = await response.json();
                    console.error('Error checking grammar (HTTP status:', response.status, '):', errorResult);
                    showGrammarStatus(`Error checking grammar: ${errorResult.detail || 'Could not check grammar.'}`, true);
                    originalGrammarTextSpan.textContent = '';
                    correctedGrammarTextSpan.textContent = '';
                    grammarExplanationSpan.textContent = '';
                    grammarErrorsDetailsDiv.innerHTML = 'Failed to load grammar details.';
                }
            } catch (error) {
                console.error('Network error checking grammar:', error);
                showGrammarStatus('Network error. Could not check grammar.', true);
                originalGrammarTextSpan.textContent = '';
                correctedGrammarTextSpan.textContent = '';
                grammarExplanationSpan.textContent = '';
                grammarErrorsDetailsDiv.innerHTML = 'Failed to load grammar details.';
            }
        });
    }

    // --- Vocabulary Form ---

    // Event Listener for the Suggest Translation & Comment button
    if (suggestDetailsButton) {
        suggestDetailsButton.addEventListener('click', async () => {
            const russianWord = russianWordInput.value.trim();
            const targetLanguage = targetLanguageSelect.value;
            console.log("Suggest details button clicked. Word:", russianWord, "Target Language:", targetLanguage);

            if (!russianWord) {
                showCustomModal('Input Required', 'Please enter a Russian word to get suggestions.');
                return;
            }

            try {
                // This calls the /api/vocabulary/suggest-translation endpoint
                const response = await fetchWithAuth('/api/vocabulary/suggest-translation', { 
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ russian_word: russianWord, target_language: targetLanguage }) 
                });

                if (response.ok) {
                    const result = await response.json();
                    console.log("Suggestions received:", result);
                    translationInput.value = result.suggested_translation || '';
                    exampleSentenceInput.value = result.suggested_example_sentence || '';
                } else {
                    const errorResult = await response.json();
                    console.error('Error getting suggestions (HTTP status:', response.status, '):', errorResult);
                    showCustomModal('Suggestion Error', `Error getting suggestions: ${errorResult.detail || 'Could not get suggestions.'}`);
                    translationInput.value = '';
                    exampleSentenceInput.value = '';
                }
            } catch (error) {
                console.error('Network error getting suggestions:', error);
                showCustomModal('Network Error', 'Network error. Could not get suggestions.');
                translationInput.value = '';
                exampleSentenceInput.value = '';
            }
        });
    }

    vocabForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const russianWord = russianWordInput.value;
        const translation = translationInput.value;
        const exampleSentence = exampleSentenceInput.value;
        console.log("Vocabulary form submitted. Word:", russianWord);
        try {
            const response = await fetchWithAuth('/api/vocabulary/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ russian_word: russianWord, translation: translation, example_sentence: exampleSentence })
            });
            if (response.ok) {
                console.log("Vocabulary item added successfully.");
                showCustomModal('Success', 'Vocabulary item added successfully!');
                loadVocabulary();
                vocabForm.reset();
            } else {
                const errorResult = await response.json();
                console.error('Error adding vocabulary item (HTTP status:', response.status, '):', errorResult);
                showCustomModal('Error', `Error: ${errorResult.detail || 'Could not add vocabulary item.'}`);
            }
        } catch (error) {
            console.error('Network error adding vocabulary item:', error);
            showCustomModal('Network Error', 'Network error. Could not add vocabulary item.');
        }
    });

    // --- Data Loading Functions ---

    /**
     * Loads transcriptions from the backend and displays them.
     * @param {boolean} loadAll - If true, requests all transcriptions; otherwise, requests a limited number.
     */
    async function loadTranscriptions(loadAll = false) {
        console.log("Loading transcriptions. Load all:", loadAll);
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                console.log("No token for loading transcriptions, skipping.");
                return;
            }

            let url = '/api/audio/my-transcriptions';
            if (loadAll) {
                url += '?limit=0'; // Request all audio
            }

            const response = await fetchWithAuth(url);
            const transcriptions = await response.json();
            console.log("Transcriptions loaded:", transcriptions.length, "items.");
            transcriptionList.innerHTML = '';
            if (transcriptions.length === 0) {
                const li = document.createElement('li');
                li.textContent = 'No transcriptions found.';
                transcriptionList.appendChild(li);
                return;
            }
            // Reverse to show most recent first
            transcriptions.reverse();
            transcriptions.forEach(t => {
                const li = document.createElement('li');
                li.classList.add('transcription-item');
                const timestamp = new Date(t.created_at).toLocaleString();
                const displayLanguage = t.language ? ` [${t.language.toUpperCase()}]` : ' [Unknown Language]';

                const textContainer = document.createElement('div');
                textContainer.innerHTML = `<strong>${timestamp}:</strong> ${displayLanguage} <code>${t.original_transcript}</code>`;

                const deleteButton = document.createElement('button');
                deleteButton.textContent = 'X';
                deleteButton.classList.add('delete-btn');
                deleteButton.title = 'Delete Transcription'; // Add title for accessibility
                deleteButton.dataset.id = t.id;

                li.appendChild(textContainer);
                li.appendChild(deleteButton);
                transcriptionList.appendChild(li);
            });

            // Re-attach event listeners after updating the list
            document.querySelectorAll('.delete-btn').forEach(button => {
                button.addEventListener('click', async (e) => {
                    const transcriptionId = e.target.dataset.id;
                    const confirmed = await showCustomModal('Confirm Deletion', 'Are you sure you want to delete this transcription?', true);
                    if (confirmed) {
                        await deleteTranscription(transcriptionId, loadAll);
                    }
                });
            });

        } catch (error) {
            console.error('Error loading transcriptions:', error);
            transcriptionList.innerHTML = '<li>Error loading transcriptions.</li>';
        }
    }

    /**
     * Deletes a transcription by its ID.
     * @param {number} transcriptionId - The ID of the transcription to delete.
     * @param {boolean} currentLoadAllState - The current state of the 'loadAll' flag for transcriptions.
     */
    async function deleteTranscription(transcriptionId, currentLoadAllState = false) {
        console.log("Deleting transcription with ID:", transcriptionId);
        try {
            const response = await fetchWithAuth(`/api/audio/transcriptions/${transcriptionId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                console.log("Transcription deleted successfully:", transcriptionId);
                showCustomModal('Success', 'Transcription deleted successfully!');
                loadTranscriptions(currentLoadAllState);
            } else {
                const errorResult = await response.json();
                console.error('Error deleting transcription (HTTP status:', response.status, '):', errorResult);
                showCustomModal('Error', `Error deleting transcription: ${errorResult.detail || 'Unknown error'}`);
            }
        } catch (error) {
            showCustomModal('Network Error', 'Network error. Could not delete transcription.');
            console.error('Network error during transcription deletion:', error);
        }
    }

    /**
     * Deletes a vocabulary item by its ID.
     * @param {number} itemId - The ID of the vocabulary item to delete.
     */
    async function deleteVocabularyItem(itemId) {
        console.log("Attempting to delete vocabulary item with ID:", itemId);
        const confirmed = await showCustomModal('Confirm Deletion', 'Are you sure you want to delete this vocabulary item?', true);
        if (!confirmed) {
            return;
        }

        try {
            const response = await fetchWithAuth(`/api/vocabulary/${itemId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                console.log("Vocabulary item deleted successfully:", itemId);
                showCustomModal('Success', 'Vocabulary item deleted successfully!');
                loadVocabulary(); // Reload vocabulary list after deletion
            } else {
                const errorResult = await response.json();
                console.error('Error deleting vocabulary item (HTTP status:', response.status, '):', errorResult.detail);
                showCustomModal('Error', `Error deleting item: ${errorResult.detail || 'Unknown error'}`);
            }
        } catch (error) {
            console.error('Network error deleting vocabulary item:', error);
            showCustomModal('Network Error', 'Network error. Could not delete vocabulary item.');
        }
    }

    /**
     * Loads vocabulary items from the backend and displays them.
     */
    async function loadVocabulary() {
        console.log("Loading vocabulary.");
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                console.log("No token for loading vocabulary, skipping.");
                return;
            }

            const response = await fetchWithAuth('/api/vocabulary/');
            const items = await response.json();
            console.log("Vocabulary loaded:", items.length, "items.");

            vocabList.innerHTML = '';

            if (items.length === 0) {
                const li = document.createElement('li');
                li.textContent = 'No vocabulary items found.';
                vocabList.appendChild(li);
                return;
            }

            // Invert the order of items so the most recent appear first.
            items.reverse();

            items.forEach(item => {
                const li = document.createElement('li');
                li.classList.add('list-item'); // Add a class for consistent styling

                const contentSpan = document.createElement('span');
                // Display original field names for existing vocabulary
                contentSpan.innerHTML = `<strong>${item.russian_word}</strong> - ${item.translation} ${item.example_sentence ? `(${item.example_sentence})` : ''}`;
                li.appendChild(contentSpan);

                const deleteButton = document.createElement('button');
                deleteButton.textContent = 'X';
                deleteButton.classList.add('delete-btn');
                deleteButton.title = 'Delete Vocabulary Item';
                deleteButton.addEventListener('click', () => deleteVocabularyItem(item.id)); // Attach delete function

                li.appendChild(deleteButton);
                vocabList.appendChild(li);
            });
        } catch (error) {
            console.error('Error loading vocabulary:', error);
            vocabList.innerHTML = '<li>Error loading vocabulary items.</li>';
        }
    }

    // Event Listener for the "Show All Transcriptions" button
    if (loadAllTranscriptionsButton) {
        loadAllTranscriptionsButton.addEventListener('click', () => {
            console.log("Load All Transcriptions button clicked.");
            loadTranscriptions(true);
        });
    }

    // Initial check on page load
    checkAuthenticationAndRenderUI();
});
