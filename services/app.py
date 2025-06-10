# speech_text/services/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_core.messages import HumanMessage
from langchain_community.document_loaders import PyPDFLoader
import os # Needed for file path manipulation or temporary saves
from llm_response import compiled_graph
from deepgram_test import transcription_service_deepgram
app = Flask(__name__)
CORS(app) # Enable CORS for all origins

# Resume Analysis endpoint
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
            temp_dir = "/tmp" # Using /tmp for temporary files, adjust if needed
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
