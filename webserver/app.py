from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import requests
import re

# Serve static files from /app/static so docker volume mount works
# (compose.yaml mounts ./webserver/static -> /app/static)
app = Flask(__name__, static_folder="/app/static", static_url_path="/static")

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1")

@app.route('/')
def index():
    # Serve the SPA/HTML from the configured static folder
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    prompt = data.get('prompt', '')
    include_thinking = bool(data.get('include_thinking', False))

    # Build payload for Ollama. Per your backend contract, the toggle
    # must be a top-level "think" property on the payload object.
    payload = {
        'model': OLLAMA_MODEL,
        'prompt': prompt,
        'stream': False,
        'think': include_thinking,
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        # Ollama may return both 'response' and (optionally) 'thinking' when think=true
        text = result.get('response', '')
        thinking = result.get('thinking', '') if include_thinking else ''
        return jsonify({'response': text, 'thinking': thinking})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
