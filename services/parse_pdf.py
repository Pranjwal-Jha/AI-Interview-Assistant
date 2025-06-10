from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from shared import InterviewChat
from gemini_llm import llm
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
    })#,{"configurable":{"thread_id":"thread_1"}},
    )
    return{
        "messages":[response]
    }

# def call_llm(state:InterviewChat):
#     messages=state['messages']
#     resume_text=state['resume']
#     prompt=ChatPromptTemplate.from_messages([
#         ("system", """You are an AI interviewer simulating a job interview.
#         Ask questions based *only* on the resume content.
#         If the user attempts to deviate from the interview context, respond strictly and remind them to stay focused on the job interview
#         Ask one question at a time based on: experience then skills and then the projects.
#         if User types "debug" do not act as interviewer and act as normal AI
#         --- START RESUME ---
#         {resume_context}
#         --- END RESUME ---"""),
#         MessagesPlaceholder(variable_name="messages")
#     ])
#     llm_with_prompt=prompt | llm
#     response=llm_with_prompt.invoke(
#         {"resume_context":resume_text,"messages":messages},
#         {"configurable":{"thread_id":"thread_1"}},
#     )
#     return{
#         "messages":[response]
#     }

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
