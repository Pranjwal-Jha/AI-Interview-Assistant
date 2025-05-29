# speech_text/services/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
import io # Needed to read file from request
import os # Needed for file path manipulation or temporary saves

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

    if file:
        try:
            # Read the file directly from the stream
            # langchain_community.document_loaders.PyPDFLoader can take a file path.
            # We might need to save it temporarily or find a way to load from memory.
            # Let's save it temporarily for simplicity for now.
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

            # TODO: Use an LLM (like Gemini or your Ollama setup) to analyze the full_text
            # and extract skills, experience, education, and summary.
            # For now, let's return dummy data based on the extracted text.
            # You'll replace this with actual LLM calls.

            # Dummy analysis (replace with actual LLM call)
            analyzed_data = {
                "skills": ["Python", "Machine Learning"], # Extract from text
                "experience": ["3 years in NLP"], # Extract from text
                "education": ["Bachelor's Degree"], # Extract from text
                "summary": full_text[:200] + "..." # A snippet of the text as a dummy summary
            }


            return jsonify({"success": True, "data": analyzed_data}), 200

        except Exception as e:
            print(f"Error processing file: {e}")
            return jsonify({"success": False, "error": f"Error processing file: {e}"}), 500
    else:
         return jsonify({"success": False, "error": "File upload failed"}), 500


if __name__ == '__main__':
    # Ensure you are running this script and not your main.py for the backend API
    # Use debug=True for development (auto-reloads on code changes)
    app.run(debug=True, port=5000)
