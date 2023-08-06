# 2022.7.4 merge verbnet and terms code 
# 2022.5.28, redisgears's python is 3.7 , to be compatible 
# 2022.3.20, usage:  import en |  spacy.nlp("hello")   
import json,spacy,os,builtins
from spacy.tokens import DocBin,Doc,Token
from spacy.tokenizer import Tokenizer
from spacy.matcher import Matcher,DependencyMatcher
from spacy.lang.char_classes import ALPHA, ALPHA_LOWER, ALPHA_UPPER, CONCAT_QUOTES, LIST_ELLIPSES, LIST_ICONS
from spacy.util import compile_infix_regex

def custom_tokenizer(nlp): #https://stackoverflow.com/questions/58105967/spacy-tokenization-of-hyphenated-words
	infixes = (
		LIST_ELLIPSES
		+ LIST_ICONS
		+ [
			r"(?<=[0-9])[+\-\*^](?=[0-9-])",
			r"(?<=[{al}{q}])\.(?=[{au}{q}])".format(
				al=ALPHA_LOWER, au=ALPHA_UPPER, q=CONCAT_QUOTES
			),
			r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
			#r"(?<=[{a}])(?:{h})(?=[{a}])".format(a=ALPHA, h=HYPHENS),
			r"(?<=[{a}0-9])[:<>=/](?=[{a}])".format(a=ALPHA),
		]
	)
	infix_re = compile_infix_regex(infixes)
	return Tokenizer(nlp.vocab, prefix_search=nlp.tokenizer.prefix_search,
								suffix_search=nlp.tokenizer.suffix_search,
								infix_finditer=infix_re.finditer,
								token_match=nlp.tokenizer.token_match,
								rules=nlp.Defaults.tokenizer_exceptions)

def spacydoc(snt, use_cache=True): 
	''' added 2022.3.20 '''
	from en.spacybs import Spacybs
	if not use_cache: return spacy.nlp(snt)
	if not hasattr(spacydoc, 'db'): spacydoc.db = Spacybs("spacy311.sqlite")
	bs = spacydoc.db[snt]
	if bs is not None : return spacy.frombs(bs)
	doc = spacy.nlp(snt) 
	spacydoc.db[snt] = spacy.tobs(doc) 
	spacydoc.db.conn.commit()
	return doc 

def sqlitedoc(snt, table): 
	'''multiple tables supported,  added 2022.3.27 '''
	import sqlite3
	if not hasattr(sqlitedoc, 'conn'): 
		sqlitedoc.conn =	sqlite3.connect("spacy311.sntbs", check_same_thread=False) 
		sqlitedoc.conn.execute('PRAGMA synchronous=OFF')

	sqlitedoc.conn.execute(f'CREATE TABLE IF NOT EXISTS {table} (key varchar(512) PRIMARY KEY, value blob)')
	item = sqlitedoc.conn.execute(f'SELECT value FROM "{table}" WHERE key = ? limit 1', (key,)).fetchone()
	if item	is not None: return spacy.frombs(item[0]) 

	doc = spacy.nlp(snt) 
	sqlitedoc.conn.execute(f'REPLACE	INTO {table} (key,	value) VALUES (?,?)',	(snt, spacy.tobs(doc) ))
	sqlitedoc.conn.commit()
	return doc 

def to_docbin(doc):
	doc_bin= spacy.tokens.DocBin()
	doc_bin.add(doc)
	return doc_bin.to_bytes()

def from_docbin(bs): 
	return list(spacy.tokens.DocBin().from_bytes(bs).get_docs(spacy.nlp.vocab))[0] if bs else None

if not hasattr(spacy, 'nlp'):
	spacy.nlp		= spacy.load('en_core_web_sm') 
	spacy.tobs		= to_docbin # for old codes
	spacy.frombs	= from_docbin
	spacy.nlp.tokenizer = custom_tokenizer(spacy.nlp)	#nlp.tokenizer.infix_finditer = infix_re.finditer
	#print([t.text for t in nlp("It's 1.50, up-scaled haven't")]) # ['It', "'s", "'", '1.50', "'", ',', 'up-scaled', 'have', "n't"]

def rgetdoc(rbs, snt, prefix="bs:", ttl:int=37200): 
	''' bytes , 2022.5.28 '''
	bs = rbs.get( prefix + snt) 
	if bs: return Doc(spacy.nlp.vocab).from_bytes(bs)  # spacy.frombs(bs) 
	doc = spacy.nlp(snt) 
	rbs.setex(prefix + snt, ttl, doc.to_bytes()) 
	return doc 

def getdoc(snt, bs):  # execute("GET", f"bytes:{snt}") 
	return Doc(spacy.nlp.vocab).from_bytes(bs) if bs else spacy.nlp(snt) 

def phrase_matcher(name:str='pp', patterns:list=[[{'POS': 'ADP'},{"POS": {"IN": ["DET","NUM","ADJ",'PUNCT','CONJ']}, "OP": "*"},{"POS": {"IN": ["NOUN","PART"]}, "OP": "+"}]]):
	''' for name, ibeg,iend in matcher(doc) : print(spacy.nlp.vocab[name].text, doc[ibeg:iend].text) '''
	matcher = Matcher(spacy.nlp.vocab)
	matcher.add(name, patterns,  greedy ='LONGEST')
	return matcher

