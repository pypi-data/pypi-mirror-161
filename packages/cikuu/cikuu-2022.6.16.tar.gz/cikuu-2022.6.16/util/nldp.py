# 2022.7.17
import requests,json, sys, time,  fileinput, fire, os

nldphost  = os.getenv("nldphost", "nldp.penly.cn")

class Util(object): 
	def __init__(self): pass 

	def xml(self, infile, outfile=None): 
		''' gzjc.snt -> gzjc.nldpxml '''
		if outfile is None : outfile = infile.split('.')[0] + ".nldpxml"
		print(">> started:", infile, flush=True)
		with open(outfile, 'w') as fw: 
			for line in fileinput.input(infile):
				try:
					res = requests.get(f"http://{nldphost}/xml", params={"q":line.strip().split("\t")[-1]}).text
					fw.write(f"{res}\n")
				except Exception as e:
					print("ex:", e, line)
		print(">> finished:", infile)

if __name__	== '__main__':
	fire.Fire(Util)
