from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import services.main as main
app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/transcribe")
async def transcribe_endpoint(audio: UploadFile = File(...)):
    # Read the file as bytes
    audio_bytes = await audio.read()
    
    # Call your service function from services/main.py
    transcribed_text = main.transcribe_text(audio_bytes)
    
    # Return the result
    return {"text": transcribed_text}

# Other endpoints would follow a similar pattern

@app.post("/analyze_resume")
async def analyze_resume_endpoint(resume: UploadFile = File(...)):
    # You would import and call a function from services/resume.py
    # For now, returning mock data
    return {
        "skills": ["Python", "Machine Learning"],
        "experience": ["ML Engineer at Tech Co"],
        "education": ["MS in Computer Science"],
        "summary": "Experienced ML engineer"
    }

@app.post("/generate_response")
async def generate_response_endpoint(request: dict = Body(...)):
    # You would import and call a function from services/llm.py
    # For now, returning mock data
    return {"response": f"This is an AI response to: {request.get('user_input', '')}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)

