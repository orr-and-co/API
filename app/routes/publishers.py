from flask import jsonify, request

from .. import db
from ..models import Publisher
from . import app


@app.route("/api/publisher", methods=["PUT"])
def create_publisher():
    # TODO check authorization
    name = request.json.get("name")
    email = request.json.get("email")
    password = request.json.get("password")

    publisher = Publisher(name=name, email=email)
    publisher.password = password

    db.session.add(publisher)
    db.session.commit()

    return "", 201


@app.route("/api/publisher", methods=["GET"])
def get_publisher():
    id = request.json.get("id")

    publisher = Publisher.query.get(id)

    if publisher is not None:
        json_data = {"name": publisher.name, "email": publisher.email}

        return jsonify(json_data)
    else:
        return {}, 404
