# 2022.6.30  # 2022.2.10  uvicorn exchunk:app --host 0.0.0.0 --port 7058 --reload | 8004 @ cpu76
from uvirun import *
import spacy, traceback, sys,sqlite3
from spacy.matcher import Matcher
if not hasattr(spacy,'nlp'): spacy.nlp	= spacy.load('en_core_web_sm')

kvlist  = lambda s = "dead:104,super:44", topk=10: [ {'w': pair.split(':')[0], 'cnt': int(pair.split(':')[-1])}  for pair in s.split(',')[0:topk]]
conn	= sqlite3.connect("/data/model/exchunk/grampos-exchunk.svdb", check_same_thread=False)  # how to set readonly ? 
getdb	= lambda keys=['pay attention to:_jj:1','is _rb beautiful'] : { row[0] : row[1] for row in conn.execute("select s,v from sv where s in ('"+"','".join([k for k in keys])+"')") } # in ('one','two')
conn.execute(f'CREATE TABLE IF NOT EXISTS sv (s varchar(128) PRIMARY KEY, v blob)')

#NP_start= {"ENT_TYPE": "NP", "IS_SENT_START": True}
rules = { #  pay attention to:_jj:1  =>  close:133,closer:27
"pay attention to=_jj:1" : [[{"POS": {"IN": ["VERB"]}},{"POS": {"IN": ["NOUN"]}},{"POS": {"IN": ["ADP"]}}]], 
"is pretty/destroyed=_rb:1" : [[{"LEMMA": "be"},{"TAG": {"IN": ["JJ"]}}], [{"LEMMA": "be"}, {"TAG": {"IN": ["VBN"]}}]], 
"finished homework=_rb:2": [[{"POS": {"IN": ["VERB"]}},{"POS": {"IN": ["NOUN"]}},{"IS_PUNCT": True}]], 
"solve the problem=_rb:3": [[{"POS": {"IN": ["VERB"]}},{"POS": {"IN": ["DET"]}},{"POS": {"IN": ["NOUN"]}},{"IS_PUNCT": True}]], 
"to open the door=_rb:1": [[{"TAG": {"IN": ["TO"]}},{"POS": {"IN": ["VERB"]}},{"POS": {"IN": ["DET"]}},{"POS": {"IN": ["NOUN"]}}],[{"TAG": {"IN": ["TO"]}},{"POS": {"IN": ["VERB"]}},{"POS": {"IN": ["NOUN"]}}],[{"TAG": {"IN": ["TO"]}},{"POS": {"IN": ["VERB"]}},{"POS":"PRP$"}]],
"make it *dead simple to=_jj:2": [[{"POS": {"IN": ["VERB"]}},{"LEMMA": "it"},{"TAG": {"IN": ["JJ"]}},{"TAG": {"IN": ["TO"]}}]],  #It will make it *dead simple to utilize the tools.
}
patterns = {
"NP-DET NOUN": [":_jj:1"], 
"NP-DET ADJ NOUN": [":_rb:1"], 
"VP-VERB NOUN ADP": [":_jj:1"], #pay attention to
}

def hit(doc):  # [ "pay attention to:_jj:1"]
	if not hasattr(hit,'matcher'): 
		hit.matcher	= Matcher(spacy.nlp.vocab)  # :1 , verb's offset 
		[ hit.matcher.add(name, pattern) for name, pattern in rules.items() ]
	return [" ".join([ t.text.lower() for t in doc[ibeg:iend] ]) + ":"  + spacy.nlp.vocab[name].text.split('=')[-1].strip() for name, ibeg, iend in hit.matcher(doc) ]

