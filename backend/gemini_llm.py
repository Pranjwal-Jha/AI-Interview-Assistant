from langchain_google_genai import ChatGoogleGenerativeAI
import os
gemini_api_key=os.environ.get("GEMINI_API_KEY")
if not gemini_api_key:
    print("Error GEMINI API KEY missing")
llm=ChatGoogleGenerativeAI(model="gemini-2.0-flash",api_key=gemini_api_key)