def sntbr(essay, trim:bool=False, with_pid:bool=False): 
	''' added 2022.5.28 '''
	from spacy.lang import en
	if not hasattr(sntbr, 'inst'): 
		sntbr.inst = en.English()
		sntbr.inst.add_pipe("sentencizer")

	doc = sntbr.inst(essay)
	if not with_pid: return [ snt.text.strip() if trim else snt.text for snt in  doc.sents]

	pid = 0 #spacy.sntpidoff	= lambda essay: (pid:=0, doc:=spacy.sntbr(essay), [ ( pid := pid + 1 if "\n" in snt.text else pid,  (snt.text, pid, doc[snt.start].idx))[-1] for snt in  doc.sents] )[-1]
	arr = []
	for snt in  doc.sents:
		if "\n" in snt.text: pid = pid + 1 
		arr.append( (snt.text, pid) ) 
	return arr 

#token_split	= lambda sent: re.findall(r"[\w']+|[.,!?;]", sent) # return list
def common_perc(snt="She has ready.", trans="She is ready."): 
	toks = set([t.text for t in spacy.nlp.tokenizer(snt)])
	return len([t for t in spacy.nlp.tokenizer(trans) if t.text in toks]) / (len(toks)+0.01)

merge_nps		= lambda : spacy.nlp.create_pipe("merge_noun_chunks")
new_matcher		= lambda : Matcher(spacy.nlp.vocab) # by exchunk
toks			= lambda doc:  [{'i':t.i, "head":t.head.i, 'lex':t.text, 'lem':t.lemma_, 'pos':t.pos_, 'tag':t.tag_, 'dep':t.dep_, "gpos":t.head.pos_, "glem":t.head.lemma_} for t in doc ] # JSONEachRow 
postag			= lambda doc:  "_^ " + " ".join([ f"{t.text}_{t.lemma_}_{t.pos_}_{t.tag_}" for t in doc]) + " _$"
non_root_verbs	= lambda doc:  [t for t in doc if t.pos_ == 'VERB' and t.dep_ != 'ROOT'] 
simple_sent		= lambda doc:  len([t for t in doc if t.pos_ == 'VERB' and t.dep_ != 'ROOT']) <= 0 # else is complex sent 
compound_snt	= lambda doc:  len([t for t in doc if t.dep_ == 'conj' and t.head.dep_ == 'ROOT']) > 0
snt_source		= lambda sid, doc: {'type':'snt', 'src': sid, 'snt':doc.text, 'pred_offset': pred_offset(doc), 
				'postag':'_^ ' + ' '.join([f"{t.text}_{t.lemma_}_{t.pos_}_{t.tag_}" if t.text == t.text.lower() else f"{t.text}_{t.text.lower()}_{t.lemma_}_{t.pos_}_{t.tag_}" for t in doc]) + ' _$',
			   'tc': len(doc)}

def pred_offset(doc):
	ar = [ t.i for t in doc if t.dep_ == "ROOT"]
	offset = ar[0] if len(ar) > 0 else 0
	return offset/( len(doc) + 0.1) 

def JSONEachRow(snt): #[{'i': 0, 'head': 1, 'lex': 'The', 'lem': 'the', 'pos': 'DET', 'tag': 'DT', 'dep': 'det', 'gov': 'boy_NOUN', 'chunks': []}, {'i': 1, 'head': 2, 'lex': 'boy', 'lem': 'boy', 'pos': 'NOUN', 'tag': 'NN', 'dep': 'nsubj', 'gov': 'be_AUX', 'chunks': [{'lempos': 'boy_NOUN', 'type': 'NP', 'chunk': 'the boy'}]}, {'i': 2, 'head': 2, 'lex': 'is', 'lem': 'be', 'pos': 'AUX', 'tag': 'VBZ', 'dep': 'ROOT', 'gov': 'be_AUX', 'chunks': []}, {'i': 3, 'head': 2, 'lex': 'happy', 'lem': 'happy', 'pos': 'ADJ', 'tag': 'JJ', 'dep': 'acomp', 'gov': 'be_AUX', 'chunks': []}, {'i': 4, 'head': 2, 'lex': '.', 'lem': '.', 'pos': 'PUNCT', 'tag': '.', 'dep': 'punct', 'gov': 'be_AUX', 'chunks': []}]
	''' added 2022.6.25 ''' 
	doc = spacy.nlp(snt) 
	dic = {}
	for t in doc:
		dic[t.i] = {'i':t.i, "head":t.head.i, 'offset':t.idx, 'lex':t.text, 'lem':t.lemma_, 'pos':t.pos_, 'tag':t.tag_, 'dep':t.dep_, "gov":t.head.lemma_ + "_" + t.head.pos_, "chunks":[] }
	for sp in doc.noun_chunks: 
		dic[ sp.end - 1 ]['chunks'].append( {'lempos': doc[sp.end - 1].lemma_ + "_NOUN", "type":"NP", "chunk":sp.text.lower() } ) ## start/end ? 
	return [ v for v in dic.values()]

