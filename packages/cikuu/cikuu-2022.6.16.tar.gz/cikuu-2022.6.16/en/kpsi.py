# 2022.7.21 , sit(text),  select * from gzjc_snt where sid = '3,xx2,3'/substring_index('1,2,3',',',1)
# 2022.7.6 cp from silite.py, since clickhouse DONOT support  sql with 'match' 
import json, traceback,sys, time, fire,os,traceback
from collections import	Counter, defaultdict
import en 
from en.spacybs import Spacybs
from tqdm import tqdm
add = lambda *names: [fire.si.update({name: 1}) for name in names if  not '\t' in name and len(name) <= 80 and len(name) > 0 ]
reg = lambda name, sid: fire.st[name].append(sid) if len(fire.st[name]) <= 100 else None

def walk(sid, doc): 
	from dic.wordlist import wordlist 
	add(f"#SNT")  #, f"{t.tag_}:{t.lemma_.lower()}" where s like '%:VERB:VBG' => where s like 'VBG:%'
	[add( f"{t.lemma_}:POS:{t.pos_}", f"{t.lemma_}:LEX:{t.text.lower()}", f"LEM:{t.lemma_.lower()}", f"LEX:{t.text.lower()}", f"{t.pos_}:{t.lemma_.lower()}"
		,f"{t.lemma_.lower()}:{t.pos_}:{t.tag_}:{t.text.lower()}",f"{t.lemma_.lower()}:{t.pos_}:{t.tag_}",f"*:{t.pos_}:{t.tag_}", f"{t.lemma_.lower()}:{t.pos_}") for t in doc if not t.pos_ in ('PROPN','X', 'PUNCT') and t.is_alpha  and t.lemma_.lower() in wordlist]
	for t in doc:
		add( "#LEX", f"#{t.pos_}", f"#{t.tag_}",f"#{t.dep_}",) # book:VERB:VBG
		if t.pos_ not in ("PROPN","PUNCT","SPACE") and t.is_alpha and t.head.is_alpha and t.lemma_.lower() in wordlist and t.head.lemma_.lower() in wordlist: #*:VERB:~punct:VERB:wink
			reg(f"{t.lemma_.lower()}:{t.pos_}:{t.tag_}:{t.text.lower()}", sid) 
			add(f"{t.head.lemma_}:{t.head.pos_}:{t.dep_}:{t.pos_}:{t.lemma_}", f"{t.head.lemma_}:{t.head.pos_}:{t.dep_}:{t.pos_}",f"{t.head.lemma_}:{t.head.pos_}:{t.dep_}", f"*:{t.head.pos_}:{t.dep_}")
			reg(f"{t.head.lemma_}:{t.head.pos_}:{t.dep_}:{t.pos_}:{t.lemma_}", sid)
			if t.dep_ not in ('ROOT'): 
				add(f"{t.lemma_}:{t.pos_}:~{t.dep_}:{t.head.pos_}:{t.head.lemma_}", f"{t.lemma_}:{t.pos_}:~{t.dep_}:{t.head.pos_}", f"{t.lemma_}:{t.pos_}:~{t.dep_}", f"*:{t.pos_}:~{t.dep_}")
				reg(f"{t.lemma_}:{t.pos_}:~{t.dep_}:{t.head.pos_}:{t.head.lemma_}", sid)		
			
	for sp in doc.noun_chunks: #book:NOUN:np:a book
		add(f"{sp.root.lemma_.lower()}:{sp.root.pos_}:np:{sp.text.lower()}", f"{sp.root.lemma_.lower()}:{sp.root.pos_}:np", f"*:{sp.root.pos_}:np", f"#np",)
		reg(f"{sp.root.lemma_.lower()}:{sp.root.pos_}:np:{sp.text.lower()}", sid)

	# [('pp', 'on the brink', 2, 5), ('ap', 'very happy', 9, 11)]
	for lem, pos, type, chunk in en.kp_matcher(doc): #brink:NOUN:pp:on the brink
		add(f"{lem}:{pos}:{type}:{chunk}", f"{lem}:{pos}:{type}", f"*:{pos}:{type}", f"#{type}")
		reg(f"{lem}:{pos}:{type}:{chunk}", sid)
	for trpx, row in en.dep_matcher(doc): #[('svx', [1, 0, 2])] ## consider:VERB:vnpn:**** 
		verbi = row[0] #consider:VERB:be_vbn_p:be considered as
		add(f"{doc[verbi].lemma_}:{doc[verbi].pos_}:{trpx}", f"*:{doc[verbi].pos_}:{trpx}", f"#{trpx}") #consider:VERB:svx
		reg(f"{doc[verbi].lemma_}:{doc[verbi].pos_}:{trpx}", sid)
		if trpx == 'sva' and doc[row[0]].lemma_ == 'be': # fate is sealed, added 2022.7.25
			add(f"{doc[row[1]].lemma_}:{doc[row[1]].pos_}:sbea:{doc[row[2]].pos_}:{doc[row[2]].lemma_}", f"{doc[row[1]].lemma_}:{doc[row[1]].pos_}:sbea", f"*:{doc[row[1]].pos_}:sbea")
			reg(f"{doc[row[1]].lemma_}:{doc[row[1]].pos_}:sbea:{doc[row[2]].pos_}:{doc[row[2]].lemma_}", sid)
			add(f"{doc[row[2]].lemma_}:{doc[row[2]].pos_}:~sbea:{doc[row[1]].pos_}:{doc[row[1]].lemma_}", f"{doc[row[2]].lemma_}:{doc[row[2]].pos_}:~sbea", f"*:{doc[row[2]].pos_}:~sbea")
			reg(f"{doc[row[2]].lemma_}:{doc[row[2]].pos_}:~sbea:{doc[row[1]].pos_}:{doc[row[1]].lemma_}", sid)

	# last to be called, since NP is merged
	for row in en.verbnet_matcher(doc): #[(1, 0, 3, 'NP V S_ING')]
		if len(row) == 4: 
			verbi, ibeg, iend, chunk = row
			if doc[verbi].lemma_.isalpha() : 
				add(f"{doc[verbi].lemma_}:{doc[verbi].pos_}:verbnet:{chunk}") #consider:VERB:verbnet:NP V S_ING
				reg(f"{doc[verbi].lemma_}:{doc[verbi].pos_}:verbnet:{chunk}", sid)

	for name,ibeg,iend in en.post_np_matcher(doc): #added 2022.7.25
		if name in ('v_n_vbn','v_n_adj'): 
			add(f"{doc[ibeg].lemma_}:{doc[ibeg].pos_}:{name}:{doc[ibeg].lemma_} {doc[ibeg+1].lemma_} {doc[ibeg+2].text}", f"{doc[ibeg].lemma_}:{doc[ibeg].pos_}:{name}", f"*:{doc[ibeg].pos_}:{name}")
			reg(f"{doc[ibeg].lemma_}:{doc[ibeg].pos_}:{name}:{doc[ibeg].lemma_} {doc[ibeg+1].lemma_} {doc[ibeg+2].text}", sid)

