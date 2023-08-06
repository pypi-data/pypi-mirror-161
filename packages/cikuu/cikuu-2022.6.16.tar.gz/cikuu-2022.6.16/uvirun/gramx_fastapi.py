# 2022.6.30, add snt support   /data/model/gramx/gram2.marisa,  1,2,3,4,5
from uvirun import *
import collections, marisa_trie
toint	= lambda bs:  int.from_bytes(bs, byteorder='little', signed=True)
gram2i	= lambda gram: int.from_bytes(model(gram.strip().count(' ') + 1).get(gram, [b'\x00\x00\x00\x00'])[0], byteorder='little', signed=True)

def model(i): #lazy loading
	if not hasattr(model, f"gram{i}"):  setattr(model, f"gram{i}", marisa_trie.BytesTrie().load( f"/data/model/gramx/gram{i}.marisa" ) )
	return getattr(model, f"gram{i}")

@app.get('/gramx', tags=["gramx"])
def gramx(gram: str = 'overcome difficulty'): 
	''' return count of given chunk,  gram1..gram5, 2022.6.30 '''
	i = gram.strip().count(' ') + 1
	if i > 5 : i = 5 
	return int.from_bytes(model(i).get(gram, [b'\x00\x00\x00\x00'])[0], byteorder='little', signed=True)

@app.post('/gramx', tags=["gramx"])
def gramx_post(grams: list = ['overcome difficulty','overcame difficulty','overcame difficulty***']): 
	return { gram.strip(): gramx(gram.strip()) for gram in grams }

@app.get('/gramx/grams', tags=["gramx"])
def gramx_grams(grams: str = 'overcome difficulty,overcame difficulty,overcame difficulty***', sepa:str=','): 
	return { gram.strip(): gramx(gram.strip()) for gram in grams.strip().split(sepa) }

@app.get('/gramx/startswith', tags=["gramx"])
def gramx_startswith(prefix: str = 'overcome diffi', topk:int=10): 
	i = prefix.strip().count(' ') + 1
	words = [ (k,toint(v)) for k,v in list(model(i).iteritems(prefix))] # iterkeys
	return [{"gram":gram, "cnt":i} for gram, i in collections.Counter(dict(words)).most_common(topk)]

#valid_token	= lambda t: t.pos_ not in ("PUNCT","PROPN","NUM",'SPACE') and t.text.isalpha()
@app.get('/gramx/check', tags=["gramx"])
def gramx_check(text: str = 'The quick fox jumped over the lazy dog. Justice delayed is justice denied.', n:int=2): 
	''' check snt grami, with spacy,  added 2022.6.27'''
	import spacy 
	if not hasattr(spacy, 'nlp'): spacy.nlp = spacy.load('en_core_web_sm') 
	tdoc = spacy.nlp(text)
	res = []
	for sent in tdoc.sents: 
		doc = sent.as_doc()
		res.extend( [{"i":i, "gram": " ".join([ doc[i+j].text for j in range(n)]).lower()
		, "pos": ",".join([ doc[i+j].pos_ for j in range(n)])
		, "tag": ",".join([ doc[i+j].tag_ for j in range(n)]) #, "morph": ",".join([ doc[i+j].morph.to_json() for j in range(n)])
		, 'grami': gram2i(" ".join([ doc[i+j].text for j in range(n)]).lower())
		, 'sent': sent.sent.text
		} for i in range(len(doc) - n + 1)])
	return res 

if __name__ == '__main__': 
	#print (gramx())
	#print ( gramx_startswith(), flush=True) 
	print (gramx_check()[-1])

'''
	if i == 2:	return [{'i':t.i, 'lex':t.text, 'text_with_ws':t.text_with_ws, 'lem':t.lemma_, 'pos':t.pos_, 'tag':t.tag_, 'valid':valid_token(t), 
			f"gram{i}": gram2i(t.text.lower() + ' ' + doc[t.i+1].text.lower()) if t.i+1 < len(doc) and valid_token(t) and valid_token(doc[t.i+1]) else -1 }  for t in doc]
	elif i == 3:	return [{'i':t.i, 'lex':t.text, 'text_with_ws':t.text_with_ws, 'lem':t.lemma_, 'pos':t.pos_, 'tag':t.tag_, 'valid':valid_token(t), 
			f"gram{i}": gram2i(t.text.lower() + ' ' + doc[t.i+1].text.lower()+ ' ' + doc[t.i+2].text.lower()) if t.i+2 < len(doc) and valid_token(t) and valid_token(doc[t.i+1])  and valid_token(doc[t.i+2]) else -1 }  for t in doc]
	elif i == 4:	return [{'i':t.i, 'lex':t.text, 'text_with_ws':t.text_with_ws, 'lem':t.lemma_, 'pos':t.pos_, 'tag':t.tag_, 'valid':valid_token(t), 
			f"gram{i}": gram2i(t.text.lower() + ' ' + doc[t.i+1].text.lower()+ ' ' + doc[t.i+2].text.lower() + ' ' + doc[t.i+3].text.lower() ) if t.i+3 < len(doc) and valid_token(t) and valid_token(doc[t.i+1])  and valid_token(doc[t.i+2])  and valid_token(doc[t.i+3]) else -1 }  for t in doc]
	elif i == 5:	return [{'i':t.i, 'lex':t.text, 'text_with_ws':t.text_with_ws, 'lem':t.lemma_, 'pos':t.pos_, 'tag':t.tag_, 'valid':valid_token(t), 
			f"gram{i}": gram2i(t.text.lower() + ' ' + doc[t.i+1].text.lower()+ ' ' + doc[t.i+2].text.lower() + ' ' + doc[t.i+3].text.lower() + ' ' + doc[t.i+4].text.lower() ) if t.i+4 < len(doc) and valid_token(t) and valid_token(doc[t.i+1])  and valid_token(doc[t.i+2])  and valid_token(doc[t.i+3]) and valid_token(doc[t.i+4]) else -1 }  for t in doc]
	return []
'''