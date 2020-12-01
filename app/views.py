# app/views.py
# coding = utf-8

import json
import time
import datetime
from flask import request, jsonify, render_template, redirect, session, url_for
import math
from .models import User, Team, Match, Game
from app import db
from . import guest_blueprint as guest
from . import umpire_blueprint as umpire
from . import admin_blueprint as admin


def string_toDatetime(string):
    return datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S")


def datetime_toTimestamp(dateTime):
    return time.mktime(dateTime.timetuple()) * 1000.0 + (dateTime.microsecond / 1000.0)


def datetime_toString(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")


# compare current time and match time, return status 
# (since there is no 'status' column in database)
#   variables: match: a query result from db
def matchStatus(match):
    current_time = datetime.datetime.now()
    if match.point is None:
        if match.matchTime > current_time:
            return '未开始'
        else:
            return '进行中'
    else:
        if match.matchTime > current_time: 
            # There must be something wrong here
            return '??????'
        else:
            return '已结束'
    

@guest.route('/')
def index():
    return '''INDEX'''


@guest.route('/login/', methods = ['GET', 'POST'])
def login():
    if 'username' in session:
        username = session['username']
        isAdmin = session['isAdmin']
        return f"login successfully as {username}, an " + ('Admin' if isAdmin else 'Umpire')
    else:
        if request.method == 'POST':
            username = str(json.loads(request.values.get("username")))
            password = str(json.loads(request.values.get("password")))
        #    username = request.form['username']
        #    password = request.form['password']
            current_user = db.session.query(User).filter(User.username == username).first()
            if current_user is None:
                # username doesn't exist
                return 'username doesn\'t exist'
            elif current_user.password != password:
                # wrong password
                return 'password error'
            else:
                # login successfully
                session['username'] = username
                session['isAdmin'] = current_user.isAdmin
                return f"login successfully as {username}, an " + ('Admin' if current_user.isAdmin else 'Umpire')
                   
        else:
            # GET method gives a form here for testing database
            return '''
            <form action = "" method = "post">
                <p><input type = "text" name = "username"></p>
                <p><input type = "password" name = "password"></p>
                <p><input type = "submit" value = "登录"></p>
            </form>
                '''
    
    
@guest.route('/logout/')
def logout():
    if 'username' in session:
        session.pop('username', None)
        session.pop('isAdmin', None)
    return redirect(url_for('guest.login'))
    
   
@guest.route('/viewMatches/', methods = ['GET', 'POST'])
def viewMatches():
    if request.method == 'POST':
        lastShowed = int(json.loads(request.values.get("lastShowed")))
        numLimit = int(json.loads(request.values.get("numOfMatchesRequesting")))
        # lastShowed = int(request.form['lastShowed'])
        # numLimit = int(request.form['numOfMatchesRequesting'])
        print('viewMatches', lastShowed, numLimit)
        
        matchList = []
        matches = db.session.query(Match).filter().all()
        
        def getMatchTime(m):
            return m.matchTime
            
        matches.sort(key = getMatchTime)
        
        # get appropriate num of matches to respond
        
        if lastShowed == -1:                
            matches = matches[-numLimit:]
        else:
            lastShowedMatch = db.session.query(Match).filter(Match.id == lastShowed).all()
            try:
                lastShowedIndex = matches.index(lastShowedMatch[0])
                
                if lastShowedIndex <= numLimit:
                    matches = matches[0:lastShowedIndex]
                else:
                    matches = matches[lastShowedIndex - numLimit : lastShowedIndex]
            except ValueError:
                print("the match indicated by \"lastShowed\" doesn't exist in the database")
                
        # convert database object into dict and then JSON
        
        for m in matches:
            match_dict = {
                'id': m.id,
                'gender': m.gender,
                'for_group_X_or_knockout_X': m.stage,
                'time': datetime_toString(m.matchTime),
                'status': matchStatus(m),
                'teamA': m.teamA,
                'teamB': m.teamB,
                'location': m.location,
                'umpire': m.umpire,
                'viceUmpire': m.viceUmpire,
                'point': m.point,
            }
            matchList.append(match_dict)
        jsonData = {
            'matches': matchList
        }
        return json.dumps(jsonData)
        
    else:
        # GET method gives a form here for testing database & logic
        return '''
        <form action = "" method = "post">
            <p><input type = "text" name = "lastShowed"></p>
            <p><input type = "text" name = "numOfMatchesRequesting"></p>
            <p><input type = "submit" value = "确定"></p>
        </form>
            '''
    

@guest.route('/matchInfo/<id>/')
def matchInfo(id):
    print('matchInfo:', id)
    match = db.session.query(Match).filter(Match.id == id).first()
    if match is None:
        # corresponding match doesn't exist
        return f"match {id} not found"
    else:
        # respond match info to front-end
        games = db.session.query(Game).filter(Game.inMatchID == id).all()
        
        def getGameNum(g):
            return g.num
        games.sort(key = getGameNum)
        
        game_list = []
        for g in games:
            game_dict = {
                'point': g.point,
                'duration': str(g.duration),
                'procedure': g.gameProcedure
            }
            game_list.append(game_dict)
        
        match_dict = {
            'id': match.id,
            'gender': match.gender,
            'for_group_X_or_knockout_X': match.stage,
            'time': datetime_toString(match.matchTime),
            'status': matchStatus(match),
            'teamA': match.teamA,
            'teamB': match.teamB,
            'location': match.location,
            'umpire': match.umpire,
            'viceUmpire': match.viceUmpire,
            'point': match.point,
            'detailedPoints': game_list
        }
        return json.dumps(match_dict)
    