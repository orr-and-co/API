import string
from secrets import randbelow

from flask import abort, jsonify, request

from .. import db
from ..models import Publisher
from . import app

PASSWORD_CHARACTERS = string.digits + string.ascii_letters + string.punctuation


@app.route("/api/publisher", methods=["PUT"])
def create_publisher():
    """

    Create new publisher. Authorization required.

    **Route:** /api/publisher/

    **Method:** PUT

    :param name: The name of the new :class:`Publisher`
    :param email: The valid email of the new :class:`Publisher`

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
    name = request.json.get("name")
    email = request.json.get("email")

    # check if any parameters are not provided
    if name and email is None:
        abort(400)

    # check if the email is invalid
    if "@" not in email or "." not in email:
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


@app.route("/api/publisher", methods=["GET"])
def get_publisher():
    """
    Get name and email of publisher by ID. Authorization required

    **Route:** /api/publisher/

    **Method:** GET

    :param id: The ID of the publisher to lookup

    :returns: :class:`Publisher`

    .. code-block:: json

            {
                "name": "name",
                "email": "email"
            }
    """
    id = request.json.get("id")

    publisher = Publisher.query.get(id)

    if publisher is not None:
        json_data = {"name": publisher.name, "email": publisher.email}

        return jsonify(json_data)
    else:
        abort(404)
