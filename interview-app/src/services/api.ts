// src/services/api.ts

const API_URL = "http://localhost:5000"; // Base URL for your Python backend

// Interface for API responses
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

// Interface for transcription response
interface TranscriptionResponse {
  text: string;
}

// Interface for LLM response
interface LLMResponse {
  response: string;
}

// Interface for resume analysis
interface ResumeAnalysisResponse {
  skills: string[];
  experience: string[];
  education: string[];
  summary: string;
}

/**
 * Transcribes audio using Whisper API
 * @param audioBlob - The recorded audio blob
 * @returns The transcribed text
 */
export const transcribeAudio = async (audioBlob: Blob): Promise<string> => {
  try {
    const formData = new FormData();
    formData.append("audio", audioBlob, "recording.wav");

    const response = await fetch(`${API_URL}/transcribe`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Server responded with ${response.status}`);
    }

    const data: TranscriptionResponse = await response.json();
    return data.text;
  } catch (error) {
    console.error("Error transcribing audio:", error);
    throw error;
  }
};

/**
 * Uploads and analyzes a resume
 * @param file - The resume file
 * @returns Structured data extracted from resume
 */
export const analyzeResume = async (
  file: File,
): Promise<ResumeAnalysisResponse> => {
  try {
    const formData = new FormData();
    formData.append("resume", file);

    const response = await fetch(`${API_URL}/analyze_resume`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Server responded with ${response.status}`);
    }

    const data: ResumeAnalysisResponse = await response.json();
    return data;
  } catch (error) {
    console.error("Error analyzing resume:", error);
    throw error;
  }
};

/**
 * Gets AI response for an interview question based on user input
 * @param userText - The user's transcribed text or message
 * @param resumeData - Optional resume data for context
 * @returns The AI's interview response
 */
export const getAIResponse = async (
  userText: string,
  resumeData?: ResumeAnalysisResponse,
): Promise<string> => {
  try {
    const response = await fetch(`${API_URL}/generate_response`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_input: userText,
        resume_data: resumeData || null,
      }),
    });

    if (!response.ok) {
      throw new Error(`Server responded with ${response.status}`);
    }

    const data: LLMResponse = await response.json();
    return data.response;
  } catch (error) {
    console.error("Error getting AI response:", error);
    throw error;
  }
};
