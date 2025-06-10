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

    // NUEVO: Botón para cargar todos los audios
    const loadAllTranscriptionsButton = document.getElementById('loadAllTranscriptionsButton');

    // NEW UI Elements - Upload Audio
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
    const registerEmailInput = document.getElementById('registerEmail'); // CORRECCIÓN CLAVE AQUÍ
    const registerPasswordInput = document.getElementById('registerPassword');
    const loginMessage = document.getElementById('loginMessage');
    const registerMessage = document.getElementById('registerMessage');

    // NEW UI Elements for Grammar Correction (from previous interaction)
    const correctGrammarButton = document.getElementById('correctGrammarButton');
    const transcriptionLanguageSelect = document.getElementById('transcriptionLanguage');
    const originalGrammarTextSpan = document.getElementById('originalGrammarText');
    const correctedGrammarTextSpan = document.getElementById('correctedGrammarText');
    const grammarExplanationSpan = document.getElementById('grammarExplanation');
    const grammarErrorsDetailsDiv = document.getElementById('grammarErrorsDetails');

    // NEW UI Elements for Vocabulary Suggestion (from current interaction)
    const suggestDetailsButton = document.getElementById('suggestDetailsButton');
    const targetLanguageSelect = document.getElementById('targetLanguage');
    const russianWordInput = document.getElementById('russianWord');
    const translationInput = document.getElementById('translation');
    const exampleSentenceInput = document.getElementById('exampleSentence');


    let mediaRecorder;
    let audioChunks = [];

    // --- Authentication & UI State Management ---

    function showSection(sectionId) {
        document.querySelectorAll('.auth-section').forEach(section => {
            section.style.display = 'none';
        });
        // Remove 'active' class from all tabs
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
        console.log("checkAuthenticationAndRenderUI called."); // DEBUG
        const token = localStorage.getItem('token');
        console.log("Token from localStorage:", token ? "Token found (length: " + token.length + ")" : "No token found."); // DEBUG
        if (token) {
            console.log("Token found. Hiding authContainer, showing appContainer."); // DEBUG
            authContainer.style.display = 'none';
            appContainer.style.display = 'block';
            // MODIFICADO: Cargar solo los audios por defecto al inicio (no todos)
            await loadTranscriptions(false);
            await loadVocabulary();
        } else {
            console.log("No token found. Showing authContainer, hiding appContainer."); // DEBUG
            authContainer.style.display = 'block';
            appContainer.style.display = 'none';
            showSection('loginForm'); // Default to showing login form
        }
    }

    // Login Form Submission
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = loginUsernameInput.value;
        const password = loginPasswordInput.value;
        loginMessage.textContent = ''; // Clear previous messages
        console.log("Attempting login for user:", username); // DEBUG

        try {
            const response = await fetch('/api/auth/token', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
            });
            const result = await response.json();
            if (response.ok) {
                console.log("Login successful! Received token (first 20 chars):", result.access_token ? result.access_token.substring(0, 20) + "..." : "No token in response."); // DEBUG
                localStorage.setItem('token', result.access_token);
                loginMessage.textContent = 'Login successful!';
                loginMessage.style.color = 'green';
                checkAuthenticationAndRenderUI(); // Redirect to main app
            } else {
                console.error("Login failed (HTTP status:", response.status, "):", result.detail); // DEBUG
                // Improved error display
                loginMessage.textContent = `Login failed: ${result.detail || 'Invalid credentials. Please try again.'}`;
                loginMessage.style.color = 'red';
            }
        } catch (error) {
            console.error('Network error during login:', error); // DEBUG
            loginMessage.textContent = 'Network error. Could not log in.';
            loginMessage.style.color = 'red';
        }
    });

    // Register Form Submission
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = registerUsernameInput.value;
        // *** CAMBIO CLAVE AQUÍ: Asegurarse de enviar null si el email está vacío ***
        const email = registerEmailInput.value.trim() === '' ? null : registerEmailInput.value.trim();
        const password = registerPasswordInput.value;
        registerMessage.textContent = ''; // Clear previous messages
        console.log("Attempting registration for user:", username, "Email:", email); // DEBUG

        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });
            const result = await response.json();
            if (response.ok) {
                console.log("Registration successful for user:", username); // DEBUG
                registerMessage.textContent = 'User registered successfully! Please log in.';
                registerMessage.style.color = 'green';
                showSection('loginForm');
                registerForm.reset();
            } else {
                console.error("Registration failed (HTTP status:", response.status, "):", result.detail); // DEBUG
                // Improved error display for registration
                const errorMessage = result.detail ?
                                        (Array.isArray(result.detail) ? result.detail.map(d => d.msg).join(', ') : result.detail) :
                                        'Please try again.';
                registerMessage.textContent = `Registration failed: ${errorMessage}`;
                registerMessage.style.color = 'red';
            }
        } catch (error) {
            console.error('Network error during registration:', error); // DEBUG
            registerMessage.textContent = 'Network error. Could not register user.';
            registerMessage.style.color = 'red';
        }
    });

    // Logout Functionality
    logoutButton.addEventListener('click', () => {
        console.log("Logout button clicked."); // DEBUG
        localStorage.removeItem('token');
        checkAuthenticationAndRenderUI();
        transcriptionResult.innerHTML = '';
        uploadTranscriptionResult.innerHTML = ''; // Clear upload transcription too
        transcriptionList.innerHTML = '<li>No transcriptions yet.</li>';
        vocabList.innerHTML = '<li>No vocabulary items yet.</li>';
        // Using a modal or custom message box would be better than alert
        alert('You have been logged out.');
    });

    // Switch between Login and Register forms
    showLoginButton.addEventListener('click', () => {
        console.log("Show Login button clicked."); // DEBUG
        showSection('loginForm');
    });
    showRegisterButton.addEventListener('click', () => {
        console.log("Show Register button clicked."); // DEBUG
        showSection('registerForm');
    });

    // --- Recording Logic ---

    startButton.addEventListener('click', async () => {
        console.log("Start recording button clicked."); // DEBUG
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
                    console.log("Transcribe recorded audio button clicked."); // DEBUG
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
                            // MODIFICADO: Cargar solo los audios por defecto después de una nueva transcripción
                            loadTranscriptions(false);
                        } else {
                            console.error("Transcription failed (HTTP status:", response.status, "):", result.detail); // DEBUG
                            transcriptionResult.innerHTML = `<p style="color: red;">Error: ${result.detail || 'Unknown error'}</p>`;
                        }
                    } catch (error) {
                        transcriptionResult.innerHTML = `<p style="color: red;">Network Error: ${error.message}</p>`;
                        console.error('Fetch error during transcription:', error); // DEBUG
                    } finally {
                        transcribeButton.style.display = 'none';
                    }
                };
            };
            mediaRecorder.start();
        } catch (error) {
            console.error('Error accessing microphone:', error); // DEBUG
            recordingStatus.textContent = 'Error: Microphone access denied.';
            alert('Error accessing microphone. Please allow microphone access in your browser settings.');
        }
    });

    stopButton.addEventListener('click', () => {
        console.log("Stop recording button clicked."); // DEBUG
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
        }
    });

    // --- NEW: Audio Upload Logic ---
    audioUploadInput.addEventListener('change', () => {
        console.log("Audio file selected for upload."); // DEBUG
        if (audioUploadInput.files.length > 0) {
            uploadAndTranscribeButton.disabled = false;
            uploadStatus.textContent = `File selected: ${audioUploadInput.files[0].name}`;
            uploadTranscriptionResult.innerHTML = ''; // Clear previous results
        } else {
            uploadAndTranscribeButton.disabled = true;
            uploadStatus.textContent = 'No file selected.';
        }
    });

    uploadAndTranscribeButton.addEventListener('click', async () => {
        const file = audioUploadInput.files[0];
        console.log("Upload and Transcribe button clicked."); // DEBUG
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
            const response = await fetch('/api/audio/upload-and-transcribe', { // NEW ENDPOINT
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
                // MODIFICADO: Cargar solo los audios por defecto después de una nueva transcripción de subida
                loadTranscriptions(false);
            } else {
                console.error("Upload transcription failed (HTTP status:", response.status, "):", result.detail); // DEBUG
                uploadTranscriptionResult.innerHTML = `<p style="color: red;">Error: ${result.detail || 'Unknown error'}</p>`;
                uploadStatus.textContent = 'Transcription failed.';
                uploadStatus.style.color = 'red';
            }
        } catch (error) {
            uploadTranscriptionResult.innerHTML = `<p style="color: red;">Network Error: ${error.message}</p>`;
            uploadStatus.textContent = 'Network error during upload.';
            uploadStatus.style.color = 'red';
            console.error('Fetch error during upload transcription:', error); // DEBUG
        } finally {
            uploadAndTranscribeButton.disabled = false; // Re-enable button
            audioUploadInput.value = null; // Clear the selected file
        }
    });

    // --- Grammar Correction Logic (from previous interaction) ---
    if (correctGrammarButton) {
        correctGrammarButton.addEventListener('click', async () => {
            const lastTranscriptionText = transcriptionResult.textContent.trim();
            const language = transcriptionLanguageSelect.value;
            console.log("Grammar check button clicked. Text:", lastTranscriptionText, "Language:", language); // DEBUG

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
                    console.log("Grammar check successful:", result); // DEBUG
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
                                    li.textContent = `Оригинал: "${detail.original_segment}" -> Исправлено: "${detail.corrected_segment}" (${detail.notes})`;
                                    ul.appendChild(li);
                                });
                                errorP.appendChild(ul);
                            }
                            grammarErrorsDetailsDiv.appendChild(errorP);
                        });
                    } else {
                        grammarErrorsDetailsDiv.textContent = "Конкретных ошибок не обнаружено или незначительны.";
                    }

                } else {
                    const errorResult = await response.json();
                    console.error('Error al verificar la gramática (HTTP status:', response.status, '):', errorResult); // DEBUG
                    alert(`Ошибка при проверке грамматики: ${errorResult.detail || 'Не удалось проверить грамматику.'}`);
                    originalGrammarTextSpan.textContent = '';
                    correctedGrammarTextSpan.textContent = '';
                    grammarExplanationSpan.textContent = '';
                    grammarErrorsDetailsDiv.innerHTML = '';
                }
            } catch (error) {
                console.error('Ошибка сети при проверке грамматики:', error); // DEBUG
                alert('Ошибка сети. Не удалось проверить грамматику.');
                originalGrammarTextSpan.textContent = '';
                correctedGrammarTextSpan.textContent = '';
                grammarExplanationSpan.textContent = '';
                grammarErrorsDetailsDiv.innerHTML = '';
            }
        });
    }

    // --- Vocabulary Form ---

    // NEW: Event Listener for the Suggest Translation & Comment button
    if (suggestDetailsButton) {
        suggestDetailsButton.addEventListener('click', async () => {
            const russianWord = russianWordInput.value.trim();
            const targetLanguage = targetLanguageSelect.value;
            console.log("Suggest details button clicked. Word:", russianWord, "Target Language:", targetLanguage); // DEBUG

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

                // Limpiar campos antes de la sugerencia
                translationInput.value = 'Suggesting...';
                exampleSentenceInput.value = 'Suggesting...';

                // URL CORRECTA
                const response = await fetch('/api/vocabulary/suggest-translation', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({ russian_word: russianWord, target_language: targetLanguage })
                });

                if (response.ok) {
                    const result = await response.json();
                    console.log("Suggestions received:", result); // DEBUG
                    translationInput.value = result.suggested_translation;
                    exampleSentenceInput.value = result.suggested_example_sentence || '';
                } else {
                    const errorResult = await response.json();
                    console.error('Error getting suggestions (HTTP status:', response.status, '):', errorResult); // DEBUG
                    alert(`Error getting suggestions: ${errorResult.detail || 'Could not get suggestions.'}`);
                    translationInput.value = ''; // Limpiar si hubo error
                    exampleSentenceInput.value = ''; // Limpiar si hubo error
                }
            } catch (error) {
                console.error('Network error getting suggestions:', error); // DEBUG
                alert('Network error. Could not get suggestions.');
                translationInput.value = ''; // Limpiar si hubo error
                exampleSentenceInput.value = ''; // Limpiar si hubo error
            }
        });
    }

    vocabForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const russianWord = russianWordInput.value;
        const translation = translationInput.value;
        const exampleSentence = exampleSentenceInput.value;
        console.log("Vocabulary form submitted. Word:", russianWord); // DEBUG
        try {
            // This URL is correct for adding new vocabulary items (POST /api/vocabulary/)
            const response = await fetch('/api/vocabulary/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({ russian_word: russianWord, translation, example_sentence: exampleSentence })
            });
            if (response.ok) {
                console.log("Vocabulary item added successfully."); // DEBUG
                loadVocabulary();
                vocabForm.reset();
            } else {
                const errorResult = await response.json();
                console.error('Error adding vocabulary item (HTTP status:', response.status, '):', errorResult); // DEBUG
                alert(`Error: ${errorResult.detail || 'Could not add vocabulary item.'}`);
            }
        } catch (error) {
            console.error('Network error adding vocabulary item:', error); // DEBUG
            alert('Network error. Could not add vocabulary item.');
        }
    });

    // --- Data Loading Functions (UPDATED for delete button) ---

    // MODIFICADO: loadTranscriptions ahora acepta un parámetro `loadAll`
    async function loadTranscriptions(loadAll = false) {
        console.log("Loading transcriptions. Load all:", loadAll); // DEBUG
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                console.log("No token for loading transcriptions, skipping."); // DEBUG
                return;
            }

            let url = '/api/audio/my-transcriptions';
            if (loadAll) {
                // Si loadAll es true, pide un límite de 0 para obtener todos los audios
                url += '?limit=0';
            }
            // Si loadAll es false, usará el límite por defecto del backend (actualmente 5)

            const response = await fetch(url, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const transcriptions = await response.json();
            console.log("Transcriptions loaded:", transcriptions.length, "items."); // DEBUG
            transcriptionList.innerHTML = ''; // Limpiar la lista antes de añadir
            if (transcriptions.length === 0) {
                const li = document.createElement('li');
                li.textContent = 'No transcriptions found.';
                transcriptionList.appendChild(li);
                return;
            }
            transcriptions.forEach(t => {
                const li = document.createElement('li');
                li.classList.add('transcription-item'); // Añadir una clase para estilos si es necesario
                const timestamp = new Date(t.created_at).toLocaleString();
                const displayLanguage = t.language ? ` [${t.language.toUpperCase()}]` : ' [Unknown Language]';

                // Contenedor para el texto y el botón
                const textContainer = document.createElement('div');
                textContainer.innerHTML = `<strong>${timestamp}:</strong> ${displayLanguage} <code>${t.original_transcript}</code>`;

                const deleteButton = document.createElement('button');
                deleteButton.textContent = 'X'; // O un ícono de basura
                deleteButton.classList.add('delete-btn'); // Clase para estilos CSS
                deleteButton.dataset.id = t.id; // Guardar el ID de la transcripción en el botón

                li.appendChild(textContainer);
                li.appendChild(deleteButton);
                transcriptionList.appendChild(li);
            });

            // Añadir event listeners a los botones de borrar después de que se han creado
            document.querySelectorAll('.delete-btn').forEach(button => {
                button.addEventListener('click', async (e) => {
                    const transcriptionId = e.target.dataset.id;
                    console.log("Delete transcription button clicked for ID:", transcriptionId); // DEBUG
                    if (confirm('Are you sure you want to delete this transcription?')) {
                        // MODIFICADO: Al borrar, recargar la lista de transcripciones con el mismo estado (loadAll o no)
                        await deleteTranscription(transcriptionId, loadAll);
                    }
                });
            });

        } catch (error) {
            console.error('Error loading transcriptions:', error); // DEBUG
            transcriptionList.innerHTML = '<li>Error loading transcriptions.</li>';
        }
    }

    // --- NUEVA FUNCIÓN: deleteTranscription (MODIFICADA para mantener el estado de 'loadAll') ---
    async function deleteTranscription(transcriptionId, currentLoadAllState = false) {
        console.log("Deleting transcription with ID:", transcriptionId); // DEBUG
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
                console.log("Transcription deleted successfully:", transcriptionId); // DEBUG
                alert('Transcription deleted successfully!');
                // Recarga la lista para reflejar el cambio, manteniendo el estado de carga
                loadTranscriptions(currentLoadAllState);
            } else {
                const errorResult = await response.json();
                console.error('Error deleting transcription (HTTP status:', response.status, '):', errorResult); // DEBUG
                alert(`Error deleting transcription: ${errorResult.detail || 'Unknown error'}`);
            }
        } catch (error) {
            alert('Network error. Could not delete transcription.');
            console.error('Network error during transcription deletion:', error); // DEBUG
        }
    }

    async function loadVocabulary() {
        console.log("Loading vocabulary."); // DEBUG
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                console.log("No token for loading vocabulary, skipping."); // DEBUG
                return;
            }

            // URL CORRECTA
            const response = await fetch('/api/vocabulary/', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const items = await response.json();
            console.log("Vocabulary loaded:", items.length, "items."); // DEBUG
            vocabList.innerHTML = '';
            if (items.length === 0) {
                const li = document.createElement('li');
                li.textContent = 'No vocabulary items found.';
                vocabList.appendChild(li);
                return;
            }
            items.forEach(item => {
                const li = document.createElement('li');
                li.innerHTML = `<strong>${item.russian_word}</strong> - ${item.translation} (${item.example_sentence || ''})`;
                vocabList.appendChild(li);
            });
        } catch (error) {
            console.error('Error loading vocabulary:', error); // DEBUG
            vocabList.innerHTML = '<li>Error loading vocabulary items.</li>';
        }
    }

    // NUEVO: Event Listener para el botón "Show All Transcriptions"
    if (loadAllTranscriptionsButton) {
        loadAllTranscriptionsButton.addEventListener('click', () => {
            console.log("Load All Transcriptions button clicked."); // DEBUG
            loadTranscriptions(true); // Carga *todos* los audios
        });
    }

    // Initial check on page load
    checkAuthenticationAndRenderUI();
});