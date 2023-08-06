# 2022.6.30  #uvicorn trf_unmasker_fastapi:app --reload --port 80 --host 0.0.0.0
from uvirun import *

@app.get('/unmasker', tags=["unmasker"])
def unmasker(q:str="The goal of life is *.", model:str='native', topk:int=10, verbose:bool=False): 
	''' model: native/nju/fengtai/sino/sci/gblog/twit	'''
	from transformers import pipeline
	if not hasattr(unmasker, model): 
		setattr(unmasker, model, pipeline('fill-mask', model=f'/data/model/unmasker/distilbert-base-uncased-{model}') )
	arr = getattr(unmasker, model)(q.replace('*','[MASK]'), top_k = topk) #result: [{'score': 0.03619174659252167, 'token': 8404, 'token_str': 'happiness', 'sequence': 'the goal of life is happiness.'}, {'score': 0.030553610995411873, 'token': 7691, 'token_str': 'survival', 'sequence': 'the goal of life is survival.'}, {'score': 0.016977205872535706, 'token': 12611, 'token_str': 'salvation', 'sequence': 'the goal of life is salvation.'}, {'score': 0.016698481515049934, 'token': 4071, 'token_str': 'freedom', 'sequence': 'the goal of life is freedom.'}, {'score': 0.015267301350831985, 'token': 8499, 'token_str': 'unity', 'sequence': 'the goal of life is unity.'}]
	return [ dict( row, **{"name": model}) for row in arr ] if verbose else [ {"name": model, "word": row["token_str"], "score": round(row["score"], 4)} for row in arr ]

@app.get('/unmaskers', tags=["unmasker"])
def unmaskers(q:str="The goal of life is *.", models:str='native,nju', topk:int=10): 
	''' model: native/nju/fengtai/sino/sci/gblog/twit  2022.7.1 '''
	arr = []
	[ arr.extend(unmasker(q, model, topk)) for model in models.strip().split(',') ]
	return arr

@app.get('/unmasker/html', response_class=HTMLResponse)
def unmasker_html(q:str="The goal of life is *.", model:str='native', topk:int=10): 
	''' return HTML <ol><li> , 2022.7.23 '''
	rows = unmasker(q, model, topk) 
	maxscore = rows[0]['score'] + 0.01 # font-weight: 100, 200, ..., 900
	snts = "\n".join([f"<li><span style='font-weight:{int(10*row['score']/maxscore)}00'>{row.get('word','')}<span></li>" for row in rows])
	return HTMLResponse(content=f"<ol>{snts}</ol>")

if __name__ == '__main__': #print (models['native']("The goal of life is [MASK]."))
	print("result:", unmasker_html())