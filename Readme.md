# Languages: My Toolbox

This web service is designed as an **intelligent and personalized toolbox** to facilitate language learning and practice, with a particular focus on Russian, but with multi-language capabilities. It offers advanced functionalities for vocabulary management, AI-powered audio transcription, smart grammar checking, and secure authentication for a personalized daily learning experience.

---

## Features

-   **User Authentication:** Secure registration and login system using JWT access tokens, enabling a personalized user experience.
-   **Vocabulary Management:** Allows users to create, retrieve, and delete their own vocabulary items (Russian word, translation, example sentence). Includes support for **AI-powered suggestions** (utilizing pre-trained NLP models) that offer translations and example phrases.
-   **AI-Powered Audio Transcription:** Functionality to submit audio files (e.g., user pronunciation recordings) for transcription into text. It leverages **OpenAI's advanced Whisper model** to convert audio to text and detect the language, facilitating speaking practice.
-   **Smart Grammar Checking:** Enables users to submit text to identify and correct grammar errors. It integrates with an **external LanguageTool server** to provide accurate and high-performance grammatical analysis.
-   **Persistent Data Storage:** All user data, vocabulary items, and audio transcriptions are securely stored in a relational database.
-   **Telegram Bot Integration (Potential):** Based on the project structure, it is assumed that integration with a Telegram bot is possible to extend the service's functionalities.

---

## Tech Stack

-   **Backend Framework:** [FastAPI](https://fastapi.tiangolo.com/) - A modern, fast web framework for building APIs with Python, including auto-generated documentation (Swagger UI).
-   **Database:** [SQLAlchemy ORM](https://www.sqlalchemy.org/) with [SQLite](https://www.sqlite.org/index.html) (for development/testing) - Provides flexible interaction with the relational database.
-   **Password Hashing:** `bcrypt` - For secure password storage.
-   **JWT Handling:** `PyJWT` - For creating and verifying JSON Web Tokens.
-   **Audio Transcription (ASR):** [Whisper (OpenAI)](https://openai.com/research/whisper) - An advanced Automatic Speech Recognition model used via the `whisper` library, alongside [PyTorch](https://pytorch.org/) and [TorchAudio](https://pytorch.org/audio/) for audio processing. Requires `ffmpeg` for handling audio formats.
-   **Grammar Checking (NLP):** `language-tool-python` client with an external [LanguageTool](https://languagetool.org/) HTTP server (which requires [OpenJDK 17 JRE](https://openjdk.org/)).
-   **Database Migrations:** [Alembic](https://alembic.sqlalchemy.org/en/latest/) - For managing database schemas in a controlled manner.
-   **Dependency Management:** `pip` with `requirements.txt`.
-   **Environment Variables:** `python-dotenv` - For managing application configuration.
-   **Asynchronous Web Server:** [Uvicorn](https://www.uvicorn.org/) - A high-performance ASGI server for FastAPI.
-   **Testing:** `pytest`, `pytest-asyncio`, `httpx` - For automated API testing.
-   **Deployment:** [Docker](https://www.docker.com/) / [Docker Compose](https://docs.docker.com/compose/) - For containerization and orchestration of the application environment, including the database and LanguageTool server.

---

## Getting Started

These instructions will help you get your project running on your local machine for development and testing.

### Prerequisites

-   **Python 3.12**
-   `pip` (Python package installer)
-   `git`
-   **Docker Desktop** (or Docker Engine and Docker Compose) if you plan to use Docker.

### Important Notes for First Run

-   **Model and Data Downloads:** The `whisper` transcription model and grammar correction data (via LanguageTool) might be downloaded or initialized automatically the first time they are used. This may take some time depending on your internet connection and the configured Whisper model size.

### 1. Running with Docker Compose (Recommended)

This is the easiest way to run the entire application, including the database and LanguageTool server.

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/pascaltll/Russian-simulator.git](https://github.com/pascaltll/Russian-simulator.git)
    cd Russian-simulator
    ```

2.  **Configure Environment Variables:**

    -   **Create a `.env` file:** In the root of your project, copy the example file `env.example` and rename it to `.env`.
        ```bash
        cp env.example .env
        ```
    -   **Edit `.env`:** Open the newly created `.env` file and fill in your actual values for the variables. **Make sure to add `.env` to your `.gitignore` file to prevent it from being committed to version control!**
        ```env
        # .env (example values - replace with your own)
        DATABASE_URL=sqlite:///./database_volume_data/app.db
        SECRET_KEY="your_very_secret_key_here_please_generate_a_strong_one"
        ALGORITHM=HS256
        ACCESS_TOKEN_EXPIRE_MINUTES=30
        TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
        WHISPER_MODEL_SIZE=base # Can be 'tiny', 'base', 'small', 'medium', 'large'
        WHISPER_FP16=False # Set to True if you have an FP16-compatible GPU for better performance
        LANGUAGETOOL_API_URL=http://languagetool:8010/v2/check
        ```

3.  **Build and run the Docker containers:**

    ```bash
    docker compose up --build -d
    ```

    The `--build` flag builds the Docker image (necessary the first time or after `Dockerfile`/`requirements.txt` changes). The `-d` flag runs containers in the background.

    **Database Persistence (SQLite):** Your `app.db` database will be persisted using a Docker volume (`db_data`), ensuring your data is not lost when containers are stopped or rebuilt.

4.  **Access the application:** Open your web browser and go to `http://localhost:8000/docs` to see the FastAPI interactive API documentation (Swagger UI).

<!-- ### 2. Running Locally (Alternative)

If you prefer to run the application directly on your machine:

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/pascaltll/Russian-simulator.git](https://github.com/pascaltll/Russian-simulator.git)
    cd Russian-simulator
    ```

2.  **Create and activate a Python virtual environment:**

    ```bash
    python -m venv venv
    # On macOS/Linux:
    source venv/bin/activate
    # On Windows:
    .\venv\Scripts\activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**

    -   **Create a `.env` file:** In the root of the project, copy the example file `env.example` and rename it to `.env`.
    -   **Edit `.env`:** Open `.env` and fill in your actual values for the variables, as described in the Docker section above. Ensure `LANGUAGETOOL_API_URL` points to a running LanguageTool instance (e.g., if you run it locally outside Docker).

5.  **Run Alembic database migrations:** This sets up your database tables.

    ```bash
    alembic upgrade head
    ```

6.  **Start the FastAPI application:**

    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```

    The `--reload` flag enables auto-reloading on code changes, useful for development.

7.  **Access the application:** Open your web browser and go to `http://localhost:8000/docs`. -->

---

## Code Quality

Code quality is checked using `Pylint`.

To check the code quality:

1.  **Install Pylint:**
    ```bash
    pip install pylint
    ```
2.  **Run Pylint and generate a report:**
    ```bash
    pylint $(find . -name "*.py" ! -path "./venv/*" ! -path "./__pycache__/*" ! -path "./alembic/*") > pylint.txt
    ```
    The project requires a Pylint score of **at least 7.5 out of 10**. Review the `pylint.txt` file and fix issues to reach this target.

---
my results: [pylint.txt](pylint.txt)

## Testing

The service includes automated tests using `pytest` and `httpx.AsyncClient` for asynchronous endpoint testing.

To run the tests:

1.  **Activate your virtual environment** (if running locally).
2.  **Ensure all dependencies, including testing dependencies, are installed.**
3.  **Execute the tests:**
    ```bash
    PYTHONPATH=$(pwd) pytest
    ```
    All tests should pass without errors or warnings.

---
my results: [pytest](salida_test)