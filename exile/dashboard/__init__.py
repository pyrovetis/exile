from flask import Blueprint

bp = Blueprint("dashboard", __name__)

from exile.dashboard import routes
