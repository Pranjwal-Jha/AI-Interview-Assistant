from langchain_google_genai import ChatGoogleGenerativeAI
import os
gemini_api_key=os.environ.get("GEMINI_API_KEY")
llm=ChatGoogleGenerativeAI(model="gemini-2.0-flash")
