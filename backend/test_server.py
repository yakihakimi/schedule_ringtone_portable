from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'Test endpoint working'})

@app.route('/api/ringtones', methods=['GET'])
def list_ringtones():
    return jsonify({'success': True, 'ringtones': [], 'count': 0})

if __name__ == '__main__':
    print("Starting test server...")
    app.run(host='0.0.0.0', port=5001, debug=True)



