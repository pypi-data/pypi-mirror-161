# 2022.7.2  depart from pypi/so/__main__.py
import json,fire,sys, os, hashlib ,time , requests,logging, warnings
from collections import Counter , defaultdict
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
warnings.filterwarnings("ignore")

from qcloud_cos import CosConfig,CosS3Client  #https://console.cloud.tencent.com/cam/capi
config = CosConfig(Region='ap-shanghai', SecretId='AKIDd5HCqZ2EAoCI7f16uQjlX3IHzQaU7TXL', SecretKey='YppXzA4g27vSihOoxpQknZ4JGWVCcleF' , Token=None, Scheme='https')  #test-1308226317
client = CosS3Client(config) #https://json-1257827020.cos.ap-shanghai.myqcloud.com/gzjc.trp
upload = lambda name, content : client.put_object("json-1257827020", Body=content, Key=name)
esname = os.getenv("esname", "es.corpusly.com:9200")

#from so import * 
cursor_sql = lambda query, cursor: requests.post(f"http://{esname}/_sql", json={"query":query, "cursor":cursor}).json() #  move to so/__init__ later

def cursor_rows(query="select dep, gov, lem, pos, count(*) cnt from gzjc where type='tok' group by dep, gov, lem, pos"):
	rows = []				
	cursor=''
	while True : 
		res = cursor_sql(query, cursor)  
		rows.extend(res['rows'])
		cursor = res.get('cursor','') 
		if not cursor: break
	return rows 

def upload_tsv(name, query, rows_f=lambda rows: [ "\t".join([str(a) for a in row]) for row in rows]):
	rows = cursor_rows(query)
	arr  = rows_f(rows) 
	upload( name, "\n".join(arr))

def sqlsi(query): #select lex, count(*)
	si = Counter()
	cursor=''
	while True : 
		res = cursor_sql(query, cursor)  
		si.update( dict(res['rows']) )
		cursor = res.get('cursor','') 
		if not cursor: break
	return si #dict(si.most_common())

def sqlssi(query="select lem, lex, count(*) cnt from gzjc where type = 'tok' and lem rlike '[a-z]+' group by lem, lex"
		, iftrue = lambda s1, s2: s1 and s2
		, s1_func = lambda s: s
		, s2_func = lambda s: s  # lower()
		): 
	ssi = defaultdict(Counter)
	cursor=''
	while True : 
		res = cursor_sql(query, cursor) 
		[ ssi[ s1_func(s1) ].update({ s2_func(s2) :cnt}) for s1, s2, cnt in res['rows'] if iftrue(s1, s2) ] 
		cursor = res.get('cursor','') 
		if not cursor: break
	return ssi 

trpssi	= lambda idxname, dep='dobj', gpos='VERB', dpos='NOUN': sqlssi(f"select gov, lem, count(*) cnt from {idxname} where type = 'tok' and pos = '{dpos}' and dep ='{dep}' and lem rlike '[a-z]+' and gov like '%_{gpos}' group by gov, lem", s1_func =lambda s: s.split('_')[0])
_trpssi = lambda idxname, dep='dobj', gpos='VERB', dpos='NOUN': sqlssi(f"select lem, gov, count(*) cnt from {idxname} where type = 'tok' and pos = '{dpos}' and dep ='{dep}' and lem rlike '[a-z]+' and gov like '%_{gpos}' group by lem, gov", s2_func =lambda s: s.split('_')[0])

def save_ssi(idxname, suffix, ssi, dic): 
	with open(f"{idxname}.{suffix}", 'w') as fw: 
		start = time.time()
		fw.write( json.dumps( dict({ k: dict(v.most_common()) for k,v in ssi.items()}, **dic ) ) + "\n") 
		print( f"saved: {idxname}.{suffix}, \t using: ", time.time() - start, flush=True)

