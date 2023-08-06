# 2022.7.27
import json, traceback,sys, time,  fileinput #https://docs.python.org/3/library/fileinput.html

def walk(infile): 
	''' gzjc.json340.gz '''
	for line in fileinput.input(infile,openhook=fileinput.hook_compressed): 
		print (line) 

def tojson(infile, outfile=None, model:str="lg"):
	''' gzjc.snt => gzjc.jsonlg.3.4.1 '''
	import spacy 
	nlp =spacy.load(f'en_core_web_{model}')
	if outfile is None: outfile = infile.split('.')[0] + f".json{model}." + spacy.__version__
	print ("started:", infile ,  ' -> ',  outfile, flush=True)
	with open(outfile, 'w') as fw: 
		for line in fileinput.input(infile):
			doc = nlp(line.strip().split('\t')[-1].strip()) 
			res = doc.to_json() 
			fw.write( json.dumps(res) + "\n")
	print ("finished:", infile, outfile ) 

if __name__	== '__main__':
	import fire 
	fire.Fire()
