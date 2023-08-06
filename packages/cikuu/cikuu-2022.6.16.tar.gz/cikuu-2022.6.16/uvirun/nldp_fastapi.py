# 2022.7.16  C:\Program Files (x86)\IIS Express>iisexpress.exe /path:c:\nldp7091\ /port:80 | https://www.microsoft.com/en-us/download/confirmation.aspx?id=48264
from uvirun import *
import requests, itertools,re,sys,traceback
import xml.etree.cElementTree as ET

nldphost	= os.getenv("nldp_host","nldp.penly.cn") #http://win3.penly.cn/syn/
syn_xml		= lambda snt: requests.get(f"http://{nldphost}/syn/",params={"q":snt}).text
lf_xml		= lambda snt: requests.get(f"http://{nldphost}/xml/",params={"q":snt}).text
syn_value	= lambda syn, name, attr="Value", default='': ( n:= syn.find(name), n.get(attr) if n is not None else default )[-1]
syn_node	= lambda syn:  {} if syn is None else {"String": syn.find("String").get('Value'), "ft": int(syn.find("String").get('FirstToken')), "lt": int(syn.find("String").get('LastToken'))
			, "Word":  syn_value(syn, 'Word'), "Lemma":  syn_value(syn, 'Lemma'), "Segtype":  syn_value(syn, "Segtype")
			, "Bit":  ",".join([b.get('Name') for b in syn.findall("Bit")]), 'head_NLID': syn_value(syn, "Head/*","NLID", '-1') } #1 if syn.find('Head') else 0
sem_node	= lambda n:  {} if n is None else {"tag": n.tag, "NLID": n.get('NLID')
			, "NLIDREF": ( t:=n.find("SynNode/SYNNode_REF"), "" if t is None else t.get("NLIDREF")) [-1]
			, "POS":  syn_value(n,"POS") , "Nodename":  syn_value(n,"Nodename")
			, "Bit":  ",".join([b.get('Name') for b in n.findall("Bit")]) }

syn_nodes	= lambda root: {a.get('NLID'):syn_node(a) for a in root.findall("Sentence/Parse[1]/Syntax//*[@Type='SYN']")}
sem_trps	= lambda root: [ (sem_node(a), sem_node(b) ) for a in root.findall("Sentence/Parse[1]/LogicalForm/LFNode/*[@Type='SEM']")  for b in a.findall("./*[@Type='SEM']")]
#{'tag': 'LFNode', 'NLID': 'id10', 'NLIDREF': 'id1', 'POS': 'VERB', 'Nodename': 'hit', 'Bit': 'Past,Pres'} {'tag': 'Dsub', 'NLID': 'id11', 'NLIDREF': 'id2', 'POS': 'PRON', 'Nodename': 'I', 'Bit': 'Sing,Pronoun'}
#{'tag': 'LFNode', 'NLID': 'id10', 'NLIDREF': 'id1', 'POS': 'VERB', 'Nodename': 'hit', 'Bit': 'Past,Pres'} {'tag': 'Dobj', 'NLID': 'id12', 'NLIDREF': 'id5', 'POS': 'NOUN', 'Nodename': 'ball', 'Bit': 'Sing'}
#{'tag': 'Dobj', 'NLID': 'id12', 'NLIDREF': 'id5', 'POS': 'NOUN', 'Nodename': 'ball', 'Bit': 'Sing'} {'tag': 'Ops', 'NLID': 'id13', 'NLIDREF': 'id6', 'POS': 'ADJ', 'Nodename': 'the', 'Bit': ''}

@app.get("/nldp/trp", tags=["nldp"])
def nldp_trp(snt:str="I hit the ball."):
	''' return syn_nodes and sem_trps '''
	root	= ET.fromstring(lf_xml(snt))
	return { "syn": syn_nodes(root), "trp": sem_trps(root)}

