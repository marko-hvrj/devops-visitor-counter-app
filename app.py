import os
import socket
from flask import Flask, jsonify

app = Flask(__name__)

@app.get("/")
def home():
    return jsonify({
        "message": "Hello DevOps",
        "host": socket.gethostname()
    })

if __name__ == "__main__":
    port = int(os.environ["APP_PORT"])
    app.run(host="0.0.0.0", port=port)