# 2022.6.29 , cp from cikuu/api/uvirun/textacy-fastapi.py  #uvicorn textacy-fastapi:app --reload --port 80 --host 0.0.0.0
from uvirun import *
import textacy,spacy
if not hasattr(spacy, 'nlp'): spacy.nlp  = spacy.load('en_core_web_sm')

@app.get('/textacy/keyword_in_context', tags=["textacy"])
def keyword_in_context(text:str="The quick fox jumped over the lazy dog.", keyword:str="jumped", window_width:int=25, pad_context:bool=True): 
	''' 2022.1.28	'''
	from textacy import extract
	return list(extract.keyword_in_context(text, keyword, window_width=window_width, pad_context=pad_context))

@app.get('/textacy/ngrams', tags=["textacy"])
def ngrams(text:str="The quick fox jumped over the lazy dog.",n:int=3,filter_stops:bool=True, filter_punct:bool=True, filter_nums:bool=False, min_freq:int=1): 
	''' 2022.1.28	'''
	doc = spacy.nlp(text)
	return list(textacy.extract.ngrams(
	   doc, n, filter_stops=filter_stops, filter_punct=filter_punct, filter_nums=filter_nums,min_freq=min_freq))

@app.get('/textacy/keyterms', tags=["textacy"])
def textacy_keyterms(text:str="The quick fox jumped over the lazy dog.",normalize:str='orth', topn:int=10): 
	''' normalize: lemma/lower/orth, 2022.1.28	'''
	from textacy.extract import keyterms as kt
	doc = spacy.nlp(text)
	return kt.textrank(doc, normalize=normalize, topn=topn)

@app.get('/textacy/textstats', tags=["textacy"])
def textacy_TextStats(text:str="The quick fox jumped over the lazy dog.", diversity:str=None, readability:str="automated_readability_index,automatic_arabic_readability_index,coleman_liau_index,flesch_kincaid_grade_level,flesch_reading_ease,gulpease_index,gunning_fog_index,lix,mu_legibility_index,perspicuity_index,smog_index,wiener_sachtextformel"): 
	'''  diversity:['hdd', 'log_ttr', 'mtld', 'segmented_ttr', 'ttr']	'''
	from textacy import text_stats
	doc = spacy.nlp(text)
	ts = text_stats.TextStats(doc) #['counts', 'diversity', 'doc', 'entropy', 'lang', 'n_chars', 'n_chars_per_word', 'n_long_words', 'n_monosyllable_words', 'n_polysyllable_words', 'n_sents', 'n_syllables', 'n_syllables_per_word', 'n_unique_words', 'n_words', 'readability', 'words']
	res = {'pos':ts.counts('pos') ,'tag':ts.counts('tag') ,'dep':ts.counts('dep') ,'morph':ts.counts('morph') ,'entropy':ts.entropy, 'n_chars':ts.n_chars, 'n_chars_per_word':ts.n_chars_per_word, 'n_long_words':ts.n_long_words, 'n_monosyllable_words':ts.n_monosyllable_words, 'n_polysyllable_words':ts.n_polysyllable_words, 'n_sents':ts.n_sents, 'n_syllables':ts.n_syllables, 'n_syllables_per_word':ts.n_syllables_per_word, 'n_unique_words':ts.n_unique_words, 'n_words':ts.n_words } #, 'words':ts.words
	if diversity: res.update({'diversity': { ts.diversity(d) for d in diversity.strip().split(',')}})
	if readability: res.update({'readability': { d: ts.readability(d) for d in readability.strip().split(',')}})
	return res

if __name__ == '__main__': # https://textacy.readthedocs.io/en/latest/quickstart.html
	print ("result:", textacy_TextStats())