@app.get("/nldp/syn", tags=["nldp"])
def nldp_syn(snt:str="That the book is good will be what we said."):
	''' # {"snt": snt, "stype": stype, "bits": bits, "syn": syns, "toks": toks} 2022.7.14 '''
	root	= ET.fromstring(syn_xml(snt))
	syns	= [ {"String": syn.find("String").get('Value'), "ft": int(syn.find("String").get('FirstToken')), "lt": int(syn.find("String").get('LastToken'))
			, "Word":  syn_value(syn, 'Word'), "Lemma":  syn_value(syn, 'Lemma'), "Segtype":  syn.find("Segtype").get('Value') 
			, "Bit":  ",".join([b.get('Name') for b in syn.findall("Bit")])
		} for syn in root.findall(".//*[@Type='SYN']") ] 	#[{{'String': 'That the book is good', 'ft': 1, 'lt': 5, 'Word': 'is', 'Lemma': 'be', 'Segtype': 'COMPCL', 'Bit': []}, {'String': 'That', 'ft': 1, 'lt': 1, 'Word': 'That', 'Lemma': 'that', 'Segtype': 'CONJP', 'Bit': []}, {'String': 'That', 'ft': 1, 'lt': 1, 'Word': 'That', 'Lemma': 'that', 'Segtype': 'CONJ', 'Bit': []}, {'String': 'the book', 'ft': 2, 'lt': 3, 'Word': 'book', 'Lemma': 'book', 'Segtype': 'NP', 'Bit': ['Art']}, {'String': 'the', 'ft': 2, 'lt': 2, 'Word': 'the', 'Lemma': 'the', 'Segtype': 'AJP', 'Bit': ['Art']}, {'String': 'the', 'ft': 2, 'lt': 2, 'Word': 'the', 'Lemma': 'the', 'Segtype': 'ADJ', 'Bit': ['Art']}, {'String': 'book', 'ft': 3, 'lt': 3, 'Word': 'book', 'Lemma': 'book', 'Segtype': 'NOUN', 'Bit': []}, {'String': 'is', 'ft': 4, 'lt': 4, 'Word': 'is', 'Lemma': 'be', 'Segtype': 'VERB', 'Bit': []}, {'String': 'good', 'ft': 5, 'lt': 5, 'Word': 'good', 'Lemma': 'good', 'Segtype': 'AJP', 'Bit': []}, {'String': 'good', 'ft': 5, 'lt': 5, 'Word': 'good', 'Lemma': 'good', 'Segtype': 'ADJ', 'Bit': []}, {'String': 'is', 'ft': 6, 'lt': 6, 'Word': 'is', 'Lemma': 'be', 'Segtype': 'VERB', 'Bit': []}, {'String': 'what we said', 'ft': 7, 'lt': 9, 'Word': 'said', 'Lemma': 'say', 'Segtype': 'WHCL', 'Bit': ['Past']}, {'String': 'what', 'ft': 7, 'lt': 7, 'Word': 'what', 'Lemma': 'what', 'Segtype': 'NP', 'Bit': ['Wh']}, {'String': 'what', 'ft': 7, 'lt': 7, 'Word': 'what', 'Lemma': 'what', 'Segtype': 'PRON', 'Bit': ['Wh']}, {'String': 'we', 'ft': 8, 'lt': 8, 'Word': 'we', 'Lemma': 'we', 'Segtype': 'NP', 'Bit': ['Anim', 'Humn']}, {'String': 'we', 'ft': 8, 'lt': 8, 'Word': 'we', 'Lemma': 'we', 'Segtype': 'PRON', 'Bit': ['Anim', 'Humn']}, {'String': 'said', 'ft': 9, 'lt': 9, 'Word': 'said', 'Lemma': 'say', 'Segtype': 'VERB', 'Bit': ['Past']}, {'String': '.', 'ft': 10, 'lt': 10, 'Word': '.', 'Lemma': '.', 'Segtype': 'CHAR', 'Bit': []}]
	toks	= { syn['ft'] : syn['Word'] for syn in syns if syn['ft'] == syn['lt'] } # start from 1, for show highlight
	synroot = root.find("Sentence/Parse/Syntax/*")
	stype	= synroot.tag if synroot else None # DECL
	bits	= [t.get('Name') for t in synroot.findall("Bit")] if synroot else []
	return {"snt": snt, "stype": stype, "bits": bits, "syns": syns, "toks": toks}

