import ollama 

conversation_history=[]

def blocked_output(user_query:str):
    response=ollama.chat(model='gemma3:4b',messages=[
        {
            'role':'user',
            'content':user_query,
        },
    ])
    print(response['message']['content'])

def streaming_response(user_query : str):
    global conversation_history
    conversation_history.append({
        'role':'user',
        'content':user_query,
    })
    assistant_response=""
    for chunk in ollama.chat(model='gemma3:4b',messages=conversation_history,stream=True):
        content_chunk=chunk['message']['content']
        print(content_chunk,end='',flush=True)
        assistant_response+=content_chunk

    conversation_history.append({
        'role':'assistant',
        'content':'assistant_response'
    })
    print('\n')

#streaming_response("Write a story about cat and owner from cat perspective")


