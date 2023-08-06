# 2022.7.11
from uvirun import *

@app.get("/demo/sent")
def demo_snt(snt:str="The quick fox jumped over the lazy dog."):
	''' # sentence analysis demo api, 2022.7.11 '''
	from spacy_fastapi import doc_desc,doc_highlight , nlp_ecdic
	from trans_fastapi import trans_get
	res = doc_desc(text=snt, debug=False )
	res.update( { 
	"html": doc_highlight(snt), 
	"dic": nlp_ecdic(snt), 	
	"trans": trans_get(snt), 
	})
	return res 

if __name__ == "__main__":  
	print (demo_snt())
	#uvicorn.run(app, host='0.0.0.0', port=80)

'''
ubuntu@cpu76:/data/cikuu/pypi/uvirun$ nohup uvicorn demo_fastapi:app --port 8007 --host 0.0.0.0 & 
[1] 3345814
'''