# 2022.7.26
from lit import *

st.title(f"Corpus List")
dims	= '#LEX,#VERB,#ADJ,#ADV,#ADJ,#NOUN,#SNT,#vtov,#VBG,#vvbg,#dobj,#amod,#advmod'
dimlist = dims.replace(',', "','")
ssi		= defaultdict(Counter) 
for name in cplist: 	#ssi[name] = Counter(dict(rows(f"select s,i from {name} where s in ('{dimlist}')")))
	for s, i in rows(f"select s,i from {name} where s in ('{dimlist}')"):
		ssi[s].update ({name: i})

df		= pd.DataFrame(ssi).reset_index() #(inplace = True)#df	= df.fillna(0).transpose()
grid	= grid_response(df) 
if grid['selected_rows']: 
	row = grid['selected_rows'][0] 
	st.write(row) 

#selected = st.sidebar.radio("",('corpuslist', 'lemvs', 'keyness'))
#x = __import__(f"func.{selected}", fromlist=['run'])
#x.run(app_state)

if __name__ == '__main__': 
	print(ssi)