@app.post("/nldp/sent", tags=["nldp"])
def nldp_sent(dic:dict={"DECL":"陈述句", "QUES":"疑问句", "IMPR":"祈使句","FITTED":"非规范句","Past":"过去时","Futr":"将来时","Pres":"现在时" ,"Pass":"被动态","COMPCL":"COMP从句","WHCL":"WH从句"}
			, snt:str="Clapping for the performers was considered essential."):
	''' # sentence analysis demo api, 2022.7.15 '''
	from spacy_fastapi import doc_desc,doc_highlight , nlp_ecdic

	syn		= nldp_syn(snt) 
	tense	= [ dic[bit] for bit in syn.get('bits',[]) if bit in dic ]
	res		= doc_desc(text=snt, debug=False )
	res.update( { 
	"stype":  dic.get(syn.get('stype',''), "未知句型"), 
	"tense":  tense[0] if tense else "现在时", 
	"voice":  '被动语态' if 'ROOT:auxpass' in res.get('kp',{}) else '主动语态',
	"html": doc_highlight(snt), 
	"dic": nlp_ecdic(snt), 
	"chunk": [ dict(ar, **{"label":dic[ar['Segtype']]}) for ar in syn.get('syns',[]) if ar['Segtype'] in dic ], 
	"syntax": syn, # Because we doing it. => fitted
	})
	return res 


def _bits_tense(bits, dic , root, NLID) :  
	for a,b in itertools.permutations(bits,2): ##['Past', 'Prog']
		s = a + "," + b
		if s in dic: return dic[s]
	for s in bits:  
		if s in dic: return dic[s]
	# I am from China and she is from another country.
	crds_lfnode = root.find("Sentence/Parse[1]/LogicalForm/LFNode/Crds[@ListType='SEM']/LFNode")
	if crds_lfnode is not None: 
		nlid = syn_value(crds_lfnode, "SynNode/SYNNode_REF", "NLIDREF")
		chunk = NLID[nlid].get("String","") if nlid and nlid in NLID else ""
		for bit in crds_lfnode.findall("Bit"):
			if bit.get("Name") in dic: return dic[bit.get("Name")] +f" [{chunk}]"

def _get_tense(root, snt, dic , NLID): 

	synroot = root.find("Sentence/Parse[1]/Syntax/*")
	stype	= synroot.tag if synroot else None # DECL
	#pred	= root.find("Sentence/Parse[1]/Syntax/*/Head/*/String[@FirstToken]")
	bits	= { bit.get('Name') for bit in root.findall("Sentence/Parse[1]/LogicalForm/LFNode/Bit")} #['Past', 'Pass']
	res		= { "stype": dic.get(stype, dic.get("stype_unk","unknown")), "voice": dic['Pass'] if 'Pass' in bits else dic['~Pass'],} # Pass, ~Pass must exist in dic | "predi":  -1 if pred is None else int(pred.get("FirstToken")), 
	bits.discard('Pass')
	res.update( {"bits": ','.join([b for b in bits]), "tense": _bits_tense(list(bits), dic, root, NLID)})
	for name, rule in dic.get('tense_exceptions',{}).items(): #if re.search(futr_past, snt): res['tense'] = '过去将来时'
		if re.search(rule, snt) and name in dic:  
			res['tense'] = dic[name]
	return res 

def _hit_dic ( dic, *names): 
	for name in names: # in sequence, the left, the first
		if name in dic : return dic[name] + ":" + name  # the latter is for debug only 

def _sem_clause(sem, dic, NLID):
	## The trouble is that I have lost his address. 
	lemma = sem.get("Nodename","")  # predicate
	for k,v in sem.items():
		if k.startswith('rel:') and v["SynNode"] == "SYNNode_REF":
			nlid	= v["NLID"]
			hit		= _hit_dic(dic,  f"{k}:{lemma}:" + NLID[nlid]["Segtype"], f"{k}:" + NLID[nlid]["Segtype"] ) # rel:Dcmp:COMPCL 
			if hit is not None: 
				NLID[nlid]["label"] = hit
				#print (nlid,  hit, flush=True) 

