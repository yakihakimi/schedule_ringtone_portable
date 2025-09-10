from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'], 
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

@app.route('/health', methods=['GET', 'OPTIONS'])
def health():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response
    return jsonify({'status': 'healthy', 'message': 'Debug server running'})

@app.route('/api/ringtones', methods=['GET', 'OPTIONS'])
def list_ringtones():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response
    
    print("DEBUG: list_ringtones endpoint called")
    response = jsonify({
        'success': True,
        'ringtones': [],
        'count': 0,
        'message': 'Debug endpoint working'
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/api/ringtones', methods=['POST', 'OPTIONS'])
def save_ringtone():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response
    
    print("DEBUG: save_ringtone endpoint called")
    response = jsonify({
        'success': True,
        'message': 'Ringtone created successfully!',
        'format': 'mp3',
        'filename': 'test_ringtone.mp3',
        'file_path': '/ringtones/mp3_ringtones/test_ringtone.mp3',
        'mp3_created': True,
        'wav_created': False
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == '__main__':
    print("Starting debug server on port 5000...")
    print("Available endpoints:")
    print("  GET  /health")
    print("  GET  /api/ringtones")
    print("  POST /api/ringtones")
    app.run(host='0.0.0.0', port=5000, debug=True)
