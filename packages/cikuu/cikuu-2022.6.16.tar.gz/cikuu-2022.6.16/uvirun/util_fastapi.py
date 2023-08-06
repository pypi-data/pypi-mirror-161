# 2022.6.30 cp from uvicorn corpusly-19200:app --host 0.0.0.0 --port 19200 --reload
from uvirun import *
from util import likelihood

@app.post('/util/dualarr_keyness')
def dualarr_keyness(src:dict={"one":2, "two":12}, tgt:dict={"three":3, "one":1}, sum1:float=None, sum2:float=None, threshold:float=0.0, leftonly:bool=False): 
	'''  "src": {"one":2, "two":12}, "tgt": {"three":3, "one":1}, added 2021.10.24  '''
	if not sum1: sum1 = sum([i for s,i in src.items()])
	if not sum2: sum2 = sum([i for s,i in tgt.items()])
	if not sum1: sum1 = 0.0001
	if not sum2: sum2 = 0.0001
	words = set(src.keys()) | set(tgt.keys()) if not leftonly else set(src.keys())
	res  = [(w, src.get(w,0), tgt.get(w,0), sum1, sum2, likelihood(src.get(w,0.01), tgt.get(w,0.01), sum1, sum2))  for w in words]
	res.sort(key=lambda a:a[-1], reverse=True)
	return [ar for ar in res if abs(ar[-1]) > threshold ]

@app.get('/essays')
def dic_docs(name:str='hello'): 
	''' src data in pypi/dic/__init__.py '''
	import dic 
	return dic.docs(name) 

four_int = lambda four, denom=100: [int( int(a)/denom) for a in four]
xy = lambda four : [f"{a},{b}" for a in range(four[0], four[2]+2) for b in range( four[1], four[3] + 2) ] # xy_to_item
@app.post('/penly/xy_to_item')
def penly_xy_to_items(arr:list=[[2500,2960,3000,3160,"select-11:C"],[3500,2960,3700,3160,"select-11:D"]], denom:int=100): 
	''' submit data into the permanent store, updated 2021.10.8 '''
	return {k:tag for x1,y1,x2,y2,tag in arr for k in xy( ( int(x1/denom), int(y1/denom), int(x2/denom), int(y2/denom)) ) }

if __name__ == "__main__":  
	print (penly_xy_to_items())
	#uvicorn.run(app, host='0.0.0.0', port=80)

'''
@app.get('/dsk/annotate', tags=["dsk"])
def dsk_annotate(text:str='The quick fox jumped over the lazy dog.', cates:str='e_snt.nv_agree,e_spell'): 
	# 2022.7.27 night 
	from dsk_fastapi import dsk_wrapper
	cates = cates.strip().split(',') 
	dsk = dsk_wrapper(text ) 
	tokens = []
	for ar in dsk['snt']:
		for mkf in ar:
			arrlex = mkf.get("meta",{}).get("lex_list",'').split()
			si = {}
			for k,v in mkf.get('feedback',{}).items(): 
				si[ v['ibeg'] ] = v['cate']
			tokens.extend( [ {'text': w} if not i in si else {'text': t.text, "labels":[si[i]]} for i, w in enumerate(arrlex) ] )
	
	return {"tokens": tokens,"labels": [ {"text": cate} for cate in cates] }
'''