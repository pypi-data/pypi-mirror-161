# 22-6-14
import json, sys, time, fire,traceback, requests,os

def eev(infile, host='172.17.0.1',port=3306,user='root',password='cikuutest!',db='dskmkf'):
	''' parse bupt.json -> dskmkf , 2022.5.28 | python __main__.py json_to_dskmkf  2491939.json '''
	import pymysql
	conn = pymysql.connect(host=host,port=port,user=user,password=password,db=db)
	cursor= conn.cursor()
	for line in open(infile, 'r').readlines(): #util.readline(infile) :
		try:
			arr = json.loads(line)
			essay = arr.get("essay", "") 
			if not essay: continue 
			id, eid,rid,uid,ver = int( arr.get('id',0) ), int( arr.get('essay_id',0) ),int( arr.get('request_id',0) ),int( arr.get('user_id',0) ),int( arr.get('version',0) )
			cursor.execute("insert ignore into eev(id,eid,rid,uid,ver, essay, arr) values(%s,%s,%s,%s,%s,%s,%s)", (id, eid, rid, uid, ver, essay, line ) )
			conn.commit()
		except Exception as ex: 
			print(">>line Ex:", ex, "\t|", line) #>>line Ex: 'NoneType' object is not subscriptable
			exc_type, exc_value, exc_traceback_obj = sys.exc_info()
			traceback.print_tb(exc_traceback_obj)
	print("finished parsing:", infile)
	
if __name__ == '__main__': 
	fire.Fire({"eev":eev}) 

'''
create table eev(
id bigint not null default 0 primary key, 
eid int not null default 0, 
rid int not null default 0, 
uid int not null default 0, 
ver int not null default 0, 
essay text, 
arr json, 
 KEY `rid` (`rid`),
 KEY `uid` (`uid`),
 KEY `eid` (`eid`)
);
'''