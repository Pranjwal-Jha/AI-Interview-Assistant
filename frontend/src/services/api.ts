const API_URL = "http://localhost:5000"; // Base URL for your Python backend

interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}
interface TranscriptionResponse {
  text: string;
}

interface LLMResponse {
  response: string;
}

interface ResumeAnalysisResponse {
  skills: string[];
  experience: string[];
  education: string[];
  summary: string;
}
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

export const analyzeResume = async (
  file: File,
  sessionId: string,
): Promise<string> => {
  try {
    const formData = new FormData();
    formData.append("resume", file);
    formData.append("sessionId", sessionId);

    const response = await fetch(`${API_URL}/analyze_resume`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Server responded with ${response.status}`);
    }

    const data = await response.json();
    return data.data;
  } catch (error) {
    console.error("Error analyzing resume:", error);
    throw error;
  }
};

export const getAIResponse = async (
  userText: string,
  sessionId: string,
  resumeData?: ResumeAnalysisResponse | null,
): Promise<string> => {
  try {
    const response = await fetch(`${API_URL}/generate_response`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_input: userText,
        session_id: sessionId,
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

export const getAIResponseStream = async (
  userText: string,
  sessionId: string,
  onChunk: (chunk: string) => void,
  resumeData?: ResumeAnalysisResponse | null,
): Promise<void> => {
  try {
    const response = await fetch(`${API_URL}/generate_response_stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_input: userText,
        session_id: sessionId,
        resume_data: resumeData || null,
      }),
    });

    if (!response.ok) {
      throw new Error(`Server responded with ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error("Failed to get response reader");
    }

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const data = JSON.parse(line.slice(6));
            if (data.type === "chunk" && data.content) {
              onChunk(data.content);
            } else if (data.type === "end") {
              return; // Stream ended successfully
            } else if (data.error) {
              throw new Error(data.error);
            }
          } catch (parseError) {
            console.error("Error parsing streaming data:", parseError);
          }
        }
      }
    }
  } catch (error) {
    console.error("Error getting AI response stream:", error);
    throw error;
  }
};