def mysql(dbfile, host='127.0.0.1', port=3307, cutoff=0):  
	''' clec.spacybs -> mysql:kpsi/clec,clec_snt , 2022.7.20 '''
	import pymysql
	print ("started index:", dbfile, flush=True)
	name = dbfile.lower().split('.')[0]
	fire.si = Counter()
	fire.st = defaultdict(list) # name -> sidlist, added 2022.7.21 
	my_conn = pymysql.connect(host=host,port=port,user='root',password='cikuutest!',db='kpsi')
	with my_conn.cursor() as cursor: 
		cursor.execute(f"drop TABLE if exists {name}")
		cursor.execute(f"CREATE TABLE if not exists {name}(s varchar(128) COLLATE latin1_bin not null primary key, i int not null default 0, t text) engine=myisam  DEFAULT CHARSET=latin1 COLLATE=latin1_bin") # not null default ''
		cursor.execute(f"drop TABLE if exists {name}_snt")
		cursor.execute(f"CREATE TABLE if not exists {name}_snt(sid int primary key, snt text not null, kps text not null, fulltext key `snt`(`snt`), fulltext key `kps`(`kps`) ) engine=myisam  DEFAULT CHARSET=latin1 COLLATE=latin1_bin")

		for rowid, snt, doc in tqdm(Spacybs(dbfile).docs()) :
			try:
				cursor.execute(f"insert ignore into {name}_snt(sid, snt, kps) values(%s, %s, %s)", (rowid,snt, 
					" ".join([ f"{t.lemma_}_{t.pos_}" for t in doc  if t.pos_ not in ('PUNCT')] 
					+ [ f"{t.lemma_}_{t.pos_}_{t.tag_}_{t.text.lower()}" for t in doc  if t.pos_ not in ('PUNCT')] # consider:VERB:VBG:considering
					+ [ f"{t.head.lemma_}_{t.head.pos_}_{t.dep_}_{t.pos_}_{t.lemma_}" for t in doc if t.pos_ not in ('PRON','PUNCT') and t.dep_ in ('dobj','nsubj','advmod','acomp','amod','compound','xcomp','ccomp','oprd')]) ))
				walk(rowid, doc)
			except Exception as e: 
				print ("ex:", e, rowid, snt)
				exc_type, exc_value, exc_traceback_obj = sys.exc_info()
				traceback.print_tb(exc_traceback_obj)

		#cursor.executemany(f"insert ignore into {name}(s, i) values(%s, %s)",[(k,v) for k,v in fire.si.items() if v > cutoff]) 
		cursor.executemany(f"insert ignore into {name}(s, i, t) values(%s, %s, %s)",[(k,v, ','.join([str(sid) for sid in fire.st[k] ]) ) for k,v in fire.si.items() if v > cutoff]) 
		cursor.execute(f"DROP FUNCTION IF EXISTS {name}i")
		cursor.execute(f'''CREATE FUNCTION {name}i(term varchar(64)) RETURNS INT
 READS SQL DATA
BEGIN
	RETURN (SELECT i FROM {name} WHERE s = term limit 1);
END''')
		my_conn.commit()
	print ("finished submitting:", dbfile, flush=True) 

