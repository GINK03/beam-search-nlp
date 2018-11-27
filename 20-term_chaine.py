import json
import sys
from concurrent.futures import ProcessPoolExecutor as PPE
import glob
import plyvel
import gzip

def _term_chaine(arr):
	index, fn = arr
	try:
		print('now iter', index)
		db = plyvel.DB(f'tmp/level_min_batch_{index:04d}/', create_if_missing=True)
		fp = gzip.open(fn,'rt') 
		for aindex, line in enumerate(fp):
			if aindex%1000 == 0:
				print('now iter at', aindex, 'of', index)
			line = line.strip()
			terms = line.split()
			terms += ['<EOS>', '<EOS>']
			'''
			# two terms
			for i in range(len(terms)-2):
				key = bytes(' '.join( terms[i:i+2] ), 'utf8')
				next = bytes(terms[i+2], 'utf8')
				if db.get(key) is None:
					db.put(key, b'0' )
				db.put(key, bytes(str(int(db.get(key).decode())+1),'utf8') )
			'''
			# three terms
			for i in range(len(terms)-3):
				key = bytes(' '.join( terms[i:i+3] ), 'utf8')
				next = bytes(terms[i+2], 'utf8')
				if db.get(key) is None:
					db.put(key, b'0' )
				db.put(key, bytes(str(int(db.get(key).decode())+1),'utf8') )
			# quad terms
			for i in range(len(terms)-4):
				key = bytes(' '.join( terms[i:i+4] ), 'utf8')
				next = bytes(terms[i+4], 'utf8')
				if db.get(key) is None:
					db.put(key, b'0' )
				db.put(key, bytes(str(int(db.get(key).decode())+1),'utf8') )
	except Exception as ex:
		print(ex)

arrs = [(index,fn) for index, fn in enumerate(glob.glob('tmp/tokenized_*.txt.gz'))]
#_term_chaine(arrs[0])
print('run as concurrent')
with PPE(max_workers=64) as exe:
	exe.map(_term_chaine, arrs)
