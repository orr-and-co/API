from flask import Blueprint

api = Blueprint("api", __name__)


@api.after_request  # blueprint can also be app~~
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    # Other headers can be added here if required
    return response


from .interests import *
from .posts import *
from .publishers import *
