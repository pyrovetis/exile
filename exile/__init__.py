import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_compress import Compress
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_minify import Minify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = "auth.login"
login.login_message = "Please log in to access this page."
mail = Mail()
moment = Moment()
compress = Compress()
limiter = Limiter(
    get_remote_address,
    default_limits=["200 per day", "500 per hour"],
    storage_uri="memory://",
)
minify = Minify(html=True, js=True, cssless=True, static=True)


def get_cache_key(request):
    return request.url


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    compress.init_app(app)
    minify.init_app(app)
    limiter.init_app(app)

    # errors
    from exile.errors import bp as errors_bp

    app.register_blueprint(errors_bp)

    # auth
    from exile.auth import bp as auth_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")

    # api
    from exile.api import bp as api_bp

    app.register_blueprint(api_bp, url_prefix="/api")

    # dashboard
    from exile.dashboard import bp as dashboard_bp

    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")

    # main
    from exile.main import bp as main_bp

    app.register_blueprint(main_bp)

    if not app.debug and not app.testing:

        if not os.path.exists("logs"):
            os.mkdir("logs")
        file_handler = RotatingFileHandler("logs/log", maxBytes=10240, backupCount=10)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s " "[in %(pathname)s:%(lineno)d]"
            )
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info("Exile startup")

    return app


from exile import models
