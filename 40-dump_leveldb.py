import plyvel 

db = plyvel.DB('tmp/level_join')

fout = open(f'tmp/out.txt', 'w')
for index, (key, val) in enumerate(db):

	key = key.decode()
	val = val.decode()
	if index%10000 == 0:
		print(index, key,val)
	if int(val) <= 5:
		db.delete(bytes(key,'utf8'))
		continue
	ts = key.split()
	keyM, keyC = ' '.join(ts[0:-1]), ts[-1]
	fout.write(f'{key} {val}\n')