def tsv(jsonfile, cutoff=0, model:str="lg"):  
	''' gzjc.json341 => gzjc.tsv.si, gzjc.tsv.snt , added 2022.7.30 '''
	import spacy 
	nlp =spacy.load(f'en_core_web_{model}')
	print ("started index:", dbfile, model, flush=True)
	name = jsonfile.lower().split('.')[0]
	fire.si = Counter()
	fire.st = defaultdict(list)
	with open (f"{name}.tsv.snt", "w", encoding='UTF-8') as fw:
		for rowid, line in enumerate(fileinput.input(jsonfile,openhook=fileinput.hook_compressed)): 
			try: 
				doc_json =json.loads(line) 
				doc = Doc(nlp.vocab).from_json(doc_json)
				terms = " ".join([ f"{t.lemma_}_{t.pos_}" for t in doc] + [ f"{t.lemma_}_{t.tag_}" for t in doc] + [ f"{t.head.lemma_}_{t.head.pos_}_{t.dep_}_{t.pos_}_{t.lemma_}" for t in doc if t.pos_ not in ('PRON','PUNCT') and t.dep_ in ('dobj','nsubj','advmod','acomp','amod','compound','xcomp','ccomp','prep')]) 
				fw.write(f"{rowid}\t{snt}\t{terms}\n")
				walk(rowid, doc)
			except Exception as e:
				print ("ex:", e, rowid, snt)
	with open (f"{name}.tsv.si", "w", encoding='UTF-8') as fw:
		[ fw.write(f"{k}\t{v}\n") for k,v in fire.si.items() if v > cutoff ] 
	print ("finished submitting:", jsonfile, flush=True) 

def kpyes(dbfile, host='127.0.0.1', port=3309):  
	''' dic.spacybs -> kpyes , 2022.7.13 '''
	import pymysql
	print ("started register:", dbfile, flush=True)
	name = dbfile.lower().split('.')[0]
	my_conn = pymysql.connect(host=host,port=port,user='root',password='cikuutest!',db='kpsi')
	with my_conn.cursor() as cursor: 
		cursor.execute(f"CREATE TABLE if not exists kpyes(s varchar(128) COLLATE latin1_bin not null primary key, i int not null default 0, src varchar(32) not null default '', snt varchar(128) not null default '') engine=myisam  DEFAULT CHARSET=latin1 COLLATE=latin1_bin")
		for rowid, snt, doc in tqdm(Spacybs(dbfile).docs()) :
			try:
				cursor.executemany(f"insert ignore into kpyes(s, src, snt) values(%s, %s, %s)",[ (f"{t.lemma_}:{t.pos_}:{t.tag_}", name, snt ) for t in doc] + [ (f"{t.lemma_}:{t.pos_}:{t.text.lower()}", name, snt ) for t in doc]) 
				cursor.executemany(f"insert ignore into kpyes(s, src, snt) values(%s, %s, %s)",[ (f"{t.head.lemma_}:{t.head.pos_}:{t.dep_}:{t.pos_}:{t.lemma_}", name, snt ) for t in doc if t.pos_ not in ('PRON','PUNCT')]) 
			except Exception as e: 
				print ("ex:", e, rowid, snt)
		my_conn.commit()
	print ("finished submitting:", dbfile, flush=True) 

