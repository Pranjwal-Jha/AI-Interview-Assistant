from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.document_loaders import PyPDFLoader
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage,HumanMessage
import json
import os
RESUME_PATH="resume.pdf"
history_file='test_template.json'
model=ChatGoogleGenerativeAI(model="gemini-2.0-flash",temperature=0.7)
print("Loading Resume...")
loader=PyPDFLoader(RESUME_PATH)
pages=loader.load_and_split()
if not pages:
    print("No Text could be extracted from the pages")
full_text="\n".join([page.page_content for page in pages])

try:
    if os.path.getsize(history_file)>0:
        with open(history_file,'r') as f:
            history_data=json.load(f)
            chat_history=[
                HumanMessage(content=msg['content']) if msg['type']=='human'
                else AIMessage(content=msg['content'])
                for msg in history_data
            ]
    else:
        chat_history=[]
except(FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Error loading the chat history ",e)
    chat_history=[]

def clear_history_file(history_file):
    with open(history_file,'w') as f:
        json.dump([],f)
    print("History is cleared")

def template_format_message(input):
    template=ChatPromptTemplate.from_messages([ 
        ("system", """You are an AI interviewer simulating a job interview.
        Ask questions based *only* on the resume content.
        Ask one question at a time based on: experience → skills → projects.
        if User types "debug" do not act as interviewer and act as normal AI
        --- START RESUME ---
        {resume_context}
        --- END RESUME ---"""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human","{user_input}")
    ])
    return template.invoke({
        "resume_context":full_text,
        "chat_history":chat_history,
        "user_input":input
    }) 
    

def main():
    initial_prompt="Okay I am ready for Interview"
    message=template_format_message(initial_prompt)
    result=model.invoke(message)
    print("AI Interviewer reply -> ",result.content)
    chat_history.append(HumanMessage(initial_prompt))
    chat_history.append(AIMessage(content=result.content))
    while True: 
        user_input=input("your input (Write 'exit' to exit, 'clear' to wipe history): ")
        if user_input=='exit':
            break
        elif user_input=='clear':
            chat_history.clear()
            clear_history_file(history_file)
            continue
        message=template_format_message(user_input)
        result=model.invoke(message)
        print("AI Interviewer reply -> ",result.content)
        chat_history.append(HumanMessage(content=user_input))
        chat_history.append(AIMessage(content=result.content))

    with open(history_file,'w') as f:
        json.dump([
            {'type':msg.type,"content":msg.content}
            for msg in chat_history
        ],f,indent=2)


if __name__=="__main__":
    main()
