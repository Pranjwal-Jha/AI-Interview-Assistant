"use client";
import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input"; // Although not used in the current UI flow, keeping import
import { Mic, MicOff, FileUp, Send, Play, Loader2 } from "lucide-react";
import { Label } from "@/components/ui/label"; // Although not used in the current UI flow, keeping import
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { analyzeResume, getAIResponse, transcribeAudio } from "@/services/api"; // Import API functions

// Define message types for better clarity and type safety
interface Message {
  role: "user" | "assistant";
  content: string;
}

// Define type for resume data
interface ResumeAnalysisResponse {
  skills: string[];
  experience: string[];
  education: string[];
  summary: string;
}

export default function AIInterviewer() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hello! I'm your AI interviewer today. Could you please upload your resume so I can better tailor my questions to your experience?",
    },
  ]);
  const [isRecording, setIsRecording] = useState(false);
  const [resumeUploaded, setResumeUploaded] = useState(false);
  const [resumeName, setResumeName] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const scrollAreaRef = useRef<HTMLDivElement | null>(null); // Explicitly type the ref

  // State to potentially store resume data after analysis, if needed for subsequent AI calls
  const [resumeData, setResumeData] = useState<ResumeAnalysisResponse | null>(
    null,
  );

  // Scroll to bottom when messages update
  useEffect(() => {
    if (scrollAreaRef.current) {
      // Add null check before querying
      const scrollContainer = scrollAreaRef.current.querySelector(
        "[data-radix-scroll-area-viewport]",
      );
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  }, [messages]);

  const handleRecordToggle = async () => {
    if (isRecording) {
      // --- Stop recording logic ---
      setIsRecording(false);
      setIsProcessing(true);

      // Placeholder for actual audio recording stop logic
      // Once recording stops, you would get an audio Blob

      try {
        // Placeholder for getting audioBlob from recording
        // const audioBlob = await stopRecordingAndGetBlob(); // You need to implement this

        // Simulate getting a dummy audioBlob for demonstration
        const dummyAudioBlob = new Blob(["dummy audio data"], {
          type: "audio/wav",
        }); // Replace with actual audio blob

        // Transcribe the audio
        const transcribedText = await transcribeAudio(dummyAudioBlob);

        // Add user's transcribed message to state
        setMessages((prev) => [
          ...prev,
          { role: "user", content: transcribedText },
        ]);

        // Get AI response based on transcribed text and resume data
        const aiResponse = await getAIResponse(
          transcribedText,
          resumeData || undefined,
        );

        // Add AI's response to state
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: aiResponse },
        ]);
      } catch (error) {
        console.error("Error during transcription or AI response:", error);
        // Optionally, add an error message to the chat
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: "Sorry, there was an error processing your request.",
          },
        ]);
      } finally {
        setIsProcessing(false);
      }
    } else {
      // --- Start recording logic ---
      setIsRecording(true);
      // Placeholder for actual audio recording start logic
      // e.g., using MediaRecorder API
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]; // Use optional chaining
    if (file) {
      setResumeName(file.name);
      setResumeUploaded(true);

      // Add a message indicating file upload started
      setMessages((prev) => [
        ...prev,
        { role: "user", content: `I've uploaded my resume: ${file.name}` },
      ]);

      setIsProcessing(true);

      try {
        // Call the analyzeResume API
        const analysisResult = await analyzeResume(file);
        // setResumeData(analysisResult); // Store resume data if needed for getAIResponse

        setIsProcessing(false);
        // Add the AI's response after processing the resume
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: analysisResult,
            // "Thanks for uploading your resume! I see you have experience with machine learning models and data processing. Let's begin the interview. Could you tell me about your background in machine learning?",
          },
        ]);
      } catch (error) {
        console.error("Error analyzing resume:", error);
        setIsProcessing(false);
        // Add an error message to the chat
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: "Sorry, there was an error analyzing your resume.",
          },
        ]);
        setResumeUploaded(false); // Reset upload state on error
        setResumeName("");
      }
    }
  };

  const triggerFileUpload = () => {
    fileInputRef.current?.click(); // Use optional chaining
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto p-4">
      <header className="text-center mb-4">
        <h1 className="text-2xl font-bold">AI Interview Assistant</h1>
        <p className="text-gray-500">
          Speak naturally - your responses will be transcribed and evaluated
        </p>
      </header>

      <Card className="flex-grow flex flex-col">
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>Interview Session</CardTitle>
            {resumeUploaded && (
              <Badge variant="outline" className="flex items-center gap-1">
                <FileUp className="h-3 w-3" />
                Resume uploaded: {resumeName}
              </Badge>
            )}
          </div>
          <CardDescription>
            Speak clearly and concisely. The AI will analyze your responses.
          </CardDescription>
        </CardHeader>

        <CardContent className="flex-grow flex flex-col">
          <ScrollArea className="flex-grow pr-4" ref={scrollAreaRef}>
            <div className="space-y-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.role === "assistant" ? "justify-start" : "justify-end"}`}
                >
                  <div
                    className={`flex items-start gap-3 max-w-3/4 ${message.role === "assistant" ? "" : "flex-row-reverse"}`}
                  >
                    <Avatar
                      className={
                        message.role === "assistant"
                          ? "bg-blue-100"
                          : "bg-green-100"
                      }
                    >
                      <AvatarFallback>
                        {message.role === "assistant" ? "AI" : "You"}
                      </AvatarFallback>
                    </Avatar>
                    <div
                      className={`rounded-lg p-3 ${
                        message.role === "assistant"
                          ? "bg-gray-100 text-gray-800"
                          : "bg-blue-600 text-white"
                      }`}
                    >
                      {message.content}
                    </div>
                  </div>
                </div>
              ))}
              {isProcessing && (
                <div className="flex justify-start">
                  <div className="flex items-start gap-3 max-w-3/4">
                    <Avatar className="bg-blue-100">
                      <AvatarFallback>AI</AvatarFallback>
                    </Avatar>
                    <div className="rounded-lg p-3 bg-gray-100 text-gray-800">
                      <Loader2 className="h-5 w-5 animate-spin" />
                    </div>
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>
        </CardContent>

        <Separator />

        <CardFooter className="pt-4">
          <div className="w-full space-y-4">
            {!resumeUploaded && (
              <div className="flex flex-col items-center justify-center">
                <p className="text-gray-500 mb-2">
                  Please upload your resume to begin
                </p>
                <input
                  type="file"
                  ref={fileInputRef}
                  className="hidden"
                  accept=".pdf,.doc,.docx" // Specify accepted file types
                  onChange={handleFileUpload}
                />
                <Button
                  onClick={triggerFileUpload}
                  className="flex items-center gap-2"
                >
                  <FileUp className="h-4 w-4" />
                  Upload Resume
                </Button>
              </div>
            )}

            {resumeUploaded && (
              <div className="flex items-center gap-4">
                <Button
                  variant={isRecording ? "destructive" : "default"}
                  className="rounded-full w-12 h-12 p-0 flex items-center justify-center"
                  onClick={handleRecordToggle}
                  disabled={isProcessing}
                >
                  {isRecording ? (
                    <MicOff className="h-5 w-5" />
                  ) : (
                    <Mic className="h-5 w-5" />
                  )}
                </Button>
                <div className="flex-grow text-sm text-gray-500">
                  {isRecording
                    ? "Recording... Click to stop"
                    : "Click to start speaking"}
                </div>
                {/* Playback button - currently does nothing */}
                {/* <Button variant="outline" className="rounded-full w-12 h-12 p-0 flex items-center justify-center" disabled>
                  <Play className="h-5 w-5" />
                </Button> */}
              </div>
            )}
          </div>
        </CardFooter>
      </Card>
    </div>
  );
}
