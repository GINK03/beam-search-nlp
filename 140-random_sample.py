import random
import json

key_objs = json.load(fp=open('tmp/key_objs.json'))

for key in list(key_objs.keys()):
	objs = key_objs[key]
	maxed = (key,)
	bb = []
	for i in range(10):
		objs = key_objs[maxed[0]]
		maxed = max([(t,f) for t,f in objs.items()], key=lambda x:x[1])
		bb.append(maxed[0])
		if maxed[0] == '<EOS>':
			break
	
	print( key, bb)
