from typing import Annotated, Sequence, TypedDict,Optional
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages

class InterviewChat(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    resume: str
    current_question_name:Optional[str]
    current_question_id:Optional[str]
