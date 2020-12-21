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
from sqlalchemy import or_, and_


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


'''
    given a school name, find its group in gender 'M' and 'F'.
    pay attention if the school belongs to a unified team.
'''
@guest.route('/school2group/<school>/')
def school2group(school):
    Mteam = db.session.query(Team).filter(
        Team.gender == 'M', or_(Team.name == school, 
            and_(Team.isUnified == True, 
                or_(Team.schoolA == school, Team.schoolB == school)))).first()
    Fteam = db.session.query(Team).filter(
        Team.gender == 'F', or_(Team.name == school, 
            and_(Team.isUnified == True, 
                or_(Team.schoolA == school, Team.schoolB == school)))).first()
                
    returnDict = {
        'Mgroup': '',
        'Fgroup': ''
    }
    
    if Mteam is not None:
        returnDict['Mgroup'] = Mteam.inGroup
    if Fteam is not None:
        returnDict['Fgroup'] = Fteam.inGroup
    
    return json.dumps(returnDict)
    
    
@admin.route('/addMatch/', methods = ['GET', 'POST'])
def addMatch():
    curIden = testIdentity()
    if curIden == 0:
            # no permission, error
        return 'no permission'
    elif curIden == -1:
        # not login yet, error
        return 'not login yet'
    if request.method == 'POST':
        # '''
        gender = json.loads(request.values.get("gender"))
        stage = json.loads(request.values.get("for_group_X_or_knockout_X"))
        # what type is "time"?
        matchTime = json.loads(request.values.get("time"))
        teamA = json.loads(request.values.get("teamA"))
        teamB = json.loads(request.values.get("teamB"))
        location = json.loads(request.values.get("location"))
        '''
        teamA = request.form["teamA"]
        teamB = request.form["teamB"]
        location = None
        matchTime = "2020-10-10 20:00:00"
        gender = 'M'
        stage = 'D'
        # '''
        
        try:
            Agroup = db.session.query(Team).filter(Team.name == teamA, Team.gender == gender).first().inGroup
            
        except:
            return 'Unknown team: \"' + teamA + '\"'
        
        try:
            Bgroup = db.session.query(Team).filter(Team.name == teamB, Team.gender == gender).first().inGroup
        except:
            return 'Unknown team: \"' + teamB + '\"'
            
        if teamA == teamB:
            return 'Repeated team name'
            
        if 'A' <= stage <= 'D' and (Agroup != Bgroup or Agroup != stage):
            return 'Group error'
        

        newMatch = Match(
            id = 0, location = location, matchTime = matchTime, gender = gender,
            stage = stage, teamA = teamA, teamB = teamB, point = "0:0",
            umpire = None, viceUmpire = None
        )
        db.session.add(newMatch)
        db.session.commit()
        return 'Add new match successfully'
        
        
    else:
        return '''
            <form action = "" method = "post">
                <p><input type = "text" name = "teamA"></p>
                <p><input type = "text" name = "teamB"></p>
                <p><input type = "submit" value = "OK"></p>
            </form>
                '''


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
        # '''
        newUsername = json.loads(request.values.get("newUsername"))
        newPassword = json.loads(request.values.get("newPassword"))
        newUserIsAdmin = bool(json.loads(request.values.get("newIsAdmin")))
        newSchool = json.loads(request.values.get("newSchool"))
        '''
        newUsername = request.form["newUsername"]
        newPassword = request.form["newPassword"]
        newUserIsAdmin = ("newUserIsAdmin" in request.form)
        newSchool = request.form["newUserSchool"]
        '''
        
        # maybe school name should be checked here?
        
        if db.session.query(User).filter(User.username == newUsername).count() != 0:
            return 'User \"' + newUsername + '\" already existed'
        newUser = User(
            id = 0, username = newUsername, password = newPassword,
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
                <p><input type = "text" name = "newPassword"></p>
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
    returnDict = {
        'success': None,
        'username': '',
        'isAdmin': None,
        'school': '',
        'errorType': ''
    }
    if 'username' in session:
        returnDict['success'] = True
        returnDict['username'] = session['username']
        returnDict['isAdmin'] = session['isAdmin']
        returnDict['school'] = session['school']
        return json.dumps(returnDict)
    else:
        if request.method == 'POST':
            # '''
            username = json.loads(request.values.get("username"))
            password = json.loads(request.values.get("password"))
            '''
            username = request.form['username']
            password = request.form['password']
            '''
            current_user = db.session.query(User).filter(User.username == username).first()
            if current_user is None:
                # username doesn't exist
                returnDict['success'] = False
                returnDict['errorType'] = 'username'
                returnDict['username'] = username
                return json.dumps(returnDict)
            elif current_user.password != password:
                # wrong password
                returnDict['success'] = False
                returnDict['errorType'] = 'password'
                return json.dumps(returnDict)
            else:
                # login successfully
                session['username'] = username
                session['isAdmin'] = current_user.isAdmin
                session['school'] = current_user.school
                returnDict['success'] = True
                returnDict['username'] = session['username']
                returnDict['isAdmin'] = session['isAdmin']
                returnDict['school'] = session['school']
                return json.dumps(returnDict)
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
        session.pop('school', None)
    return redirect(url_for('guest.login'))
    
@guest.route('/viewGrouping/')
def viewGrouping():
    groupLists = []
    # Querying Male Grouping
    for g in 'M', 'F':
        curGenderGroup = {"gender": g}
        curGroupList = []
        for G in 'A', 'B', 'C', 'D':
            curGroup = {"name": G}
            curTeamList = []
            curQuery = db.session.query(Team).filter(Team.gender == g, Team.inGroup == G).all()
            for t in curQuery:
                curTeamList.append(t.name)
            curGroup["teamList"] = curTeamList
            curGroupList.append(curGroup)
        curGenderGroup["groupList"] = curGroupList
        groupLists.append(curGenderGroup)
    return json.dumps({"groupLists": groupLists})

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
        # '''
        gender = json.loads(request.values.get("gender"))
        group = json.loads(request.values.get("group"))
        '''
        gender = request.form['gender']
        group = json.loads(request.form['group'])
        '''
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
                    db.session.rollback()
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
                            db.session.rollback()
                            return 'repeated team: ' + v[0]
                        elif v[1] in teams:
                            db.session.rollback()
                            return 'repeated team: ' + v[1]
                        curTeam = Team(
                            name = k, gender = gender, inGroup = groupName,
                            isUnified = True, schoolA = v[0], schoolB = v[1]
                        )
                    db.session.add(curTeam)
        
        if max(groupSize) - min(groupSize) >= 2:
            # Grouping is not balanced, error
            db.session.rollback()
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
        # '''
        beginsAt = json.loads(request.values.get("beginsAt"))
        matchDays = int(json.loads(request.values.get("matchDaysRequesting")))
        direction = json.loads(request.values.get("direction"))
        '''
        beginsAt = request.form['beginsAt']
        matchDays = 2
        direction = 'D'
        '''
        print('viewMatches', beginsAt)
        
        matchList = []
        if direction == 'U':
            matches = db.session.query(Match).filter(Match.matchTime < (beginsAt + " 00:00:00")).all()
        else:
            matches = db.session.query(Match).filter(Match.matchTime > (beginsAt + " 00:00:00")).all()
        
        def getMatchTime(m):
            return m.matchTime
            
        matches.sort(key = getMatchTime)
        
        
            
        # get matches in the latest 2 match days where matches are not showed to respond
        
        totalNumMatches = len(matches)
        matchDayCounter = 0
        if direction == 'U':
            for _ in range(totalNumMatches-1, -1, -1):
                curMatchDate = datetime_toString(matches[_].matchTime).split(' ')[0]
                if curMatchDate != beginsAt:
                    if matchDayCounter == matchDays:
                        matches = matches[_+1 : ]
                        break
                    else:
                        matchDayCounter = matchDayCounter + 1
                        beginsAt = curMatchDate
        else:
            for _ in range(totalNumMatches):
                curMatchDate = datetime_toString(matches[_].matchTime).split(' ')[0]
                if curMatchDate != beginsAt:
                    if matchDayCounter == matchDays:
                        matches = matches[:_]
                        break
                    else:
                        matchDayCounter = matchDayCounter + 1
                        beginsAt = curMatchDate
                        
        # convert database object into dict and then JSON
        
        for m in matches:
            if m.umpire is not None:
                umpireIcon = db.session.query(User).filter(User.id == m.umpire).first().icon
            else:
                umpireIcon = ''
            if m.viceUmpire is not None:
                viceUmpireIcon = db.session.query(User).filter(User.id == m.viceUmpire).first().icon
            else:
                viceUmpireIcon = ''
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
                'umpireIcon': umpireIcon,
                'viceUmpire': m.viceUmpire,
                'viceUmpireIcon': viceUmpireIcon,
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
            
        if match.umpire is not None:
            umpireIcon = db.session.query(User).filter(User.id == match.umpire).first().icon
        else:
            umpireIcon = ''
        if match.viceUmpire is not None:
            viceUmpireIcon = db.session.query(User).filter(User.id == match.viceUmpire).first().icon
        else:
            viceUmpireIcon = ''
                
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
            'umpireIcon': umpireIcon,
            'viceUmpire': match.viceUmpire,
            'viceUmpireIcon': viceUmpireIcon,
            'point': match.point,
            'detailedPoints': game_list
        }
        return json.dumps(match_dict)