def parse(snt, merge_np= False):
	''' used in the notebook, for debug '''
	import pandas as pd
	doc = spacy.nlp(snt)
	if merge_np : spacy.merge_nps(doc)
	return pd.DataFrame({'word': [t.text for t in doc], 'tag': [t.tag_ for t in doc],'pos': [t.pos_ for t in doc],'head': [t.head.orth_ for t in doc],'dep': [t.dep_ for t in doc], 'lemma': [t.text.lower() if t.lemma_ == '-PRON-' else t.lemma_ for t in doc],
	'n_lefts': [ t.n_lefts for t in doc], 'left_edge': [ t.left_edge.text for t in doc], 
	'n_rights': [ t.n_rights for t in doc], 'right_edge': [ t.right_edge.text for t in doc],
	'subtree': str([ list(t.subtree) for t in doc]),'children': str([ list(t.children) for t in doc]),
	'morph': [ t.morph for t in doc],
	}) 

trp_rel		= lambda t:  f"{t.dep_}_{t.head.pos_}_{t.pos_}"  # dobj_VERB_NOUN
trp_reverse = set({"amod_NOUN_ADJ","nsubj_VERB_NOUN"})
trp_tok		= lambda doc, arr:  [ t for t in doc if [ t.dep_, t.head.pos_, t.pos_, t.head.lemma_, t.lemma_ ] == arr ] # arr is exactly 5 list 
gov_dep		= lambda rel, arr : (arr[0], arr[1]) if lemma_order.get(rel, True) else (arr[1], arr[0])  # open door
hit_trp		= lambda t, _rel, _gov_dep:   _rel == trp_rel(t) and _gov_dep == (t.head.lemma_, t.lemma_)
trp_high	= lambda doc, i, ihead :   "".join([ f"<b>{t.text_with_ws}</b>" if t.i in (i, ihead) else t.text_with_ws for t in doc ])
lem_high	= lambda doc, lem :   "".join([ f"<b>{t.text_with_ws}</b>" if t.lemma_ == lem else t.text_with_ws for t in doc ]) # highlight the first lemma 
vp_span		= lambda doc,ibeg,iend: doc[ibeg].lemma_ + " " + doc[ibeg+1:iend].text.lower()

def hyb(doc, start, pat): #l:lemma x:text, p:pos t:tag , e:ent_type 
	arr = []
	for i,c in enumerate(pat): 
		if c == 'l':	arr.append(doc[start +i].lemma_)
		elif c == 'p':	arr.append(doc[start +i].pos_)
		elif c == 't':	arr.append(doc[start +i].tag_)
		elif c == 'e':	arr.append(doc[start +i].ent_type_)
		elif c == 'x':	arr.append(doc[start +i].text.lower())
		else :			arr.append(doc[start +i].text.lower())
	return ' '.join(arr) 

def kp_span(doc, start, end, name):  # base:VERB:be_vbn_p:be based on   | lem, pos, type, chunk 
	if name.startswith('v'):		return (doc[start].lemma_,doc[start].pos_, name,vp_span(doc,start,end) )
	elif name.startswith("be_") :	return (doc[start+1].lemma_,doc[start+1].pos_,name,vp_span(doc,start,end))
	elif name in ('ap','pp','Vend'):return (doc[end-1].lemma_,doc[end-1].pos_,name,doc[start:end].text.lower())
	else:							return (doc[start].lemma_,doc[start].pos_,name,doc[start:end].text.lower())

kp_rules = {
"Vend":[[{"POS": {"IN": ["AUX","VERB"]}},{"POS": {"IN": ["ADV"]}, "OP": "*"}, {"POS": {"IN": ["ADJ","VERB"]}, "OP": "*"},{"POS": {"IN": ["PART","ADP","TO"]}, "OP": "*"},{"POS": 'VERB'}]], # could hardly wait to meet
"vp":  [[{'POS': 'VERB'},{"POS": {"IN": ["DET","ADP","ADJ"]}, "OP": "*"},{"POS": 'NOUN'}, {"POS": {"IN": ["ADP","TO"]}, "OP": "*"}], [{'POS': 'VERB'},{"POS": {"IN": ["DET","ADP","ADJ","TO","PART"]}, "OP": "*"},{"POS": 'VERB'}]], # wait to meet
"pp":  [[{'POS': 'ADP'},{"POS": {"IN": ["DET","NUM","ADJ",'PUNCT','CONJ']}, "OP": "*"},{"POS": {"IN": ["NOUN","PART"]}, "OP": "+"}]],    
"ap":  [[{"POS": {"IN": ["ADV"]}, "OP": "+"}, {"POS": 'ADJ'}]],  
"vprt":	[[{"POS": 'VERB', "TAG": {"NOT_IN": ["VBN"]}}, {"POS": {"IN": ["PREP", "ADP",'TO']}, "OP": "+"}]],   # look up /look up from,  computed twice
"vtov":	[[{"POS": 'VERB', "TAG": {"NOT_IN": ["VBN"]}}, {"TAG": 'TO'},{"TAG": 'VB'}]],   # plan to go
"vvbg":	[[{"POS": 'VERB', "TAG": {"NOT_IN": ["VBN"]}}, {"TAG": 'VBG'}]],   # consider going
"vpg":	[[{"POS": 'VERB', "TAG": {"NOT_IN": ["VBN"]}}, {"POS": {"IN": ["PREP", "ADP",'PART']}, "OP": "+"},{"TAG": 'VBG'}]],   # insisted on going
"be_vbn_p": [[{'LEMMA': 'be'},{"TAG": {"IN": ["VBN"]}}, {"POS": {"IN": ["PREP", "ADP",'PART']}}]],   # base:VERB:be_vbn_p:be based on   
"be_adj_p": [[{'LEMMA': 'be'},{"POS": {"IN": ["ADJ"]}}, {"POS": {"IN": ["PREP", "ADP",'PART']}}]],   # be angry with
} #for name, ibeg,iend in matcher(doc) : print(spacy.nlp.vocab[name].text, doc[ibeg:iend].text)

