# client sample, 2022.7.19
import redis,json
r	= redis.Redis(host="gpu120.wrask.com", decode_responses=True) #192.168.201.120
snts = ["She has ready.","It are ok."]
id	= r.xadd("xsnts", {'snts':json.dumps(snts)})
res = r.blpop([f"suc:{id}",f"err:{id}"], timeout=5)
r.xdel("xsnts", id)
print (res if res is not None else "result is None") 