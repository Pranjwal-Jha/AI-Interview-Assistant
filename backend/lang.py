from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import Field,BaseModel
from langchain_core.tools import tool
from typing import cast,TypedDict,Annotated,Sequence
from langchain_core.messages import AIMessage, HumanMessage,BaseMessage
from langgraph.constants import END, START
from langgraph.graph import StateGraph,add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
sql_conn=sqlite3.connect("checkpoint.sqlite",check_same_thread=False)
memory=SqliteSaver(sql_conn)

class Question(BaseModel):
    description:str=Field(...,description="Question statement")
    name:str=Field(...,description="Name of a LeetCode question in lowercase joined with '-'")
    id:str=Field(...,description="question ID of the LeetCode question")

class InterviewChat(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
llm=ChatGoogleGenerativeAI(model="gemini-2.0-flash")
@tool
def leetcode(question:str)->dict:
    """getting a leetcode question and it's corresponding id """
    parser=PydanticOutputParser(pydantic_object=Question)

    template = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful AI that gives a single LeetCode question on the topic {topic}.
    Respond ONLY with JSON in the following format:
    {{
    "description":"<leetcode question statement with input/output>"
    "name": "<question-name-in-lowercase-with-hyphens>",
    "id": "<leetcode-question-id>"
    }}"""),
    ])
    try:
        prompt=template.format(topic=question)
        response=llm.invoke(prompt)
        response_string=cast(str,response.content)
        output=parser.parse(response_string)
        # print(output)
        return {"description":output.description,"question":output.name,"id":output.id}
    except Exception as e:
        print(e)
        return {}
tool_node=ToolNode([leetcode])
llm_with_tools=llm.bind_tools([leetcode])
def should_continue(state:InterviewChat):
    """Determine if you want to ask a leetcode question"""
    last_message=state["messages"][-1]
    if isinstance(last_message,AIMessage) and last_message.tool_calls:
        return "tools"
    else:
        return END

def generate_response(state:InterviewChat):
    return{
        "messages":[llm_with_tools.invoke(state["messages"])]
    }

graph=StateGraph(InterviewChat)
graph.add_node("generate",generate_response)
graph.set_entry_point("generate")
graph.add_node("tools",tool_node)
graph.add_conditional_edges(
    "generate",
    should_continue,
    {
        "tools":"tools",
        END:END
    }
)
app=graph.compile()

while True:
    user_input=input("Enter _> ")
    if user_input.lower() in ['exit','quit']:
        break
    response=app.invoke(
        {
            "messages":HumanMessage(content=user_input)
    },{"configurable":{"thread_id":"thread_1"}}
    )
    print("AI -> ",response["messages"][-1].content)
