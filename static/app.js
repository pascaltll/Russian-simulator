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
        console.log(`[Modal] Mostrando modal: "${title}" - "${message}" (Confirmación: ${isConfirm})`); // DEBUG
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
                console.log(`[Modal] Confirmado: "${title}"`); // DEBUG
                customModal.classList.add('hidden');
                resolve(true);
            };
            modalConfirmBtn.addEventListener('click', currentConfirmHandler);

            if (isConfirm) {
                currentCancelHandler = () => {
                    console.log(`[Modal] Cancelado: "${title}"`); // DEBUG
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
        console.log(`[API] Solicitud a: ${url} (Método: ${options.method || 'GET'})`); // DEBUG
        const token = localStorage.getItem('token');
        const headers = {
            ...options.headers,
            'Authorization': token ? `Bearer ${token}` : ''
        };

        const response = await fetch(url, { ...options, headers });
        if (response.status === 401 || response.status === 403) {
            console.warn('[API] Acceso no autorizado, redirigiendo a login.'); // DEBUG
            await showCustomModal('Sesión Expirada', 'Tu sesión ha expirado. Por favor, inicia sesión de nuevo.');
            localStorage.removeItem('token');
            localStorage.removeItem('username');
            checkAuthenticationAndRenderUI();
            throw new Error('Unauthorized'); // Stop further processing
        }
        console.log(`[API] Respuesta de ${url}: HTTP ${response.status}`); // DEBUG
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
                loggedInUsernameSpan.textContent = `¡Bienvenido, ${username}!`;
            }

            showAppSection('audioSection'); // Show audio tools by default
            console.log('[Auth] Usuario autenticado, cargando datos iniciales...'); // DEBUG
            await loadTranscriptions(false); // Asegurarse de que se cargan las transcripciones
            await loadVocabulary(); // Asegurarse de que se carga el vocabulario
        } else {
            authContainer.style.display = 'flex';
            appContainer.style.display = 'none';
            showAuthSection('loginForm');
            console.log('[Auth] Usuario no autenticado, mostrando pantalla de login.'); // DEBUG
        }
    }

    // --- Authentication Event Listeners ---

    // Login Form Submission
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = loginUsernameInput.value;
        const password = loginPasswordInput.value;
        loginMessage.textContent = '';
        console.log('[Auth] Intentando iniciar sesión...'); // DEBUG

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
                loginMessage.textContent = '¡Inicio de sesión exitoso!';
                loginMessage.classList.remove('error');
                loginMessage.classList.add('success');
                checkAuthenticationAndRenderUI();
                console.log('[Auth] Inicio de sesión exitoso.'); // DEBUG
            } else {
                loginMessage.textContent = `Fallo al iniciar sesión: ${result.detail || 'Credenciales inválidas. Intenta de nuevo.'}`;
                loginMessage.classList.remove('success');
                loginMessage.classList.add('error');
                console.error('[Auth] Fallo al iniciar sesión:', result.detail); // DEBUG
            }
        } catch (error) {
            console.error('[Auth] Error de red durante el inicio de sesión:', error); // DEBUG
            loginMessage.textContent = 'Error de red. No se pudo iniciar sesión.';
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
        console.log('[Auth] Intentando registrar usuario...'); // DEBUG

        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });
            const result = await response.json();
            if (response.ok) {
                showCustomModal('Éxito', '¡Usuario registrado exitosamente! Por favor, inicia sesión.').then(() => {
                    registerMessage.textContent = ''; // Clear message after modal
                    registerForm.reset();
                    showAuthSection('loginForm');
                });
                console.log('[Auth] Registro exitoso.'); // DEBUG
            } else {
                const errorMessage = result.detail ?
                                        (Array.isArray(result.detail) ? result.detail.map(d => d.msg).join(', ') : result.detail) :
                                        'Por favor, intenta de nuevo.';
                registerMessage.textContent = `Fallo en el registro: ${errorMessage}`;
                registerMessage.classList.remove('success');
                registerMessage.classList.add('error');
                console.error('[Auth] Fallo en el registro:', result.detail); // DEBUG
            }
        } catch (error) {
            console.error('[Auth] Error de red durante el registro:', error); // DEBUG
            registerMessage.textContent = 'Error de red. No se pudo registrar el usuario.';
            registerMessage.classList.remove('success');
            registerMessage.classList.add('error');
        }
    });

    // Logout Functionality
    logoutButton.addEventListener('click', async () => {
        console.log('[Logout] Botón de cerrar sesión clicado.'); // DEBUG
        const confirmed = await showCustomModal('Confirmar Cierre de Sesión', '¿Estás seguro de que quieres cerrar sesión?', true);
        if (confirmed) {
            console.log('[Logout] Cierre de sesión confirmado por el usuario.'); // DEBUG
            localStorage.removeItem('token');
            localStorage.removeItem('username');
            console.log('[Logout] Token y nombre de usuario eliminados de localStorage.'); // DEBUG
            
            // Verify localStorage is indeed empty
            console.log('Current token in localStorage:', localStorage.getItem('token')); // DEBUG
            console.log('Current username in localStorage:', localStorage.getItem('username')); // DEBUG

            checkAuthenticationAndRenderUI();
            
            // Clear UI elements explicitly for a clean logout state
            transcriptionResult.innerHTML = '';
            uploadTranscriptionResult.innerHTML = '';
            transcriptionList.innerHTML = '<li>No hay transcripciones todavía.</li>';
            vocabList.innerHTML = '<li>No hay elementos de vocabulario todavía.</li>';
            
            showCustomModal('Sesión Cerrada', 'Has cerrado sesión exitosamente.');
            console.log('[Logout] Sesión cerrada completamente.'); // DEBUG
        } else {
            console.log('[Logout] Cierre de sesión cancelado.'); // DEBUG
        }
    });

    // Switch between Login and Register forms
    showLoginButton.addEventListener('click', () => {
        showAuthSection('loginForm');
        console.log('[UI] Cambiando a formulario de login.'); // DEBUG
    });
    showRegisterButton.addEventListener('click', () => {
        showAuthSection('registerForm');
        console.log('[UI] Cambiando a formulario de registro.'); // DEBUG
    });

    // --- Main Navigation Tab Logic ---
    navTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetId = tab.dataset.target;
            showAppSection(targetId);
            console.log(`[UI] Cambiando a sección: ${targetId}`); // DEBUG
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
            console.log('[Audio] Transcripción exitosa, recargando transcripciones...'); // DEBUG
            const detectedLanguage = result.language ? result.language.toUpperCase() : 'Unknown';
            resultElement.innerHTML = `
                <p><strong>Resultado de la Transcripción</strong></p>
                <p><strong>Idioma Detectado:</strong> ${detectedLanguage}</p>
                <p><code>${result.original_transcript}</code></p>
            `;
            if (statusElement) {
                statusElement.textContent = '¡Transcripción exitosa!';
                statusElement.classList.remove('error');
                statusElement.classList.add('success');
            }
            await loadTranscriptions(false); // Asegurarse de que esta función se complete
            console.log('[Audio] Transcripciones recargadas después de nueva transcripción.'); // DEBUG
        } else {
            console.error("[Audio] Fallo en la transcripción (estado HTTP:", response.status, "):", result.detail); // DEBUG
            resultElement.innerHTML = `<p style="color: red;">Error: ${result.detail || 'Error desconocido'}</p>`;
            if (statusElement) {
                statusElement.textContent = 'Fallo en la transcripción.';
                statusElement.classList.remove('success');
                statusElement.classList.add('error');
            }
        }
    }


    // --- Recording Logic ---

    startButton.addEventListener('click', async () => {
        console.log('[Audio] Iniciando grabación...'); // DEBUG
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            startButton.disabled = true;
            stopButton.disabled = false;
            transcribeButton.style.display = 'none';
            recordingStatus.textContent = 'Grabando...';
            recordingStatus.classList.add('recording-indicator');
            transcriptionResult.innerHTML = '';

            mediaRecorder.ondataavailable = e => audioChunks.push(e.data);

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                const formData = new FormData();
                formData.append('audio_file', audioBlob, 'recording.webm');
                console.log('[Audio] Grabación detenida. Archivo de audio listo para transcribir.'); // DEBUG

                recordingStatus.textContent = 'Grabación detenida.';
                recordingStatus.classList.remove('recording-indicator');
                startButton.disabled = false;
                stopButton.disabled = true;
                transcribeButton.style.display = 'inline-block';

                // Assign the transcribe function to the button click
                transcribeButton.onclick = async () => {
                    transcriptionResult.innerHTML = '<p>Transcribiendo...</p>';
                    console.log('[Audio] Iniciando transcripción de audio grabado...'); // DEBUG
                    try {
                        const response = await fetchWithAuth('/api/audio/transcribe-audio', {
                            method: 'POST',
                            body: formData
                        });
                        await handleTranscriptionResponse(response, transcriptionResult);
                    } catch (error) {
                        transcriptionResult.innerHTML = `<p style="color: red;">Error de Red: ${error.message}</p>`;
                        console.error('[Audio] Error de fetch durante la transcripción:', error); // DEBUG
                    } finally {
                        transcribeButton.style.display = 'none';
                    }
                };
            };
            mediaRecorder.start();
        } catch (error) {
            console.error('[Audio] Error al acceder al micrófono:', error); // DEBUG
            recordingStatus.textContent = 'Error: Acceso al micrófono denegado.';
            showCustomModal('Error de Acceso al Micrófono', 'Error al acceder al micrófono. Por favor, permite el acceso al micrófono en la configuración de tu navegador.');
        }
    });

    stopButton.addEventListener('click', () => {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            console.log('[Audio] Botón de detener grabación clicado.'); // DEBUG
        }
    });

    // --- Audio Upload Logic ---
    audioUploadInput.addEventListener('change', () => {
        if (audioUploadInput.files.length > 0) {
            uploadAndTranscribeButton.disabled = false;
            uploadStatus.textContent = `Archivo seleccionado: ${audioUploadInput.files[0].name}`;
            uploadTranscriptionResult.innerHTML = '';
            console.log(`[Audio] Archivo seleccionado para subir: ${audioUploadInput.files[0].name}`); // DEBUG
        } else {
            uploadAndTranscribeButton.disabled = true;
            uploadStatus.textContent = 'Ningún archivo seleccionado.';
            console.log('[Audio] Ningún archivo seleccionado para subir.'); // DEBUG
        }
    });

    uploadAndTranscribeButton.addEventListener('click', async () => {
        const file = audioUploadInput.files[0];
        if (!file) {
            uploadStatus.textContent = 'Por favor, selecciona primero un archivo de audio.';
            uploadStatus.classList.add('error');
            return;
        }

        uploadStatus.textContent = 'Subiendo y transcribiendo...';
        uploadStatus.classList.remove('error', 'success');
        uploadAndTranscribeButton.disabled = true;
        uploadTranscriptionResult.innerHTML = '';
        console.log('[Audio] Iniciando subida y transcripción de audio.'); // DEBUG

        const formData = new FormData();
        formData.append('audio_file', file);

        try {
            const response = await fetchWithAuth('/api/audio/upload-and-transcribe', {
                method: 'POST',
                body: formData
            });
            await handleTranscriptionResponse(response, uploadTranscriptionResult, uploadStatus);
        } catch (error) {
            uploadTranscriptionResult.innerHTML = `<p style="color: red;">Error de Red: ${error.message}</p>`;
            uploadStatus.textContent = 'Error de red durante la subida.';
            uploadStatus.classList.remove('success');
            uploadStatus.classList.add('error');
            console.error('[Audio] Error de fetch durante la transcripción de subida:', error); // DEBUG
        } finally {
            uploadAndTranscribeButton.disabled = false;
            audioUploadInput.value = null; // Clear file input
            console.log('[Audio] Subida y transcripción de audio finalizada.'); // DEBUG
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
            showGrammarStatus('Comprobando gramática...', false);
            console.log('[Grammar] Iniciando comprobación de gramática...'); // DEBUG

            let textToCorrect = grammarTextInput.value.trim();
            console.log(`[Grammar] Texto inicial en grammarTextInput: "${textToCorrect}"`); // DEBUG

            if (!textToCorrect) {
                // If input field is empty, try to get from last transcription result
                const lastTranscriptionCodeElement = transcriptionResult.querySelector('code');
                if (lastTranscriptionCodeElement) {
                    textToCorrect = lastTranscriptionCodeElement.textContent.trim();
                    console.log(`[Grammar] Texto tomado de transcriptionResult: "${textToCorrect}"`); // DEBUG
                } else {
                    // If no transcription in audioSection, try from the first item in the transcription list
                    const firstTranscriptionInList = transcriptionList.querySelector('.transcription-item code');
                    if (firstTranscriptionInList) {
                        textToCorrect = firstTranscriptionInList.textContent.trim();
                        console.log(`[Grammar] Texto tomado de la primera transcripción en la lista: "${textToCorrect}"`); // DEBUG
                    } else {
                        console.log('[Grammar] No se encontró texto en transcriptionResult ni en la lista de transcripciones.'); // DEBUG
                    }
                }
            }

            const language = transcriptionLanguageSelect.value;
            console.log(`[Grammar] Idioma seleccionado para la comprobación: "${language}"`); // DEBUG

            if (!textToCorrect) {
                showGrammarStatus('No se encontró texto para revisar la gramática. Por favor, escribe texto, graba o sube audio primero.', true);
                console.warn('[Grammar] No hay texto para revisar la gramática. Deteniendo operación.'); // DEBUG
                return;
            }

            console.log(`[Grammar] Enviando texto para corregir: "${textToCorrect}" con idioma: "${language}"`); // DEBUG

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
                    showGrammarStatus('¡Comprobación de gramática completada!', false);
                    console.log('[Grammar] Comprobación de gramática exitosa. Resultado de la API:', result); // DEBUG

                    originalGrammarTextSpan.textContent = result.original_text || 'N/A';
                    correctedGrammarTextSpan.textContent = result.corrected_text || 'N/A';
                    grammarExplanationSpan.textContent = result.explanation || 'No se proporcionó una explicación específica.';

                    grammarErrorsDetailsDiv.innerHTML = '';
                    if (result.errors && result.errors.length > 0) {
                        console.log('[Grammar] Errores detectados:', result.errors); // DEBUG
                        const errorList = document.createElement('ul');
                        result.errors.forEach(error => {
                            const errorLi = document.createElement('li'); // Changed to li for list (Pylint equivalent: C0103)
                            errorLi.innerHTML = `<strong>Error:</strong> ${error.message || 'N/A'}<br>`;
                            errorLi.innerHTML += `<strong>Texto problemático:</strong> "${error.bad_word || 'N/A'}"<br>`;
                            if (error.suggestions && error.suggestions.length > 0) {
                                errorLi.innerHTML += `<strong>Sugerencias:</strong> ${error.suggestions.join(', ')}<br>`;
                            }
                            errorList.appendChild(errorLi);
                        });
                        grammarErrorsDetailsDiv.appendChild(errorList);
                    } else {
                        grammarErrorsDetailsDiv.textContent = "No se detectaron errores específicos o son menores.";
                        console.log('[Grammar] No se detectaron errores específicos.'); // DEBUG
                    }

                } else {
                    const errorResult = await response.json();
                    showGrammarStatus(`Error al revisar la gramática: ${errorResult.detail || 'No se pudo revisar la gramática.'}`, true);
                    originalGrammarTextSpan.textContent = '';
                    correctedGrammarTextSpan.textContent = '';
                    grammarExplanationSpan.textContent = '';
                    grammarErrorsDetailsDiv.innerHTML = 'Fallo al cargar detalles de la gramática.';
                    console.error('[Grammar] Error de API al revisar la gramática. Estado HTTP:', response.status, 'Detalles:', errorResult); // DEBUG
                }
            } catch (error) {
                console.error('[Grammar] Error de red o durante el procesamiento de la revisión gramatical:', error); // DEBUG
                showGrammarStatus('Error de red. No se pudo revisar la gramática.', true);
                originalGrammarTextSpan.textContent = '';
                correctedGrammarTextSpan.textContent = '';
                grammarExplanationSpan.innerHTML = '';
                grammarErrorsDetailsDiv.innerHTML = 'Fallo al cargar detalles de la gramática.';
            }
        });
    }

    // --- Vocabulary Form ---

    // Event Listener for the Suggest Translation & Comment button
    if (suggestDetailsButton) {
        suggestDetailsButton.addEventListener('click', async () => {
            const russianWord = russianWordInput.value.trim();
            const targetLanguage = targetLanguageSelect.value;

            if (!russianWord) {
                showCustomModal('Entrada Requerida', 'Por favor, introduce una palabra en ruso para obtener sugerencias.');
                return;
            }
            console.log(`[Vocab] Solicitando sugerencia para "${russianWord}" en ${targetLanguage}`); // DEBUG

            try {
                const response = await fetchWithAuth('/api/vocabulary/suggest-translation', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ russian_word: russianWord, target_language: targetLanguage })
                });

                if (response.ok) {
                    const result = await response.json();
                    translationInput.value = result.suggested_translation || '';
                    exampleSentenceInput.value = result.suggested_example_sentence || '';
                    console.log('[Vocab] Sugerencia recibida:', result); // DEBUG
                } else {
                    const errorResult = await response.json();
                    showCustomModal('Error de Sugerencia', `Error al obtener sugerencias: ${errorResult.detail || 'No se pudieron obtener sugerencias.'}`);
                    translationInput.value = '';
                    exampleSentenceInput.value = '';
                    console.error('[Vocab] Error de API al obtener sugerencias:', errorResult); // DEBUG
                }
            } catch (error) {
                console.error('[Vocab] Error de red al obtener sugerencias:', error); // DEBUG
                showCustomModal('Error de Red', 'Error de red. No se pudieron obtener sugerencias.');
                translationInput.value = '';
                exampleSentenceInput.value = '';
            }
        });
    }

    // New clear button for vocabulary suggestion
    if (clearSuggestionButton) {
        clearSuggestionButton.addEventListener('click', () => {
            russianWordInput.value = '';
            translationInput.value = '';
            exampleSentenceInput.value = '';
            // Reset target language to default if desired, e.g., targetLanguageSelect.value = 'es';
            console.log('[Vocab] Formulario de vocabulario limpiado.'); // DEBUG
        });
    }

    vocabForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const russianWord = russianWordInput.value.trim();
        const translation = translationInput.value.trim();
        const exampleSentence = exampleSentenceInput.value.trim();

        if (!russianWord || !translation) {
            showCustomModal('Entrada Requerida', 'La palabra en ruso y la traducción son obligatorias.');
            return;
        }
        console.log('[Vocab] Intentando añadir elemento de vocabulario...'); // DEBUG

        try {
            const response = await fetchWithAuth('/api/vocabulary/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ russian_word: russianWord, translation: translation, example_sentence: exampleSentence })
            });
            if (response.ok) {
                showCustomModal('Éxito', '¡Elemento de vocabulario añadido exitosamente!');
                await loadVocabulary(); // Asegurarse de que esta función se complete
                vocabForm.reset();
                console.log('[Vocab] Elemento de vocabulario añadido y lista recargada.'); // DEBUG
            } else {
                const errorResult = await response.json();
                showCustomModal('Error', `Error: ${errorResult.detail || 'No se pudo añadir el elemento de vocabulario.'}`);
                console.error('[Vocab] Error de API al añadir vocabulario:', errorResult); // DEBUG
            }
        } catch (error) {
            console.error('[Vocab] Error de red al añadir elemento de vocabulario:', error); // DEBUG
            showCustomModal('Error de Red', 'Error de red. No se pudo añadir el elemento de vocabulario.');
        }
    });

    // --- Data Loading Functions ---

    /**
     * Loads transcriptions from the backend and displays them.
     * @param {boolean} loadAll - If true, requests all transcriptions; otherwise, requests a limited number.
     */
    async function loadTranscriptions(loadAll = false) {
        console.log('[Transcriptions] Cargando transcripciones, loadAll:', loadAll); // DEBUG
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                console.log('[Transcriptions] No hay token, omitiendo carga de transcripciones.'); // DEBUG
                return;
            }

            let url = '/api/audio/my-transcriptions';
            if (loadAll) {
                url += '?limit=0';
            }

            const response = await fetchWithAuth(url);
            const transcriptions = await response.json();
            transcriptionList.innerHTML = '';
            if (transcriptions.length === 0) {
                const li = document.createElement('li');
                li.textContent = 'No hay transcripciones encontradas.';
                transcriptionList.appendChild(li);
                console.log('[Transcriptions] No hay transcripciones encontradas.'); // DEBUG
                return;
            }
            // Display most recent first by reversing the array as API might return oldest first
            transcriptions.reverse();
            transcriptions.forEach(t => {
                const li = document.createElement('li');
                li.classList.add('transcription-item');
                const timestamp = new Date(t.created_at).toLocaleString();
                const displayLanguage = t.language ? ` [${t.language.toUpperCase()}]` : ' [Idioma Desconocido]';

                const textContainer = document.createElement('div');
                textContainer.innerHTML = `<strong>${timestamp}:</strong> ${displayLanguage} <code>${t.original_transcript}</code>`;

                const deleteButton = document.createElement('button');
                deleteButton.textContent = 'X';
                deleteButton.classList.add('delete-btn');
                deleteButton.title = 'Eliminar Transcripción';
                deleteButton.dataset.id = t.id;

                li.appendChild(textContainer);
                li.appendChild(deleteButton);
                transcriptionList.appendChild(li);
            });
            console.log('[Transcriptions] Transcripciones renderizadas, adjuntando controladores de eventos.'); // DEBUG

            // Re-attach event listeners after updating the list
            document.querySelectorAll('.delete-btn').forEach(button => {
                button.addEventListener('click', async (e) => {
                    console.log('[Transcriptions] Botón de eliminar transcripción clicado.'); // DEBUG
                    const transcriptionId = e.target.dataset.id;
                    const confirmed = await showCustomModal('Confirmar Eliminación', '¿Estás seguro de que quieres eliminar esta transcripción?', true);
                    if (confirmed) {
                        console.log(`[Transcriptions] Eliminando transcripción con ID: ${transcriptionId}`); // DEBUG
                        await deleteTranscription(transcriptionId, loadAll);
                    } else {
                        console.log('[Transcriptions] Eliminación de transcripción cancelada.'); // DEBUG
                    }
                });
            });

        } catch (error) {
            console.error('[Transcriptions] Error al cargar transcripciones:', error); // DEBUG
            transcriptionList.innerHTML = '<li>Error al cargar transcripciones.</li>';
        }
    }

    /**
     * Deletes a transcription by its ID.
     * @param {number} transcriptionId - The ID of the transcription to delete.
     * @param {boolean} currentLoadAllState - The current state of the 'loadAll' flag for transcriptions.
     */
    async function deleteTranscription(transcriptionId, currentLoadAllState = false) {
        console.log(`[Transcriptions] Intentando eliminar transcripción ID: ${transcriptionId}`); // DEBUG
        try {
            const response = await fetchWithAuth(`/api/audio/transcriptions/${transcriptionId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                console.log('[Transcriptions] Transcripción eliminada exitosamente de la API. Recargando lista.'); // DEBUG
                loadTranscriptions(currentLoadAllState);
            } else {
                const errorResult = await response.json();
                showCustomModal('Error', `Error al eliminar transcripción: ${errorResult.detail || 'Error desconocido'}`);
                console.error('[Transcriptions] Error de API al eliminar transcripción:', errorResult); // DEBUG
            }
        } catch (error) {
            showCustomModal('Error de Red', 'Error de red. No se pudo eliminar la transcripción.');
            console.error('[Transcriptions] Error de red durante la eliminación de transcripción:', error); // DEBUG
        }
    }

    /**
     * Deletes a vocabulary item by its ID.
     * @param {number} itemId - The ID of the vocabulary item to delete.
     */
    async function deleteVocabularyItem(itemId) {
        console.log(`[Vocab] Intentando eliminar elemento de vocabulario ID: ${itemId}`); // DEBUG
        const confirmed = await showCustomModal('Confirmar Eliminación', '¿Estás seguro de que quieres eliminar este elemento de vocabulario?', true);
        if (!confirmed) {
            console.log('[Vocab] Eliminación de vocabulario cancelada.'); // DEBUG
            return;
        }

        try {
            const response = await fetchWithAuth(`/api/vocabulary/${itemId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                console.log('[Vocab] Elemento de vocabulario eliminado exitosamente de la API. Recargando lista.'); // DEBUG
                loadVocabulary(); // Reload vocabulary list after deletion
            } else {
                const errorResult = await response.json();
                showCustomModal('Error', `Error al eliminar elemento: ${errorResult.detail || 'Error desconocido'}`);
                console.error('[Vocab] Error de API al eliminar elemento de vocabulario:', errorResult); // DEBUG
            }
        } catch (error) {
            console.error('[Vocab] Error de red al eliminar elemento de vocabulario:', error); // DEBUG
            showCustomModal('Error de Red', 'Error de red. No se pudo eliminar el elemento de vocabulario.');
        }
    }

    /**
     * Loads vocabulary items from the backend and displays them.
     */
    async function loadVocabulary() {
        console.log('[Vocab] Cargando vocabulario...'); // DEBUG
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                console.log('[Vocab] No hay token, omitiendo carga de vocabulario.'); // DEBUG
                return;
            }

            const response = await fetchWithAuth('/api/vocabulary/');
            const items = await response.json();

            vocabList.innerHTML = '';

            if (items.length === 0) {
                const li = document.createElement('li');
                li.textContent = 'No hay elementos de vocabulario encontrados.';
                vocabList.appendChild(li);
                console.log('[Vocab] No hay elementos de vocabulario encontrados.'); // DEBUG
                return;
            }

            items.reverse(); // Display most recent first

            items.forEach(item => {
                const li = document.createElement('li');
                li.classList.add('list-item');

                const contentSpan = document.createElement('span');
                contentSpan.innerHTML = `<strong>${item.russian_word}</strong> - ${item.translation} ${item.example_sentence ? `(${item.example_sentence})` : ''}`;
                li.appendChild(contentSpan);

                const deleteButton = document.createElement('button');
                deleteButton.textContent = 'X';
                deleteButton.classList.add('delete-btn');
                deleteButton.title = 'Eliminar Elemento de Vocabulario';
                deleteButton.addEventListener('click', () => { // Usar una función de flecha para capturar item.id
                    console.log(`[Vocab] Botón de eliminar vocabulario clicado para ID: ${item.id}`); // DEBUG
                    deleteVocabularyItem(item.id);
                });

                li.appendChild(deleteButton);
                vocabList.appendChild(li);
            });
            console.log('[Vocab] Vocabulario renderizado, adjuntando controladores de eventos.'); // DEBUG
        } catch (error) {
            console.error('[Vocab] Error al cargar vocabulario:', error); // DEBUG
            vocabList.innerHTML = '<li>Error al cargar elementos de vocabulario.</li>';
        }
    }

    // Event Listener for the "Show All Transcriptions" button
    if (loadAllTranscriptionsButton) {
        loadAllTranscriptionsButton.addEventListener('click', () => {
            console.log('[Transcriptions] Botón "Mostrar todas las transcripciones" clicado.'); // DEBUG
            loadTranscriptions(true);
        });
    }

    // Initial check on page load
    checkAuthenticationAndRenderUI();
});