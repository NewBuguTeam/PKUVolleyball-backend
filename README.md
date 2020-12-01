## PKUVolleyball-backend

### This is a test branch

Now the unit test for the modules completed has been implemented in /test.py.

The database name is changed in the testing environment. Please create new database showed as follows.

### Database configuration

Here shows the commands that should be run in in the MySQL commandline, which configs username & pw, and the database name used in the back-end, and also showed in /instance/config.py .

```
mysql> create user 'PKUVolleyball'@'localhost' identified with mysql_native_password by 'PKU_Vo11eyball';

mysql> create database PKUVolleyballDB_test;

mysql> grant all privileges on PKUVolleyballDB_test . * to 'PKUVolleyball'@'localhost';

mysql> flush privileges;

```

Database structures are now given in /app/models.py, which may be uncompleted yet.


Finally, `python test.py` in the windows commandline will run the test.

### Cautions when debugging

When testing functions in the browser, please don't forget to comment the inputs like `username = str(json.loads(request.values.get("username")))`, and uncomment the inputs like `username = request.form['username']`. These input handlers are at the top of functions. The former ones are used for the WeChat mini-program, and the latter ones are used for the browser testing.