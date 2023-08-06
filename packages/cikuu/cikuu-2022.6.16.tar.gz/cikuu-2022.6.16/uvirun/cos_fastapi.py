# 2022.6.30  
from uvirun import *
from util import likelihood
import pandas as pd
import requests, requests_cache
requests_cache.install_cache('/data/model/cos/cos_cache') # walk over, to load all, to fill the cache , to be used offline 
cos_url = os.getenv('cos_url', 'https://json-1257827020.cos.ap-shanghai.myqcloud.com') #cos  = lambda key="bnc.pos.VERB": requests.get(f"https://json-1257827020.cos.ap-shanghai.myqcloud.com/{key}").json()

@app.get('/cos', tags=["cos"])
def cos(key="gzjc.dobj_VERB_NOUN", default={}): 
	try:
		return requests.get(f"{cos_url}/{key}").json()
	except Exception as e:
		return default 

@app.get('/cos/get', tags=["cos"])
def cosget(key:str="gzjc.dobj_VERB_NOUN", hkey:str="open", default={}): 
	''' {'mouth': 3, 'curtain': 2, 'window': 2, 'calendar': 1, 'cupboard': 1, 'door': 1, 'envelope': 1, 'eye': 1, 'frontier': 1, 'hook': 1, 'letter': 1, 'message': 1, 'office': 1, 'outward': 1, 'park': 1, 'railway': 1, 'resource': 1, 'school': 1} '''
	try:
		return requests.get(f"{cos_url}/{key}").json().get(hkey, default)
	except Exception as e:
		return default 

@app.get('/cos/keyness', tags=["cos"])
def cos_keyness(suffix:str="poslemcnt",  hkey:str='VERB', cp1:str='clec', cp2:str='dic', words:str=None): 
	''' words: consider,increase,close '''
	arr1, arr2 = cos(f"{cp1}.{suffix}").get(hkey, {}), cos(f"{cp2}.{suffix}").get(hkey, {})
	sum1, sum2 = cosget(f"{cp1}.{suffix}", "_sntsum", 1), cosget(f"{cp2}.{suffix}", "_sntsum", 1)
	words = set( [ k for k,v in arr1.items()] ).union(set( [ k for k,v in arr2.items()] )) if words is None else words.strip().split(',')
	return [(w, arr1.get(w,0), arr2.get(w,0), likelihood(arr1.get(w,0), arr2.get(w,0), sum1, sum2))  for w in words]

@app.get('/cos/lemma_keyness', tags=["cos"])
def cos_lemma_keyness(hkey:str='VERB', hval:str='consider', cp1:str='clec', cp2:str='dic', suffix:str="poslemcnt"): 
	'''  '''
	return  likelihood( cosget(f"{cp1}.{suffix}", hkey).get(hval, 0), cosget(f"{cp2}.{suffix}", hkey).get(hval, 0), cosget(f"{cp1}.{suffix}", "_sntsum", 1), cosget(f"{cp2}.{suffix}", "_sntsum", 1))

cos_ssi_mf =lambda key="dic.dobj_VERB_NOUN", hkey='open', hval='door': round(cos(key).get(hkey, {}).get(hval, 0) * 1000000 / cos(key).get('_sntsum', 1) , 2)
@app.get('/cos/trp_mf', tags=["cos"])
def cos_trp_mf(cps:str='clec,gzjc,dic,bnc,twit', rel:str='dobj_VERB_NOUN', gov:str='learn', dep:str='knowledge'): 
	''' [{'corpus': 'gzjc', 'mf': 112.7}, {'corpus': 'dic', 'mf': 373.93}, {'corpus': 'bnc', 'mf': 405.38}]  2022.6.27 '''
	return [ {"corpus": cp,  "mf": cos_ssi_mf(f"{cp}.{rel}", gov, dep)} for cp in cps.split(',')] #"trp":f"{rel}/{gov} {dep}",

@app.get('/cos/posrank', tags=["cos"])
def cos_posrank(cp:str='dic', pos:str='VERB', topk:int=10): 
	''' VERB/LEX/LEM/ADJ =>  [('be', 66486), ('have', 41853), ('make', 21694), ('go', 18666), ('take', 16745), ('get', 15897), ('say', 14685), ('do', 12853), ('give', 12252), ('come', 12231)] '''
	return list(cosget(f"{cp}.poslemcnt", pos).items())[0:topk]  # the first one is _sum 

@app.get('/cos/lemvs', tags=["cos"])
def cos_lemvs(pos:str='VERB', cp1:str='clec', cp2:str='dic', topk:int=0): 
	''' VERB rank vs  '''
	arr1, arr2 = cosget(f"{cp1}.poslemcnt", pos), cosget(f"{cp2}.poslemcnt", pos)
	sum1, sum2 = cosget(f"{cp1}.poslemcnt", "_sntsum", 1), cosget(f"{cp2}.poslemcnt", "_sntsum", 1)
	if topk ==0: topk = len(arr1) 
	return [ {"word":w, cp1: round(1000000 * cnt/sum1, 2), cp2: round(1000000 * arr2.get(w, 0)/sum2, 2), 'keyness': likelihood(cnt, arr2.get(w, 0), sum1, sum2) } for w, cnt in list(arr1.items())[0:topk] ]

@app.get('/cos/getsi', tags=["cos"])
def cos_getsi(key:str="gzjc.dobj_VERB_NOUN", hkey:str="open", hval:str='door'): return {"count": cosget(key, hkey).get(hval, 0)}

@app.get('/cos/trpvs', tags=["cos"])
def cos_trpvs(w:str='knowledge', rel:str='~dobj_VERB_NOUN', cp1:str='clec', cp2:str='dic', added:str='perc', topk:int=0): 
	''' * knowlege/~dobj_VERB_NOUN in two corpus | added=perc/keyness '''
	df =  pd.DataFrame({cp1: cos(f'{cp1}.{rel}').get(w,{}), cp2: cos(f'{cp2}.{rel}').get(w,{})}).fillna(0)
	if added == 'perc': 
		for col in df.columns: 	df[f"{col}_perc"] = round((df[col] / df[col].sum()) * 100, 2)
		df = df.sort_values(df.columns[0], ascending=False) #if topk > 0 : 
	elif added == 'keyness': 
		sum1, sum2 = df[cp1].sum() + 0.0001, df[cp2].sum() + 0.0001
		df["keyness"] = [ likelihood(row[cp1], row[cp2], sum1, sum2) for index, row in df.iterrows() ]

	arr = [ dict(dict(row), **{"term": index} ) for index, row in df.iterrows()] 
	return arr[0:topk] if topk > 0  else arr 

if __name__ == "__main__":   #uvicorn.run(app, host='0.0.0.0', port=80)
	print ( cos_lemma_keyness()) 	