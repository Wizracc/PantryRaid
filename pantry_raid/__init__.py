from flask import Flask, flash
from flask_login import LoginManager
from pantry_raid.models.database import Database
from pantry_raid.models.user import User
from pantry_raid.routes.api import api
from pantry_raid.routes.routes import router
from pantry_raid.routes.user_manager import user_manager


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config_name)
    app.db = Database(app.config)

    # Set up user authentication details
    app.secret_key = app.config['SECRET_KEY']  # CSRF prevention
    app.logman = LoginManager()
    app.logman.init_app(app)

    # Set up routes (views)
    app.register_blueprint(api)           # JSON API
    app.register_blueprint(router)        # Front-end routing
    app.register_blueprint(user_manager)  # User management
    app.logman.login_view = "user_manager.login"

    @app.logman.user_loader
    def load_user(uid):
        """Function to load a user based on ID. Must be nested to access the current Flask application without circular imports or working outside the application context.

        Returns
        -------
        string
            Unique ID associated with user, or None if no user found
        """
        try:
            user = User(doc=app.db.users.find_by_username(uid))
            return user
        except Exception:
            flash("Login failed.", "danger")
            return None


    return app
