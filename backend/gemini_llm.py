from langchain_google_genai import ChatGoogleGenerativeAI
import os
from fetch_question import leetcode
gemini_api_key=os.environ.get("GEMINI_API_KEY")
if not gemini_api_key:
    print("Error GEMINI API KEY missing")
model=ChatGoogleGenerativeAI(model="gemini-2.0-flash",api_key=gemini_api_key)
llm=model.bind_tools([leetcode])
