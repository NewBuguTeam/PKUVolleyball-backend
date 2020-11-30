# app/__init__.py

# third-party imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Blueprint


# db variable initialization
db = SQLAlchemy()
user_blueprint = Blueprint('user', __name__)

from . import views

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')
db.init_app(app)

migrate = Migrate(app, db)

from app import models

app.register_blueprint(user_blueprint)


