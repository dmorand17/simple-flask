#!/usr/bin/env python3
from flask import Flask, jsonify
import platform

app = Flask(__name__)


@app.route("/", methods=["GET"])
def say_hello():
    return jsonify({"msg": f"Hello from Flask - {platform.machine()}"})


@app.route("/health")
def health():
    return jsonify({"msg": "Healthy"})


if __name__ == "__main__":
    # Please do not set debug=True in production
    app.run(host="0.0.0.0", port=5000, debug=True)
