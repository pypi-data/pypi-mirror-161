#2022.7.1 #2022-1-30  uvicorn mt-en-zh:app --port 80 --host 0.0.0.0  #https://huggingface.co/Helsinki-NLP/opus-mt-zh-en
from uvirun import * 
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

@app.post('/trans', tags=["trans"])
def trans(examples:list=["I love you.","I am too tired to move on."], max_length:int=128, name:str="Helsinki-NLP/opus-mt-en-zh", asdic:bool=False):  
	''' ["我来自北京。","锄禾日当午","能穿多少穿多少。"] | Helsinki-NLP/opus-mt-zh-en '''
	if not hasattr(trans,name): 
		setattr(trans, f"{name}_tokenizer", AutoTokenizer.from_pretrained(f"/data/model/trans/{name}") )
		setattr(trans, name, AutoModelForSeq2SeqLM.from_pretrained(f"/data/model/trans/{name}") )
	tokenizer = getattr(trans, f"{name}_tokenizer")
	model	  = getattr(trans, name)
	inputs	  = tokenizer(examples, padding=True, return_tensors="pt")
	outputs	  = model.generate(**inputs, max_length=max_length)
	tgts	  = [tokenizer.decode(ids, skip_special_tokens=True) for ids in outputs]
	return  {src: tgt for src, tgt in zip(examples, tgts)} if asdic else [ {"src": src, "tgt": tgt} for src, tgt in zip(examples, tgts) ]

@app.get('/trans', tags=["trans"])
def trans_get(text:str="I love you. I am too tired to move on.", max_length:int=128, name:str="Helsinki-NLP/opus-mt-en-zh"):  
	return trans([text], max_length, name, asdic=True).get(text, text ) 

if __name__ == '__main__':	#uvicorn.run(app, host='0.0.0.0', port=8889)
	print (trans()) 
	print (trans(["我来自北京。","锄禾日当午","能穿多少穿多少。"], name="Helsinki-NLP/opus-mt-zh-en")) 
	print (trans_get()) 

'''
[{'src': 'I love you.', 'tgt': '我爱你'}, {'src': 'I am too tired to move on.', 'tgt': '我太累了,不能继续往前走了。'}]
[{'src': '我来自北京。', 'tgt': "I'm from Beijing."}, {'src': '锄禾日当午', 'tgt': "It's noon in the morning."}, {'src': '能穿多少穿多少。', 'tgt': 'You can wear as much as you want.'}]
[{'src': 'I love you. I am too tired to move on.', 'tgt': '我爱你,我太累了,不能继续生活'}]
'''