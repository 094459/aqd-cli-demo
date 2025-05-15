import os
from flask import Flask
from src.extensions import db, login_manager
from src.models.user import User

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_mapping(
            SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
            SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///survey_app.db'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            VERSION=os.environ.get('APP_VERSION', 'dev'),
        )
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Set up user loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from src.routes.auth import auth_bp
    from src.routes.main import main_bp
    from src.routes.surveys import survey_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(survey_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
