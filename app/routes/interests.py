from flask import abort, jsonify, request

from .. import db
from ..models import Interest
from . import api
from .authentication import auth


@api.route("/interests/", methods=["GET"])
def get_interests():
    """
    Returns all current :class:`Interests`.

    **Route**: /api/v1/interests/

    **Method**: GET

    :return: Array of interest names + descriptions
    """
    return jsonify(
        [
            {"name": interest.name, "description": interest.description}
            for interest in Interest.query.all()
        ]
    )


@api.route("/interests/", methods=["PUT"])
@auth.login_required
def create_interests():
    """
    Create a new interest.

    **Route**: /api/v1/interests/

    **Method**: PUT

    :param name: Name of the Interest.
    :type name: str

    :param description: Brief description of the Interest.
    :type description: str

    :return: 201
    """
    if request.json is None:
        abort(400)

    name = request.json.get("name") or abort(400)
    description = request.json.get("description") or abort(400)

    interest = Interest(name=name, description=description)

    db.session.add(interest)
    db.session.commit()

    return 201, ""


@api.route("/interests/<name>/", methods=["PATCH"])
@auth.login_required
def update_interests(name: str):
    """
    Update an interest by name.

    **Route**: /api/v1/interests/name/

    **Method**: PATCH

    :param description: New description of the Interest.
    :type description: str

    :return: 201
    """
    if request.json is None:
        abort(400)

    description = request.json.get("description") or abort(400)

    interest = Interest.query.filter(Interest.name == name).first_or_404()
    interest.description = description

    db.session.commit()

    return 201, ""


@api.route("/interests/<name>/", methods=["DELETE"])
@auth.login_required
def delete_interests(name: str):
    """
    Delete an interest by name.

    **Route**: /api/v1/interests/name/

    **Method**: DELETE

    :return: 201
    """
    Interest.query.filter(Interest.name == name).delete(synchronize_session="fetch")
    db.session.commit()

    return 201, ""