@app.get('/exchunk', tags=["exchunk"])
def exchunk_chk(chunk:str="the fox:NP-DET NOUN", topk:int=10): 
	''' 2022.7.8 '''
	chk,pat = chunk.strip().split(':')[0:2] 
	pats	= patterns.get(pat, []) 
	cands	= [ chk.strip() + pat for pat in pats] # [ "pay attention to:_jj:1"]
	dic		= getdb(cands)  #{'make it simple to:_jj:2': 'dead:104,super:44', 'the tools:_jj:1': 'right:183768,necessary:105685,basic:56316,new:42693,proper:40433,various:26135,essential:23783,appropriate:20588,main:19884,analytical:17571,available:14929,administrative:13103,many:12895,different:12689,mobile:11898,primary:10681,powerful:9955,required:9352,free:8600,standard:8598,correct:8583,advanced:8387,integrated:7993,practical:7809,financial:7231,technological:6808,online:6791,major:6743,mathematical:6631,diagnostic:6472,technical:6059,current:6057,traditional:6022,fundamental:5827,legal:5426,specific:4927,conceptual:4498,special:4487,intellectual:4330,visual:4070,cool:3901,first:3898,old:3887,critical:3769,statistical:3668,professional:3511,automated:3470,usual:3413,theoretical:3366,perfect:3357,important:3258,simple:3230,great:3168,physical:3122,interactive:3088,individual:3057,additional:3045,principal:3031,modeling:3029,wrong:2894,modern:2885,educational:2840,common:2774,analytic:2697,graphical:2674,computational:2558,digital:2428,associated:2425,wireless:2398,collaborative:2345,electronic:2301,relevant:2289,external:2118,sophisticated:2067,familiar:2002,related:1983,actual:1824,creative:1819,useful:1773,scientific:1720,specialized:1701,commercial:1637,methodological:1633,ideal:1514,general:1481,original:1465,mod:1393,ultimate:1390,native:1347,remote:1331,vital:1270,modelling:1247,exact:1232,promotional:1221,extra:1213,economic:1207,developed:1204,normal:1189,regulatory:1186,navigational:1179,innovative:1152,formatting:1134,mental:1124,molecular:1081,comprehensive:1074,quantitative:1046,effective:1042,corresponding:1037,surgical:1011,valuable:1009,putty:997,formal:973,unique:969,real:962,limited:951,parallel:941,investigative:910,genetic:879,proven:865,small:863,conventional:849,preferred:831,lean:821,possible:815,aforementioned:799,helpful:796,experimental:794,linguistic:785,hibernate:775,audio:770,smart:750,graphic:743,strategic:743,rational:735,indispensable:725,particular:722,wonderful:714,numerous:713,abc:689,legislative:651,academic:644,numerical:644,popular:643,fine:633,classic:630,social:613,classical:605,open:603,operational:594,organizational:578,spiritual:576,optimal:572,generic:571,primitive:571,clinical:561,typical:558,previous:552,proactive:547,adequate:537,central:530,good:525,convenient:518,cultural:514,proprietary:506,automatic:501,personal:497,excellent:480,respective:474,crucial:469,political:461,instructional:458,internal:439,automotive:438,little:437,pedagogical:434,motivational:407,awesome:397,listed:397,early:395,psychological:384,forensic:383,present:383,initial:382,ancient:375,everyday:374,ordinary:374,predictive:374,potential:369,neat:363,installed:355,big:345,favorite:343,global:340,net:339,multiple:335,artistic:332,emotional:328,robust:328,several:326,expensive:322,industrial:315,optional:315,flexible:312,virtual:310,cordless:309,procedural:303,temporary:302,handy:294,next:294,embedded:293,fancy:293,informational:292,prime:291,sharp:288,supplemental:287,precise:285,improved:284,natural:283,portal:283,deadly:282,regular:281,disciplinary:279,official:278,clumsy:276,apt:272,auxiliary:270,added:267,nice:266,logical:265,separate:265,functional:262,local:260,revolutionary:260,amazing:254,foundational:254,hidden:251,raw:249,incredible:246,enhanced:244,medical:242,diverse:241,genealogical:239,complex:237,nifty:234,hot:233,easy:231,mechanical:231,myriad:228,rudimentary:228,lexical:223,potent:222,therapeutic:221,final:220,institutional:219,cryptographic:218,pneumatic:217,complete:212,suitable:207,solid:205,heavy:203,extensive:202,interpretive:202,public:202,wooden:197,customized:195,miscellaneous:195,complementary:194,agricultural:192,hydraulic:191,equivalent:190,invaluable:190,musical:187,diplomatic:184,fantastic:182,magical:182,obvious:182,latter:181,tiny:181,bibliographic:180,accessory:178,symbolic:178,econometric:176,applicable:173,statutory:172,algebraic:171,democratic:171,fiscal:171,computerized:167,binary:165,military:163,sap:163,exciting:162,secret:161,dynamic:160,elementary:160,inner:160,dental:158,foremost:157,wil
	return [ row for k,v in dic.items() for row in kvlist(v, topk) ]