def kp_matcher(doc): #[('vend', 'consider going', 1, 3), ('vp', 'consider going', 1, 3), ('vvbg', 'consider going', 1, 3), ('vprt', 'going to', 2, 4)]
	if not hasattr(kp_matcher, 'matcher'): 
		kp_matcher.matcher = Matcher(spacy.nlp.vocab)
		[kp_matcher.matcher.add(name, patterns,  greedy ='LONGEST') for name, patterns in kp_rules.items() ]
	tups = set()  # remove the duplicated entries 
	[tups.add( kp_span(doc,ibeg,iend, spacy.nlp.vocab[name].text) ) for name, ibeg,iend in kp_matcher.matcher(doc)] 
	return tups

# added 2022.7.25
post_np_rules = { # after np is merged 
"v_n_vbn": [[{"POS": 'VERB', "TAG": {"NOT_IN": ["VBN"]}},{"POS": {"IN": ["NOUN"]}}, {"TAG": {"IN": ["VBN"]}}]],   # leave the book opened 
"v_n_adj": [[{"POS": 'VERB', "TAG": {"NOT_IN": ["VBN"]}},{"POS": {"IN": ["NOUN"]}}, {"POS": {"IN": ["ADJ"]}}]],
} #for name, ibeg,iend in matcher(doc) : print(spacy.nlp.vocab[name].text, doc[ibeg:iend].text)
def post_np_matcher(doc): 
	if not hasattr(post_np_matcher, 'matcher'): 
		post_np_matcher.matcher = Matcher(spacy.nlp.vocab)
		[post_np_matcher.matcher.add(name, patterns,  greedy ='LONGEST') for name, patterns in post_np_rules.items() ]
	return [(spacy.nlp.vocab[name].text,ibeg,iend) for name, ibeg,iend in post_np_matcher.matcher(doc)] 

def new_matcher(patterns, name='pat'):
	matcher = Matcher(spacy.nlp.vocab)
	matcher.add(name, patterns, greedy ='LONGEST')
	return matcher
matchers = {  # for name,start,end in matchers['ap'](doc) :
"vend":new_matcher([[{"POS": {"IN": ["AUX","VERB"]}},{"POS": {"IN": ["ADV"]}, "OP": "*"}, {"POS": {"IN": ["ADJ","VERB"]}, "OP": "*"},{"POS": {"IN": ["PART","ADP","TO"]}, "OP": "*"},{"POS": 'VERB'}]]), # could hardly wait to meet
"vp":  new_matcher([[{'POS': 'VERB'},{"POS": {"IN": ["DET","ADP","ADJ"]}, "OP": "*"},{"POS": 'NOUN'}, {"POS": {"IN": ["ADP","TO"]}, "OP": "*"}], #He paid a close attention to the book. |He looked up from the side. | make use of
                     [{'POS': 'VERB'},{"POS": {"IN": ["DET","ADP","ADJ","TO","PART"]}, "OP": "*"},{"POS": 'VERB'}]]), # wait to meet
"pp":  new_matcher([[{'POS': 'ADP'},{"POS": {"IN": ["DET","NUM","ADJ",'PUNCT','CONJ']}, "OP": "*"},{"POS": {"IN": ["NOUN","PART"]}, "OP": "+"}]]),    
"ap":  new_matcher([[{"POS": {"IN": ["ADV"]}, "OP": "*"}, {"POS": 'ADJ'}]]),  
"vprt": new_matcher([[{"POS": 'VERB', "TAG": {"NOT_IN": ["VBN"]}}, {"POS": {"IN": ["PREP", "ADP",'TO']}, "OP": "+"}]]),   # look up /look up from,  computed twice
"vtov": new_matcher([[{"POS": 'VERB', "TAG": {"NOT_IN": ["VBN"]}}, {"TAG": 'TO'},{"TAG": 'VB'}]]),   # plan to go
"vvbg": new_matcher([[{"POS": 'VERB', "TAG": {"NOT_IN": ["VBN"]}}, {"TAG": 'VBG'}]]),   # consider going
"vpg":  new_matcher([[{"POS": 'VERB', "TAG": {"NOT_IN": ["VBN"]}}, {"POS": {"IN": ["PREP", "ADP",'PART']}, "OP": "+"},{"TAG": 'VBG'}]]),   # insisted on going
"vAp":  new_matcher([[{'LEMMA': 'be'},{"TAG": {"IN": ["VBN"]}}, {"POS": {"IN": ["PREP", "ADP",'PART']}}]]),   # be based on   
"vap":  new_matcher([[{'LEMMA': 'be'},{"POS": {"IN": ["ADJ"]}}, {"POS": {"IN": ["PREP", "ADP",'PART']}}]]),   # be angry with
} #for name, ibeg,iend in matcher(doc) : print(spacy.nlp.vocab[name].text, doc[ibeg:iend].text)

