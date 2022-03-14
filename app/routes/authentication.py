from flask import abort, current_app, g, jsonify
from flask_httpauth import HTTPBasicAuth

from ..models import Publisher
from . import api

auth = HTTPBasicAuth()

"""
Authentication scheme provided by Flask-HTTPAuth

Uses standard Authentication header, with "Basic TOKEN", where TOKEN is the base64 
    encoding of "username:password".
"""


@auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == "":
        return False

    if password == "":
        if email_or_token == current_app.config["ADMIN_OVERRIDE"]:
            return Publisher(name="admin", email="", full_admin=True)

        g.current_user = Publisher.verify_auth_token(email_or_token)
        g.token_used = True
        if g.current_user is not None:
            return g.current_user
        else:
            return None

    publisher = Publisher.query.filter_by(email=email_or_token.lower()).first()
    if not publisher:
        return None

    g.current_user = publisher
    g.token_used = False

    if publisher.check_password(password):
        return g.current_user
    else:
        return None


@api.route("/tokens/", methods=["POST"])
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        abort(403)
    return jsonify(
        {"token": g.current_user.generate_auth_token(43200), "expiration": 43200}
    )
