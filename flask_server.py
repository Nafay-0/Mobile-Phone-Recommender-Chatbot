import os
import time
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import requests

load_dotenv()

DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')

app = Flask(__name__, static_folder="build/static", template_folder = 'build')
CORS(app)

AUDIO_FOLDER = 'Temp_Audio'
os.makedirs(AUDIO_FOLDER, exist_ok=True)

def generate_unique_filename(prefix, extension):
    """Generate a unique filename with a timestamp."""
    timestamp = int(time.time() * 1000)  # Current time in milliseconds
    return f"{prefix}_{timestamp}.{extension}"

def generate_response(question):
    time.sleep(2)
    return f"Dummy Response for {question}"

def generate_transcript(filepath):

    url = "https://api.deepgram.com/v1/listen?nova-2-general"

    file = open(filepath,"rb")
    payload = file
    headers = {
        "Content-Type": "audio/*",
        "Accept": "application/json",
        "Authorization": f"token {DEEPGRAM_API_KEY}",
    }

    response = requests.post(url, data=payload, headers=headers)

    file.close()
    os.remove(filepath)

    text = response.json()["results"]["channels"][0]['alternatives'][0]["transcript"]

    return text

@app.route('/text-query', methods=['POST'])
def query_text():
    data = request.json.get('question')
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    answer = generate_response(data)
    # Process the text data here
    return jsonify({'answer': answer})

@app.route('/audio-query', methods=['POST'])
def query_audio():
    
    if 'audio' not in request.files:
        return 'No audio part', 400

    file = request.files['audio']

    if file.filename == '':
        return 'No selected file', 400

    if file:
        filename = generate_unique_filename('temp_recording', 'mp3')
        filepath = (os.path.join(AUDIO_FOLDER,filename))
        file.save(filepath)

        answer = generate_transcript(filepath)

        return jsonify({'answer': answer})

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)