@app.get('/exchunk/snt', tags=["exchunk"])
def exchunk_snt(snt:str="I pay attention to the box, and she is beautiful.", topk:int=10, verbose:bool=True): 
	''' It will make it simple to utilize the tools.  * dead  * super,  2022.2.10 '''
	doc		= spacy.nlp(snt)
	cands	= hit(doc) # [ "pay attention to:_jj:1"]
	for np in doc.noun_chunks:
		if doc[np.start].pos_ == 'DET' : 
			if len(np) == 2  and doc[np.start+1].pos_ == 'NOUN': 
				cands.append(np.text.lower() + ":_jj:1")
			elif len(np) == 3  and doc[np.start+1].tag_ == 'JJ'  and doc[np.start+2].pos_ == 'NOUN': 
				cands.append(np.text.lower() + ":_rb:1")

	dic = getdb(cands)  #[ ar.update({"cands": dic[ ar['pattern'] ]}) for ar in res if ar['pattern'] in dic ]
	#{'make it simple to:_jj:2': 'dead:104,super:44', 'the tools:_jj:1': 'right:183768,necessary:105685,basic:56316,new:42693,proper:40433,various:26135,essential:23783,appropriate:20588,main:19884,analytical:17571,available:14929,administrative:13103,many:12895,different:12689,mobile:11898,primary:10681,powerful:9955,required:9352,free:8600,standard:8598,correct:8583,advanced:8387,integrated:7993,practical:7809,financial:7231,technological:6808,online:6791,major:6743,mathematical:6631,diagnostic:6472,technical:6059,current:6057,traditional:6022,fundamental:5827,legal:5426,specific:4927,conceptual:4498,special:4487,intellectual:4330,visual:4070,cool:3901,first:3898,old:3887,critical:3769,statistical:3668,professional:3511,automated:3470,usual:3413,theoretical:3366,perfect:3357,important:3258,simple:3230,great:3168,physical:3122,interactive:3088,individual:3057,additional:3045,principal:3031,modeling:3029,wrong:2894,modern:2885,educational:2840,common:2774,analytic:2697,graphical:2674,computational:2558,digital:2428,associated:2425,wireless:2398,collaborative:2345,electronic:2301,relevant:2289,external:2118,sophisticated:2067,familiar:2002,related:1983,actual:1824,creative:1819,useful:1773,scientific:1720,specialized:1701,commercial:1637,methodological:1633,ideal:1514,general:1481,original:1465,mod:1393,ultimate:1390,native:1347,remote:1331,vital:1270,modelling:1247,exact:1232,promotional:1221,extra:1213,economic:1207,developed:1204,normal:1189,regulatory:1186,navigational:1179,innovative:1152,formatting:1134,mental:1124,molecular:1081,comprehensive:1074,quantitative:1046,effective:1042,corresponding:1037,surgical:1011,valuable:1009,putty:997,formal:973,unique:969,real:962,limited:951,parallel:941,investigative:910,genetic:879,proven:865,small:863,conventional:849,preferred:831,lean:821,possible:815,aforementioned:799,helpful:796,experimental:794,linguistic:785,hibernate:775,audio:770,smart:750,graphic:743,strategic:743,rational:735,indispensable:725,particular:722,wonderful:714,numerous:713,abc:689,legislative:651,academic:644,numerical:644,popular:643,fine:633,classic:630,social:613,classical:605,open:603,operational:594,organizational:578,spiritual:576,optimal:572,generic:571,primitive:571,clinical:561,typical:558,previous:552,proactive:547,adequate:537,central:530,good:525,convenient:518,cultural:514,proprietary:506,automatic:501,personal:497,excellent:480,respective:474,crucial:469,political:461,instructional:458,internal:439,automotive:438,little:437,pedagogical:434,motivational:407,awesome:397,listed:397,early:395,psychological:384,forensic:383,present:383,initial:382,ancient:375,everyday:374,ordinary:374,predictive:374,potential:369,neat:363,installed:355,big:345,favorite:343,global:340,net:339,multiple:335,artistic:332,emotional:328,robust:328,several:326,expensive:322,industrial:315,optional:315,flexible:312,virtual:310,cordless:309,procedural:303,temporary:302,handy:294,next:294,embedded:293,fancy:293,informational:292,prime:291,sharp:288,supplemental:287,precise:285,improved:284,natural:283,portal:283,deadly:282,regular:281,disciplinary:279,official:278,clumsy:276,apt:272,auxiliary:270,added:267,nice:266,logical:265,separate:265,functional:262,local:260,revolutionary:260,amazing:254,foundational:254,hidden:251,raw:249,incredible:246,enhanced:244,medical:242,diverse:241,genealogical:239,complex:237,nifty:234,hot:233,easy:231,mechanical:231,myriad:228,rudimentary:228,lexical:223,potent:222,therapeutic:221,final:220,institutional:219,cryptographic:218,pneumatic:217,complete:212,suitable:207,solid:205,heavy:203,extensive:202,interpretive:202,public:202,wooden:197,customized:195,miscellaneous:195,complementary:194,agricultural:192,hydraulic:191,equivalent:190,invaluable:190,musical:187,diplomatic:184,fantastic:182,magical:182,obvious:182,latter:181,tiny:181,bibliographic:180,accessory:178,symbolic:178,econometric:176,applicable:173,statutory:172,algebraic:171,democratic:171,fiscal:171,computerized:167,binary:165,military:163,sap:163,exciting:162,secret:161,dynamic:160,elementary:160,inner:160,dental:158,foremost:157,wil
	return [ dict(row, **{"chunk": k}) for k,v in dic.items() for row in kvlist(v, topk) ] if verbose else 	[ {"chunk":k.split(":")[0], "pos":k.split(":")[1], "offset":k.split(":")[-1], "cands":kvlist(v, topk)} for k,v in dic.items() ]

