from flask import Flask, jsonify
import os

app = Flask(__name__)

PORT = os.environ.get("PORT", 5000)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "okay", "instance": PORT})

@app.route('/process', methods=['GET'])
def process():
    return jsonify({"status": "in process", "instance": PORT})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)