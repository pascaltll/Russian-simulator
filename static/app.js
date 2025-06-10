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

    // UI Elements for Vocabulary (REVERTED TO ORIGINAL NAMES)
    const suggestDetailsButton = document.getElementById('suggestDetailsButton');
    const targetLanguageSelect = document.getElementById('targetLanguage');
    const russianWordInput = document.getElementById('russianWord'); // REVERTED
    const translationInput = document.getElementById('translation'); // REVERTED
    const exampleSentenceInput = document.getElementById('exampleSentence'); // REVERTED


    let mediaRecorder;
    let audioChunks = [];

    // --- Authentication & UI State Management ---

    function showSection(sectionId) {
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

    async function checkAuthenticationAndRenderUI() {
        console.log("checkAuthenticationAndRenderUI called.");
        const token = localStorage.getItem('token');
        console.log("Token from localStorage:", token ? "Token found (length: " + token.length + ")" : "No token found.");
        if (token) {
            console.log("Token found. Hiding authContainer, showing appContainer.");
            authContainer.style.display = 'none';
            appContainer.style.display = 'block';
            await loadTranscriptions(false);
            await loadVocabulary();
        } else {
            console.log("No token found. Showing authContainer, hiding appContainer.");
            authContainer.style.display = 'block';
            appContainer.style.display = 'none';
            showSection('loginForm');
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
                loginMessage.textContent = 'Login successful!';
                loginMessage.style.color = 'green';
                checkAuthenticationAndRenderUI();
            } else {
                console.error("Login failed (HTTP status:", response.status, "):", result.detail);
                loginMessage.textContent = `Login failed: ${result.detail || 'Invalid credentials. Please try again.'}`;
                loginMessage.style.color = 'red';
            }
        } catch (error) {
            console.error('Network error during login:', error);
            loginMessage.textContent = 'Network error. Could not log in.';
            loginMessage.style.color = 'red';
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
                registerMessage.style.color = 'green';
                showSection('loginForm');
                registerForm.reset();
            } else {
                console.error("Registration failed (HTTP status:", response.status, "):", result.detail);
                const errorMessage = result.detail ?
                                        (Array.isArray(result.detail) ? result.detail.map(d => d.msg).join(', ') : result.detail) :
                                        'Please try again.';
                registerMessage.textContent = `Registration failed: ${errorMessage}`;
                registerMessage.style.color = 'red';
            }
        } catch (error) {
            console.error('Network error during registration:', error);
            registerMessage.textContent = 'Network error. Could not register user.';
            registerMessage.style.color = 'red';
        }
    });

    // Logout Functionality
    logoutButton.addEventListener('click', () => {
        console.log("Logout button clicked.");
        localStorage.removeItem('token');
        checkAuthenticationAndRenderUI();
        transcriptionResult.innerHTML = '';
        uploadTranscriptionResult.innerHTML = '';
        transcriptionList.innerHTML = '<li>No transcriptions yet.</li>';
        vocabList.innerHTML = '<li>No vocabulary items yet.</li>';
        alert('You have been logged out.');
    });

    // Switch between Login and Register forms
    showLoginButton.addEventListener('click', () => {
        console.log("Show Login button clicked.");
        showSection('loginForm');
    });
    showRegisterButton.addEventListener('click', () => {
        console.log("Show Register button clicked.");
        showSection('registerForm');
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
                        const response = await fetch('/api/audio/transcribe-audio', {
                            method: 'POST',
                            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
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
            alert('Error accessing microphone. Please allow microphone access in your browser settings.');
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
            uploadStatus.style.color = 'red';
            return;
        }

        uploadStatus.textContent = 'Uploading and transcribing...';
        uploadStatus.style.color = '#777';
        uploadAndTranscribeButton.disabled = true;
        uploadTranscriptionResult.innerHTML = '';

        const formData = new FormData();
        formData.append('audio_file', file);

        try {
            const response = await fetch('/api/audio/upload-and-transcribe', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
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
                uploadStatus.style.color = 'green';
                loadTranscriptions(false);
            } else {
                console.error("Upload transcription failed (HTTP status:", response.status, "):", result.detail);
                uploadTranscriptionResult.innerHTML = `<p style="color: red;">Error: ${result.detail || 'Unknown error'}</p>`;
                uploadStatus.textContent = 'Transcription failed.';
                uploadStatus.style.color = 'red';
            }
        } catch (error) {
            uploadTranscriptionResult.innerHTML = `<p style="color: red;">Network Error: ${error.message}</p>`;
            uploadStatus.textContent = 'Network error during upload.';
            uploadStatus.style.color = 'red';
            console.error('Fetch error during upload transcription:', error);
        } finally {
            uploadAndTranscribeButton.disabled = false;
            audioUploadInput.value = null;
        }
    });

    // --- Grammar Correction Logic ---
    if (correctGrammarButton) {
        correctGrammarButton.addEventListener('click', async () => {
            const lastTranscriptionText = transcriptionResult.textContent.trim();
            const language = transcriptionLanguageSelect.value;
            console.log("Grammar check button clicked. Text:", lastTranscriptionText, "Language:", language);

            if (!lastTranscriptionText) {
                alert('Пожалуйста, сначала расшифруйте аудио или загрузите аудио, чтобы получить текст для коррекции.');
                return;
            }

            try {
                const token = localStorage.getItem('token');
                if (!token) {
                    alert('Вы должны войти в систему, чтобы проверить грамматику.');
                    return;
                }

                const response = await fetch('/api/audio/grammar-check', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({ text: lastTranscriptionText, language: language })
                });

                if (response.ok) {
                    const result = await response.json();
                    console.log("Grammar check successful:", result);
                    originalGrammarTextSpan.textContent = result.original_text;
                    correctedGrammarTextSpan.textContent = result.corrected_text;
                    grammarExplanationSpan.textContent = result.explanation;

                    grammarErrorsDetailsDiv.innerHTML = '';
                    if (result.errors && result.errors.length > 0) {
                        result.errors.forEach(error => {
                            const errorP = document.createElement('p');
                            errorP.innerHTML = `<strong>Тип ошибки:</strong> ${error.type}<br>`;
                            errorP.innerHTML += `<strong>Сообщение:</strong> ${error.message}<br>`;
                            if (error.explanation_summary) {
                                errorP.innerHTML += `<strong>Краткое объяснение:</strong> ${error.explanation_summary}<br>`;
                            }
                            if (error.details && error.details.length > 0) {
                                const ul = document.createElement('ul');
                                error.details.forEach(detail => {
                                    const li = document.createElement('li');
                                    li.textContent = `Original: "${detail.original_segment}" -> Corrected: "${detail.corrected_segment}" (${detail.notes})`;
                                    ul.appendChild(li);
                                });
                                errorP.appendChild(ul);
                            }
                            grammarErrorsDetailsDiv.appendChild(errorP);
                        });
                    } else {
                        grammarErrorsDetailsDiv.textContent = "No specific errors detected or they are minor.";
                    }

                } else {
                    const errorResult = await response.json();
                    console.error('Error checking grammar (HTTP status:', response.status, '):', errorResult);
                    alert(`Error checking grammar: ${errorResult.detail || 'Could not check grammar.'}`);
                    originalGrammarTextSpan.textContent = '';
                    correctedGrammarTextSpan.textContent = '';
                    grammarExplanationSpan.textContent = '';
                    grammarErrorsDetailsDiv.innerHTML = '';
                }
            } catch (error) {
                console.error('Network error checking grammar:', error);
                alert('Network error. Could not check grammar.');
                originalGrammarTextSpan.textContent = '';
                correctedGrammarTextSpan.textContent = '';
                grammarExplanationSpan.textContent = '';
                grammarErrorsDetailsDiv.innerHTML = '';
            }
        });
    }

    // --- Vocabulary Form ---

    // Event Listener for the Suggest Translation & Comment button (Still calls the new endpoint /api/translate/phrase)
    if (suggestDetailsButton) {
        suggestDetailsButton.addEventListener('click', async () => {
            const russianWord = russianWordInput.value.trim(); // Now refers to russianWordInput
            const targetLanguage = targetLanguageSelect.value;
            console.log("Suggest details button clicked. Word:", russianWord, "Target Language:", targetLanguage);

            if (!russianWord) {
                alert('Please enter a Russian word to get suggestions.');
                return;
            }

            try {
                const token = localStorage.getItem('token');
                if (!token) {
                    alert('You must be logged in to get suggestions.');
                    return;
                }

                // Clear fields before suggestion
                translationInput.value = 'Suggesting...'; // Now refers to translationInput
                exampleSentenceInput.value = 'Suggesting...'; // Now refers to exampleSentenceInput

                // This still points to the new endpoint, which needs backend implementation.
                // If this is giving 404, your backend needs to implement /api/translate/phrase
                const response = await fetch('/api/translate/phrase', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({ russian_phrase: russianWord, target_language: targetLanguage })
                });

                if (response.ok) {
                    const result = await response.json();
                    console.log("Suggestions received:", result);
                    // These fields (translated_text, notes) are what the new /api/translate/phrase endpoint should return
                    translationInput.value = result.translated_text;
                    exampleSentenceInput.value = result.notes || '';
                } else {
                    const errorResult = await response.json();
                    console.error('Error getting suggestions (HTTP status:', response.status, '):', errorResult);
                    alert(`Error getting suggestions: ${errorResult.detail || 'Could not get suggestions.'}`);
                    translationInput.value = '';
                    exampleSentenceInput.value = '';
                }
            } catch (error) {
                console.error('Network error getting suggestions:', error);
                alert('Network error. Could not get suggestions.');
                translationInput.value = '';
                exampleSentenceInput.value = '';
            }
        });
    }

    vocabForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const russianWord = russianWordInput.value; // REVERTED
        const translation = translationInput.value; // REVERTED
        const exampleSentence = exampleSentenceInput.value; // REVERTED
        console.log("Vocabulary form submitted. Word:", russianWord);
        try {
            // This URL is correct for adding new vocabulary items (POST /api/vocabulary/)
            const response = await fetch('/api/vocabulary/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                // REVERTED: Sending original field names
                body: JSON.stringify({ russian_word: russianWord, translation: translation, example_sentence: exampleSentence })
            });
            if (response.ok) {
                console.log("Vocabulary item added successfully.");
                loadVocabulary();
                vocabForm.reset();
            } else {
                const errorResult = await response.json();
                console.error('Error adding vocabulary item (HTTP status:', response.status, '):', errorResult);
                alert(`Error: ${errorResult.detail || 'Could not add vocabulary item.'}`);
            }
        } catch (error) {
            console.error('Network error adding vocabulary item:', error);
            alert('Network error. Could not add vocabulary item.');
        }
    });

    // --- Data Loading Functions ---

    // loadTranscriptions now accepts a `loadAll` parameter
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

            const response = await fetch(url, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const transcriptions = await response.json();
            console.log("Transcriptions loaded:", transcriptions.length, "items.");
            transcriptionList.innerHTML = '';
            if (transcriptions.length === 0) {
                const li = document.createElement('li');
                li.textContent = 'No transcriptions found.';
                transcriptionList.appendChild(li);
                return;
            }
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
                deleteButton.dataset.id = t.id;

                li.appendChild(textContainer);
                li.appendChild(deleteButton);
                transcriptionList.appendChild(li);
            });

            document.querySelectorAll('.delete-btn').forEach(button => {
                button.addEventListener('click', async (e) => {
                    const transcriptionId = e.target.dataset.id;
                    console.log("Delete transcription button clicked for ID:", transcriptionId);
                    if (confirm('Are you sure you want to delete this transcription?')) {
                        await deleteTranscription(transcriptionId, loadAll);
                    }
                });
            });

        } catch (error) {
            console.error('Error loading transcriptions:', error);
            transcriptionList.innerHTML = '<li>Error loading transcriptions.</li>';
        }
    }

    async function deleteTranscription(transcriptionId, currentLoadAllState = false) {
        console.log("Deleting transcription with ID:", transcriptionId);
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                alert('You are not logged in.');
                return;
            }

            const response = await fetch(`/api/audio/transcriptions/${transcriptionId}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (response.ok) {
                console.log("Transcription deleted successfully:", transcriptionId);
                alert('Transcription deleted successfully!');
                loadTranscriptions(currentLoadAllState);
            } else {
                const errorResult = await response.json();
                console.error('Error deleting transcription (HTTP status:', response.status, '):', errorResult);
                alert(`Error deleting transcription: ${errorResult.detail || 'Unknown error'}`);
            }
        } catch (error) {
            alert('Network error. Could not delete transcription.');
            console.error('Network error during transcription deletion:', error);
        }
    }

    // NEW FUNCTION: deleteVocabularyItem - Handles deletion of vocabulary items
    async function deleteVocabularyItem(itemId) {
        console.log("Attempting to delete vocabulary item with ID:", itemId);
        if (!confirm('Are you sure you want to delete this vocabulary item?')) {
            return;
        }

        try {
            const token = localStorage.getItem('token');
            if (!token) {
                alert('You must be logged in to delete vocabulary items.');
                return;
            }

            const response = await fetch(`/api/vocabulary/${itemId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                console.log("Vocabulary item deleted successfully:", itemId);
                loadVocabulary(); // Reload vocabulary list after deletion
            } else {
                const errorResult = await response.json();
                console.error('Error deleting vocabulary item (HTTP status:', response.status, '):', errorResult.detail);
                alert(`Error deleting item: ${errorResult.detail || 'Unknown error'}`);
            }
        } catch (error) {
            console.error('Network error deleting vocabulary item:', error);
            alert('Network error. Could not delete vocabulary item.');
        }
    }

    async function loadVocabulary() {
        console.log("Loading vocabulary.");
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                console.log("No token for loading vocabulary, skipping.");
                return;
            }

            const response = await fetch('/api/vocabulary/', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
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
