# 2022.7.5  clickhouse DONOT support  sql with 'match' 
import json, traceback,sys, time, fire,sqlite3,os
from collections import	Counter
import en #from en import terms
from en.spacybs import Spacybs
from tqdm import tqdm

add = lambda *names: [fire.si.update({name: 1}) for name in names ] #incr(si, "one", "two")
doc_fts = lambda conn, rowid, snt, doc: conn.execute(f"insert or ignore into fts(rowid, snt,terms) values(?,?,?)", (rowid, snt, " ".join([ f"{t.lemma_}_{t.pos_}" for t in doc] + [ f"{t.lemma_}_{t.tag_}" for t in doc] + [ f"{t.head.lemma_}_{t.head.pos_}_{t.dep_}_{t.pos_}_{t.lemma_}" for t in doc if t.pos_ not in ('PRON','PUNCT') and t.dep_ in ('dobj','nsubj','advmod','acomp','amod','compound','xcomp','ccomp')]) ))

def newdb(name):  
	''' clec -> clec.silite,'''
	dbfile = name +".silite"
	if os.path.exists(dbfile): os.remove(dbfile)
	conn =	sqlite3.connect(dbfile, check_same_thread=False) 
	conn.execute(f'CREATE TABLE si (s varchar(128) not null primary key, i int not null ) without rowid')
	conn.execute('''CREATE VIRTUAL TABLE if not exists fts USING fts5(snt, terms, columnsize=0, detail=full,tokenize = "unicode61 remove_diacritics 0 tokenchars '-_'")''') #self.conn.execute('''CREATE VIRTUAL TABLE if not exists fts USING fts5(snt, terms, columnsize=0, detail=none,tokenize = "unicode61 remove_diacritics 0 tokenchars '-_:'")''')
	conn.execute('PRAGMA synchronous=OFF')
	return conn 

def walk(doc): 
	add(f"#SNT") 
	for t in doc:
		if not t.pos_ in ('PROPN','X', 'PUNCT'): add( f"{t.lemma_}:POS:{t.pos_}")
		add(f"{t.lemma_}:LEX:{t.text.lower()}", f"LEM:{t.lemma_}", f"LEX:{t.text}", f"{t.pos_}:{t.lemma_}", "#LEX", f"#{t.pos_}", f"#{t.tag_}",f"#{t.dep_}",)
		add(f"{t.lemma_}:{t.pos_}:{t.tag_}:{t.text.lower()}",f"{t.lemma_}:{t.pos_}:{t.tag_}", f"{t.lemma_}:{t.pos_}") # book:VERB:VBG
		if t.pos_ not in ("PROPN","PUNCT"): 
			add(f"{t.head.lemma_}:{t.head.pos_}:{t.dep_}:{t.pos_}:{t.lemma_}", f"{t.head.lemma_}:{t.head.pos_}:{t.dep_}")
			if t.dep_ not in ('ROOT'): add(f"{t.lemma_}:{t.pos_}:~{t.dep_}:{t.head.pos_}:{t.head.lemma_}", f"{t.lemma_}:{t.pos_}:~{t.dep_}")
	for sp in doc.noun_chunks: #book:NOUN:np:a book
		add(f"{sp.root.lemma_.lower()}:{sp.root.pos_}:np:{sp.text.lower()}", f"{sp.root.lemma_.lower()}:{sp.root.pos_}:np", f"#np",)

	for type, chunk, start, end in en.vp_matcher(doc): #[('vend', 'consider going', 1, 3)
		add(f"{doc[start].lemma_}:{doc[start].pos_}:{type}:{chunk}") #consider:VERB:vtov:consider to go

def index(dbfile):  
	''' clec.spacybs -> clec.kplite, 2022.7.4 '''
	print ("started index:", dbfile, flush=True)
	conn	= newdb(dbfile.split('.')[0])
	fire.si = Counter()
	for rowid, snt, bs in tqdm(Spacybs(dbfile).items()) :
		try:
			doc =  spacy.frombs(bs)
			doc_fts(conn, rowid, snt, doc) 
			walk(doc)
		except Exception as e:
			print ("ex:", e, rowid, snt)
	
	for k,v in fire.si.items(): conn.execute(f"replace into si(s,i) values(?,?)", (k,v))
	conn.commit()
	print ("finished submitting:", dbfile, flush=True) 

if __name__	== '__main__':
	fire.Fire(index)

'''
# 2022.7.4  
select snt from fts where terms match('dobj_VERB_NOUN_overcome_difficulty')  limit 10;

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

'''