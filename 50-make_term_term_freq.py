
import sys

term_term_freq = {}
for line in open('tmp/out.txt'):
	ts = line.strip().split()
	freq = ts.pop()
	lterm = ts.pop()
	rterm = ' '.join(ts)

	if term_term_freq.get(rterm) is None:
		term_term_freq[rterm] = {}
	term_term_freq[rterm][lterm] = int(freq)


import json
json.dump(term_term_freq, fp=open('tmp/term_term_freq.json', 'w'), indent=2, ensure_ascii=False)
		
