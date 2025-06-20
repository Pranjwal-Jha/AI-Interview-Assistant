from langchain_core.messages import AIMessage,BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langgraph.graph import StateGraph
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import Field,BaseModel

class LeetCode(BaseModel):
    name: str = Field(..., description="Name of a LeetCode question in lowercase joined with '-'")
    id: str = Field(..., description="question ID of the LeetCode question")

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
parser = PydanticOutputParser(pydantic_object=LeetCode)

template = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful AI that gives a single LeetCode question on the topic {topic}.
Respond ONLY with JSON in the following format:
{format_instructions}
"""),
])

# Use the chain approach - this is the correct way
chain = template | llm | parser

while True:
    user_input = input("Enter -> ")
    if user_input.lower() in ["exit", "break"]:
        break
    
    try:
        # This will work correctly
        output = chain.invoke({
            "topic": user_input,
            "format_instructions": parser.get_format_instructions()
        })
        print(output)
    except Exception as e:
        print(f"Error: {e}")
