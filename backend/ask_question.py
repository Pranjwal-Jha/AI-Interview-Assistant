from langchain_core.messages import AIMessage,BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langgraph.graph import StateGraph
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import Field,BaseModel
from gemini_llm import llm
from typing import cast

class Question(BaseModel):
    name:str=Field(...,description="Name of a LeetCode question in lowercase joined with '-'")
    id:str=Field(...,description="question ID of the LeetCode question")

def leetcode(question:str):
    parser=PydanticOutputParser(pydantic_object=Question)

    template = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful AI that gives a single LeetCode question on the topic {topic}.
    Respond ONLY with JSON in the following format:
    {{
    "name": "<question-name-in-lowercase-with-hyphens>",
    "id": "<leetcode-question-id>"
    }}"""),
    ])
    try:
        prompt=template.format(topic=question)
        response=llm.invoke(prompt)
        response_string=cast(str,response.content)
        output=parser.parse(response_string)
        return {"question":output.name,"id":output.id}
    except Exception as e:
        print(e)
        return None

# leetcode("dp")

# while True:
#     user_input=input("Enter -> ")
#     if user_input.lower() in ["exit","break"]:
#         break
#     try:
#         prompt=template.format(topic=user_input)
#         response=llm.invoke(prompt)
#         output=parser.parse(response.content)
#         print(f"{output.name} : {output.id}")
#     except Exception as e:
#         print(e)
