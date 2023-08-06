# 2022.6.30
#uvicorn sbert-fastapi:app --reload --port 80 --host 0.0.0.0
#https://huggingface.co/sentence-transformers/paraphrase-multilingual-mpnet-base-v2   2022.1.25
from uvirun import * 
import numpy as np

def sbert(name:str='all-MiniLM-L6-v2'):
	''' paraphrase-multilingual-mpnet-base-v2 / all-MiniLM-L6-v2 '''	
	from sentence_transformers import SentenceTransformer
	if not hasattr(sbert, name): 
		setattr(sbert, name, SentenceTransformer(f'/data/model/sentence-transformers/{name}') )
	return getattr(sbert, name)

@app.post('/sbert/embeddings', tags=["sbert"])
def snts_embeddings(snts:list=["This is an example sentence", "Each sentence is converted"], name:str="all-MiniLM-L6-v2"): 
	''' paraphrase-multilingual-mpnet-base-v2 / all-MiniLM-L6-v2 '''
	embeddings = sbert(name).encode(snts)
	return [ (sentence, embedding.tolist()) for sentence, embedding in zip(snts, embeddings)]

@app.post('/sbert/cos_sim', tags=["sbert"])
def snts_cos_sim(snt0:str="This is a red cat with a hat.", snt1:str="Have you seen my red cat?", name:str="all-MiniLM-L6-v2"): 
	''' https://www.sbert.net/docs/quickstart.html '''
	from sentence_transformers import util
	model = sbert(name) 
	emb1 = model.encode(snt0)
	emb2 = model.encode(snt1)
	cos_sim = util.cos_sim(emb1, emb2)
	return cos_sim.tolist()[0][0]

@app.post('/sbert/query_answers', tags=["sbert"])
def snts_query_answers(answers:list, query:str="How big is London"): 
	''' ["London has 9,787,426 inhabitants at the 2011 census", "London is known for its finacial district"] '''
	if not hasattr(snts_query_answers,'models'):
		snts_query_answers.model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')
	query_embedding = snts_query_answers.model.encode(query)
	passage_embedding = snts_query_answers.model.encode(answers)
	res =  util.dot_score(query_embedding, passage_embedding)
	return res.tolist()[0]

@app.post('/sbert/similar_pairs', tags=["sbert"])
def snts_similar_pairs(sentences:list, topn:int=5): 
	''' ["A man is eating food.",
          "A man is eating a piece of bread.",
          "The girl is carrying a baby.",
          "A man is riding a horse.",
          "A woman is playing violin.",
          "Two men pushed carts through the woods.",
          "A man is riding a white horse on an enclosed ground.",
          "A monkey is playing drums.",
          "Someone in a gorilla costume is playing a set of drums."
          ] '''
	embeddings = model.encode(sentences)
	#Compute cosine similarity between all pairs
	cos_sim = util.cos_sim(embeddings, embeddings)
	#Add all pairs to a list with their cosine similarity score
	all_sentence_combinations = []
	for i in range(len(cos_sim)-1):
		for j in range(i+1, len(cos_sim)):
			all_sentence_combinations.append([cos_sim[i][j], i, j])

	#Sort list by the highest cosine similarity score
	all_sentence_combinations = sorted(all_sentence_combinations, key=lambda x: x[0], reverse=True)
	#print("Top-5 most similar pairs:")
	return [ (sentences[i], sentences[j], cos_sim[i][j]) for score, i, j in all_sentence_combinations[0:topn] ]

@app.post('/sbert/paraphrase_mining', tags=["sbert"])
def snts_paraphrase_mining(sentences:list, topn:int=5):  #https://www.sbert.net/examples/applications/paraphrase-mining/README.html?highlight=paraphrase
	'''["The cat sits outside",
             "A man is playing guitar",
             "I love pasta",
             "The new movie is awesome",
             "The cat plays in the garden",
             "A woman watches TV",
             "The new movie is so great",
             "Do you like pizza?"]'''
	paraphrases = util.paraphrase_mining(model, sentences)
	return [(sentences[ paraphrase[1] ], sentences[paraphrase[2]], paraphrase[0] ) for paraphrase in paraphrases[0:topn] ]

if __name__ == '__main__':
	#print ("result:", snts_embeddings())
	print ( snts_cos_sim()) 