"""
Secure Flask Application for Exercise 5: Docker Security with AppArmor
Listens on 0.0.0.0:5000 and provides root greeting and health check endpoints.
"""
import os
import sys
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, this is a secure Flask application running inside a Docker container!"

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "flask-apparmor",
        "python_version": sys.version.split()[0],
        "pid": os.getpid()
    }), 200

if __name__ == '__main__':
    # Flask listening on 0.0.0.0:5000
    app.run(host='0.0.0.0', port=5000)
