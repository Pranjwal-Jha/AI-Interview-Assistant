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
import { Mic, MicOff, FileUp, Loader2, Code } from "lucide-react"; // Added Code icon
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  analyzeResume,
  transcribeAudio,
  getAIResponseStream,
  submitCode, // We will add this later if needed
} from "@/services/api";
import CodeEditor from "@/components/CodeEditor"; // Import the CodeEditor component

// Define message types for better clarity and type safety
interface Message {
  role: "user" | "assistant";
  content: string;
}

// Define type for resume data

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
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const [setResumeName] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const scrollAreaRef = useRef<HTMLDivElement | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  // State to potentially store resume data after analysis, if needed for subsequent AI calls
  // const [resumeData] = useState<ResumeAnalysisResponse | null>(null);

  // New state for Code Editor visibility
  const [isCodeEditorVisible, setIsCodeEditorVisible] = useState(false);

  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector(
        "[data-radix-scroll-area-viewport]",
      );
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  }, [messages]);
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      // Cleanup on component unmount
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
      if (
        mediaRecorderRef.current &&
        mediaRecorderRef.current.state !== "inactive"
      ) {
        mediaRecorderRef.current.stop();
      }
    };
  }, []);
  const handleRecordToggle = async () => {
    if (isRecording) {
      // --- Stop recording logic ---
      setIsRecording(false);
      setIsProcessing(true);

      // Stop the media recorder
      if (
        mediaRecorderRef.current &&
        mediaRecorderRef.current.state !== "inactive"
      ) {
        mediaRecorderRef.current.stop();
      }

      // Stop all tracks in the stream
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    } else {
      // --- Start recording logic ---
      try {
        // Request microphone access
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: {
            sampleRate: 16000, // Match your backend expectation
            channelCount: 1, // Mono audio
            echoCancellation: true,
            noiseSuppression: true,
          },
        });

        streamRef.current = stream;
        audioChunksRef.current = [];

        // Create MediaRecorder
        const mediaRecorder = new MediaRecorder(stream, {
          mimeType: "audio/webm;codecs=opus", // Most browsers support this
        });

        mediaRecorderRef.current = mediaRecorder;

        // Handle data available event
        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunksRef.current.push(event.data);
          }
        };

        // Handle recording stop event
        mediaRecorder.onstop = async () => {
          // Create blob from recorded chunks
          const audioBlob = new Blob(audioChunksRef.current, {
            type: "audio/webm;codecs=opus",
          });

          try {
            console.log(
              "Sending audio blob to transcription...",
              audioBlob.size,
              "bytes",
            );

            // Send the REAL recorded audio to transcription
            const transcribedText = await transcribeAudio(audioBlob);

            // Add user's transcribed message to state
            setMessages((prev) => [
              ...prev,
              { role: "user", content: `${transcribedText}` },
            ]);
            console.log("Sending transcribed text to A.I for response...");
            setIsProcessing(true);
            if (sessionId) {
              setMessages((prev) => [
                ...prev,
                { role: "assistant", content: "" }, // Empty placeholder
              ]);

              let accumulatedContent = "";

              try {
                await getAIResponseStream(
                  transcribedText,
                  sessionId,
                  (chunk: string) => {
                    // This callback is called for each chunk
                    accumulatedContent += chunk;

                    // Update the last assistant message with accumulated content
                    setMessages((prev) => {
                      const newMessages = [...prev];
                      const lastIndex = newMessages.length - 1;
                      if (newMessages[lastIndex]?.role === "assistant") {
                        newMessages[lastIndex] = {
                          ...newMessages[lastIndex],
                          content: accumulatedContent,
                        };
                      }
                      return newMessages;
                    });
                  },
                  null,
                );
              } catch (error) {
                console.error("Error during streaming:", error);
                // Replace the placeholder with error message
                setMessages((prev) => {
                  const newMessages = [...prev];
                  const lastIndex = newMessages.length - 1;
                  if (newMessages[lastIndex]?.role === "assistant") {
                    newMessages[lastIndex] = {
                      ...newMessages[lastIndex],
                      content: `Error: ${error instanceof Error ? error.message : "Unknown error"}`,
                    };
                  }
                  return newMessages;
                });
              }
              //If want to revert back to normal non streaming text inputs
              // const aiResponseContent = await getAIResponse(
              //   transcribedText,
              //   sessionId,
              //   null,
              // );
              // setMessages((prev) => [
              //   ...prev,
              //   { role: "assistant", content: aiResponseContent },
              // ]);
            } else {
              console.log("Session ID not available");
              setMessages((prev) => [
                ...prev,
                { role: "assistant", content: "Error: Interview ID not found" },
              ]);
            }
          } catch (error) {
            console.error("Error during transcription:", error);
            setMessages((prev) => [
              ...prev,
              {
                role: "assistant",
                content: `Transcription error: ${error instanceof Error ? error.message : "Unknown error"}`,
              },
            ]);
          } finally {
            setIsProcessing(false);
          }
        };

        // Start recording
        mediaRecorder.start();
        setIsRecording(true);
      } catch (error) {
        console.error("Error accessing microphone:", error);
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: "Error accessing microphone. Please check permissions.",
          },
        ]);
      }
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]; // Use optional chaining
    if (file) {
      setResumeUploaded(true);
      const newSessionID = crypto.randomUUID();
      setSessionId(newSessionID);
      // Add a message indicating file upload started
      setMessages((prev) => [
        ...prev,
        { role: "user", content: `I've uploaded my resume: ${file.name}` },
      ]);

      setIsProcessing(true);

      try {
        const analysisResult = await analyzeResume(file, newSessionID);
        setIsProcessing(false);
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: analysisResult,
          },
        ]);
      } catch (error) {
        console.error("Error analyzing resume:", error);
        setIsProcessing(false);
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: "Sorry, there was an error analyzing your resume.",
          },
        ]);
        setResumeUploaded(false); // Reset upload state on error
      }
    }
  };

  const triggerFileUpload = () => {
    fileInputRef.current?.click(); // Use optional chaining
  };

  // Handle code submission from the CodeEditor
  const handleCodeSubmit = async (code: string) => {
    console.log("Code submitted:", code);

    if (!sessionId) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Error: Cannot submit code without an active interview session.",
        },
      ]);
      setIsCodeEditorVisible(false);
      return;
    }

    setIsProcessing(true);

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: "Code Submitted !",
      },
    ]);
    setIsCodeEditorVisible(false);

    const submissionResult = await submitCode(code, sessionId);
    if (submissionResult.success) {
      if (submissionResult.run_success === "Accepted") {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: `All tests passed !`,
          },
        ]);
      } else {
        let failureMessage = `${submissionResult.run_success || "Unknown Status"}`;

        if (submissionResult.failed_testcase) {
          failureMessage += `\nFailed on Test Case: ${submissionResult.failed_testcase}`;
        }
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: failureMessage,
          },
        ]);
      }
    } else {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Code submission failed: ${submissionResult.error || "Unknown error from backend"}`,
        },
      ]);
    }
    setIsProcessing(false);
  };

  return (
    // Outer container to center the main content initially
    <div className="relative flex justify-center h-screen w-full overflow-hidden">
      {/* Main content area - centered initially, shifts left when editor is visible */}
      <div
        className={`p-4 transition-all duration-300 flex-shrink-0 w-full max-w-4xl ${
          isCodeEditorVisible ? "translate-x-[-25vw]" : "" // Translate left by half editor width
        }`}
      >
        <header className="text-center mb-4">
          <h1 className="text-2xl font-bold">AI Interview Assistant</h1>
          <p className="text-gray-500">
            Speak naturally - your responses will be transcribed and evaluated
          </p>
        </header>

        {/* Adjust Card height to fit within the flex container */}
        <Card className="flex-grow flex flex-col h-[calc(100vh-120px)]">
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle>Interview Session</CardTitle>
              {/* Container for right-aligned items */}
              <div className="flex items-center gap-2">
                {resumeUploaded && (
                  <Badge variant="outline" className="flex items-center gap-1">
                    <FileUp className="h-3 w-3" />
                    Resume uploaded
                  </Badge>
                )}
                {/* Button to toggle Code Editor visibility - moved to be the last item in this flex container */}
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setIsCodeEditorVisible(!isCodeEditorVisible)}
                  className="flex items-center gap-1"
                >
                  <Code className="h-4 w-4" />
                  Code Editor
                </Button>
              </div>
            </div>
            <CardDescription>
              Speak clearly and concisely. The AI will analyze your responses.
            </CardDescription>
          </CardHeader>

          <CardContent className="flex-grow flex flex-col p-6">
            <ScrollArea
              className="flex-grow pr-4  h-[calc(50vh-450px)]"
              ref={scrollAreaRef}
            >
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
                    aria-label={
                      isRecording ? "Stop recording" : "Start recording"
                    }
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

      {/* Code Editor Component - Renders always but slides into view */}
      <CodeEditor
        isVisible={isCodeEditorVisible}
        onClose={() => setIsCodeEditorVisible(false)}
        onCodeSubmit={handleCodeSubmit}
      />
    </div>
  );
}
