import os
from flask import Flask
from config import Config
from app.extensions import db, login_manager
from flask import Flask, render_template


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Make sure the instance and upload folders exist
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions with this app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    with app.app_context():
        from app import models  # noqa: F401 — ensures models are registered

    # Register blueprints
   # Register blueprints
    from app.main.routes import main_bp
    app.register_blueprint(main_bp)

    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp)

    from app.admin.routes import admin_bp
    app.register_blueprint(admin_bp)

    from app.products.routes import products_bp
    app.register_blueprint(products_bp)

    @app.context_processor
    def inject_globals():
        from app.models import Category
        return dict(
            whatsapp_number=app.config['WHATSAPP_NUMBER'],
            nav_categories=Category.query.all()
        )
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    return app