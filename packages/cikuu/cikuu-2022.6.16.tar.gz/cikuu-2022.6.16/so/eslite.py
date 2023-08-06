# 2022.7.3 store terms from es to sqlite3 (COS),  gzjc.eslite
from so import *
import sqlite3,fire,time

def newdb(name):  
	''' clec -> clec.eslite, --debug True 2022.7.3 '''
	dbfile = name +".eslite"
	if os.path.exists(dbfile): os.remove(dbfile)
	conn =	sqlite3.connect(dbfile, check_same_thread=False) 
	conn.execute(f'CREATE TABLE IF NOT EXISTS snt (sid int PRIMARY KEY, snt varchar(512)) without rowid') # 
	conn.execute(f'CREATE TABLE tok (lem varchar(64) not null, pos varchar(32) not null, tag varchar(32) not null,  lex varchar(64) not null, cnt int not null )')
	conn.execute(f'CREATE TABLE trp (rel varchar(64) not null, gov varchar(32) not null, dep varchar(32) not null,  cnt int not null )')
	conn.execute(f'CREATE TABLE meta (type varchar(64) not null primary key, cnt int not null ) without rowid')
	conn.execute("create unique index uk_tok on tok (lem, pos,tag,lex)") #ALTER TABLE COMPANY ADD PRIMARY KEY (ID);
	conn.execute("create unique index uk_trp on trp (rel,gov,dep)") #create unique index indx_email on emp (email);
	conn.execute('create index indx_dep on trp (rel, dep)')	
	conn.execute('PRAGMA synchronous=OFF')
	return conn 

def run(idxname):
	'''  python eslite.py gzjc 
	* trp(rel, gov, dep, cnt) 
	* tok(lem, pos, tag, lex, cnt) 
	'''
	start = time.time()
	print("started:", idxname, flush=True)
	conn = newdb(idxname) 

	for lem, pos,tag,lex,cnt in cursor_rows(f"select lem, pos, tag, lex, count(*) cnt from {idxname} group by lem,pos,tag,lex"): 
		conn.execute(f"insert or ignore into tok(lem, pos,tag,lex, cnt) values(?,?,?,?,?)", (lem, pos,tag,lex,cnt))
	
	for dep,gov,lem,pos,cnt in cursor_rows(f"select dep, gov, lem, pos, count(*) cnt from {idxname} where type='tok' and dep not in ('PUNCT','ROOT','X') and pos not in ('PROPN') group by dep, gov, lem, pos "): 
		conn.execute(f"insert or ignore into trp(rel, gov, dep, cnt) values(?,?,?,?)", (f"{dep}_{gov.split('_')[-1]}_{pos}", gov.split('_')[0],lem,cnt))

	for type,cnt in cursor_rows(f"select type, count(*) cnt from {idxname} group by type"): 
		conn.execute(f"insert or ignore into meta(type, cnt) values(?,?)", (type,cnt))
	for sid,snt in cursor_rows(f"select src, snt from {idxname} where type ='snt'"): 
		conn.execute(f"insert or ignore into snt(sid, snt) values(?,?)", (sid,snt))

	conn.commit()
	#conn.execute("vacuum")
	print("finished:", idxname, "\t using:", time.time() - start)

if __name__ == '__main__':
	fire.Fire(run)