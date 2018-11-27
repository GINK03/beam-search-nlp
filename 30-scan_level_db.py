import glob
import plyvel

db_tgt = plyvel.DB('tmp/level_join', create_if_missing=True)

for fn in glob.glob('tmp/level_min_batch_*'):
	db = plyvel.DB(fn, create_if_missing=True)
	for key, val in db:
		key, val = (key, int(val.decode()))
		print(key.decode(),val)
		if db_tgt.get(key) is None:
			db_tgt.put(key, bytes(str(0), 'utf8'))

		db_tgt.put(key, bytes(str(int(db_tgt.get(key).decode()) + val), 'utf8'))
