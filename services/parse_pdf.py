from typing import Annotated, Sequence, TypedDict
from langgraph.constants import END, START
from langgraph.graph import StateGraph,add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import PyPDFLoader
import sqlite3
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import HumanMessage,AIMessage,BaseMessage
RESUME_PATH="resume.pdf"
llm=ChatGoogleGenerativeAI(model="gemini-2.0-flash")
sql_conn=sqlite3.connect(database="checkpoint.sqlite",check_same_thread=False)
memory=SqliteSaver(sql_conn)

class InterviewChat(TypedDict):
    messages:Annotated[Sequence[BaseMessage],add_messages]
    resume:str

# loader=PyPDFLoader(RESUME_PATH)
# resume_text=loader.load()

def greet_candidate(state:InterviewChat):
    messages=state["messages"]
    resume_text=state['resume']
    greeting_prompt=ChatPromptTemplate.from_messages([
        ("system", """You are an AI interviewer. Your first task is to greet the candidate warmly and briefly acknowledge their resume, mentioning something specific if possible. Then, ask an opening question based on their resume.
        --- START RESUME ---
        {resume_context}
        --- END RESUME ---"""),
        MessagesPlaceholder(variable_name="messages")
    ])
    response=llm.invoke(greeting_prompt.invoke({
        "resume_context":resume_text,
        "messages":messages
    }))
    return{
        "messages":[response]
    }

def call_llm(state:InterviewChat):
    messages=state['messages']
    resume_text=state['resume']
    prompt=ChatPromptTemplate.from_messages([
        ("system", """You are an AI interviewer simulating a job interview.
        Ask questions based *only* on the resume content.
        If the user attempts to deviate from the interview context, respond strictly and remind them to stay focused on the job interview
        Ask one question at a time based on: experience then skills and then the projects.
        if User types "debug" do not act as interviewer and act as normal AI
        --- START RESUME ---
        {resume_context}
        --- END RESUME ---"""),
        MessagesPlaceholder(variable_name="messages")
    ])
    llm_with_prompt=prompt | llm
    response=llm_with_prompt.invoke({"resume_context":resume_text,"messages":messages})
    return{
        "messages":[response]
    }

graph=StateGraph(InterviewChat)
graph.add_node("greet_candidate",greet_candidate)
graph.add_edge(START,"greet_candidate")
graph.add_edge("greet_candidate",END)

compiled_graph=graph.compile(checkpointer=memory)

# while True:
#     user_input=input("_>")
#     if user_input in ['exit','quit']:
#         break

#     result=compiled_graph.invoke({
#         "messages":[HumanMessage(content=user_input)],
#         "resume":"\n".join([doc.page_content for doc in resume_text])
#     },
#     config={"configurable": {"thread_id": "thread_1"}}
#     )
#     print("Output -> ",result['messages'][-1].content)

# memory.delete_thread("thread_1")
# print("Conversation History Cleared")
