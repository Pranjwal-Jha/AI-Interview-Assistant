# AI Interview Assistant

The AI Interview Assistant is a comprehensive tool designed to enhance interview preparation. It integrates speech-to-text capabilities, AI-driven question generation, resume analysis, and real-time coding question integration with submission validation. This platform provides an interactive and effective environment for users to practice and refine their interview skills.

## Features

-   **Speech-to-Text Processing**: Converts spoken responses into text for analysis using Deepgram.
-   **AI-Generated Follow-up Questions**: Leverages AI models (Google Gemini, Langchain) to analyze responses and provide relevant, context-aware follow-up questions.
-   **Resume Analysis**: Processes uploaded resumes to tailor interview questions based on the candidate's experience, skills, and projects.
-   **LeetCode Integration**: Provides dynamic coding challenges with direct code submission and evaluation capabilities against LeetCode problems.
-   **Session Management**: Maintains interview context throughout the session.

## Installation

### Prerequisites

Ensure the following are installed on your system:

-   **Python** (latest stable version)
-   **Node.js** (LTS version, includes npm)
-   **FFmpeg** (required for audio processing)

### Backend Setup

1.  Navigate to the `backend` directory:
    ```bash
    cd speech_text/backend
    ```
2.  Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Create a `.env` file in the `backend` directory and add your API keys:
    ```
    DEEPGRAM_API_KEY=your_deepgram_api_key
    GEMINI_API_KEY=your_gemini_api_key
    LEETCODE_CSRF=your_leetcode_csrf_token
    LEETCODE_SESSION=your_leetcode_session_cookie
    ```
    *   `LEETCODE_CSRF` and `LEETCODE_SESSION` can be obtained from your browser's cookies after logging into LeetCode.

### Frontend Setup

1.  Navigate to the `frontend` directory:
    ```bash
    cd speech_text/frontend
    ```
2.  Install Node.js dependencies:
    ```bash
    npm install
    ```
3.  Create a `.env.local` file in the `frontend` directory:
    ```
    NEXT_PUBLIC_API_URL=http://localhost:5000
    ```

## Usage

### Running the Backend

From the `speech_text/backend` directory, run the Flask application:
```bash
python app.py
```

### Running the Frontend

From the `speech_text/frontend` directory, start the Next.js development server:
```bash
npm run dev
```

Access the application in your web browser at `http://localhost:3000`.