def batch(names="qdu,gzjc,gaokao,clec"):
	''' batch model, --names qdu,gzjc,gaokao,clec '''
	[mysql(f"{name}.spacybs") for name in names.strip().split(',')]

def trp(dbfile, cutoff=1):  
	''' bnc.spacybs -> bnc.trp.tsv, commonly large file, so filtered with cutoff '''
	print ("started index:", dbfile, flush=True)
	name = dbfile.lower().split('.')[0]
	fire.si = Counter()
	for rowid, snt, doc in Spacybs(dbfile).docs() : 
		try: 
			[add(f"{t.head.lemma_}:{t.head.pos_}:{t.dep_}:{t.pos_}:{t.lemma_}") for t in doc if t.pos_ not in ("PROPN","PUNCT","SPACE") and t.is_alpha and t.head.is_alpha ]
		except Exception as e:
			print ("ex:", e, rowid, snt)
	with open (f"{name}.trp.si", "w", encoding='UTF-8') as fw:
		[ fw.write(f"{k}\t{v}\n") for k,v in fire.si.items() if v > cutoff ] 
	print ("finished writing trp.si:", dbfile, flush=True) 
	
def dump(name, port=3309): 
	''' dump twit --port 3309 @ lanxum '''
	print ('start to dump :', name, flush=True) 
	os.remove(f"{name}.sql.gz") if os.path.exists(f"{name}.sql.gz") else None 
	os.system(f"mysqldump -uroot -pcikuutest! --port {port} --host=127.0.0.1 kpsi {name} {name}_snt --result-file={name}.sql")
	os.system(f"gzip {name}.sql")
	#os.system(f"sshpass -p Cikuutest1 scp {name}.sql.gz ubuntu@lab.jukuu.com:/ftp")

def load(name, port=3307): 
	''' load twit --port 3307 @ lab.jukuu.com '''
	name = name.strip().split('.')[0]
	os.system(f"gzip -d {name}.sql.gz") if os.path.exists(f"{name}.sql.gz") else None 
	os.system(f"mysql -uroot -pcikuutest! -h 127.0.0.1 --port {port} kpsi  < {name}.sql")

if __name__	== '__main__':
	fire.Fire({"mysql":mysql, "batch":batch, 'trp':trp , 'kpyes':kpyes, "dump":dump, "load":load})

