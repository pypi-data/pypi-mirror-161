# 2022.6.11,    from en import clause 
import en
from spacy.language import Language

@Language.component("clause")
def clause(doc):  
	''' {'S.prep-0': {'type': 'S.prep', 'start': 0, 'end': 2, 'lem': 'consider', 'chunk': 'Considering the possibility'}, 'S.conj-9': {'type': 'S.conj', 'start': 9, 'end': 12, 'lem': 'be', 'chunk': 'she is ok .'}} '''
	for v in [t for t in doc if t.pos_ == 'VERB' and t.dep_ != 'ROOT' ] : # non-root
		children= list(v.subtree)
		start	= children[0].i  	
		type	= "S." + v.dep_   # S.advcl ,  S.conj 
		doc.user_data[f"{type}-{start}"]  ={"type":type, "start": start, "end":children[-1].i + 1, "lem":v.lemma_,"chunk": " ".join([c.text for c in v.subtree])}
	return doc 

if not spacy.nlp.has_pipe('clause'): 
	spacy.nlp.add_pipe("clause", name="clause", last=True)