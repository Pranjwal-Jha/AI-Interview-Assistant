from langchain_core.messages import AIMessage
from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from fetch_question import leetcode
from parse_pdf import greet_candidate
from shared import InterviewChat
from gemini_llm import llm
sql_conn=sqlite3.connect("checkpoint.sqlite",check_same_thread=False)
memory=SqliteSaver(sql_conn)
tool_node=ToolNode([leetcode])

def get_gemini_response(state:InterviewChat):
    messages=state["messages"]
    resume_text=state["resume"]
    interview_prompt=ChatPromptTemplate.from_messages([
        ("system","""You are an AI interviewer currently conducting an interview with the candidate. Briefly acknowledge the candidate’s previous answers or progress so far, mentioning specifics when possible. Then, ask a follow-up or next question that logically continues the conversation based on the candidate’s responses or resume. If a user asks for leetcode or any type of coding question you must use the tools to pass a topic of your choice. (dynamic programming, greedy etc.)
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
    })#,{"configurable":{"thread_id":"thread_1"}},
    )
    return{
        "messages":[response]
    }

def should_continue(state:InterviewChat):
    """Determine if you want to ask a leetcode question or continue with the interview"""
    last_message=state["messages"][-1]
    if isinstance(last_message,AIMessage) and last_message.tool_calls:
        return "tools"
    else:
        return END

def route_message(state: InterviewChat):
    messages = state["messages"]
    # Check if this is the first user message (resume upload)
    if len(messages) == 1 and "resume" in messages[0].content.lower():
        return "greet_candidate"
    else:
        return "get_gemini_response"

def custom_tool_node(state:InterviewChat):
    message=state["messages"]
    last_message=message[-1]
    if isinstance(last_message,AIMessage) and last_message.tool_calls:
        tool_call=last_message.tool_calls[0]
        if tool_call["name"]=="leetcode":
            topic=tool_call["args"]["topic"]
            result=leetcode.invoke(topic)

            updated_state={
                "current_question_name":result.get("question"),
                "current_question_id":result.get("id")
            }
            tool_message={
                "role":"assistant",
                "content": f"Here's a coding question for you:\n\n{result.get('description', 'No description available')}"
            }
            return{
                "messages":[AIMessage(content=tool_message["content"])],
                **updated_state
            }
    return {"messages":[]}

graph=StateGraph(InterviewChat)
graph.add_node("greet_candidate",greet_candidate)
graph.add_node("get_gemini_response",get_gemini_response)
graph.add_node("tools",custom_tool_node)
graph.add_conditional_edges(
    START,
    route_message,
    {
        "greet_candidate":"greet_candidate",
        "get_gemini_response":"get_gemini_response"
    }
)
# graph.add_edge(START,"greet_candidate")
graph.add_edge("greet_candidate",END)
graph.add_conditional_edges(
    "get_gemini_response",
    should_continue,
    {
        "tools":"tools",
        END:END
    }
)
compiled_graph=graph.compile(checkpointer=memory)