'''
mysqldump -uroot -pcikuutest! --port 3307 --host=172.18.0.1 kpsi word_attr --result-file=word_attr.sql

docker run -d --restart=always --name=kpsi --env='MYSQL_ROOT_PASSWORD=cikuutest!' --volume=/data/mariadb-mysi:/var/lib/mysql -p 3307:3306 mariadb --max_allowed_packet=100M --max_connections=1000 --disable-log-bin --innodb_file_per_table=1  --read_buffer_size=64M --read_rnd_buffer_size=64M --join_buffer_size=16M --tmp_table_size=512M
docker run -it --restart=always --name=kpsi --env='MYSQL_ROOT_PASSWORD=cikuutest!' --volume=/data/model/mariadb-kpsi:/var/lib/mysql -p 3310:3306 mariadb --max_allowed_packet=100M --max_connections=1000 --disable-log-bin --innodb_file_per_table=1  --read_buffer_size=64M --read_rnd_buffer_size=64M --join_buffer_size=16M --tmp_table_size=512M

select * from gzjc where s like 'consider:VERB:%' and s not like 'consider:VERB:%:%';

select * from gzjc_snt where match(kps) against('write_VERB_dobj_NOUN_book')  limit 10;
select * from gzjc_snt where match(kps) against('book_VERB')  limit 10;
select * from gzjc_snt where match(snt) against('book')  limit 10;

#for k,v in fire.si.items(): cursor.execute(f"insert ignore into {name}(s, i) values(%s, %s)", (k,v))

consider:VERB:vtov:considered to be|22 / consider:VERB:vtov:consider to be|22  is different
-- bnc.silite (s,i)  => clickhouse user_file    
open:VERB:dobj:NOUN:door  | open:VERB:dobj
book:NOUN:np:a book book:NOUN:npone:books
happen:VERB:VBG, 
book:LEX:books   knowledge:LEX:knowledges 
book:POS:VERB 
consider:VERB:vtov:consider to go  |  consider:VERB:vvbg:consider visiting
brink:NOUN:pp:on the brink
pretty:ADJ:ap:very pretty
consider:VERB:ROOTV
visit:VERB:vend:plan to visit

sqlite> select * from si where s like 'sound:VERB:%' and s not like 'sound:VERB:%:%';
sound:VERB:ROOT|12
sound:VERB:VB|1
sound:VERB:VBD|3
sound:VERB:VBG|1
sqlite> select * from si where s like 'consider:VERB:vtov:%';
consider:VERB:vtov:consider to be|3
sqlite>
sqlite> select * from si where s like 'VERB:%' order by i desc limit 10;
VERB:be|1315
VERB:have|698
VERB:make|417
VERB:go|394
sqlite> select * from si where s like 'sound:LEX:%';
sound:LEX:sound|21
sound:LEX:sounded|4
sound:LEX:sounding|1
sound:LEX:sounds|21
sqlite> select * from si where s like 'door:noun%' and s not like 'door:noun:%:%';
door:NOUN|26
door:NOUN:NN|21
door:NOUN:NNS|5
door:NOUN:ROOT|1
door:NOUN:advmod|1

(spacy311) (base) cikuu@gpu55:/data2/ftp/sntbs$ time python silite.py bnc.spacybs 
started index: bnc.spacybs
5311102it [2:11:43, 671.99it/s] 
finished submitting: bnc.spacybs

real	140m12.136s
user	132m10.230s
sys	6m16.526s

		for k,v in fire.si.items():
			if not "'" in k: 
				cursor.execute(f"INSERT INTO {name}(s,i) VALUES ('{k}', {v}) ON DUPLICATE KEY UPDATE i = i + {v}")

def submit(cursor): # NOT used 
	#cursor.executemany(f"INSERT INTO table {name}(s,i) VALUES (%s, %s) ON DUPLICATE KEY UPDATE i = i + %s", [(k,v,v) for k,v in fire.si.items()] )
	for k,v in fire.si.items():
		if not "'" in k and len(k) < 128: 
			cursor.execute(f"INSERT INTO {name}(s,i) VALUES ('{k}', {v}) ON DUPLICATE KEY UPDATE i = i + {v}")
	print ( len(fire.si), flush=True)
	fire.si.clear()

def tsv(dbfile, cutoff=1):  
	# bnc.spacybs -> bnc.si.tsv, bnc.snt.tsv ,  commonly large file, so filtered with cutoff
	print ("started index:", dbfile, flush=True)
	name = dbfile.lower().split('.')[0]
	fire.si = Counter()
	with open (f"{name}.tsv.snt", "w", encoding='UTF-8') as fw:
		for rowid, snt, doc in Spacybs(dbfile).docs() : #for rowid, snt, bs in tqdm(Spacybs(dbfile).items()) :
			try: #doc =  spacy.frombs(bs)
				terms = " ".join([ f"{t.lemma_}_{t.pos_}" for t in doc] + [ f"{t.lemma_}_{t.tag_}" for t in doc] + [ f"{t.head.lemma_}_{t.head.pos_}_{t.dep_}_{t.pos_}_{t.lemma_}" for t in doc if t.pos_ not in ('PRON','PUNCT') and t.dep_ in ('dobj','nsubj','advmod','acomp','amod','compound','xcomp','ccomp','prep')]) 
				fw.write(f"{rowid}\t{snt}\t{terms}\n")
				walk(doc)
			except Exception as e:
				print ("ex:", e, rowid, snt)
	with open (f"{name}.tsv.si", "w", encoding='UTF-8') as fw:
		[ fw.write(f"{k}\t{v}\n") for k,v in fire.si.items() if v > cutoff ] 
	print ("finished submitting:", dbfile, flush=True) 
'''