def readline(infile, sepa=None): #for line in fileinput.input(infile):
	with open(infile, 'r') as fp:
		while True:
			line = fp.readline()
			if not line: break
			yield line.strip().split(sepa) if sepa else line.strip()

# added 2022.6.30 
def register_redis(rinfo="172.17.0.1:6379:0", force:bool=False):  #rhost='172.17.0.1', rport=6379, rdb=0
	import redis
	try:
		if not hasattr(redis, 'enr') or force:
			arr = rinfo.strip().split(':')
			redis.enr = redis.Redis(host=arr[0], port=int(arr[1]), db=int(arr[2]) if len(arr) >= 2 else 0, decode_responses=True)
			redis.enbs = redis.Redis(host=arr[0],port=int(arr[1]), db=int(arr[2]) if len(arr) >= 2 else 0, decode_responses=False)
			print ( redis.enr, redis.enbs, flush=True)
			return True
	except Exception as e:
		print ( "exception : ", e) 
		return False 

def publish_newsnts( snts , name:str='xsntbytes'): 
	''' '''
	import redis
	if hasattr(redis, "enr") and snts: #rbs.setex(prefix + snt, ttl, doc.to_bytes()) 
		[redis.enr.xadd(name, {'snt':snt}) for snt in snts if snt] # notify spacy snt parser

def parse_if(snt, prefix:str="bytes:", ttl:int=37200): 
	''' bytes , 2022.6.30 '''
	import redis
	if hasattr(redis, "enbs"):
		bs = redis.enbs.get( prefix + snt) 
		if bs: return Doc(spacy.nlp.vocab).from_bytes(bs)  # spacy.frombs(bs) 
	doc =  spacy.nlp(snt) 
	if hasattr(redis, "enbs"): redis.enbs.setex(prefix + snt, ttl, doc.to_bytes()) 
	return doc 

##
## from verbnet.py
##
def merge_np(doc):
	with doc.retokenize() as retokenizer:
		for np in doc.noun_chunks:
			attrs = {"tag": np.root.tag, "dep": np.root.dep, "ent_type": "NP", "lemma":doc[np.end-1].lemma} # , "lemma":doc[np.end-1].lemma | added 2022.7.26
			retokenizer.merge(np, attrs=attrs) 
	return doc

def skenp(doc, tag="_NP"): # added 2022.3.22, for skevec
	merge_np(doc) # transform doc , finally to be called 
	return " ".join([tag if t.ent_type_ == 'NP' else t.text for t in doc])

def merge_n_of_n(doc):
	if not hasattr(merge_n_of_n, 'matcher'):
		merge_n_of_n.matcher = Matcher(spacy.nlp.vocab)
		merge_n_of_n.matcher.add("n-of-n", [[{"ENT_TYPE": "NP"}, {"LEMMA":"of"},{"ENT_TYPE": "NP"}], [{"ENT_TYPE": "NP"}, {"LEMMA":"of"},{"POS": "NOUN"}]],  greedy ='LONGEST')
	with doc.retokenize() as retokenizer:
		for name, start, end in merge_n_of_n.matcher(doc):
			if end - start > 1: 
				try:
					i = doc[start].head.i
					attrs = {"pos": doc[i].pos, "tag": doc[i].tag, "dep": doc[i].dep, "lemma":doc[i].lemma, "ent_type": "NP"}
					retokenizer.merge(doc[start : end], attrs=attrs)
				except Exception as e:
					print ( "merge_n_of_n ex:", e , start, end)
	return doc

def merge_vp(doc):
	if not hasattr(merge_vp, 'matcher'):
		merge_vp.matcher = Matcher(spacy.nlp.vocab)
		merge_vp.matcher.add("vp", [[{"POS": {"IN":["AUX","PART"]}, "op": "*"}, {"POS":"VERB"},{"POS": "ADV", "op": "*"}]],  greedy ='LONGEST')
	with doc.retokenize() as retokenizer:
		for name, start, end in merge_vp.matcher(doc):
			if end - start > 1: 
				try:
					i = doc[start].head.i
					attrs = {"pos": doc[i].pos, "tag": doc[i].tag, "dep": doc[i].dep, "lemma":doc[i].lemma, "ent_type": "VP"}
					retokenizer.merge(doc[start : end], attrs=attrs)
				except Exception as e:
					print ( "merge_vp ex:", e , start, end)
	return doc

def merge_pp(doc): 
	if not hasattr(merge_pp, 'matcher'):
		merge_pp.matcher = Matcher(spacy.nlp.vocab)
		merge_pp.matcher.add("pp", [[{"POS": {"IN":["ADP"]}, "op": "+"}, {"ENT_TYPE":"NP", "op": "+"}]],  greedy ='LONGEST')
	with doc.retokenize() as retokenizer:
		for name, start, end in merge_pp.matcher(doc):
			if end - start > 1: 
				try:
					i = doc[start].head.i
					attrs = {"pos": doc[i].pos, "tag": doc[i].tag, "dep": doc[i].dep, "lemma":doc[i].lemma, "ent_type": "PP"}
					retokenizer.merge(doc[start : end], attrs=attrs)
				except Exception as e:
					print ( "merge_pp ex:", e , start, end)
	return doc

