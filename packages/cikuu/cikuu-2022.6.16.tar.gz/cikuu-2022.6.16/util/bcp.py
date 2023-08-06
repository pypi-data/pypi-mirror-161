# 2022.7.6
import pymysql,json, sys, time,  fileinput, fire

class Util(object): 
	def __init__(self, host='127.0.0.1', port=3307, user='root',password='cikuutest!',db='kpsi'): 
		self.my_conn = pymysql.connect(host=host,port=port,user=user,password=password,db=db)

	def dumptsv(self, tab):
		''' dump the tab to {tab}.tsv, 2022.7.6 '''
		print(f">> started: [{tab}]", flush=True)
		with open(f"{tab}.tsv", 'w') as fw: 
			with self.my_conn.cursor() as cursor:
				cursor.execute(f"select * from {tab}")
				row = cursor.fetchone()
				while row is not None: 
					try:
						fw.write("\t".join([str(a) for a in row]) + "\n")
						row = cursor.fetchone()
					except Exception as e:
						print("ex:", e, row, file=sys.stderr)
		print(f">> finished: {tab}.tsv", flush=True)

	def loadtsv(self, infile, tab): 
		''' '''
		print ("start to load", infile, tab, flush=True)
		self.cursor = self.my_conn.cursor()
		for line in fileinput.input(infile):
			try:
				arr = line.strip().split("\t")
				if len(arr) != 2 : continue
				self.cursor.execute("insert ignore into eevone(eid,arr) values(%s,%s)", (arr[0], arr[1]))
			except Exception as e:
				print("ex:", e, line)
		self.my_conn.commit()
		print(">> finished:", infile, tab)

	def loadst(self, infile): 
		''' st(s, t)  '''
		print ("start to load", infile, flush=True)
		name = infile.lower().split('.')[0] 
		self.cursor = self.my_conn.cursor()
		self.cursor.execute(f"drop TABLE if exists {name}")
		self.cursor.execute(f"CREATE TABLE if not exists {name}(s varchar(128) COLLATE latin1_bin not null primary key, t text not null) engine=myisam  DEFAULT CHARSET=latin1 COLLATE=latin1_bin")
		for line in fileinput.input(infile):
			try:
				self.cursor.execute(f"insert ignore into {name}(s,t) values(%s,%s)",line.strip().split("\t") )
			except Exception as e:
				print("ex:", e, line)
		self.my_conn.commit()
		print(">> finished:", infile)

	def loadsi(self, infile): 
		''' si(s, i)  '''
		print ("start to load", infile, flush=True)
		name = infile.lower().split('.')[0] 
		self.cursor = self.my_conn.cursor()
		self.cursor.execute(f"drop TABLE if exists {name}")
		self.cursor.execute(f"CREATE TABLE if not exists {name}(s varchar(128) COLLATE latin1_bin not null primary key, i int not null default 0) engine=myisam  DEFAULT CHARSET=latin1 COLLATE=latin1_bin")
		for line in fileinput.input(infile):
			try:
				self.cursor.execute(f"insert ignore into {name}(s,i) values(%s,%s)",line.strip().split("\t") )
			except Exception as e:
				print("ex:", e, line)
		self.my_conn.commit()
		print(">> finished:", infile)

	def loadsnt(self, infile): 
		''' bnc_snt(sid,snt,kps) '''
		print ("start to load", infile, flush=True)
		name = infile.lower().split('.')[0] 
		self.cursor = self.my_conn.cursor()
		self.cursor.execute(f"drop TABLE if exists {name}_snt")
		self.cursor.execute(f"CREATE TABLE if not exists {name}_snt(sid int primary key, snt text not null, kps text not null, fulltext key `snt`(`snt`), fulltext key `kps`(`kps`) ) engine=myisam  DEFAULT CHARSET=latin1 COLLATE=latin1_bin")
		for line in fileinput.input(infile):
			try:
				self.cursor.execute(f"insert ignore into {name}_snt(sid,snt, kps) values(%s,%s,%s)",line.strip().split("\t") )
			except Exception as e:
				print("ex:", e, line)
		self.my_conn.commit()
		print(">> finished:", infile)

if __name__	== '__main__':
	fire.Fire(Util)
