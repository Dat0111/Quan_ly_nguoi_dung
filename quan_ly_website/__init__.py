from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_caching import Cache

db = SQLAlchemy()
mail = Mail()
cache = Cache()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    mail.init_app(app)
    cache.init_app(app)

    with app.app_context():
        db.create_all()  # Tạo database và bảng

    from .routes import main as main_blueprint # type: ignore
    app.register_blueprint(main_blueprint)

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app
