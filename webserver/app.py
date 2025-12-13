from flask import Flask, request, jsonify, send_from_directory
import os
import requests

# Serve static files from /app/static so docker volume mount works
# (compose.yaml mounts ./webserver/static -> /app/static)
# Use the Docker-mounted /app/static path when available; otherwise fall back to the
# local repo path `webserver/static` so the UI loads correctly during local dev.
static_path = "/app/static" if os.path.isdir("/app/static") else os.path.join(os.path.dirname(__file__), 'static')
app = Flask(__name__, static_folder=static_path, static_url_path="/static")

# URL of the brain service
BRAIN_URL = os.getenv("BRAIN_URL", "http://localhost:7000")

@app.route('/')
def index():
    # Serve the SPA/HTML from the configured static folder
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/debug/rag', methods=['GET'])
def rag_debug():
    # Proxy to brain's debug endpoint if available
    try:
        r = requests.get(f"{BRAIN_URL}/v1/debug/rag", params=request.args, timeout=30)
        return (r.text, r.status_code, {"Content-Type": r.headers.get("Content-Type", "application/json")})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_proxy():
    """Proxy the brain service health endpoint for same-origin access from the UI."""
    try:
        r = requests.get(f"{BRAIN_URL}/v1/healthz", timeout=5)
        return (r.text, r.status_code, {"Content-Type": r.headers.get("Content-Type", "application/json")})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 503

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        r = requests.post(f"{BRAIN_URL}/v1/chat", json=request.json, timeout=300)
        return (r.text, r.status_code, {"Content-Type": r.headers.get("Content-Type", "application/json")})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/memory', methods=['GET'])
def list_memory():
    try:
        r = requests.get(f"{BRAIN_URL}/v1/memory", params=request.args, timeout=60)
        return (r.text, r.status_code, {"Content-Type": r.headers.get("Content-Type", "application/json")})
    except Exception as err:
        return jsonify({'error': str(err)}), 500


@app.route('/api/memory', methods=['POST'])
def create_memory():
    try:
        r = requests.post(f"{BRAIN_URL}/v1/memory", json=request.json, timeout=60)
        return (r.text, r.status_code, {"Content-Type": r.headers.get("Content-Type", "application/json")})
    except Exception as err:
        return jsonify({'error': str(err)}), 500


@app.route('/api/memory/<mem_id>', methods=['DELETE'])
def delete_memory(mem_id: str):
    try:
        r = requests.delete(f"{BRAIN_URL}/v1/memory/{mem_id}", timeout=30)
        return (r.text, r.status_code, {"Content-Type": r.headers.get("Content-Type", "application/json")})
    except Exception as err:
        return jsonify({'error': str(err)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
