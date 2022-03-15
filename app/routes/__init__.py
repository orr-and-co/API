from flask import Blueprint

api = Blueprint("api", __name__)

from .interests import *
from .posts import *
from .publishers import *
