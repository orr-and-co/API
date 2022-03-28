from flask import Blueprint

api = Blueprint("api", __name__)


@api.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Authorization,Content-Type"
    return response


from .interests import *
from .posts import *
from .publishers import *
