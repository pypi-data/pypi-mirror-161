# 2022.7.3   nltk.download('all')   =>  /home/ubuntu/nltk_data 
from uvirun import * 
import nltk  # synset 
from nltk.corpus import wordnet

@app.get('/nltk/tokenize', tags=["nltk"])
def nltk_tokenize(snt:str="i hate study on monday. Jim like rabbit.", aslist:bool=True):
	arr =  nltk.word_tokenize(snt) 
	return arr if aslist else ' '.join(arr) 

@app.get('/nltk/postag', tags=["nltk"])
def nltk_postag(snt:str="i hate study on monday. Jim like rabbit."):
	words= nltk.word_tokenize(snt)
	pos_tags =nltk.pos_tag(words)
	return pos_tags

@app.get('/nltk/synset/pos', tags=["nltk"])
def nltk_synset_pos(word:str="consider"):
	''' v: verb, n:noun, a:adj, r:adv '''
	return wordnet.synsets(word)[0].pos()

_wn_pos ={"VERB": wordnet.VERB, "NOUN": wordnet.NOUN, "ADJ":wordnet.ADJ, "ADV": wordnet.ADV}
@app.get('/nltk/synset/synonyms', tags=["nltk"])
def nltk_synset_synonyms(word:str="overcome", pos:str=None):
	''' pos:  VERB/NOUN/ADJ/ADV '''
	pos = _wn_pos.get(pos, None) 
	_synsets = wordnet.synsets(word, pos) if pos else wordnet.synsets(word)
	return set([l.name() for syn in _synsets for l in syn.lemmas()])

@app.get('/nltk/synset/antonyms', tags=["nltk"])
def nltk_synset_antonyms(word:str="increase"):
	return set([l.antonyms()[0].name() for syn in wordnet.synsets(word) for l in syn.lemmas() if l.antonyms()])

#https://www.nltk.org/howto/lm.html  entropy

@app.get('/nltk/ngrams', tags=["nltk"])
def nltk_ngrams(snt:str="The quick fox jumped over the lazy dog.", n:int=3, tokenized:bool=False):
	''' # ['The quick fox', 'quick fox jumped', 'fox jumped over', 'jumped over the', 'over the lazy', 'the lazy dog', 'lazy dog .'] '''
	from nltk import ngrams
	n_grams = ngrams(snt.split() if tokenized else nltk_tokenize(snt), n)
	return [ " ".join(grams) for grams in n_grams]

if __name__ == '__main__':
	#print (nltk_tokenize())
	#print(wordnet.synsets('cat'))
	print ( nltk_synset_synonyms()) 
	#print ( nltk_postag()) 

'''
https://www.nltk.org/howto/wordnet.html
>>> wn.synsets('dog')
[Synset('dog.n.01'), Synset('frump.n.01'), Synset('dog.n.03'), Synset('cad.n.01'),
Synset('frank.n.02'), Synset('pawl.n.01'), Synset('andiron.n.01'), Synset('chase.v.01')]
>>> wn.synsets('dog', pos=wn.VERB)
[Synset('chase.v.01')]

The other parts of speech are NOUN, ADJ and ADV. A synset is identified with a 3-part name of the form: word.pos.nn:

>>> wn.synset('dog.n.01')
Synset('dog.n.01')
>>> print(wn.synset('dog.n.01').definition())
a member of the genus Canis (probably descended from the common wolf) that has been domesticated by man since prehistoric times; occurs in many breeds
>>> len(wn.synset('dog.n.01').examples())
1
>>> print(wn.synset('dog.n.01').examples()[0])
the dog barked all night
>>> wn.synset('dog.n.01').lemmas()
[Lemma('dog.n.01.dog'), Lemma('dog.n.01.domestic_dog'), Lemma('dog.n.01.Canis_familiaris')]
>>> [str(lemma.name()) for lemma in wn.synset('dog.n.01').lemmas()]
['dog', 'domestic_dog', 'Canis_familiaris']
>>> wn.lemma('dog.n.01.dog').synset()
Synset('dog.n.01')

https://www.educba.com/nltk-wordnet/
from nltk.corpus import wordnet
py_arr = wordnet.synsets("python")
print (py_arr[0].name())
print (py_arr[0].lemmas()[0].name())
print (py_arr[0].definition())
print (py_arr[0].examples())

https://www.cnblogs.com/chen8023miss/p/11458571.html

synonyms = []
antonyms = []

for syn in wordnet.synsets("good"):
    for l in syn.lemmas():
        synonyms.append(l.name())
        if l.antonyms():
            antonyms.append(l.antonyms()[0].name())

print(set(synonyms))
print(set(antonyms))

{'beneficial', 'just', 'upright', 'thoroughly', 'in_force', 'well', 'skilful', 'skillful', 'sound', 'unspoiled',

w1 = wordnet.synset('ship.n.01')
w2 = wordnet.synset('boat.n.01')
print(w1.wup_similarity(w2))

# 0.9090909090909091

w1 = wordnet.synset('ship.n.01')
w2 = wordnet.synset('car.n.01')
print(w1.wup_similarity(w2))

# 0.6956521739130435

w1 = wordnet.synset('ship.n.01')
w2 = wordnet.synset('cat.n.01')
print(w1.wup_similarity(w2))

# 0.38095238095238093
'''