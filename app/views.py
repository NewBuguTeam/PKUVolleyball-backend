# coding=utf-8

import json
import time
import datetime
from flask import request, jsonify, render_template, redirect
import math
from .models import User, Team, Match, Game
from app import db
from . import user_blueprint as user

@user.route('/')
def index():
    return '''INDEX'''

@user.route('/login/', methods = ['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = str(json.loads(request.values.get("username")))
        password = str(json.loads(request.values.get("password")))
        db_query = db.session.query(User).filter(User.username == username).first()
        if db_query is None:
            # username doesn't exist    
            pass
        elif db_query.password != password:
            # wrong password
            pass
        else:
            # login successfully
            pass
        
    else:
        return '''GETting /login/'''
        
        
@user.route('/login/<username>')
def login(username):
    db_query = db.session.query(User).filter(User.username == username).first()
    if db_query is None:
        # username doesn't exist    
        pass
    elif db_query.password != password:
        # wrong password
        pass
    else:
        # login successfully
        pass
    return '''login with username'''
    
    
@user.route('/viewMatches/', methods = ['GET', 'POST'])
def viewMatches():
    if request.method == 'POST':
        pass
    else:
        return '''GETting /viewMatches/'''
    

@user.route('/matchInfo/<id>/', methods = ['GET', 'POST'])
def matchInfo(id):
    matchItem = db.session.query(Match).filter(Match.id == id).first()
    if matchItem is None:
        # corresponding match doesn't exist
        pass
    else:
        # respond match info to front-end
        pass
        
    