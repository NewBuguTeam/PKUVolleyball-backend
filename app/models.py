# app/models.py
# coding=utf-8

from app import db

umpire_match = db.Table('umpire_match',
        db.Column('umpireID', db.Integer, db.ForeignKey('users.id')),
        db.Column('matchID', db.Integer, db.ForeignKey('matches.id')),
        )
        
viceumpire_match = db.Table('viceumpire_match',
        db.Column('umpireID', db.Integer, db.ForeignKey('users.id')),
        db.Column('matchID', db.Integer, db.ForeignKey('matches.id')),
        )

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    username = db.Column(db.String(32))
    password = db.Column(db.String(256))
    isAdmin = db.Column(db.Boolean)
    icon = db.Column(db.String(1024))
    school = db.Column(db.String(16))
    umpireFee = db.Column(db.Integer)
    toBeUmpireIn = db.relationship('Match', secondary = umpire_match, backref = 'umpire')
    toBeViceUmpireIn = db.relationship('Match', secondary = viceumpire_match, backref = 'viceUmpire')

class Team(db.Model):
    __tablename__ = 'teams'
    
    name = db.Column(db.String(16), primary_key = True)
    gender = db.Column(db.Enum('M', 'F'), primary_key = True)
    inGroup = db.Column(db.Enum('A', 'B', 'C', 'D'))
    isUnified = db.Column(db.Boolean, default = False)
    schoolA = db.Column(db.String(16))
    schoolB = db.Column(db.String(16))

class Match(db.Model):
    __tablename__ = 'matches'
    
    id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    location = db.Column(db.String(32))
    matchTime = db.Column(db.TIMESTAMP)
    gender = db.Column(db.Enum('M', 'F'))
    stage = db.Column(db.Enum('A', 'B', 'C', 'D', '8', '4', '2'))
    teamA = db.Column(db.String(16), db.ForeignKey('teams.name'))
    teamB = db.Column(db.String(16), db.ForeignKey('teams.name'))
    point = db.Column(db.String(8))
    # We use 'backref' in db.relationship instead of declaring these 2 columns here
    #  so there would **not** be these columns explicitly in the database
    #  but we can still request for a query with class Match (i.e. this class) in python
    #  please see app/views.py for more information.
    # umpire = db.Column(db.Integer, db.ForeignKey('users.id'))
    # viceUmpire = db.Column(db.Integer, db.ForeignKey('users.id'))

class Game(db.Model):
    __tablename__ = 'games'
    
    inMatchID = db.Column(db.Integer, db.ForeignKey('matches.id'), primary_key = True)
    num = db.Column(db.Integer, primary_key = True)
    point = db.Column(db.String(8))
    duration = db.Column(db.Time)
    gameProcedure = db.Column(db.String(128))
    