# coding=utf-8

import json
import time
import datetime
from flask import request, jsonify, render_template, redirect
import math
from .models import User, Team, Match, Game
from . import db

@app.route('/login/', method = ['GET', 'POST'])
def login():
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
        
    else
        return '''GETting /login/'''
    
    
@app.route('/viewMatches/', method = ['GET', 'POST'])
def viewMatches():
    if request.method == 'POST':
        pass
    else
        return '''GETting /viewMatches/'''
    

@app.route('/matchInfo/<id>/', method = ['GET', 'POST'])
def matchInfo(id):
    matchItem = db.session.query(Match).filter(Match.id == id).first()
    if matchItem is None:
        # corresponding match doesn't exist
        pass
    else:
        # respond match info to front-end
        
    
    
    pass