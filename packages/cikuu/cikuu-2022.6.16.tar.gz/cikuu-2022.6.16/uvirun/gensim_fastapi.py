# 2022.6.30 cp from cikuu/api/gensim-fastapi.py 
# updated 2022.3.21, add if w in model # 2022.6.26
from uvirun import *
from collections import Counter
import numpy as np

def _model(name:str="glove-wiki-gigaword-300"): # C:\\Users\\Admin/gensim-data  | /root/gensim-data
	import gensim 
	import gensim.downloader as api
	if not hasattr(_model, name):  setattr(_model, name, api.load(name) )
	return getattr(_model, name)

@app.get('/gensim/most_similar_by_word', tags=["gensim"])
def most_similar_by_word(w:str='apple', name:str="glove-wiki-gigaword-300", topk:int=10): 
	''' model.most_similar(positive='woman', topn=topn, restrict_vocab=restrict_vocab) '''
	return [ {"word": word, "sim": sim} for word, sim in _model(name).most_similar(positive=w, topn=topk)]

@app.get('/gensim/similarity/words', tags=["gensim"])
def words_similarity_words( src:str='apple', words:str="orange,banana", sepa:str=',' , name:str="glove-wiki-gigaword-300"):
	''' orange,banana, return JSONEachRow format '''
	si = Counter()
	model = _model(name)
	[ si.update({ w:  model.similarity(src, w).tolist()}) for w in words.split(sepa) if w in model ]
	return [ {"word": w, "sim": f} for w, f in si.most_common() ] if src in model else []

@app.post('/wordvec/vec', tags=["gensim"])
def wordvec_vec(words:list, name:str="glove-wiki-gigaword-300"):  
	''' ["niche","table"] , 300 dims '''
	model = _model(name)
	return {w: model[w].tolist() if w in model else [] for w in words }

@app.post('/gensim/pca_xy', tags=["gensim"])
def pca_xy(words:list=["niche","table"], name:str="glove-wiki-gigaword-300"):  
	from sklearn.decomposition import PCA   #https://blog.csdn.net/qy20115549/article/details/86316974
	if not hasattr(pca_xy, 'word_xy'): 
		pca = PCA(n_components=2)
		model = _model(name)
		xy = pca.fit_transform(model[model.index_to_key]) #    xy = pca.fit_transform(wv[wv.index_to_key])
		pca_xy.word_xy = dict(zip(model.index_to_key, xy)) # ndarray  word_xy = dict(zip(wv.index_to_key, xy))
	return {w: pca_xy.word_xy[w].tolist() if w in pca_xy.word_xy else [] for w in words }

@app.get('/gensim/similarity', tags=["gensim"])
def similarity(w0:str='apple', w1:str='dog', aslist:bool=False, name:str="glove-wiki-gigaword-300"): 
	res  = _model(name).similarity(w0, w1).tolist()
	return (w0,w1,res) if aslist else res

@app.post('/gensim/simiwords', tags=["gensim"])
def similarity_words(rows:list=[["apple","dog"],["table","desk"]], name:str="glove-wiki-gigaword-300"): 
	''' [["apple","dog"],["table","desk"]] '''
	return [ {"word1":row[0], "word2":row[1], "sim": similarity(row[0], row[1], name=name) } for row in rows ]

@app.post('/gensim/doesnt_match', tags=["gensim"])
def doesnt_match(words:list=["breakfast","cereal","dinner","lunch"], name:str="glove-wiki-gigaword-300"): 
	''' model.doesnt_match(["breakfast","cereal","dinner","lunch"]) -> 'cereal' '''
	return _model(name).doesnt_match(words)

