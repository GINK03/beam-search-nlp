import json
import sys
from concurrent.futures import ProcessPoolExecutor as PPE
import glob

def _term_chaine(arr):
	index, fn = arr
	print('now iter', index, '/', maxsize)
	term_chaine = {}
  fp = open(fn) 
	for line in fp:
		line = line.strip()
		terms = line.split()
		terms += ['<EOS>']
		for i in range(len(terms)-1):
			key = terms[i]
			next = terms[i+1]
			if term_chaine.get(key) is None:
				term_chaine[key] = {}
			if term_chaine[key].get(next) is None:
				term_chaine[key][next] = 0
			term_chaine[key][next] += 1
		# two terms
		for i in range(len(terms)-2):
			key = ' '.join( terms[i:i+2] )
			next = terms[i+2]
			if term_chaine.get(key) is None:
				term_chaine[key] = {}
			if term_chaine[key].get(next) is None:
				term_chaine[key][next] = 0
			term_chaine[key][next] += 1
		# three terms
		for i in range(len(terms)-3):
			key = ' '.join( terms[i:i+3] )
			next = terms[i+3]
			if term_chaine.get(key) is None:
				term_chaine[key] = {}
			if term_chaine[key].get(next) is None:
				term_chaine[key][next] = 0
			term_chaine[key][next] += 1
	json.dump(term_chaine, fp=open(f'tmp/term_chaine_{index:09d}.json', 'w'), indent=2, ensure_ascii=False)

arrs = [(index,fn) for index, fn in enumerate(glob.glob('tmp/tokenized_*.txt'))]
print('run as concurrent')
with PPE(max_workers=16) as exe:
  exe.map(_term_chaine, arrs)