class ES(object):
	def __init__(self): pass

	def tsv(self, idxname):
		''' trp(rel, gov, dep, cnt) '''
		upload_tsv(f"{idxname}.trp", f"select dep, gov, lem, pos, count(*) cnt from {idxname} where type='tok' and dep not in ('PUNCT','ROOT','X') and pos not in ('PROPN') group by dep, gov, lem, pos "
					, rows_f = lambda rows: [ f"{dep}_{gov.split('_')[-1]}_{pos}\t{gov.split('_')[0]}\t{lem}\t{cnt}"  for dep,gov,lem,pos,cnt in rows if gov.isascii() and lem.isascii() and lem.islower()] )
		upload_tsv(f"{idxname}.tok", f"select lem, pos, tag, lex, count(*) cnt from {idxname} group by lem,pos,tag,lex")
		upload_tsv(f"{idxname}.sum", f"select type, count(*) cnt from {idxname} group by type")

	def ssi(self, idxname): 
		''' dump to ssi file , 2022.6.29 '''
		dic = {"_sntsum": sntnum(idxname), "_lexsum": lexsum(idxname) }
		print ("started:", idxname, "\t", dic, flush=True) 

		poslemcnt = sqlssi(f"select pos, lem, count(*) cnt from {idxname} where type = 'tok' and lem rlike '[a-z]+' group by pos, lem", iftrue=lambda pos, lem: pos not in ('NNP','PUNCT','X') )
		poslemcnt['LEX'] = sqlsi(f"select lex, count(*) cnt from {idxname} where type = 'tok' and lex rlike '[a-zA-Z]+' group by lex")
		poslemcnt['LEM'] = sqlsi(f"select lem, count(*) cnt from {idxname} where type = 'tok' and lem rlike '[a-z]+' group by lem")
		save_ssi(idxname, 'poslemcnt', poslemcnt, dic) 

		save_ssi(idxname, "lemlexcnt", sqlssi(f"select lem, lex, count(*) cnt from {idxname} where type = 'tok' and lem rlike '[a-z]+' group by lem, lex", iftrue=lambda pos, lem: pos not in ('NNP','PUNCT','X') , s2_func = lambda s: s.lower() ), dic)  
		save_ssi(idxname, "lemposcnt", sqlssi(f"select lem, pos, count(*) cnt from {idxname} where type = 'tok' and lem rlike '[a-z]+' group by lem, pos", iftrue=lambda pos, lem: pos not in ('NNP','PUNCT','X') ),  dic) 

		save_ssi(idxname, "dobj_VERB_NOUN",		trpssi(idxname, 'dobj', 'VERB', 'NOUN'), dic) 
		save_ssi(idxname, "~dobj_VERB_NOUN",	_trpssi(idxname, 'dobj', 'VERB', 'NOUN'), dic) 
		save_ssi(idxname, "nsubj_VERB_NOUN",	trpssi(idxname, 'nsubj', 'VERB', 'NOUN'), dic) 
		save_ssi(idxname, "~nsubj_VERB_NOUN",	_trpssi(idxname, 'nsubj', 'VERB', 'NOUN'), dic) 
		save_ssi(idxname, "amod_NOUN_ADJ",		trpssi(idxname, 'amod', 'NOUN', 'ADJ'), dic) 
		save_ssi(idxname, "~amod_NOUN_ADJ",		_trpssi(idxname, 'amod', 'NOUN', 'ADJ'), dic) 
		save_ssi(idxname, "advmod_VERB_ADV",	trpssi(idxname, 'advmod', 'VERB', 'ADV'), dic) 
		save_ssi(idxname, "~advmod_VERB_ADV",	_trpssi(idxname, 'advmod', 'VERB', 'ADV'), dic) 
		save_ssi(idxname, "advmod_ADJ_ADV",		trpssi(idxname, 'advmod', 'ADJ', 'ADV'), dic) 
		save_ssi(idxname, "~advmod_ADJ_ADV",	_trpssi(idxname, 'advmod', 'ADJ', 'ADV'), dic) 

		save_ssi(idxname, "meta", {
			"wordlen":	sqlsi(f"select length(lex) wc, count(*) cnt from {idxname} where type = 'tok' group by wc"), 
			"pos":		sqlsi(f"select pos, count(*) cnt from {idxname} where type = 'tok' group by pos"), 
			"tag":		sqlsi(f"select tag, count(*) cnt from {idxname} where type = 'tok' group by tag"), 
			"dep":		sqlsi(f"select dep, count(*) cnt from {idxname} where type = 'tok' group by dep"), 
			"tc":		sqlsi(f"select tc, count(*) cnt from {idxname} where type = 'snt' group by tc"),
			"stype":	sqlsi(f"select tag, count(*) cnt from {idxname} where type = 'stype' group by tag"),
			"vpat":		sqlsi(f"select type, count(*) cnt from {idxname} where type like 's%' or type like 'v%' group by type"), # svo, vprt ,vtov
			"cl":		sqlsi(f"select tag, count(*) cnt from {idxname} where type = 'cl' group by tag"),
			"verbnet":	sqlsi(f"select chunk, count(*) cnt from {idxname} where type = 'verbnet' group by chunk")} ,  dic) 
		print ('[tocos] totally finished:', idxname)