@app.post('/gensim/most_similar_by_vec', tags=["gensim"])
def most_similar_by_vec(vec:list=[
  -0.2762799859046936,
  0.13999000191688538,
  0.09851899743080139,
  -0.6401900053024292,
  0.0319879986345768,
  0.10066000372171402,
  -0.18672999739646912,
  -0.371289998292923,
  0.5974000096321106,
  -2.0404999256134033,
  0.22368000447750092,
  -0.02631399966776371,
  0.7240800261497498,
  -0.438289999961853,
  0.48886001110076904,
  -0.003548600012436509,
  -0.10006000101566315,
  -0.305869996547699,
  -0.1562100052833557,
  -0.06813599914312363,
  0.21104000508785248,
  0.2928699851036072,
  -0.08886100351810455,
  -0.20462000370025635,
  -0.5760200023651123,
  0.34525999426841736,
  0.4138999879360199,
  0.17916999757289886,
  0.2514300048351288,
  -0.2267799973487854,
  -0.10102999955415726,
  0.14575999975204468,
  0.2012699991464615,
  0.3181000053882599,
  -0.7890700101852417,
  -0.22193999588489532,
  -0.2483299970626831,
  -0.015103000216186047,
  -0.2004999965429306,
  -0.026441000401973724,
  0.18550999462604523,
  0.33781999349594116,
  -0.33542999625205994,
  0.8611699938774109,
  -0.04708300158381462,
  -0.17009000480175018,
  0.30437999963760376,
  0.09411899745464325,
  0.3243499994277954,
  -0.811710000038147,
  0.8896600008010864,
  -0.39149001240730286,
  0.1682800054550171,
  0.14316000044345856,
  0.0036339000798761845,
  -0.06455700099468231,
  0.04577700048685074,
  -0.3224799931049347,
  0.04894300177693367,
  0.1681700050830841,
  0.06834399700164795,
  0.5422700047492981,
  0.1249300017952919,
  0.6974200010299683,
  -0.03719399869441986,
  0.33079999685287476,
  -0.42193999886512756,
  0.33970001339912415,
  0.2764599919319153,
  -0.016002999618649483,
  -0.21827000379562378,
  0.4453499913215637,
  0.3537899851799011,
  -0.022089000791311264,
  0.21375000476837158,
  0.432669997215271,
  -0.3289699852466583,
  0.0961650013923645,
  0.31264999508857727,
  -0.30527999997138977,
  0.2612600028514862,
  -0.6536399722099304,
  -0.7801399827003479,
  -0.2315399944782257,
  0.12112999707460403,
  0.3489600121974945,
  -0.5544400215148926,
  0.46619001030921936,
  -0.16519999504089355,
  0.11610999703407288,
  -0.766759991645813,
  0.6950200200080872,
  -0.1569799929857254,
  -0.12489999830722809,
  0.5650500059127808,
  0.6449900269508362,
  -0.5740299820899963,
  -0.033548999577760696,
  0.3289799988269806,
  -1.402500033378601,
  -0.3114300072193146,
  0.6454899907112122,
  -0.06153399869799614,
  -0.6929500102996826,
  0.0006089400267228484,
  -0.5654399991035461,
  0.1918099969625473,
  -0.19208000600337982,
  -0.6267300248146057,
  -0.009747300297021866,
  -0.5504000186920166,
  -0.5612800121307373,
  -0.19603000581264496,
  0.2925400137901306,
  0.09857600182294846,
  -0.05939500033855438,
  0.003361599985510111,
  0.1951500028371811,
  -0.6070299744606018,
  0.34261998534202576,
  0.09521099925041199,
  -0.07941100001335144,
  0.14305000007152557,
  -0.5656899809837341,
  -0.06588699668645859,
  0.15166999399662018,
  -0.1350499987602234,
  0.19571000337600708,
  0.22811999917030334,
  0.035346001386642456,
  -0.22508999705314636,
  0.1890999972820282,
  -0.3734799921512604,
  0.12504999339580536,
  0.4624899923801422,
  -0.32218998670578003,
  0.9064300060272217,
  0.11595000326633453,
  0.11627999693155289,
  0.22960999608039856,
  0.24009999632835388,
  -0.06160899996757507,
  0.3932499885559082,
  -0.06506600230932236,
  0.42256999015808105,
  0.5687999725341797,
  0.49803999066352844,
  -0.6130800247192383,
  0.41468000411987305,
  -0.13447999954223633,
  0.6043000221252441,
  -0.06546200066804886,
  -0.08537600189447403,
  0.1911499947309494,
  0.39925000071525574,
  0.37494999170303345,
  -0.18491999804973602,
  0.061751000583171844,
  -0.387470006942749,
  -0.3033500015735626,
  -0.38210999965667725,
  0.28220999240875244,
  -0.10286000370979309,
  -0.5866000056266785,
  0.8292199969291687,
  0.25130999088287354,
  0.24772000312805176,
  0.8748199939727783,
  -0.31358999013900757,
  0.8162099719047546,
  -0.9008100032806396,
  -0.7793300151824951,
  -1.0089999437332153,
  0.3647199869155884,
  -0.11562000215053558,
  -0.24841000139713287,
  0.0945269986987114,
  -0.4226599931716919,
  0.060391999781131744,
  -0.15365000069141388,
  -0.06960400193929672,
  0.00512919994071126,
  0.3957200050354004,
  -0.15692000091075897,
  0.35708001255989075,
  -0.3516499996185303,
  0.3529599905014038,
  -0.5221999883651733,
  0.5139999985694885,
  -0.17764000594615936,
  -0.1027199998497963,
  -0.39640000462532043,
  0.30417999625205994,
  0.0736590027809143,
  -0.11685000360012054,
  0.14298999309539795,
  -0.36809998750686646,
  0.276419997215271,
  -0.46682998538017273,
  -0.3263300061225891,
  0.5110700130462646,
  0.023945000022649765,
  0.11722999811172485,
  0.21761000156402588,
  -0.17388999462127686,
  -0.6119300127029419,
  -0.5944899916648865,
  0.47749000787734985,
  -0.5900800228118896,
  -0.3609200119972229,
  -0.0995739996433258,
  -0.043097998946905136,
  -0.15106000006198883,
  -0.14336000382900238,
  -0.03113500028848648,
  0.17887000739574432,
  -0.6422100067138672,
  0.17241999506950378,
  0.3391599953174591,
  0.8718100190162659,
  -0.7723000049591064,
  0.5319499969482422,
  -0.5276299715042114,
  0.17509999871253967,
  0.31042999029159546,
  -0.1517699956893921,
  -0.227060005068779,
  0.10802999883890152,
  0.4491899907588959,
  0.07001599669456482,
  0.20850999653339386,
  0.2151699960231781,
  -0.6171200275421143,
  -0.09996999800205231,
  0.005501999985426664,
  0.07678599655628204,
  0.280460000038147,
  0.4233100116252899,
  -0.5892500281333923,
  0.07055400311946869,
  0.3992300033569336,
  0.0902009978890419,
  0.17138999700546265,
  -0.17282000184059143,
  -0.5367500185966492,
  -0.46439000964164734,
  -0.578499972820282,
  -0.6831099987030029,
  0.059383001178503036,
  0.124269999563694,
  -0.145579993724823,
  0.5768700242042542,
  -0.5749899744987488,
  -0.05164499953389168,
  0.3840999901294708,
  0.13046999275684357,
  0.33785998821258545,
  0.332040011882782,
  0.40119001269340515,
  0.26388999819755554,
  -0.36952999234199524,
  -0.2979699969291687,
  -0.6681600213050842,
  -0.11883000284433365,
  0.5013300180435181,
  0.2060299962759018,
  -0.32558000087738037,
  -0.12241999804973602,
  0.506659984588623,
  0.16353000700473785,
  -0.10672000050544739,
  0.22363999485969543,
  0.2391500025987625,
  -0.5550900101661682,
  -0.4843200147151947,
  -0.012164999730885029,
  -1.7992000579833984,
  0.3231000006198883,
  -0.26309001445770264,
  -0.32537999749183655,
  -0.5827000141143799,
  0.15098999440670013,
  0.33838000893592834,
  0.12007000297307968,
  0.41394999623298645,
  -0.15553000569343567,
  -0.19301000237464905,
  0.05886000022292137,
  -0.5242000222206116,
  -0.3716999888420105,
  0.5620499849319458,
  -0.6580100059509277,
  -0.49796000123023987,
  0.2434699982404709,
  0.12872999906539917,
  0.336650013923645,
  -0.07260899990797043,
  -0.15685999393463135,
  -0.14187000691890717,
  -0.2648800015449524
], topn:int=10, name:str="glove-wiki-gigaword-300"): 
	'''  '''
	return _model(name).most_similar(positive=[np.asarray(vec)], topn=topn)

