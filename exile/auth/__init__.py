from flask import Blueprint

bp = Blueprint("auth", __name__)

from exile.auth import routes