if __name__ == '__main__':
	fire.Fire(ES)

'''
select * from url('https://json-1257827020.cos.ap-shanghai.myqcloud.com/gzjc.trp', TSV, 'rel String, gov String, dep String, cnt UInt32') where rel ='dobj_VERB_NOUN' and dep ='knowledge'

		rows = cursor_rows(f"select dep, gov, lem, pos, count(*) cnt from {idxname} where type='tok' and dep not in ('PUNCT','ROOT','X') and pos not in ('PROPN') group by dep, gov, lem, pos ") #order by dep, pos, gov, lem, cnt desc
		arr  = [ f"{dep}_{gov.split('_')[-1]}_{pos}\t{gov.split('_')[0]}\t{lem}\t{cnt}"  for dep,gov,lem,pos,cnt in rows if gov.isascii() and lem.isascii() and lem.islower()]
		upload( f"{idxname}.trp", "\n".join(arr))

-- trp join 
with a as (select dep,cnt from url('https://json-1257827020.cos.ap-shanghai.myqcloud.com/clec.trp', TSV, 'rel String, gov String, dep String, cnt UInt32') where rel ='dobj_VERB_NOUN' and gov='open'), 
b as (select dep,cnt from url('https://json-1257827020.cos.ap-shanghai.myqcloud.com/gzjc.trp', TSV, 'rel String, gov String, dep String, cnt UInt32') where rel ='dobj_VERB_NOUN' and gov='open')
select * from a full outer join b on a.dep = b.dep 
| left outer | right outer

-- sum 
select * from url('https://json-1257827020.cos.ap-shanghai.myqcloud.com/gzjc.sum', TSV, 'type String, cnt UInt32') 

-- tok
select * from url('https://json-1257827020.cos.ap-shanghai.myqcloud.com/gzjc.tok', TSV, 'lem String, pos String, tag String, lex String, cnt UInt32') where lem = 'book' 

-- trp perc 
with a as (select dep word,cnt from url('https://json-1257827020.cos.ap-shanghai.myqcloud.com/clec.trp', TSV, 'rel String, gov String, dep String, cnt UInt32') where rel ='dobj_VERB_NOUN' and gov='open'), 
suma as ( select sum(cnt) sumi from a )
select word, 100 * cnt/sumi perc from a, suma

-- trp dual vs   http://werror.com:8123/play
with src as (
with a as (select dep word,cnt from url('https://json-1257827020.cos.ap-shanghai.myqcloud.com/clec.trp', TSV, 'rel String, gov String, dep String, cnt UInt32') where rel ='dobj_VERB_NOUN' and gov='open'), 
suma as ( select sum(cnt) sumi from a )
select word, 100 * cnt/sumi perc from a, suma
), 
tgt as(
with a as (select dep word,cnt from url('https://json-1257827020.cos.ap-shanghai.myqcloud.com/gzjc.trp', TSV, 'rel String, gov String, dep String, cnt UInt32') where rel ='dobj_VERB_NOUN' and gov='open'), 
suma as ( select sum(cnt) sumi from a )
select word, 100 * cnt/sumi perc from a, suma
)
select src.*, tgt.perc from src left join tgt on src.word = tgt.word 
order by src.perc desc 
limit 10 

-- lem pos/lex 
select * from url('https://json-1257827020.cos.ap-shanghai.myqcloud.com/gzjc.tok', TSV, 'lem String, pos String, tag String, lex String, cnt UInt32') where lem = 'sound' 

'''