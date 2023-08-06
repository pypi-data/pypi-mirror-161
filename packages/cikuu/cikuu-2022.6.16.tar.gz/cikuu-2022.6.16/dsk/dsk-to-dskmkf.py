# 22-6-14 cp from json-to-dskmkf.py 
import json, sys, time, fire,traceback, requests,os,en
import util
import hashlib
md5snt	= lambda text: hashlib.md5(text.encode("utf-8")).hexdigest()
sample = {"id": 683598558, "essay_id": 123435663, "request_id": 2204638, "author_id": 297, "internal_idx": 0, "title": "\u7b2c2204638\u53f7 \u4f5c\u6587", "essay": "The speed of development of technology and science is beyond our imagination. Smartphones spread all over the world only take a few years. Without doubt, Smartphones have already made a big change to our daily life. On the one hand, they bring convenience to us, making us can do more things than before during the same period of time.On the other hand, we waste too much time on smartphones everyday. It does harm to not only our physical health, but also our mental health. \n In recent years, more and more people are in the charge of smartphones.They can't control themselves seeing a smartphone whenever they have nothing to do. There is no denying that more than half people are dropped in a cage called virtual world.In this cage, our mental withstand large quantities of damage inadvertently. What's worse, we can't realize the cage, not to mention fleeing it. \n Smartphones are just tools. We shouldn't be addicted in them, still less let them lead our life.", "essay_html": "", "tm": "", "user_id": 24126239, "sent_cnt": 0, "token_cnt": 0, "len": 966, "ctime": 1603093018, "stu_number": "2020210018", "stu_name": "\u5b8b\u777f", "stu_class": "A2122-2020\u79cb\u5b63\u5b66\u671f", "type": 0, "score": 76.4888, "qw_score": 75.9687, "sy_score": 0.0, "pigai": "", "pigai_time": 0, "gram_score": 0.0, "is_pigai": 1, "version": 8, "cate": 0, "src": "ajax_postSave__", "tid": 0, "fid": 0, "tag": "", "is_chang": 0, "jianyi": "", "anly_cnt": 1, "mp3": ""}
doc_tok	= lambda doc:  [ {'i':t.i, "head":t.head.i, 'lex':t.text, 'lem':t.lemma_, 'pos':t.pos_, 'tag':t.tag_, 'dep':t.dep_, "gpos":t.head.pos_, "glem":t.head.lemma_} for t in doc]
doc_chunk	= lambda doc:  [ {"lem": doc[sp.end-1].lemma_, "start":sp.start, "end":sp.end, "pos":"NP", "chunk":sp.text} for sp in doc.noun_chunks]
feedback	= lambda arr : [ {"cate":v.get('cate',''), "ibeg": v.get('ibeg',-1), "msg":v.get("short_msg","")} for k,v in arr.items() if v.get('cate','').startswith("e_") or v.get('cate','').startswith("w_")]

def submit_dskmkf(dsk, cursor): 
	''' '''
	snts  = [ ar.get('meta',{}).get('snt','').strip() for ar in dsk.get('snt',[])] # to md5
	info = dsk.get("info", {})
	eid,rid,uid,ver = int( info.get('essay_id',0) ),int( info.get('rid',0) ),int( info.get('uid',0) ),int( info.get('e_version',0) )
	score = float( info.get('final_score',0) ) # added 2022.2.15
	cursor.execute("insert ignore into dsk(eidv,eid,ver,rid,uid, score, snts, doc, info) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)", 
		(f"{eid}-{ver}",eid,ver,rid,uid, score, json.dumps([md5snt(snt) for snt in snts]), json.dumps(dsk.get('doc',{})), json.dumps(info)))

	for idx, snt in enumerate(snts) : 	
		if not snt: continue
		sntmd5 = md5snt(snt)
		cursor.execute(f"select * from mkf where sntmd5 = '{sntmd5}' limit 1")
		result=cursor.fetchone ()
		if result and len(result) > 0 : continue  #if sntmd5 in snts_known: continue #snts_known.add(sntmd5) 

		doc = spacy.nlp(snt)
		for ar in dsk['snt']:
			fd , meta = ar.get('feedback',{}), ar.get('meta',{})
			fds = feedback(fd)
			kps = [ f"{t.pos_}_{t.lemma_}" for t in doc] + [ f"{t.tag_}_{t.lemma_}" for t in doc] + [ f"{t.dep_}_{t.head.pos_}_{t.pos_}_{t.head.lemma_}_{t.lemma_}" for t in doc if t.pos_ not in ('PRON','PUNCT') and t.dep_ in ('dobj','nsubj','advmod','acomp','amod','compound','xcomp','ccomp')]
			[ kps.append( ar.get('cate','').replace('.','_')) for ar in fds if ar.get('cate','')] # e_prep.wrong -> e_prep_wrong

			cursor.execute("insert ignore into mkf(sntmd5, snt, kps, tok, chunk, meta, feedback) values(%s,%s,%s,%s,%s,%s,%s)", (sntmd5, snt, ' '.join(kps),
			json.dumps(doc_tok(doc)), json.dumps(doc_chunk(doc)), json.dumps(meta), json.dumps(fds)  ) 	) #, spacy.tobs(doc)


def load(infile, host='172.17.0.1',port=3306,user='root',password='cikuutest!',db='dskmkf'):  
	''' load the lined dsk to my:dskmkf  '''
	import pymysql
	conn = pymysql.connect(host=host,port=port,user=user,password=password,db=db)
	cursor= conn.cursor()
	for line in util.readline(infile) :
		try:
			res = json.loads(line)
			#res['info'].update({"essay_id": arr.get("essay_id", 0), "rid": arr.get("request_id", 0), "uid": arr.get("user_id",0), "e_version": arr.get("version",0) })
			submit_dskmkf(res, cursor)	 
			conn.commit()
		except Exception as ex: 
			print(">>line Ex:", ex, "\t|", line) #>>line Ex: 'NoneType' object is not subscriptable
			exc_type, exc_value, exc_traceback_obj = sys.exc_info()
			traceback.print_tb(exc_traceback_obj)
	print("finished parsing:", infile)
	
if __name__ == '__main__': 
	fire.Fire(load) 