def skepp(doc, tag="_PP"): # added 2022.3.24,  | From the book, this is also difficult to .. 
	merge_pp(doc) # transform doc , finally to be called 
	return " ".join([tag if t.ent_type_ == 'PP' else t.text for t in doc])

def merge_clause(doc): # subtree of a verb is the clause , https://subscription.packtpub.com/book/data/9781838987312/2/ch02lvl1sec13/splitting-sentences-into-clauses
	with doc.retokenize() as retokenizer:
		for v in [t for t in doc if t.pos_ == 'VERB' and t.dep_ != 'ROOT' ] : # non-root
			try:
				children = list(v.subtree)
				start = children[0].i  	
				end = children[-1].i 
				attrs = {"pos": v.pos, "tag": v.tag, "dep": v.dep, "lemma":v.lemma, "ent_type": "S." + v.dep_ } # S.advcl ,  S.conj 
				retokenizer.merge(doc[start : end+1], attrs=attrs)
			except Exception as e:
				print ( "merge_clause ex:", e, v )
	return doc

NP_start = {"ENT_TYPE": "NP", "IS_SENT_START": True}
VERB	 = {"POS": {"IN": ["VERB"]}}
NOUN	 = {"POS": {"IN": ["NOUN","PRON","PROPN"]}}
PUNCT	 = {"IS_PUNCT": True}
_verbnet_rules = {  # :1 , verb's offset 
	"NP V:1": [[NP_start,VERB, PUNCT]], 
	"NP of NP V:3": [[ NP_start,{"LEMMA": "of"}, {"ENT_TYPE": "NP"}, VERB,PUNCT]], 
	"NP V NP:1": [[NOUN,VERB, NOUN,{"POS": {"IN": ["PUNCT"]}}]], 
	"NP V NP ADJ:1": [[NOUN,VERB, NOUN,{"POS": {"IN": ["ADJ"]}}]], 
	"NP V NP NP:1": [[NOUN,VERB, NOUN,NOUN]], 
	"NP V NP-Dative NP:1": [[NOUN,VERB, {"DEP": {"IN": ["dative"]}},NOUN]], 
	"NP V NP PP:1": [[NOUN,VERB, NOUN,{"DEP": {"IN": ["prep"]}}]], 
	"NP V NP PP PP:1": [[NOUN,VERB, NOUN,{"DEP": {"IN": ["prep"]}}, NOUN,{"DEP": {"IN": ["prep"]}}, NOUN]], 
	"NP V S_ING:1": [[NOUN,VERB, {"TAG": {"IN": ["VBG"]}}]], 
	"NP V whether/how S_INF:1": [[NOUN,VERB, {"LEMMA": {"IN": ["whether","how"]}}, {"LEMMA": {"IN": ["to"]}}, VERB]], 
	"NP V NP to be NP:1": [[NOUN,VERB, {"LEMMA": {"IN": ["to"]}}, {"LEMMA": {"IN": ["be"]}}, NOUN]], 
	"NP V that/how S:1": [[NOUN,VERB, {"LEMMA": {"IN": ["that","how"]}, "OP":"*"}, NOUN, {"POS": {"IN": ["AUX","PART"]}, "OP":"*"},{"DEP": {"IN": ["ccomp"]}}]],  #They considered that he was the professor.
	"NP V whether/if S:1": [[NOUN,VERB, {"LEMMA": {"IN": ["whether","if"]}}, NOUN,{"POS": {"IN": ["AUX","PART"]}, "OP":"*"}, {"DEP": {"IN": ["ccomp"]}}]],  #He considered whether he should come.
	"NP V what S:1": [[NOUN,VERB, {"LEMMA": {"IN": ["what"]}}, NOUN,{"POS": {"IN": ["AUX","PART"]}, "OP":"*"}, {"DEP": {"IN": ["ccomp"]}}]],  
	"NP V what S_INF:1": [[NOUN,VERB, {"LEMMA": {"IN": ["what"]}}, {"LEMMA": {"IN": ["to"]}},VERB]],
}
def verbnet_matcher(doc): 
	if not hasattr(verbnet_matcher, 'matcher'): 
		verbnet_matcher.matcher = Matcher(spacy.nlp.vocab)
		[ verbnet_matcher.matcher.add(name, patterns, greedy ='LONGEST')  for name, patterns in _verbnet_rules.items() ]
	merge_np(doc)
	merge_vp(doc)
	res = []
	for name, ibeg, iend in verbnet_matcher.matcher(doc):
		try:
			arr = spacy.nlp.vocab[name].text.split(':') 
			verb_i = ibeg + int(arr[-1]) 
			res.append( (verb_i, ibeg, iend, arr[0].strip()) ) 
		except Exception as e:
			print ('verbnet ex:', e, name, ibeg, iend)
	return res 

