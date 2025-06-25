from flask import Flask, request, jsonify, Response
import json
from flask_cors import CORS
from langchain_core.messages import HumanMessage,AIMessage
from langchain_community.document_loaders import PyPDFLoader
import os

from langchain_core.messages.ai import AIMessage
from llm_response import compiled_graph
from submission_detail import get_submission_detail
from stt import transcription_service_deepgram
app = Flask(__name__)
CORS(app) # Enable CORS for all origins

@app.route('/analyze_resume', methods=['POST'])
def analyze_resume_endpoint():
    if 'resume' not in request.files:
        return jsonify({"success": False, "error": "No resume file provided"}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"}), 400
    session_id=request.form.get('sessionId')
    if not session_id:
        return jsonify({"success": False, "error": "Invalid Session"}), 400
    if file:
        try:
            temp_dir = "/tmp"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            filename=file.filename or "uploaded_resume.pdf"
            temp_path = os.path.join(temp_dir, filename)
            file.save(temp_path)

            print(f"Saved temporary file to {temp_path}")

            loader = PyPDFLoader(temp_path)
            pages = loader.load_and_split()
            # Clean up the temporary file
            os.remove(temp_path)
            print(f"Removed temporary file {temp_path}")


            if not pages:
                return jsonify({"success": False, "error": "No text could be extracted from the PDF"}), 400

            full_text = "\n".join([page.page_content for page in pages])
            result=compiled_graph.invoke({
                "messages":[HumanMessage(content="This is my resume")],
                "resume":full_text
            },
            config={"configurable": {"thread_id": session_id}}
            )
            response=result['messages'][-1].content
            return jsonify({"success": True, "data": response,"sessionId":session_id}), 200

        except Exception as e:
            print(f"Error processing file: {e}")
            return jsonify({"success": False, "error": f"Error processing file: {e}"}), 500
    else:
         return jsonify({"success": False, "error": "File upload failed"}), 500

@app.route('/transcribe',methods=['POST'])
def transcribe_endpoint():
    if 'audio' not in request.files:
        return jsonify({"success":False,"error":"NO FILE"}),400
    audio_file=request.files['audio']
    if audio_file.filename=='':
        return jsonify({"success": False, "error": "No selected file"}), 400
    audio_data=audio_file.read()
    transcribed_text=transcription_service_deepgram(audio_data)
    if transcribed_text:
        return jsonify({"success": True, "text": transcribed_text}), 200
    else:
        return jsonify({"success": False, "error": "Could not transcribe audio"}), 400

@app.route('/generate_response',methods=['POST'])
def get_llm_response():
    try:
        data=request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No JSON data provided"}), 400
        user_input=data.get('user_input')
        session_id=data.get('session_id')
        if not session_id:
            return jsonify({"success": False, "error": "Invalid Session"}), 400
        resume_data=data.get('resume_data')
        ai_response=compiled_graph.invoke({
            "messages":[HumanMessage(content=user_input)],
            "resume":resume_data or ""
        },{"configurable":{"thread_id":session_id}})
        response_content=ai_response['messages'][-1].content
        return jsonify({"success":True,"response":response_content}),200
    except Exception as e:
        print(f"Error in generate_response: {e}")
        return jsonify({"success": False, "error": f"Server error: {str(e)}"}), 500

#Look into streaming response more and SSE
@app.route('/generate_response_stream', methods=['POST'])
def get_llm_response_stream():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        user_input = data.get('user_input')
        session_id = data.get('session_id')

        if not user_input:
            return jsonify({"error": "No user input provided"}), 400

        if not session_id:
            return jsonify({"error": "Session ID not provided"}), 400

        resume_data = data.get('resume_data')

    except Exception as e:
        return jsonify({"error": f"Error parsing request: {str(e)}"}), 400

    def generate():
        try:
            for message_chunk, metadata in compiled_graph.stream({
                "messages": [HumanMessage(content=user_input)],
                "resume": resume_data or ""
            },
            stream_mode="messages",
            config={"configurable": {"thread_id": session_id}}
            ):
                if isinstance(message_chunk,AIMessage) and message_chunk.content:
                    # Send each chunk as Server-Sent Events (SSE)
                    print(f"MSGCHUNK {message_chunk.content}")
                    yield f"data: {json.dumps({'content': message_chunk.content, 'type': 'chunk'})}\n\n"

            # Send end signal
            yield f"data: {json.dumps({'type': 'end'})}\n\n"

        except Exception as e:
            print(f"Error in generate_response_stream: {e}")
            yield f"data: {json.dumps({'error': f'Server error: {str(e)}'})}\n\n"

    return Response(
        generate(),
        mimetype='text/event-stream',  # Changed to proper SSE mimetype
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
    )

@app.route('/submit_code', methods=['POST'])
def submit_code_endpoint():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No JSON data provided"}), 400

        code = data.get('code')
        session_id=data.get('session_id')
        if not code or not session_id:
            return  jsonify({"success": False, "error": "Missing required fields (code or session_id)"}),400
        current_state = compiled_graph.get_state({"configurable": {"thread_id": session_id}})
        if current_state and current_state.values:
            problem_slug=current_state.values.get('current_question_name')
            question_id=current_state.values.get('current_question_id')
        else:
            problem_slug = 'best-time-to-buy-and-sell-stock'
            question_id = '121'
        if not problem_slug or not question_id:
             return jsonify({"success": False, "error": "Missing required fields (code, problem_slug, or question_id)"}), 400

        submission_result = get_submission_detail(code, problem_slug, question_id)

        return jsonify(submission_result), 200

    except Exception as e:
        print(f"Error in submit_code endpoint: {e}")
        return jsonify({"success": False, "error": f"Server error processing submission: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
