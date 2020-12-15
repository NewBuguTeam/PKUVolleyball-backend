# tests.py

import os
import unittest
import json
import time
import datetime
from flask import abort, url_for, session
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Blueprint

from flask_testing import TestCase

from app import create_app, db, views
from app.models import User, Team, Match, Game

def db_add(Object):
    db.session.add(Object)
    db.session.commit()

class TestBase(TestCase):
    def create_app(self):
    
        app = create_app()
        app.config.update(
            SQLALCHEMY_DATABASE_URI='mysql://PKUVolleyball:PKU_Vo11eyball@localhost/PKUVolleyballDB_test'
        )
        
        return app

    def setUp(self):
        """
        Will be called before every test
        """
        db.create_all()
        
        db_add(User(
            id = 0, username = 'abc', password = 'abc',
            isAdmin = True, icon = None, school = None, umpireFee = 0
        ))
        
        db_add(User(
            id = 0, username = 'bcd', password = 'bcd',
            isAdmin = False, icon = None, school = None, umpireFee = 0
        ))
        
        db_add(Match(
            id = 0,
            location = '五四',
            matchTime = '2020-12-1 20:20:00',
            gender = 'M', stage = 'A',
            teamA = None, teamB = None,
            point = '3:1', umpire = None, viceUmpire = None
        ))
        
        db_add(Game(
            inMatchID = 1, num = 2, point = '25:21', duration = '00:20:20',
            gameProcedure = 'LJHSLKDJHFLKJ'
        ))
        
        db_add(Game(
            inMatchID = 1, num = 1, point = '21:25', duration = '00:24:20',
            gameProcedure = 'LJHSLKSDFLKJ'
        ))

        db_add(Game(
            inMatchID = 1, num = 4, point = '25:9', duration = '00:13:20',
            gameProcedure = 'LJHSaFLKJ'
        ))

        db_add(Game(
            inMatchID = 1, num = 3, point = '25:5', duration = '00:15:20',
            gameProcedure = 'LJHSLKDJsFLKJ'
        ))

        db_add(Match(
            id = 0,
            location = '五四',
            matchTime = '2020-11-30 20:15:00',
            gender = 'M', stage = 'A',
            teamA = None, teamB = None,
            point = None, umpire = None, viceUmpire = None
        ))
        
        db_add(Match(
            id = 0,
            location = '五四',
            matchTime = '2020-11-29 15:20:00',
            gender = 'F', stage = 'B',
            teamA = None, teamB = None,
            point = None, umpire = None, viceUmpire = None
        ))
        
        db_add(Match(
            id = 0,
            location = '五四',
            matchTime = '2020-11-28 23:20:00',
            gender = 'M', stage = 'A',
            teamA = None, teamB = None,
            point = None, umpire = None, viceUmpire = None
        ))
        
        db_add(Match(
            id = 0,
            location = '五四',
            matchTime = '2020-12-1 08:20:00',
            gender = 'M', stage = 'A',
            teamA = None, teamB = None,
            point = None, umpire = None, viceUmpire = None
        ))
        
        db_add(Match(
            id = 0,
            location = '五四',
            matchTime = '2020-12-1 13:20:00',
            gender = 'M', stage = 'A',
            teamA = None, teamB = None,
            point = None, umpire = None, viceUmpire = None
        ))
        
        db_add(Team(
            name = '信科', gender = 'M', inGroup = 'D', isUnified = False
        ))
        
        db_add(Team(
            name = '元培', gender = 'M', inGroup = 'D', isUnified = False
        ))
        
        db_add(Team(
            name = '信-政', gender = 'M', inGroup = 'B', isUnified = True,
            schoolA = '信管', schoolB = '政管'
        ))
        
    def tearDown(self):
        """
        Will be called after every test
        """
        db.session.remove()
        db.drop_all()


