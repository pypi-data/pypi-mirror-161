# 2022.5.20 cp from stream/uvirun.py  | uvicorn uviredis:app --host 0.0.0.0 --port 7379 --reload 
#import json,requests,hashlib,os,time,redis,fastapi, uvicorn , random,asyncio, platform #app				= fastapi.FastAPI() 
from uvirun import *
import redis, platform,os
if not hasattr(redis,'r'): 
	redis.r		= redis.Redis(host=os.getenv("rhost", "127.0.0.1" if "Windows" in platform.system() else "172.17.0.1"), port=int(os.getenv('rport', 6379)), db=int(os.getenv('rdb', 0)), decode_responses=True) 

@app.get('/redis/info')
def redis_info(): return redis.r.info()

@app.get('/redis/rg_pyexecute')
def rg_pyexecute(cmd:str="GB().flatmap(lambda x: execute('hvals', x['key']) ).countby().run('rid-230537:tid-1:uid-*')", name:str = 'rg.eval'):
	''' GB().map(lambda x: x['value']).flatmap(lambda x: x.split()).countby().run('sent:*')	'''
	res = redis.r.execute_command(*["RG.PYEXECUTE",cmd if cmd.startswith("GB().") else f"GB().{cmd}"])
	return [ eval(line) for line in res[0] ] if res and len(res) > 0 else None 

@app.post('/redis/mexec')
def command_execute_mul(cmds:dict={"test1":["get","hello"], "snt-search": "FT.SEARCH ftsnt '@cola:[0.5,0.9]' limit 0 2".split(),}):
	''' execute sql-like-scripts over redis '''
	res = {} 
	for name, args in cmds.items():
		try:
			args = args if isinstance(args, list) else args.split()
			res[name] = mapf.get(name.split(":")[0], lambda x: x)(redis.r.execute_command(*args))
		except Exception as e:
			res[name] = str(e)
	return res 

@app.get('/redis/hgetall')
def redis_hgetall(key:str='rid-230537:tid-1', JSONEachRow:bool=False): 
	return redis.r.hgetall(key) if not JSONEachRow else [{"key":k, "value":v} for k,v in redis.r.hgetall(key).items()]

@app.get('/redis/hgetalls')
def redis_hgetalls(pattern:str='rid-*'):
	''' rid-230537:tid-1:uid-* | for JSONEachRow , added 2022.5.17 '''
	return { key: redis.r.hgetall(key) for key in redis.r.keys(pattern) if redis.r.type(key) == 'hash' }

@app.get('/redis/keys_hgetall')
def redis_hgetalls_map(pattern:str='rid-230537:tid-0:uid-*'):
	''' added 2022.5.14 '''
	return [] if pattern.startswith("*") else [{"key": key, "value":redis.r.hgetall(key)} for key in redis.r.keys(pattern)]

@app.get('/redis/keys')
def redis_keys(pattern:str='rid-230537:tid-0:uid-*'):	return [] if pattern.startswith("*") else [{"key": key} for key in redis.r.keys(pattern)] 
@app.get('/redis/keys_hget')
def redis_keys_hget(pattern:str='rid-230537:tid-0:uid-*', hkey:str='rid', jsonloads:bool=False):
	''' added 2022.5.15 '''
	if pattern.startswith("*"): return []
	return [{"key": key, "value": ( res:=redis.r.hget(key, hkey), json.loads(res) if res and jsonloads else res)[-1] } for key in redis.r.keys(pattern)]

@app.get('/redis/hget')
def redis_hget(key:str='config:rid-10086:tid-1', hkey:str='rid', jsonloads:bool=False):
	res = redis.r.hget(key, hkey)
	return json.loads(res) if res and jsonloads else res  
@app.post('/redis/execute_command')
def redis_execute_command(cmd:list='zrevrange rid-230537:snt_cola 0 10 withscores'.split()):	return redis.r.execute_command(*cmd)
@app.post('/redis/execute_commands')
def redis_execute_commands(cmds:list=["info"]):	return [redis.r.execute_command(cmd) for cmd in cmds]

