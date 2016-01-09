import sqlite3
db=sqlite3.connect('docspad.db')
cur=db.cursor()
cur.execute("drop table if exists getid")
cur.execute("drop table if exists details")
cur.execute("create table details(pid  INTEGER AUTO_INCREMENT, pname text)")
cur.execute("create table getid(sid  int)")
cur.execute('insert into getid values("100")')
db.commit();
db.close()
