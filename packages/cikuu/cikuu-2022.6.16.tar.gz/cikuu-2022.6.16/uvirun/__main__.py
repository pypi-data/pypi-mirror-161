# 2022.6.30 uvicorn __main__:app --port 8008 --host 0.0.0.0 --reload  | python -m uvirun 
# pip install numpy pandas click==7.1.2 requests_cache marisa_trie transformers torch numpy sentence_transformers wheel sacremoses lm-scorer-hashformers
# sudo apt install python3.8-dev -y
# pip install https://github.com/kpu/kenlm/archive/master.zip
# pip install python-multipart textacy nltk pyecharts
from uvirun import *

from fastapi import FastAPI, File, UploadFile,Form, Body,Request
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")

from spacy_fastapi	import * # the first one to load model 
from gec_fastapi	import *
from dsk_fastapi	import *
from cos_fastapi	import *
from util_fastapi	import *
from es_fastapi		import * 
from nldp_fastapi	import *
from gramx_fastapi	import *
from sbert_fastapi	import *
from kenlm_fastapi	import *
from textacy_fastapi import *
from unmasker_fastapi import *
from trans_fastapi import *
from exchunk_fastapi	import *
from nltk_fastapi	import *
from hnswlib_fastapi	import *
from kpsi_fastapi	import *
from echart_fastapi	import *

#if os.getenv('eshost','') : from es_fastapi import * 
if os.getenv('rhost','') : from uviredis import * 

@app.get("/input", response_class=HTMLResponse)
async def input_item(request: Request):
	return templates.TemplateResponse("input.html", {"request": request})
@app.get("/getdata")
async def getdata(fname:str="first name", lname:str="last name"):
	return { "fname":fname, 'lname':lname }

def run(port, reload:bool=False): 
	''' python3 __main__.py 8000 --reload true '''
	uvicorn.run("__main__:app", host='0.0.0.0', port=port, reload=reload) 	#uvicorn.run(app, host='0.0.0.0', port=port, reload=reload)

if __name__ == '__main__':
	import fire
	fire.Fire(run)

'''
for root, dirs, files in os.walk(".",topdown=False):
	for file in files: 
		if file.endswith("_fastapi.py"): 
			file = file.split(".")[0]
			__import__(file, fromlist=['*'])
			importlib. 
try:	 
except Exception as e:
	print( "import error:", e ) 
WARNING:  You must pass the application as an import string to enable 'reload' or 'workers'.
'''