@app.post('/exchunk/snt', tags=["exchunk"])
def exchunk_snts(snts:list=["I pay attention to the box, and she is beautiful.","The quick fox jumped over the lazy dog."]): 
	return {snt: exchunk_snt(snt) for snt in snts}

if __name__ == "__main__":  
	#doc = spacy.nlp("I paid attention to the big box, and it is beautiful.") 
	#print (list(chunk_ex(doc))) #[(1, 4, '_jj', 1, 'paid _jj attention to'), (9, 11, '_jj', 1, 'is _jj beautiful')]
	#print( exchunk_snt("It will make it simple to utilize the tools.", verbose=False))
	print ( exchunk_chk())

'''
a girl	_dt _n	_dt _adj _n	a beautiful/tall/smart girl	
on the playground	_in _dt _n	_in _dt _n _n 	on the school playground	
in the morning	_in _dt _n	_in _dt _adj _n 	in the early morning	
To better your english skills	_to _v _prp$ _n	_to _rb _v _prp$ _n	To quickly better your english skills	
The building was destroyed	_n _v _vbn	_n _v _rb _vbn	The building was total destroyed	
finish homework	_v _n	_v _n _rb	finish homeword finally	
you should solve the problem 	_md _v _n	_md _v _n _rb	you should solve the problem properly	
overcome difficulty/dobj_VERB_NOUN  => {"ref":{"surmount difficulty/dobj_VERB_NOUN":0.83, "conque difficulty/dobj_VERB_NOUN":0.23} }

sqlite> CREATE TABLE IF NOT EXISTS sv (s varchar(128) PRIMARY KEY, v blob) without rowid;
sqlite> .separator \t
sqlite> .import grampos.mul.output sv
'''