from langchain_core.messages import HumanMessage
from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from parse_pdf import greet_candidate
from shared import InterviewChat
from gemini_llm import llm
sql_conn=sqlite3.connect("checkpoint.sqlite",check_same_thread=False)
memory=SqliteSaver(sql_conn)

def get_gemini_response(state:InterviewChat):
    messages=state["messages"]
    resume_text=state["resume"]
    interview_prompt=ChatPromptTemplate.from_messages([
        ("system","""You are an AI interviewer currently conducting an interview with the candidate. Briefly acknowledge the candidate’s previous answers or progress so far, mentioning specifics when possible. Then, ask a follow-up or next question that logically continues the conversation based on the candidate’s responses or resume.
        Example:
        'Thanks for your explanation on the last question about system design. You mentioned experience with microservices in your resume — can you elaborate on how you handled data consistency across those services?'
        Keep the tone professional but conversational, and stay focused on assessing the candidate’s skills and experience
        ---START RESUME---
        {resume_context}
        ---END RESUME---"""),
        MessagesPlaceholder(variable_name="messages")
    ])
    response=llm.invoke(interview_prompt.invoke({
        "resume_context":resume_text,
        "messages":messages
    }),{"configurable":{"thread_id":"thread_1"}},
    )
    return{
        "messages":[response]
    }

def should_continue(state:InterviewChat):
    """Determine if you want to ask more questions to the User or want to end the Interview"""
    messages = state["messages"]
    if len(messages)>0 and isinstance(messages[-1],HumanMessage):
        return "get_gemini_response"
    else:
        return END

graph=StateGraph(InterviewChat)
graph.add_node("greet_candidate",greet_candidate)
graph.add_node("get_gemini_response",get_gemini_response)
graph.add_edge(START,"greet_candidate")
# graph.add_edge("greet_candidate","get_gemini_response")
graph.add_conditional_edges(
    "greet_candidate",
    should_continue,
    {
        "get_gemini_response":"get_gemini_response",
        END:END
    }
)
graph.add_conditional_edges(
    "get_gemini_response",
    should_continue,
    {
        "get_gemini_response":"get_gemini_response",
        END:END
    }
)
# graph.add_edge("greet_candidate",END)
compiled_graph=graph.compile(checkpointer=memory)