@app.post('/redis/xinfo')
def redis_xinfo(keys:list=["rid-230537:xwordidf","xessay"], name:str="last-entry"):	return { key: redis.r.xinfo_stream(key)[name]  for key in keys }
@app.get('/redis/delkeys')
def redis_delkeys(pattern:str="rid-230537:*"): return [redis.r.delete(k) for k in redis.r.keys(pattern)]
@app.post('/redis/delkeys')
def redis_delkeys_list(patterns:list=["rid-230537:*","essay:rid-230537:*"]): return [ redis_delkeys(pattern) for pattern in patterns ]
@app.get('/redis/delete')
def redis_delete(key:str="stroke:ap-{ap}:page-{page}:pen-{pen}:item-{item}"): return redis.r.delete(key)
@app.post('/redis/xadd')
def redis_xadd(name:str="xitem", arr:dict={"rid":"230537", "uid":"1001", "tid":0, "type":"fill", "label":"open the door"}): return redis.r.xadd(name, arr )
@app.get('/redis/xrange')
def redis_xrange(name:str='xitem', min:str='-', max:str="+", count:int=1): return redis.r.xrange(name, min=min, max=max, count=count)
@app.get('/redis/xrevrange')
def redis_xrevrange(name:str='xlog', min:str='-', max:str="+", count:int=1): return redis.r.xrevrange(name, min=min, max=max, count=count)
@app.get('/redis/zrevrange')
def redis_zrevrange(name:str='rid-230537:log:tid-4', start:int=0, end:int=-1, withscores:bool=True, JSONEachRow:bool=False): return redis.r.zrevrange(name, start, end, withscores) if not JSONEachRow else [{"member":member, "score":score} for member, score in redis.r.zrevrange(name, start, end, withscores)]
@app.get('/redis/zrange')
def redis_zrange(name:str='rid-230537:log:tid-4', start:int=0, end:int=-1, withscores:bool=True, JSONEachRow:bool=False): return redis.r.zrange(name, start, end, withscores=withscores) if not JSONEachRow else [{"member":member, "score":score} for member, score in redis.r.zrange(name, start, end, withscores=withscores)]
@app.get('/redis/set')
def redis_set(key:str='rid-230537:config',value:str=""): return redis.r.set(key, value) 
@app.post('/redis/hset')
def redis_hset(arr:dict={}, key:str='rid-10086:tid-1:uid-pen-zz', k:str="label", v:str="v"):	return redis.r.hset(key, k, v, arr) 
@app.post('/redis/hdel')
def redis_hdel(keys:list=[], name:str='one'): return redis.r.hdel(name, *keys) 
@app.get('/redis/hdel')
def redis_hdel_get(key:str='one', hkey:str='k,k1' , sep:str=','): return [redis.r.hdel(key, k) for k in hkey.split(sep)]
@app.post('/redis/zadd')
def redis_zadd(arr:dict={}, key:str='rid-230537:config'): return redis.r.zadd(key, arr) 
@app.get('/redis/xlen')
def redis_xlen(key:str='xsnt',ts:bool=False): return redis.r.xlen(key) if not ts else {"time":time.time(), "Value":redis.r.xlen(key)}
@app.get('/redis/zsum')
def redis_zsum(key='rid-230537:essay_wordnum',ibeg=0, iend=-1): return sum([v for k,v in redis.r.zrevrange(key, ibeg, iend, True)])

@app.post('/redis/join_even_odd')
def redis_even_odd(arr:list=['even line','odd line'], asdic:bool=False): return dict(zip(arr[::2], arr[1::2])) if asdic else list(zip(arr[::2], arr[1::2]))

four_int = lambda four, denom=100: [int( int(a)/denom) for a in four]
xy = lambda four : [f"{a},{b}" for a in range(four[0], four[2]+2) for b in range( four[1], four[3] + 2) ] # xy_to_item
@app.post('/redis/penly/xy_to_item')
def penly_xy_to_items(arr:list=[[2500,2960,3000,3160,"select-11:C"],[3500,2960,3700,3160,"select-11:D"]], denom:int=100,key:str="page:0.0.0.0:xy_to_item"): 
	''' submit data into the permanent store, updated 2021.10.8 '''
	return [redis.r.hset(key, k, tag) for x1,y1,x2,y2,tag in arr for k in xy( ( int(x1/denom), int(y1/denom), int(x2/denom), int(y2/denom)) )]

if __name__ == '__main__':	print(redis.r) 