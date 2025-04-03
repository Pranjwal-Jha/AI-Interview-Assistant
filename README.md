# AI Interview Assistant

The AI Interview Assistant is a tool designed to help users practice for interviews by converting speech to text, processing responses using **Ollama** or **LM Studio**, and generating intelligent follow-up questions. This allows for a more interactive and effective interview preparation experience.

## Features

- **Speech-to-Text Processing** – Converts spoken responses into text for analysis.  
- **AI-Generated Follow-up Questions** – Uses **Ollama** or **LM Studio** to analyze responses and ask relevant follow-up questions.  
- **Customizable AI Models** – Supports different language models, allowing flexibility in response generation.  
- **Offline Support** – Can function without an internet connection when using local AI models.  

## Installation

### Prerequisites

Ensure you have the following installed:

- **Python** (latest stable version)
- **FFmpeg** (required for Whisper)
- **Ollama** or **LM Studio** (for local AI processing)

### Install Dependencies

Run the following command to install necessary Python libraries:

```bash
pip install openai-whisper speechrecognition pyaudio requests