class TestViews(TestBase):
    
    def test_login(self):
        # test1: username that doesn't exist
        self.assertEqual(User.query.count(), 2)
        response = self.client.post(url_for('guest.login'), 
            data = {
                'username': 'def',
                'password': 'def'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response['success'], False)
        self.assertEqual(response['errorType'], 'username')
        
        

        # test2: password error
        response = self.client.post(url_for('guest.login'), 
            data = {
                'username': 'abc',
                'password': 'def'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response['success'], False)
        self.assertEqual(response['errorType'], 'password')
        
        #test3: login correctly
        response = self.client.post(url_for('guest.login'), 
            data = {
                'username': 'abc',
                'password': 'abc'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response['success'], True)
        self.assertEqual(response['isAdmin'], True)
        self.assertEqual(response['username'], 'abc')
        
      
    def test_matchInfo(self):
        # test1: request for match that doesn't exist
        response = self.client.get(url_for('guest.matchInfo', id = 10))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'match 10 not found')
        
        # test2: request for match that has results
        response = self.client.get(url_for('guest.matchInfo', id = 1))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['detailedPoints']), 4)
        self.assertEqual(data['id'], 1)
        
        # test3: request for match that have no result
        response = self.client.get(url_for('guest.matchInfo', id = 3))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['detailedPoints']), 0)
        self.assertEqual(data['point'], None)
      

    def test_viewMatches(self):
        # test1: page loaded for the first time
        response = self.client.post(url_for('guest.viewMatches'), 
            data = {
                'beginsAt': '9999-01-01'
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['matches']
        for i in range(len(data)-1):
            assert data[i]['time'] < data[i+1]['time']
            matchDate = data[i]['time'].split(' ')[0]
            assert matchDate == '2020-12-01' or matchDate == '2020-11-30'
        
        # test2: page loaded for the second time
        response = self.client.post(url_for('guest.viewMatches'), 
            data = {
                'beginsAt': '2020-11-30'
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['matches']
        for i in range(len(data)-1):
            assert data[i]['time'] < data[i+1]['time']
            matchDate = data[i]['time'].split(' ')[0]
            assert matchDate == '2020-12-29' or matchDate == '2020-11-28'
        
       
    def test_viewGrouping(self):
        response = self.client.get(url_for('guest.viewGrouping'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)['groupLists']
        self.assertEqual(data[0]['gender'], 'M')
        self.assertEqual(len(data[0]['groupList'][3]['teamList']), 2)
        
    
    # Since permission testing has been done in test_addUser, here we no longer test this.
    def test_setGrouping(self):
        # login as admin
        self.client.post(url_for('guest.login'),
            data = {
                'username': 'abc',
                'password': 'abc'
            }
        )
        
        print("test1")
        # test1: modify grouping is not allowed
        response = self.client.post(url_for('admin.setGrouping'),
            data = {
                'gender': 'M', 'group': '\"\"'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'grouping for 联赛组 has already been given')
        
        print("test2")
        # test2: add grouping with repeated team
        response = self.client.post(url_for('admin.setGrouping'),
            data = {
                'gender': 'F', 'group': '''{
                    \"A\": {\"信科\": []},
                    \"B\": {\"信科\": []},
                    \"C\": {},
                    \"D\": {}
                }'''
            }
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'repeated team: 信科')
        self.assertEqual(db.session.query(Team).filter(Team.gender == 'F').count(), 0)
        
        print("test3")
        # test3: add unbalanced grouping
        response = self.client.post(url_for('admin.setGrouping'),
            data = {
                'gender': 'F', 'group': '''{
                    \"A\": {\"信科\": []},
                    \"B\": {\"数学\": [], \"软微\": []},
                    \"C\": {},
                    \"D\": {}
                }'''
            }
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'grouping is unbalanced in num')
        self.assertEqual(db.session.query(Team).filter(Team.gender == 'F').count(), 0)
        
        print("test4")
        # test4: success
        response = self.client.post(url_for('admin.setGrouping'),
            data = {
                'gender': 'F', 'group': '''{
                    \"A\": {\"信科\": []},
                    \"B\": {\"数学\": []},
                    \"C\": {\"软微\": []},
                    \"D\": {\"物理\": []}
                }'''
            }
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'success')
    
    
    def test_addUser(self):
        # test1: not login
        response = self.client.post(url_for('admin.addUser'),
            data = {
                'newUsername': 'def',
                'newPassword': 'def',
                'newUserSchool': ''
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'not login yet')
        
        # test2: no permission
        self.client.post(url_for('guest.login'),
            data = {
                'username': 'bcd',
                'password': 'bcd'
            }
        )
        response = self.client.post(url_for('admin.addUser'),
            data = {
                'newUsername': 'def',
                'newPassword': 'def',
                'newUserSchool': ''
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'no permission')
        self.client.get(url_for('guest.logout'))
        
        # test3: username already exists
        self.client.post(url_for('guest.login'),
            data = {
                'username': 'abc',
                'password': 'abc'
            }
        )
        response = self.client.post(url_for('admin.addUser'),
            data = {
                'newUsername': 'bcd',
                'newPassword': 'bcd',
                'newUserSchool': ''
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'User \"bcd\" already existed')
        self.client.get(url_for('guest.logout'))
        
        # test4: success
        self.client.post(url_for('guest.login'),
            data = {
                'username': 'abc',
                'password': 'abc'
            }
        )
        response = self.client.post(url_for('admin.addUser'),
            data = {
                'newUsername': 'def',
                'newPassword': 'def',
                'newUserSchool': ''
            }
        )
        self.assertEqual(response.status_code, 200)
        self.client.get(url_for('guest.logout'))
        response = self.client.post(url_for('guest.login'),
            data = {
                'username': 'def',
                'password': 'def'
            }
        )
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response['success'], True)
        self.assertEqual(response['isAdmin'], False)
        self.assertEqual(response['username'], 'def')
        
        
    # Since permission testing has been done in test_addUser, here we no longer test this.
    def test_addMatch(self):
        # login as admin
        self.client.post(url_for('guest.login'),
            data = {
                'username': 'abc',
                'password': 'abc'
            }
        )
        
        # test1: unknown team
        response = self.client.post(url_for('admin.addMatch'),
            data = {
                'teamA': '外院', 'teamB': '物理'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Unknown team: \"外院\"')
        
        # test2: repeated team
        response = self.client.post(url_for('admin.addMatch'),
            data = {
                'teamA': '信科', 'teamB': '信科'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Repeated team name')
        
        # test3: group error
        response = self.client.post(url_for('admin.addMatch'),
            data = {
                'teamA': '信科', 'teamB': '信-政'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Group error')
        
        # test4: success
        response = self.client.post(url_for('admin.addMatch'),
            data = {
                'teamA': '信科', 'teamB': '元培'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Add new match successfully')
        
        
    def test_school2group(self):
        # test1: normal team
        response = self.client.get(url_for('guest.school2group', school = '信科'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['Mgroup'], 'D')
        self.assertEqual(data['Fgroup'], '')
        
        # test2: unified team
        response = self.client.get(url_for('guest.school2group', school = '信管'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['Mgroup'], 'B')
        self.assertEqual(data['Fgroup'], '')
        

    
if __name__ == '__main__':
    unittest.main()