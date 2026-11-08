import logging
import os
import socket
import sys

import redis
from flask import Flask, jsonify
from redis.exceptions import ConnectionError

app = Flask(__name__)

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    force=True
)

redis_client = redis.Redis(
    host = os.environ["REDIS_HOST"],
    port = int(os.environ["REDIS_PORT"]),
    decode_responses = True
)

@app.get("/")
def home():
    return jsonify({
        "message": "Hello DevOps",
        "host": socket.gethostname()
    })

@app.get("/visits")
def visits():
    count = redis_client.incr("visits")
    return jsonify({"visits": count})

@app.get("/health")
def health():
    try:
        status = redis_client.ping()
    except ConnectionError:
        status = False
    if status:
        return jsonify({"status": "ok"}), 200
    else:
        return jsonify({"status": "error"}), 503

if __name__ == "__main__":
    port = int(os.environ["APP_PORT"])
    app.run(host="0.0.0.0", port=port)