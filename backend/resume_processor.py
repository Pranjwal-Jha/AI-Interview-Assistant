from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from common_types import InterviewChat
from llm_config import llm
RESUME_PATH="resume.pdf"

# loader=PyPDFLoader(RESUME_PATH)
# resume_text=loader.load()

def greet_candidate(state:InterviewChat):
    messages=state["messages"]
    resume_text=state['resume']
    greeting_prompt=ChatPromptTemplate.from_messages([
        ("system", """You are an AI interviewer. Your first task is to greet the candidate warmly and briefly acknowledge their resume, mentioning something specific if possible, you can add an opening question based on their resume.
        --- START RESUME ---
        {resume_context}
        --- END RESUME ---"""),
        MessagesPlaceholder(variable_name="messages")
    ])
    response=llm.invoke(greeting_prompt.invoke({
        "messages":messages,
        "resume_context":resume_text
    })
    )
    return{
        "messages":[response]
    }
