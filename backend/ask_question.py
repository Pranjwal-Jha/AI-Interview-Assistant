from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import Field,BaseModel
from langchain_core.tools import tool
from typing import cast

class Question(BaseModel):
    name:str=Field(...,description="Name of a LeetCode question in lowercase joined with '-'")
    id:str=Field(...,description="question ID of the LeetCode question")
llm=ChatGoogleGenerativeAI(model="gemini-2.0-flash")
# make another attribute inside the class that is "question" which is output user will see when this node is ran, the gemini_response node will just choose and send the topic, rest of work will be handled by leetcode
@tool
def leetcode(topic:str)->dict:
    """get a leetcode question and it's corresponding id by sending a topic of your choice"""
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
        prompt=template.format(topic=topic)
        response=llm.invoke(prompt)
        response_string=cast(str,response.content)
        output=parser.parse(response_string)
        print(output)
        return {"question":output.name,"id":output.id}
    except Exception as e:
        print(e)
        return {}

leetcode.invoke("dp")
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
