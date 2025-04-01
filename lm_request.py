from httpx import stream
import openai
from openai import OpenAI
from openai.resources.chat.completions import messages


client=OpenAI(base_url="http://127.0.0.1:1234/v1",api_key="not-needed")

def chunk_output(prompt:str):
    completion=client.chat.completions.create(model="local-model", messages=[{
        "role":"user","content":prompt
    }])

    model_reply=completion.choices[0].message.content
    print(model_reply)


def streaming_output(prompt : str):
    stream=client.chat.completions.create(model="local-model",messages=[
        {"role":"user","content":prompt}
    ],stream=True)
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content,end="",flush=True)

# print("The Ai says ->\n")
# print(model_reply)
