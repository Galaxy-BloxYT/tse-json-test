from flask import Flask, jsonify
import random
import time

app = Flask(__name__)

@app.get("/results")
def results():
    return jsonify({
        "simulation": True,
        "timestamp": int(time.time()),
        "candidates": [
            {"name": "Flávio Bolsonaro", "votes": random.randint(10000, 20000)},
            {"name": "Lula", "votes": random.randint(10000, 20000)}
        ]
    })