def walk_sem(root):
	try:
		semroot = root.find("Sentence/Parse[1]/LogicalForm/LFNode")
		if semroot.find("SynNode/SYNNode_REF") is None : return {} #I am from China and she is from the another country.
		res = { "POS": syn_value(semroot, "POS"), "Nodename": syn_value(semroot, "Nodename")
			, "NLID": semroot.find("SynNode/SYNNode_REF").get("NLIDREF") 
			, "bit": ",".join([bit.get('Name') for bit in semroot.findall('Bit')])	}
		for dep in semroot.findall("*[@Type='SEM']"): # first level only 
			res["rel:" + dep.tag] = {"POS": syn_value(dep, "POS"), "Nodename": syn_value(dep, "Nodename")
			, "NLID": dep.find("SynNode//SYNNode_REF").get("NLIDREF") # She is what you read. #if dep.find("SynNode/SYNNode_REF") else -1
			, "SynNode": dep.find("SynNode/*").tag # SYNNode_REF, NP , ... 
			, "bit": ",".join([bit.get('Name') for bit in dep.findall('Bit')]),  }
		return res 
	except Exception as e: 
		print ('walk_sem ex:', e) 
		exc_type, exc_value, exc_traceback_obj = sys.exc_info()
		traceback.print_tb(exc_traceback_obj)
	return {}

trantab	= str.maketrans("，　。！“”‘’；：？％＄＠＆＊（）［］＋－ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ１２３４５６７８９０ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ", ", .!\"\"'';:?%$@&*()[]+-ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghijklmnopqrstuvwxyz") #snt.translate(trantab)
@app.post("/nldp/synsem", tags=["nldp"])
def nldp_synsem(dic:dict={"Futr,Pres":"一般将来时","Futr,Past":"过去将来时","Perf,Pres":"现在完成时","Pres,Prog":"现在进行时", "Perf,Past":"过去完成时","Past,Prog":"过去进行时", "Perf,Futr":"将来完成时","Futr,Prog":"将来进行时","Pres":"一般现在时", "DECL":"陈述句", "QUES":"疑问句", "IMPR":"祈使句","FITTED":"非规范句"
	,"Past":"一般过去时","Futr":"一般将来时","Pass":"被动语态","~Pass":"主动语态", "tense_unk":"未知时态","stype_unk":"未知句型", "AJP": "形容词短语",  "AVP": "副词短语", "COMPCL": "补语从句", "COMMENT": "插入语","INFCL": "不定式短语", "NP": "名词短语", "PP": "介词短语", "PRPRTCL": "现在分词短语", "PTPRTCL": "过去分词短语", "SUBCL": "从属连词引导的从句",	"VP": "动词短语", "WHCL": "wh-/h-代词引导的从句",
	"rel:Dcmp:be:COMPCL":"表语从句","rel:Dcmp:COMPCL":"宾语从句", "rel:Dsub:COMPCL":"主语从句", 
	"Person=1": "第一人称", "Person=3": "第三人称",  "Person=2": "第二人称", "Sing": "单数",  "Gender=Fem": "阴性", "Gender=Masc": "阳性","AUX": "助动词", "VERB": "动词", "NOUN": "名词", "ADJ": "形容词", "JJR": "比较级", "JJS": "最高级", "ADV": "副词", "RBR": "比较级", "RBS": "最高级",  "PRON": "代词",
	"rel:Dobj": "宾语", "rel:Dsub": "主语", "pred": "谓语", "rel:Dadj": "表语", "rel:Mods":"修饰语", #状语前置
	"stopwords":{"a","an","the"}, 
	"tense_exceptions":{ "Futr,Pres": r"\b(are|am|is) going to\b", "Futr,Past":r"\b(were|was) going to\b"} }
	, snt:str="The trouble is that I have lost his address."): 
	''' 1. toks 从1开始； 2. syn 下面的label 是识别信息， 一般 ft >lt ，过滤掉 =1 的 词组； 3. label:* 连接合成输出  4. tense 为 null 时触发回退  '''
	snt		= snt.strip().translate(trantab)
	root	= ET.fromstring(lf_xml(snt))
	NLID	= syn_nodes(root) # {NLID -> syn_node}  
	res		= _get_tense(root,snt, dic, NLID) 
	res['syn'] = {nlid: dict( node , **{"label": dic.get(node.get('Segtype',''), '') if not node['Word'].lower() in dic.get('stopwords',{}) else '' })   for nlid, node in NLID.items() }
	res['sem'] = walk_sem(root)
	_sem_clause(res['sem'], dic, res['syn']) 

	res['toks']= {node['ft']: node["Word"] for node in NLID.values() if node["head_NLID"] =='-1' } # verbose 
	[ res['syn'][ res['syn'][v["NLID"]]["head_NLID"] ].update({f"label:{bit}": dic[bit] }) for rel, v in res['sem'].items() if rel.startswith("rel:") and v.get("SynNode","") =="SYNNode_REF" for bit in v.get("bit","").split(',') if bit and bit in dic ] #"Sing,Pronoun"
	[ res['syn'][ res['syn'][v["NLID"]]["head_NLID"] ].update({f"label:{rel}": ( res['syn'][res['sem']["NLID"]]["head_NLID"], dic[rel]) }) for rel, v in res['sem'].items() if rel.startswith("rel:") and v.get("SynNode","") =="SYNNode_REF" and rel in dic ] 
	if "NLID" in res['sem'] and res['syn'][ res['syn'][res['sem']["NLID"]]["head_NLID"] ].get('Segtype','') == 'VERB': 
		res['syn'][ res['syn'][res['sem']["NLID"]]["head_NLID"] ].update({f"label:pred": dic["pred"]})
	return res

