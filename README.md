## PKUVolleyball-backend

### Database configuration

Here shows the commands that should be run in in the MySQL commandline, which configs username & pw, and the database name used in the back-end, and also showed in /instance/config.py .

```
mysql> create user 'PKUVolleyball'@'localhost' identified with mysql_native_password by 'PKU_Vo11eyball';

mysql> create database PKUVolleyballDB;

mysql> grant all privileges on PKUVolleyballDB . * to 'PKUVolleyball'@'localhost';

mysql> flush privileges;

```

Database structures are now given in /app/models.py, which may be uncompleted yet.

**Database structures have been changed since this commit. If you have configured the database before, please re-migrate and re-upgrade. Detailed information could be found in app/model.py.**

After the database config above, run the following commands in the app direction in the windows commandline:

```
flask db init
flask db migrate
flask db upgrade

```

If error like `ERROR [root] Error: Can't locate revision identified by '0066c544c2f8'` occurred on `flask db migrate`, then you should drop the alembic_version table in the database:

```
mysql> use PKUVolleyballDB;

mysql> drop table alembic_version;

```

Finally, `flask run` in the windows commandline will run the server.

### Cautions when debugging

When testing functions in the browser, please don't forget to comment the inputs like `username = str(json.loads(request.values.get("username")))`, and uncomment the inputs like `username = request.form['username']`. These input handlers are at the top of functions. The former ones are used for the WeChat mini-program, and the latter ones are used for the browser testing.

### Unit testing

The unit test for the modules completed has been implemented in /test.py.

The database name is changed in the testing environment. The commands for creating testing database are given below:

```
mysql> create user 'PKUVolleyball'@'localhost' identified with mysql_native_password by 'PKU_Vo11eyball';

mysql> create database PKUVolleyballDB_test;

mysql> grant all privileges on PKUVolleyballDB_test . * to 'PKUVolleyball'@'localhost';

mysql> flush privileges;

```

After all are ready, `python test.py` in the windows commandline will run the test.
