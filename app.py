#!/usr/bin/env python3
import platform
import uuid

from flask import Flask, jsonify

app = Flask(__name__)

movie_list = [
    {
        "_id": str(uuid.uuid4()),
        "title": "Toy Story",
        "rating": "G",
        "release_date": "11/22/1995",
    },
    {
        "_id": str(uuid.uuid4()),
        "title": "Cast Away",
        "rating": "PG-13",
        "release_date": "07/06/1994",
    },
    {
        "_id": str(uuid.uuid4()),
        "title": "Forrest Gump",
        "rating": "PG-13",
        "date_of_birth": "07/06/1994",
    },
    {
        "_id": str(uuid.uuid4()),
        "title": "Green Mile",
        "rating": "R",
        "release_date": "12/10/1999",
    },
]


@app.route("/system", methods=["GET"])
def system_details():
    return jsonify(
        {
            "machine": f"{platform.machine()}",
            "platform": f"{platform.platform()}",
            "processor": f"{platform.processor()}",
            "architecture": f"{platform.architecture()}",
            "system": f"{platform.system()}",
        }
    )


@app.route("/", methods=["GET"])
def index():
    return jsonify(
        [
            {
                "method": "GET",
                "endpoint": "/system",
                "response": "returns system details",
            },
            {
                "method": "GET",
                "endpoint": "/api/v1/movies/list",
                "response": "returns list of movie details",
            },
            {
                "method": "GET",
                "endpoint": "/api/v1/movies/<string:movie_id>",
                "response": "returns movie information based on movie id",
            },
        ]
    )


@app.route("/ping")
def health():
    return "pong"


# @app.route("/api/v1/movies/list")
@app.route("/movies/list")
def get_movies_list():
    return jsonify(movie_list), 200


# @app.route("/api/v1/movies/<string:movie_id>")
@app.route("/movies/<string:movie_id>")
def get_movie_by_id(movie_id):
    for movie in movie_list:
        if movie_id in movie["_id"]:
            return jsonify(movie), 200
        return jsonify({"error": "Movie does not exist"}), 404


if __name__ == "__main__":
    # Please do not set debug=True in production
    app.run(host="0.0.0.0", port=5000, debug=True)
