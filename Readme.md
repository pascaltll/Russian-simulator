# Russian Language Learning App

This web service is designed to help users learn the Russian language. It offers features for managing vocabulary, transcribing audio, checking grammar, and provides secure authentication for personalized learning.

---

## Features

* **User Authentication:** Secure registration and login endpoints using JWT access tokens.
* **Vocabulary Management:** Create, read, update, and delete vocabulary items (Russian word, translation, example sentence). Includes support for AI-powered suggestions.
* **Audio Transcription:** Submit audio files for transcription (e.g., user pronunciation practice). Uses the Whisper model to transcribe audio to text and detect language.
* **Grammar Check:** Submit text to identify and correct grammar errors.
* **Persistent Data Storage:** Stores all user data, vocabulary, and audio submissions in a relational database.
* **Telegram Bot Integration:** (Assumes integration with a Telegram bot for some features based on your project structure.)

---

## Tech Stack

* **Backend Framework:** FastAPI
* **Database:** SQLAlchemy ORM with SQLite (for development/testing)
* **Password Hashing:** `bcrypt`
* **JWT Handling:** `PyJWT`
* **Audio Transcription:** `whisper`
* **NLP/AI Services:** Custom services for vocabulary suggestions and grammar checks.
* **Database Migrations:** `Alembic`
* **Dependency Management:** `pip` with `requirements.txt`
* **Environment Variables:** `python-dotenv`
* **Testing:** `pytest`, `pytest-asyncio`, `httpx`
* **Deployment:** Docker / Docker Compose

---

## Getting Started

These instructions will help you get your project running on your local machine for development and testing.

### Prerequisites

* **Python 3.12**
* **`pip`** (Python package installer)
* **`git`**
* **Docker Desktop** (or Docker Engine and Docker Compose) if you plan to use Docker.

### 1. Running with Docker Compose (Recommended)

This is the easiest way to run the entire application, including the database and applying migrations.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
    cd your-repo-name
    ```
    *(Remember to replace `your-username/your-repo-name.git` with your actual repository URL).*

2.  **Create a `.env` file:**
    In the root of your project, create a file named `.env` and add your environment variables. **Make sure to add `.env` to your `.gitignore` file!**
    ```env
    SECRET_KEY="your_very_secret_key_here_please_change_this"
    ALGORITHM="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    # Add any other environment variables your application needs
    ```

3.  **Build and run the Docker containers:**
    ```bash
    docker compose up --build -d
    ```
    The `--build` flag builds the Docker image (necessary the first time or after `Dockerfile`/`requirements.txt` changes). The `-d` flag runs containers in the background.

4.  **Access the application:**
    Open your web browser and go to `http://localhost:8000/docs` to see the FastAPI interactive API documentation (Swagger UI).

### 2. Running Locally (Alternative)

If you prefer to run the application directly on your machine.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
    cd your-repo-name
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

4.  **Create a `.env` file:**
    In the root of the project, create a file named `.env` with your environment variables (as described in the Docker section above).

5.  **Run Alembic database migrations:**
    This sets up your database tables.
    ```bash
    alembic upgrade head
    ```

6.  **Start the FastAPI application:**
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```
    The `--reload` flag enables auto-reloading on code changes, useful for development.

7.  **Access the application:**
    Open your web browser and go to `http://localhost:8000/docs`.

---

## Secret Management

This project uses `python-dotenv` to load environment variables. All sensitive information (like `SECRET_KEY`) should be stored in a `.env` file at the root of the repository.

**Important:** Remember to add `.env` to your `.gitignore` file to prevent it from being committed to version control.

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
