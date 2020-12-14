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
        
        user = User(
            id = 0,
            username = 'abc',
            password = 'abc',
            isAdmin = True,
            icon = None,
            school = None,
            umpireFee = 0
        )
        db.session.add(user)
        db.session.commit()
        
        match = Match(
            id = 1,
            location = '五四',
            matchTime = '2020-12-1 20:20:00',
            gender = 'M', stage = 'A',
            teamA = None, teamB = None,
            point = '3:1', umpire = None, viceUmpire = None
        )
        db.session.add(match)
        db.session.commit()
        
        id = Match.query.all()[0].id
        
        game = Game(
            inMatchID = 1, num = 2, point = '25:21', duration = '00:20:20',
            gameProcedure = 'LJHSLKDJHFLKJ'
        )
        db.session.add(game)
        db.session.commit()
        
        game = Game(
            inMatchID = 1, num = 1, point = '21:25', duration = '00:24:20',
            gameProcedure = 'LJHSLKSDFLKJ'
        )
        db.session.add(game)
        db.session.commit()

        game = Game(
            inMatchID = 1, num = 4, point = '25:9', duration = '00:13:20',
            gameProcedure = 'LJHSaFLKJ'
        )
        db.session.add(game)
        db.session.commit()

        game = Game(
            inMatchID = 1, num = 3, point = '25:5', duration = '00:15:20',
            gameProcedure = 'LJHSLKDJsFLKJ'
        )
        db.session.add(game)
        db.session.commit()

        match = Match(
            id = 2,
            location = '五四',
            matchTime = '2020-12-1 20:15:00',
            gender = 'M', stage = 'A',
            teamA = None, teamB = None,
            point = None, umpire = None, viceUmpire = None
        )
        db.session.add(match)
        db.session.commit()
        
        match = Match(
            id = 3,
            location = '五四',
            matchTime = '2020-12-1 15:20:00',
            gender = 'F', stage = 'B',
            teamA = None, teamB = None,
            point = None, umpire = None, viceUmpire = None
        )
        db.session.add(match)
        db.session.commit()
        
        match = Match(
            id = 4,
            location = '五四',
            matchTime = '2020-12-1 23:20:00',
            gender = 'M', stage = 'A',
            teamA = None, teamB = None,
            point = None, umpire = None, viceUmpire = None
        )
        db.session.add(match)
        db.session.commit()
        
        match = Match(
            id = 5,
            location = '五四',
            matchTime = '2020-12-1 08:20:00',
            gender = 'M', stage = 'A',
            teamA = None, teamB = None,
            point = None, umpire = None, viceUmpire = None
        )
        db.session.add(match)
        db.session.commit()
        
        match = Match(
            id = 6,
            location = '五四',
            matchTime = '2020-12-1 13:20:00',
            gender = 'M', stage = 'A',
            teamA = None, teamB = None,
            point = None, umpire = None, viceUmpire = None
        )
        db.session.add(match)
        db.session.commit()

    def tearDown(self):
        """
        Will be called after every test
        """
        db.session.remove()
        db.drop_all()


class TestViews(TestBase):
    
    def test_login(self):
        # test1: username that doesn't exist
        self.assertEqual(User.query.count(), 1)
        response = self.client.post(url_for('guest.login'), 
            data = {
                'username': 'def',
                'password': 'def'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'username doesn\'t exist')
        
        # test2: password error
        response = self.client.post(url_for('guest.login'), 
            data = {
                'username': 'abc',
                'password': 'def'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'password error')
        
        #test3: login correctly
        response = self.client.post(url_for('guest.login'), 
            data = {
                'username': 'abc',
                'password': 'abc'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'login successfully as abc, an Admin')
        
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
                'lastShowed': -1,
                'numOfMatchesRequesting': 5
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        data = data['matches']
        self.assertEqual(len(data), 5)
        for i in range(4):
            assert data[i]['time'] < data[i+1]['time']
        
        # test2: page loaded for the second time
        response = self.client.post(url_for('guest.viewMatches'), 
            data = {
                'lastShowed': 6,
                'numOfMatchesRequesting': 5
            }
        )
        self.assertEqual(response.status_code, 200)
        data2 = json.loads(response.data)
        data2 = data2['matches']
        self.assertEqual(len(data2), 1)
        assert data2[0]['time'] < data[0]['time']
        
        
        


if __name__ == '__main__':
    unittest.main()