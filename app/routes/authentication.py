from flask import abort, g, jsonify
from flask_httpauth import HTTPBasicAuth

from ..models import Publisher
from . import api

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == "":
        return False

    if password == "":
        g.current_user = Publisher.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None

    publisher = Publisher.query.filter_by(email=email_or_token.lower()).first()
    if not publisher:
        return False

    g.current_user = publisher
    g.token_used = False

    return publisher.check_password(password)


@api.route("/tokens/", methods=["POST"])
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        abort(403)
    return jsonify(
        {"token": g.current_user.generate_auth_token(43200), "expiration": 43200}
    )
