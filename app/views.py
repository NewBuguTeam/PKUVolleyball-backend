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


# Tests if current user has logged in and if so, his identity.
#  returns -1 for not logged in, 0 for umpire, 1 for admin.
def testIdentity():
    if 'username' not in session:
        return -1
    elif session['isAdmin'] == True:
        return 1
    else:
        return 0
        

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
    
    
@admin.route('/addUser/', methods = ['GET', 'POST'])
def addUser():
    curIden = testIdentity()
    if curIden == 0:
            # no permission, error
        return 'no permission'
    elif curIden == -1:
        # not login yet, error
        return 'not login yet'
    if request.method == 'POST':
        
        # newUsername = json.loads(request.values.get("newUsername"))
        # newUserIsAdmin = boolean(json.loads(request.values.get("newUserIsAdmin")))
        # newSchool = json.loads(request.values.get("newUserSchool"))
        newUsername = request.form["newUsername"]
        newUserIsAdmin = ("newUserIsAdmin" in request.form)
        newSchool = request.form["newUserSchool"]
        
        # maybe school name should be checked here?
        
        if db.session.query(User).filter(User.username == newUsername).count() != 0:
            return 'User \"' + newUsername + '\" already existed'
        newUser = User(
            id = 0, username = newUsername, password = newUsername,
            isAdmin = newUserIsAdmin, icon = None, school = newSchool,
            umpireFee = 0
        )
        db.session.add(newUser)
        db.session.commit()
        return 'New user successfully created'
    else:
        return '''
            <form action = "" method = "post">
                <p><input type = "text" name = "newUsername"></p>
                <p><input type = "text" name = "newUserSchool"></p>
                <p><input type = "checkbox" name = "newUserIsAdmin"></p>
                <p><input type = "submit" value = "登录"></p>
            </form>
                '''
        
        
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
            # username = json.loads(request.values.get("username"))
            # password = json.loads(request.values.get("password"))
            username = request.form['username']
            password = request.form['password']
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
    
@guest.route('/viewGrouping/')
def viewGrouping():
    group = {}
    # Querying Male Grouping
    for g in 'M', 'F':
        curGenderGroups = {}
        for G in 'A', 'B', 'C', 'D':
            curGroup = []
            curQuery = db.session.query(Team).filter(Team.gender == g, Team.inGroup == G).all()
            for t in curQuery:
                curGroup.append(t.name)
            curGenderGroups[G] = curGroup
        group[g] = curGenderGroups
    return json.dumps(group)

'''
1. ensure that Male or Female grouping is not set before, hence grouping can only be set only once
2. ensure that the grouping is balanced, i.e. maxnum - minnum < 2
3. ensure that there's no repeated team
4. check if the team is a unified team indicated by '-'
5. module logic:
    Firstly, front-end check all group members if there's any team named with '-'.
    if found, then it's a unified team. front-end find all unified team names, asking admin to enter how each unified team is formed, i.e. which two schools form the unified team.
    if no unified teams found or every unified team is well-defined, then the data is posted.
'''
@admin.route('/setGrouping/', methods = ['GET', 'POST'])
def setGrouping():
    curIden = testIdentity()
    if curIden == 0:
            # no permission, error
        return 'no permission'
    elif curIden == -1:
        # not login yet, error
        return 'not login yet'
        
    if request.method == 'POST':
        # gender = json.loads(request.values.get("gender"))
        # group = json.loads(request.values.get("group"))
        gender = request.form['gender']
        group = json.loads(request.form['group'])
        groupSize = []
        teams = set()
        
        # Check if the corresponding grouping is already given before
        temp = Team.query.filter(Team.gender == gender).count()
        if temp != 0:
            # error
            return 'grouping for ' + ('联赛组' if gender == 'M' else '女子组') + ' has already been given'
        
        for groupName in 'A', 'B', 'C', 'D':
            curGroup = group[groupName]
            print(curGroup)
            groupSize.append(len(curGroup))
            for k, v in curGroup.items():
                if k in teams:
                    # repeated team, error
                    return 'repeated team: ' + k
                else:
                    teams.add(k)
                    if len(v) == 0:
                        curTeam = Team(
                            name = k, gender = gender, inGroup = groupName,
                            isUnified = False
                        )
                    else:
                        if v[0] == v[1] or v[0] in teams:
                            return 'repeated team: ' + v[0]
                        elif v[1] in teams:
                            return 'repeated team: ' + v[1]
                        curTeam = Team(
                            name = k, gender = gender, inGroup = groupName,
                            isUnified = True, schoolA = v[0], schoolB = v[1]
                        )
                    db.session.add(curTeam)
        
        if max(groupSize) - min(groupSize) >= 2:
            # Grouping is not balanced, error
            return 'grouping is unbalanced in num'
            
        # No error, commit changes to database
        db.session.commit()
        return 'success'
    else:
        return '''
            <form action = "" method = "post">
                <p><input type = "text" name = "gender"></p>
                <p><input type = "text" name = "group"></p>
                <p><input type = "submit" value = "OK"></p>
            </form>
                '''
                    

'''
1. module logic:
    gets a date from the posted request, which indicates the date of the earliest match showed.
    then get the matches in the latest 2 match days before the given date.

'''
@guest.route('/viewMatches/', methods = ['GET', 'POST'])
def viewMatches():
    if request.method == 'POST':
        # beginsAt = json.loads(request.values.get("beginsAt"))
        beginsAt = request.form['beginsAt']
        print('viewMatches', beginsAt)
        
        matchList = []
        matches = db.session.query(Match).filter(Match.matchTime < (beginsAt + " 00:00:00")).all()
        
        def getMatchTime(m):
            return m.matchTime
            
        matches.sort(key = getMatchTime)
        
        
            
        # get matches in the latest 2 match days where matches are not showed to respond
        
        totalNumMatches = len(matches)
        matchDayCounter = 0
        for _ in range(totalNumMatches-1, -1, -1):
            curMatchDate = datetime_toString(matches[_].matchTime).split(' ')[0]
            if curMatchDate != beginsAt:
                if matchDayCounter == 2:
                    matches = matches[_+1 : ]
                    break
                else:
                    matchDayCounter = matchDayCounter + 1
                    beginsAt = curMatchDate
                    
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
                'umpireIcon': None,         # not implemented yet
                'viceUmpire': m.viceUmpire,
                'viceUmpireIcon': None,     # not implemented yet
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
            <p><input type = "text" name = "beginsAt"></p>
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
    