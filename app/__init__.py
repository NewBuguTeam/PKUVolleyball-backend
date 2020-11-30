# app/__init__.py

# third-party imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# db variable initialization
db = SQLAlchemy()


#def create_app(config_name):
app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')
db.init_app(app)

migrate = Migrate(app, db)

from app import models

if __name__ == '__main__':
    app.run()