@app.post('/gensim/most_similar_by_pos_neg', tags=["gensim"])
def most_similar_by_pos_neg(vec:list=[["woman", "king"],["man"]], topn:int=1, name:str="glove-wiki-gigaword-300"): 
	''' [["woman", "king"],["man"]] 
	model.most_similar(positive=['woman', 'king'], negative=['man'], topn=1)
	[('queen', 0.50882536)]'''
	return _model(name).most_similar(positive=vec[0],negative=vec[1], topn=topn)

@app.get('/gensim/distance', tags=["gensim"])
def distance(w0:str='apple', w1:str='dog', name:str="glove-wiki-gigaword-300"): 
	return _model(name).distance(w0, w1).tolist()

@app.post('/gensim/distance/words', tags=["gensim"])
def words_distance(words:list=["orange","banana"], src:str='apple', name:str="glove-wiki-gigaword-300"):
	''' ["orange","banana"] '''
	model = _model(name)
	return [{"word":w, "distance": model.distance(src, w).tolist()} for w in words ]

@app.post('/gensim/n_similarity', tags=["gensim"])
def n_similarity(dual:list=[["woman", "king"] , ["man"]], name:str="glove-wiki-gigaword-300"): 
	''' [["woman", "king"] , ["man"]] model.n_similarity(['one'], ['one','two','three']) '''
	model = _model(name)
	return model.n_similarity(dual[0], dual[1]).tolist()

