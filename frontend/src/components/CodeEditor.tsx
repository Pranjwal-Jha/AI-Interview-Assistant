"use client";
import { useState, useRef, useEffect } from "react";
import { Editor } from "@monaco-editor/react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Play, Copy, RotateCcw, CheckCircle } from "lucide-react";

interface CodeEditorProps {
  isVisible: boolean;
  onClose: () => void;
  onCodeSubmit: (code: string) => void;
}

export default function CodeEditor({
  isVisible,
  onClose,
  onCodeSubmit,
}: CodeEditorProps) {
  const [code, setCode] = useState("");
  const editorRef = useRef<any>(null);
  const language = "cpp"; // Hardcode language to C++

  const [copied, setCopied] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  useEffect(() => {
    if (isVisible) {
      setCode(getDefaultCode());
      // Reset feedback states when opening editor
      setCopied(false);
      setSubmitSuccess(false); // Reset submit feedback
    }
  }, [isVisible]);

  const getDefaultCode = () => {
    return "// Write your C++ solution here\n#include <iostream>\nusing namespace std;\n\nint main() {\n    \n    return 0;\n}";
  };

  const handleEditorDidMount = (editor: any, monaco: any) => {
    editorRef.current = editor;

    // Add Ctrl+Enter or Cmd+Enter to submit code
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      handleSubmitCode();
    });
  };

  const handleSubmitCode = () => {
    if (code.trim()) {
      onCodeSubmit(code); // Call the prop function with the code

      // Trigger submit feedback
      setSubmitSuccess(true);
      setTimeout(() => {
        setSubmitSuccess(false);
      }, 1500); // 1500 milliseconds = 1.5 seconds for the green text
    }
  };

  const handleCopyCode = () => {
    navigator.clipboard.writeText(code);
    setCopied(true); // Set copied state to true
    // Set a timeout to revert the state back to false after 3 seconds
    setTimeout(() => {
      setCopied(false);
    }, 3000); // 3000 milliseconds = 3 seconds
  };

  const handleResetCode = () => {
    setCode(getDefaultCode());
  };

  // Use the 'translate-x-full' class to hide and slide
  // The containing div will handle positioning
  return (
    <div
      className={`fixed right-0 top-0 h-full w-1/2 bg-background border-l transform transition-transform duration-300 ease-in-out z-50 ${
        isVisible ? "translate-x-0" : "translate-x-full"
      }`}
    >
      <Card className="h-full rounded-none border-0 shadow-none">
        <CardHeader className="pb-4">
          <div className="flex justify-between items-start">
            <CardTitle className="text-lg">Code Editor (C++)</CardTitle>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              aria-label="Close editor"
            >
              ×
            </Button>
          </div>

          <div className="flex items-center gap-2 mt-4">
            {/* Language is now fixed, no dropdown needed */}
            <span className="px-3 py-1 border rounded text-xs bg-secondary text-secondary-foreground">
              C++
            </span>

            <div className="flex gap-1 ml-auto">
              {/* Copy Button with conditional icon */}
              <Button
                variant="outline"
                size="sm"
                onClick={handleCopyCode}
                aria-label="Copy code"
              >
                {/* Render CheckCircle if copied is true, otherwise render Copy */}
                {copied ? (
                  <CheckCircle className="h-3 w-3 text-green-500" />
                ) : (
                  <Copy className="h-3 w-3" />
                )}
              </Button>
              {/* Reset Button */}
              <Button
                variant="outline"
                size="sm"
                onClick={handleResetCode}
                aria-label="Reset code"
              >
                <RotateCcw className="h-3 w-3" />
              </Button>
              {/* Submit Button with conditional text color */}
              <Button
                size="sm"
                onClick={handleSubmitCode}
                className={submitSuccess ? "text-green-500" : ""} // Apply green text conditionally
              >
                <Play className="h-3 w-3 mr-1" />
                Submit (Ctrl+Enter)
              </Button>
            </div>
          </div>
        </CardHeader>

        <CardContent className="p-0 h-[calc(100%-8rem)]">
          {" "}
          {/* Adjust height based on header */}
          <Editor
            height="100%"
            language={language}
            value={code}
            onChange={(value) => setCode(value || "")}
            onMount={handleEditorDidMount}
            theme="vs-dark" // Or any theme you prefer
            options={{
              minimap: { enabled: false },
              fontSize: 14,
              lineNumbers: "on",
              roundedSelection: false,
              scrollBeyondLastLine: false,
              automaticLayout: true,
              tabSize: 2,
              wordWrap: "on",
              // Disable context menu and other features for simplicity
              // contextmenu: false,
            }}
          />
        </CardContent>
      </Card>
    </div>
  );
}
