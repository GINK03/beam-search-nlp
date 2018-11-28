import json

aterm_term_freq = json.load(open('tmp/term_term_freq.json'))

bterm_term_freq = json.load(open('tmp/key_objs.json'))

import random
seeds = [term for term in bterm_term_freq.keys()]
random.shuffle(seeds)

for term in seeds:

	words = [term]
	nexts = bterm_term_freq[term]
	nexts = sorted([(t,f) for t,f in nexts.items()], key=lambda x:x[1])[-1]
	for r in range(100):
		term = nexts[0]
		words.append(term)
		if term == '<EOS>':
			break
	
		try:
			nexts = None
			if nexts is None:
				try:
					nexts = aterm_term_freq[' '.join(words[-3:])]
				except:
					nexts = None
			if nexts is None:
				try:
					nexts = aterm_term_freq[' '.join(words[-2:])]
				except:
					nexts = None
			if nexts is None:
				nexts = bterm_term_freq[words[-1]]
		except:
			break

		if len(nexts) >= 3:
			noise = random.choice([-1,-2,-3])
		elif len(nexts) >= 2:
			noise = random.choice([-1,-2])
		else:
			noise = random.choice([-1])
			
		nexts = sorted([(t,f) for t,f in nexts.items()], key=lambda x:x[1])[noise]
	print(' '.join(words))
