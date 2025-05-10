# app/__init__.py
import os
from flask import Flask
from .config import config_by_name
from .extensions import db, migrate, jwt, cors

def create_app(config_name='dev'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Ensure the instance folder exists for SQLite
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite:///'):
        instance_path = os.path.join(app.root_path, '..', 'instance') # Assuming instance folder is one level up from 'app'
        if not os.path.exists(instance_path):
            try:
                os.makedirs(instance_path)
                print(f"Created instance folder at {instance_path}")
            except OSError as e:
                print(f"Error creating instance folder at {instance_path}: {e}")
        # Adjust config if 'instance_path' is used by SQLAlchemy directly
        if 'instance' in app.config['SQLALCHEMY_DATABASE_URI'] and not app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite:///' + instance_path):
             # This logic might need refinement based on how SQLALCHEMY_DATABASE_URI is structured
             pass


    # Ensure paper save directory exists
    paper_save_dir = app.config['PAPER_SAVE_DIR']
    if not os.path.exists(paper_save_dir):
        try:
            os.makedirs(paper_save_dir, exist_ok=True)
            print(f"Paper save directory created/ensured at: {paper_save_dir}")
        except OSError as e:
            print(f"Error creating paper save directory at {paper_save_dir}: {e}")


    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}}) # Adjust origins for production

    # Register Blueprints
    from .api.auth import auth_bp
    from .api.papers import papers_bp
    from .api.rag import rag_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(papers_bp, url_prefix='/api/papers')
    app.register_blueprint(rag_bp, url_prefix='/api/rag')

    # Shell context for flask cli
    @app.shell_context_processor
    def ctx():
        from app.models.user import User # Import models here to avoid circularity
        from app.models.paper import PaperMetadata
        from app.models.chat import ChatMessage, ChatSession
        return {'app': app, 'db': db, 'User': User, 'PaperMetadata': PaperMetadata, 'ChatMessage': ChatMessage, 'ChatSession': ChatSession}

    return app