simple_sent		= lambda doc: len([t for t in doc if t.pos_ == 'VERB' and t.dep_ != 'ROOT']) <= 0 
complex_sent	= lambda doc: len([t for t in doc if t.pos_ == 'VERB' and t.dep_ != 'ROOT']) > 0
compound_sent	= lambda doc: len([t for t in doc if t.dep_ == 'conj' and t.head.dep_ == 'ROOT']) > 0  # S.conj 
stype			= lambda doc:	"simple_sent" if len([t for t in doc if t.pos_ == 'VERB' and t.dep_ != 'ROOT']) <= 0 else "complex_sent"
skeleton		= lambda doc:  " ".join([ t.ent_type_ if t.ent_type_ else t.text if t.is_punct or t.dep_ == 'ROOT' else t.pos_ for t in doc ])

def clause(doc):  # {'S.prep-0': {'type': 'S.prep', 'start': 0, 'end': 2, 'lem': 'consider', 'chunk': 'Considering the possibility'}, 'S.conj-9': {'type': 'S.conj', 'start': 9, 'end': 12, 'lem': 'be', 'chunk': 'she is ok .'}}
	arr = []
	for v in [t for t in doc if t.pos_ == 'VERB' and t.dep_ != 'ROOT' ] : # non-root
		children = list(v.subtree) #end = children[-1].i 	tag = "S." + v.dep_   # S.advcl ,  S.conj 
		start = children[0].i
		end = children[-1].i + 1 #"type":"cl", "kp": "S." + v.dep_,
		arr.append( (v, v.dep_, start, end, " ".join([c.text for c in v.subtree])) ) #last one is 'chunk'   lempos":v.lemma_ + "_" + v.pos_,"chunk": } #"lem":v.lemma_, NOT confuse with 'tok' 
	return arr 

_vp_rules = {
"vend":[[{"POS": {"IN": ["AUX","VERB"]}},{"POS": {"IN": ["ADV"]}, "OP": "*"}, {"POS": {"IN": ["ADJ","VERB"]}, "OP": "*"},{"POS": {"IN": ["PART","ADP","TO"]}, "OP": "*"},{"POS": 'VERB'}]], # could hardly wait to meet
"vp":  [[{'POS': 'VERB'},{"POS": {"IN": ["DET","ADP","ADJ"]}, "OP": "*"},{"POS": 'NOUN'}, {"POS": {"IN": ["ADP","TO"]}, "OP": "*"}], [{'POS': 'VERB'},{"POS": {"IN": ["DET","ADP","ADJ","TO","PART"]}, "OP": "*"},{"POS": 'VERB'}]], # wait to meet
"pp":  [[{'POS': 'ADP'},{"POS": {"IN": ["DET","NUM","ADJ",'PUNCT','CONJ']}, "OP": "*"},{"POS": {"IN": ["NOUN","PART"]}, "OP": "+"}]],    
"ap":  [[{"POS": {"IN": ["ADV"]}, "OP": "*"}, {"POS": 'ADJ'}]],  
"vprt":[[{"POS": 'VERB'}, {"POS": {"IN": ["PREP", "ADP",'TO']}, "OP": "+"}]],   # look up /look up from,  computed twice
"vtov":[[{"POS": 'VERB'}, {"TAG": 'TO'},{"TAG": 'VB'}]],   # plan to go
"vvbg":[[{"POS": 'VERB'}, {"TAG": 'VBG'}]],   # consider going
"vpg": [[{"POS": 'VERB'}, {"POS": {"IN": ["PREP", "ADP",'PART']}, "OP": "+"},{"TAG": 'VBG'}]],   # insisted on going
"vAp": [[{'LEMMA': 'be'},{"TAG": {"IN": ["VBN"]}}, {"POS": {"IN": ["PREP", "ADP",'PART']}}]],   # be based on   
"vap": [[{'LEMMA': 'be'},{"POS": {"IN": ["ADJ"]}}, {"POS": {"IN": ["PREP", "ADP",'PART']}}]],   # be angry with
} #for name, ibeg,iend in matcher(doc) : print(spacy.nlp.vocab[name].text, doc[ibeg:iend].text)

def vp_matcher(doc): #[('vend', 'consider going', 1, 3), ('vp', 'consider going', 1, 3), ('vvbg', 'consider going', 1, 3), ('vprt', 'going to', 2, 4)]
	if not hasattr(vp_matcher, 'matcher'): 
		vp_matcher.matcher = Matcher(spacy.nlp.vocab)
		[vp_matcher.matcher.add(name, patterns,  greedy ='LONGEST') for name, patterns in _vp_rules.items() ]
	#return [(spacy.nlp.vocab[name].text, vp_span(doc,ibeg,iend), ibeg, iend) for name, ibeg,iend in vp_matcher.matcher(doc)] 
	tups = set()  # remove the duplicated entries 
	[tups.add((spacy.nlp.vocab[name].text, vp_span(doc,ibeg,iend), ibeg, iend)) for name, ibeg,iend in vp_matcher.matcher(doc)] 
	return tups

