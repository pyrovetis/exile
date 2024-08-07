from flask import Blueprint

bp = Blueprint("main", __name__)

from exile.main import routes