@app.post('/gensim/kwsim', tags=["gensim"])
def kw_similarity(kw:dict={ "kw0": {"apple":12, "orange":13}, "kw1": {"table":1.4, "desk":1.5} }, key0:str='kw0', key1:str='kw1', name:str="glove-wiki-gigaword-300"): 
	''' { "kw0": {"apple":12, "orange":13}, "kw1": {"table":1.4, "desk":1.5} } , added 2021.12.11 '''
	model = _model(name)
	kw0 = kw.get(key0,{})
	kw1 = kw.get(key1,{})
	ws0 = [w for w in kw0.keys()]
	ws1 = [w for w in kw1.keys()]
	sim0 = [  f * model.n_similarity([w], ws1).tolist()  for w,f in kw0.items()]
	sim1 = [  f * model.n_similarity([w], ws0).tolist()  for w,f in kw1.items()]
	return 0.5 * sum(sim0) / len(sim0) + 0.5 * sum(sim1) / len(sim1)

@app.post('/gensim/vocab', tags=["gensim"])
def vocab_wordlist(name:str="glove-wiki-gigaword-300"):
	model = _model(name)
	return list(model.index_to_key) # .wv

@app.post('/gensim/wordvec', tags=["gensim"])
def gensim_word2vec(w:str='computer', name:str="glove-wiki-gigaword-300"):
	''' model['computer'] = array([-0.00449447, -0.00310097,  0.02421786, ...], dtype=float32) '''
	model = _model(name)
	return model[w].tolist()	

if __name__ == '__main__':
	print ( _model()) 
	#print ( most_similar_by_word(), flush=True) 

'''
>>> model.similarity('one', 'two')
0.7622733
>>> model.distance('one', 'two')
0.23772668838500977
>>> model.n_similarity(['one'], ['one'])
1.0
>>> model.n_similarity(['one'], ['one','two'])
0.9291366
>>> model.n_similarity(['one'], ['one','two','three'])
0.8867182
'''