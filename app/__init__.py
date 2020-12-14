# app/__init__.py

# third-party imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Blueprint


# db variable initialization
db = SQLAlchemy()
guest_blueprint = Blueprint('guest', __name__)
umpire_blueprint = Blueprint('umpire', __name__)
admin_blueprint = Blueprint('admin', __name__)

def create_app():

    from . import views

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')
    db.init_app(app)

    migrate = Migrate(app, db)

    from . import models

    app.register_blueprint(guest_blueprint)
    app.register_blueprint(umpire_blueprint, url_prefix = '/umpire')
    app.register_blueprint(admin_blueprint, url_prefix = '/admin')
    
    return app

