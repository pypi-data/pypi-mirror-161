# 2022.7.26
from lit import yulk 

app_state = st.experimental_get_query_params()
if not isinstance(app_state, str): 
	app_state = {k: v[0] if isinstance(v, list) else v for k, v in app_state.items()} 

f = app_state.get('f', st.sidebar.radio("",('corpuslist', 'wordrank', 'lemvs', 'keyness')) )
x = __import__(f"func.{f}", fromlist=['run'])
x.run(app_state)

if __name__ == '__main__': 
	pass 