_dep_rules = {
"svo":[ 
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"POS": "VERB"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "subject",
    "RIGHT_ATTRS": {"DEP": "nsubj"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "object",
    "RIGHT_ATTRS": {"DEP": "dobj"}
  }
], # [(4851363122962674176, [2, 0, 4])]
"sva":[ 
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"POS": "VERB"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "subject",
    "RIGHT_ATTRS": {"DEP": "nsubj"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "object",
    "RIGHT_ATTRS": {"DEP": "acomp"}
  }
], 
"svx":[  # plan to go , enjoy swimming 
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"POS": "VERB"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "subject",
    "RIGHT_ATTRS": {"DEP": "nsubj"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "object",
    "RIGHT_ATTRS": {"DEP": "xcomp"}
  }
], 
"svc":[  # I think it is right.
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"POS": "VERB"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "subject",
    "RIGHT_ATTRS": {"DEP": "nsubj"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "object",
    "RIGHT_ATTRS": {"DEP": "ccomp"}
  }
], 
"sattr":[  #She is  a girl.
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"LEMMA": "be"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "subject",
    "RIGHT_ATTRS": {"DEP": "nsubj"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "object",
    "RIGHT_ATTRS": {"DEP": "attr"}
  }
], 
"vpn":[ # turn off the light
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"POS": "VERB"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "subject",
    "RIGHT_ATTRS": {"DEP": "prt"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "object",
    "RIGHT_ATTRS": {"DEP": "dobj"}
  }
], 
"vap":[ # be happy with
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"POS": "VERB"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "acomp",
    "RIGHT_ATTRS": {"DEP": "acomp"}
  },
  {
    "LEFT_ID": "acomp",
    "REL_OP": ">",
    "RIGHT_ID": "prep",
    "RIGHT_ATTRS": {"DEP": "prep"}
  }
], 
"vdp":[ # be based on
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"TAG": "VBN"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "be",
    "RIGHT_ATTRS": {"LEMMA": "be"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "prep",
    "RIGHT_ATTRS": {"DEP": "prep"}
  }
], 
"vppn":[ # look up from phone
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"POS": "VERB"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "prt",
    "RIGHT_ATTRS": {"DEP": "prt"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "prep",
    "RIGHT_ATTRS": {"DEP": "prep"}
  },
  {
    "LEFT_ID": "prep",
    "REL_OP": ">",
    "RIGHT_ID": "object",
    "RIGHT_ATTRS": {"DEP": "pobj"}
  }
], 
"vpnpn":[ # vary from A to B
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"POS": "VERB"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "prep1",
    "RIGHT_ATTRS": {"DEP": "prep"}
  },
  {
    "LEFT_ID": "prep1",
    "REL_OP": ">",
    "RIGHT_ID": "object1",
    "RIGHT_ATTRS": {"DEP": "pobj"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "prep2",
    "RIGHT_ATTRS": {"DEP": "prep"}
  },
  {
    "LEFT_ID": "prep2",
    "REL_OP": ">",
    "RIGHT_ID": "object2",
    "RIGHT_ATTRS": {"DEP": "pobj"}
  }
], 
"vnp":[ # turn it down
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"POS": "VERB"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "object",
    "RIGHT_ATTRS": {"DEP": "dobj"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "subject",
    "RIGHT_ATTRS": {"DEP": "prt"}
  }
], 
"vnpn":[  # make use of books, take sth into account
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"POS": "VERB"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "object",
    "RIGHT_ATTRS": {"DEP": "dobj"}
  },
  {
    "LEFT_ID": "object",
    "REL_OP": ">",
    "RIGHT_ID": "prep",
    "RIGHT_ATTRS": {"DEP": "prep"}
  },
  {
    "LEFT_ID": "prep",
    "REL_OP": ">",
    "RIGHT_ID": "pobj",
    "RIGHT_ATTRS": {"DEP": "pobj"}
  }  
], 
} # for name, ar in depmatchers['svx'](doc) : print(doc[ar[1]], doc[ar[0]], doc[ar[2]])

def dep_matcher(doc): #[('svx', [1, 0, 2])]
	if not hasattr(dep_matcher, 'matcher'): 
		dep_matcher.matcher = DependencyMatcher(spacy.nlp.vocab)
		[dep_matcher.matcher.add(name, [pattern]) for name, pattern in _dep_rules.items() ]
	return [(spacy.nlp.vocab[name].text, ar) for name, ar in dep_matcher.matcher(doc)] 
	#for name, ar in depmatchers['svx'](doc) : print(doc[ar[1]], doc[ar[0]], doc[ar[2]])

[setattr(builtins, k, v) for k, v in globals().items() if not k.startswith("_") and not '.' in k and not hasattr(builtins,k) ] #setattr(builtins, "spacy", spacy)			
if __name__	== '__main__': 
	doc = spacy.nlp("It is on the brink, and I am very happy, and I leave these books opened.") 
	merge_np(doc)
	print ( post_np_matcher(doc) ) 
	#print (parse("I love you."))
	#print(sntbr("[\u8bd1\u6587]The 55-kilometre Hong Kong Zhuhai-Macau Bridge is an extraordinary engineering. It is the world's longest sea-crossing transportation system combining bridges and tunnels, which joins the three cities of Hong Kong Zhuhai and Macao, cutting the travelling time among them from 3 hours to 30 minutes. The reinforced concrete bridge with huge spans fully not only proves that China has the ability to complete the record-breaking mega-construction, but also will enhance the regional integration and boost the economic growth. It plays a crucial role in the overall plan to develop China’s Great Bay Area, which China intends to turn into one rivaling those of San Francisco, New York and Tokyo in terms of technological innovation and economic prosperity.", with_pid=True))
#c:\users\zhang\appdata\local\programs\python\python38\lib\site-packages  
#/home/ubuntu/.local/lib/python3.8/site-packages/en