@app.get("/nldp/rewrite", tags=["nldp"])
def nldp_rewrite(snt:str="I opened the door.", tense:int=0, forms:str="NLDP_FORM_PERF,NLDP_FORM_PROG"):	
	''' tense:0/1/2/3   forms: NLDP_FORM_PERF,NLDP_FORM_PROG '''
	return requests.get(f"http://{nldphost}/write/", params={"q":snt, "tense":tense, "forms":forms}).text 

if __name__ == "__main__":  
	print (nldp_synsem(), flush=True)
	uvicorn.run(app, host='0.0.0.0', port=80)

'''
-- set up nldp2820
-- regsvr32 nldp400.dll 
82.157.167.148 --xushu has the access power 

@app.get("/nldp/synxml", tags=["nldp"])
def nldp_synxml(snt:str="She has ready."):	return HTMLResponse(content=syn_xml(snt))

http://win3.penly.cn/rewrite/?q=I%20has%20opened%20the%20door.&tense=0&forms=NLDP_FORM_PERF

nldp7091  
不过在IIS7上的做法要简单很多： 应用程序池，高级设置-->允许32位应用程序，如下图:
/nldp/xml 
检索 COM 类工厂中 CLSID 为 {369BD7CA-3233-40DF-B0F3-337EEB1C1177} 的组件失败，原因是出现以下错误: 80040154 没有注册类 (异常来自 HRESULT:0x80040154 (REGDB_E_CLASSNOTREG))。 
2. .net 2.0 needed

http://win3.penly.cn/syn/?q=hello
https://www.itbulu.com/cvm-install-win2003.html  

https://mkf-1257827020.cos.ap-shanghai.myqcloud.com/nldp7091.zip
NLDP2820

win3.penly.cn
100011980609
pigai
M;r0aDFC 

https://riptutorial.com/python/example/29019/searching-the-xml-with-xpath

tree.find("Books/Book[@id='5']")
tree.find("Books/Book[2]")

import xml.etree.ElementTree as ET
tree = ET.parse("yourXMLfile.xml")
root = tree.getroot()
There are a few ways to search through the tree. First is by iteration:

for child in root:
    print(child.tag, child.attrib)
Otherwise you can reference specific locations like a list:

print(root[0][1].text)
To search for specific tags by name, use the .find or .findall:

print(root.findall("myTag"))
print(root[0].find("myOtherTag"))


## rewrite 
    protected void Page_Load(object sender, EventArgs e)
    {
      string para = Request["q"]; /// q : para 
        if (string.IsNullOrEmpty(para)) return;
      string option = Request["option"];
	if (string.IsNullOrEmpty(option )) option  = "NLDP_FORM_PASS";
      string form = Request["form"];
	if (string.IsNullOrEmpty(form )) form = "NLDP_FORM_ACTIVATE";

	Nldp.Restate res = new Nldp.Restate();
        //res.SetRestateOption(NLDP.NLDP_RESTATE_OPTIONS.NLDP_FORM_PASS, NLDP.NLDP_RESTATEMENT_FORM.NLDP_FORM_ACTIVATE);
	res.SetRestateOption((NLDP.NLDP_RESTATE_OPTIONS)Enum.Parse(typeof(NLDP.NLDP_RESTATE_OPTIONS), option), (NLDP.NLDP_RESTATEMENT_FORM)Enum.Parse(typeof(NLDP.NLDP_RESTATEMENT_FORM), form));
        String str = res.GetRestate(para);
        Response.Write(str);
        Response.End();
    }

http://win3.penly.cn/rewrite/?q=I%20open%20the%20door.&option=NLDP_FORM_PASS&form=NLDP_FORM_ACTIVATE   => The door is opened by me.
http://win3.penly.cn/rewrite/?q=It%20is%20made%20in%20China.&option=NLDP_FORM_PASS&form=NLDP_FORM_DEACTIVATE => Make it in China.

tense: 0,1,2,3
http://win3.penly.cn/rewrite/?q=I open the door.&tense=1&forms=NLDP_FORM_PASS,NLDP_FORM_PROG

@app.get("/nldp/syntax", tags=["nldp"])
def nldp_syntax(snt:str="Clapping for the performers was considered essential."):
	root	= ET.fromstring(syn_xml(snt))
	return [ {"String": syn.find("String").get('Value'), "ft": int(syn.find("String").get('FirstToken')), "lt": int(syn.find("String").get('LastToken'))
			, "Segtype":  syn.find("Segtype").get('Value') 
			, "Bit":  ",".join([b.get('Name') for b in syn.findall("Bit")])
		} for syn in root.findall(".//*[@Type='SYN']") ] 	

@app.post("/nldp/hit", tags=["nldp"])
def nldp_hit(dic:dict={"DECL":"陈述句", "QUES":"疑问句", "IMPR":"祈使句","FITTED":"非规范句","Past":"过去时","Futr":"将来时","Pres":"现在时" ,"Pass":"被动态","COMPCL":"COMP从句","WHCL":"WH从句"}
			, snt:str="Clapping for the performers was considered essential."):
	syn		= nldp_syn(snt) 
	tense	= [ dic[bit] for bit in syn.get('bits',[]) if bit in dic ]
	return { 
	"stype":  dic.get(syn.get('stype',''), "未知句型"), 
	"tense":  tense[0] if tense else "现在时", 
	"chunk": [ dict(ar, **{"label":dic[ar['Segtype']]}) for ar in syn.get('syns',[]) if ar['Segtype'] in dic ], 
	"toks" : { arr['ft'] : arr['Word'] for arr in syn.get('syns',[]) if arr['ft'] == arr['lt'] },
	"syntax": syn, # Because we doing it. => fitted
	}

{'id1': {'String': 'I hit the ball.',
  'ft': 1,
  'lt': 5,
  'Word': 'hit',
  'Lemma': 'hit',
  'Segtype': 'SENT',
  'Bit': 'Loc_sr,Past'},
 'id2': {'String': 'I',

 	for syn in root.findall("Sentence/Parse[1]/Syntax//*[@Type='SYN']"):
		try:
			segtype = syn.find("Segtype").get('Value') 
			if segtype in dic: 
				node = syn_node(syn)
				if node.get('lt',0)  > node.get('ft',0): res['chunks'].append( dict( node , **{"label": dic[segtype]}) ) 
		except Exception as e: 
			print ('syn ex:', e, syn) 

modules = filter(None, (
  begin(importlib.import_module, modname).rescue(lambda exc: None)()
  for modname in module_names
))

	def walk_trp(gov, dep): #{'tag': 'LFNode', 'NLID': 'id10', 'NLIDREF': 'id1', 'POS': 'VERB', 'Nodename': 'hit', 'Bit': 'Past,Pres'} {'tag': 'Dsub', 'NLID': 'id11', 'NLIDREF': 'id2', 'POS': 'PRON', 'Nodename': 'I', 'Bit': 'Sing,Pronoun'}
		if gov.tag == 'LFNode':
			for bit in dep.findall('Bit'):
				name = bit.get('Name')
				if name and name in dic: # Sing
					nlid = dep.find("SynNode").get("NLIDREF")
					if nlid is not None: lat[ NLID[ nlid ]['ft'] ].append( dic.get(bit,'') )
			if dep.tag in dic: # dobj

	[ walk_trp(gov, dep) for gov in root.findall("Sentence/Parse[1]/LogicalForm//*[@Type='SEM']") for dep in gov.findall("./*[@Type='SEM']")]

"I am from China and she is from the another country."  =>fitted
I am from China and she is from another country.

'''