@umpire.route('/confirmPoints/', methods = ['GET', 'POST'])
def confirmPoints():
    curIden = testIdentity()
    if curIden == 1:
            # no permission, error
        return 'no permission'
    elif curIden == -1:
        # not login yet, error
        return 'not login yet'
    if request.method == 'POST':
        # '''
        id = int(json.loads(request.values.get("id")))
        point = json.loads(request.values.get("point"))
        detailedPoints = json.loads(json.loads(request.values.get("detailedPoints")))
        '''
        id = int(request.form["id"])
        point = request.form["point"]
        detailedPoints = json.loads(request.form["detailedPoints"])
        '''
        
        returnDict = {
            'success': None,
            'error': ''
        }
        
        curMatch = db.session.query(Match).filter(Match.id == id).first()
        if curMatch is None:
            returnDict['success'] = False
            returnDict['error'] = 'Match id doesn\'t exist'
            return json.dumps(returnDict)
        
        intpoint = [int(p) for p in point.split(':')]
        gameNum = sum(intpoint)
        if gameNum != len(detailedPoints):
            returnDict['success'] = False
            returnDict['error'] = 'Number of games doesn\'t match the point'
            return json.dumps(returnDict)
        
        pointTest = [0, 0]
        for g in detailedPoints:
            gPoint = g['point'].split(':')
            if int(gPoint[0]) > int(gPoint[1]):
                pointTest[0] = pointTest[0] + 1
            else:
                pointTest[1] = pointTest[1] + 1
        if intpoint != pointTest:
            returnDict['success'] = False
            returnDict['error'] = 'Detailed points doesn\'t match the point'
            return json.dumps(returnDict)
            
        curMatch.point = point
        db.session.commit()
        
        curGameNum = 1
        for g in detailedPoints:
            game = Game(
                inMatchID = id, num = curGameNum, point = g['point'], 
                duration = g['duration'], gameProcedure = g['procedure']
            )
            print(game)
            db.session.add(game)
            db.session.commit()
            curGameNum = curGameNum + 1
        returnDict['success'] = True
        return json.dumps(returnDict)
    else:
        # GET method gives a form here for testing database & logic
        return '''
        <form action = "" method = "post">
            <p><input type = "text" name = "id"></p>
            <p><input type = "text" name = "point"></p>
            <p><input type = "text" name = "detailedPoints"></p>
            <p><input type = "submit" value = "确定"></p>
        </form>
            '''


@umpire.route('/umpireRequest/', methods = ['GET', 'POST']
def umpireRequest():
    curIden = testIdentity()
    if curIden == 1:
            # no permission, error
        return 'no permission'
    elif curIden == -1:
        # not login yet, error
        return 'not login yet'
    
    if request.method == 'POST':
        pass
    else:
        pass
