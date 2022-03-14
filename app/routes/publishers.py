import re
import string
from secrets import randbelow

from flask import abort, jsonify, request

from .. import db
from ..models import Publisher
from . import api
from .authentication import auth

PASSWORD_CHARACTERS = string.digits + string.ascii_letters + string.punctuation


@api.route("/publisher/", methods=["PUT"])
@auth.login_required
def create_publisher():
    """
    Create new publisher. Authorization required.

    **Route:** /api/v1/publisher/

    **Method:** PUT

    :param name: The name of the new :class:`Publisher`
    :type name: str
    :param email: The valid email of the new :class:`Publisher`
    :type email: str

    :returns: :class:`Publisher` *with* plaintext password. The :class:`Publisher` will be
        prompted to change this on login. This is the **only** time you can view the
        first-login password!

    .. code-block:: json

            {
                "name": "name",
                "email": "email",
                "password": "..."
            }

    """
    if not auth.current_user().full_admin:
        abort(403)

    name = request.json.get("name")
    email = request.json.get("email")

    # check if any parameters are not provided
    if name and email is None:
        abort(400)

    # check if the email is invalid
    if not re.match(r"\S+@\S+\.\S+", email):
        abort(400)

    # if a publisher already exists with this email, abort
    existing = Publisher.query.filter(Publisher.email == email).first()

    if existing is not None:
        abort(409)

    else:
        # generate a random first-login password, that the user will be prompted to change
        # secrets module is used for cryptographically secure generation
        password = "".join(
            PASSWORD_CHARACTERS[randbelow(len(PASSWORD_CHARACTERS))] for _ in range(16)
        )

        publisher = Publisher(name=name, email=email)
        publisher.password = password

        db.session.add(publisher)
        db.session.commit()

        return jsonify({"name": name, "email": email, "password": password})


@api.route("/publisher/<int:id>/", methods=["GET"])
@auth.login_required
def get_publisher(id: int):
    """
    Get name and email of publisher by ID. Authorization required

    **Route:** /api/v1/publisher/id/

    **Method:** GET

    :param id: The ID of the publisher to lookup
    :type id: int

    :returns: :class:`Publisher`

    .. code-block:: json

            {
                "name": "name",
                "email": "email"
            }
    """
    if id is None:
        abort(400)

    publisher = Publisher.query.get(id)

    if publisher is not None:
        json_data = {"name": publisher.name, "email": publisher.email}

        return jsonify(json_data)
    else:
        abort(404)


@api.route("/publisher/", methods=["PATCH"])
@auth.login_required
def update_publisher():
    """
    Update :class:`Publisher` details.

    :param password: New password
    :type password: str
    :param email: New email
    :type email: str

    :return: 201
    """
    if request.json is None:
        abort(400)

    publisher = auth.current_user()

    if (password := request.json.get("password")) is not None:
        publisher.password = password

    if (email := request.json.get("email")) is not None:
        publisher.email = email

    db.session.commit()

    return "", 201
