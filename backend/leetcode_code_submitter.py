import requests,json,os
from dotenv import load_dotenv
# from pathlib import Path
load_dotenv()

def get_submission_id(typed_code:str,problem_slug:str,question_id:str):
    csrf_token = os.environ.get("LEETCODE_CSRF")
    session = os.environ.get("LEETCODE_SESSION")

    if not csrf_token or not session:
        print("No Keys 2")
        exit()

    headers = {
        "Content-Type": "application/json",
        "x-csrftoken": csrf_token,
        "Cookie": f"LEETCODE_SESSION={session}; csrftoken={csrf_token}",
        "Referer": "https://leetcode.com/",
        "Origin": "https://leetcode.com",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36", #!imp
    }
    submission_url=f"https://leetcode.com/problems/{problem_slug}/submit/"
    payload = {
        "lang": "cpp",
        "question_id": question_id,
        "typed_code":typed_code}
    submit_response=requests.post(
        submission_url,
        headers=headers,
        json=payload
    )
    print("Status ->",submit_response.status_code)
    if submit_response.status_code==200:
        response_data=submit_response.json()
        # print(json.dumps(response_data,indent=2))
        submission_id=response_data["submission_id"]
    else:
        print(f"Error -> {submit_response.status_code}")
        print(f"Error -> {submit_response.text}")
        exit()
    print("The code submitted succesfully!")
    return submission_id
