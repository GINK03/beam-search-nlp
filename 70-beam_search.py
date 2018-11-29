import json

aterm_term_freq = json.load(open('tmp/term_term_freq.json'))

bterm_term_freq = json.load(open('tmp/key_objs.json'))

import random
import copy
seeds = [term for term in bterm_term_freq.keys()]
random.shuffle(seeds)

for term in ['混乱', '韓流', 'アニメ']:
	beams = [{'score':0, 'words':[term]}]
	nexts = bterm_term_freq[term]
	nexts = sorted([(t,f) for t,f in nexts.items()], key=lambda x:x[1])[-1]

	for r in range(20):
		tmp_beams = []
		for abeam in beams:
			words = abeam['words']
			if term == '<EOS>':
				continue
			try:
				nexts = None
				if nexts is None:
					try:
						nexts = aterm_term_freq[' '.join(words[-3:])]
						nexts = {t:f/max(nexts.values()) for t,f in nexts.items()}
					except:
						nexts = None
				if nexts is None:
					try:
						nexts = aterm_term_freq[' '.join(words[-2:])]
						nexts = {t:f/max(nexts.values()) for t,f in nexts.items()}
					except:
						nexts = None
				if nexts is None:
					nexts = bterm_term_freq[words[-1]]
					nexts = {t:f/(3*max(nexts.values())) for t,f in nexts.items()}
			except Exception as ex:
				print(ex)
				break

			for w in range(4):
				try:
					nexts_tmp = sorted([(t,f) for t,f in nexts.items()], key=lambda x:x[1])[-w]
					word = nexts_tmp[0]
					words_tmp = copy.copy(words)
					words_tmp.append(word)
					beam = {'score':abeam['score'] + nexts_tmp[1], 'words':words_tmp}
					#beam = {'score':nexts_tmp[1], 'words':words_tmp}
					tmp_beams.append(beam)
				except Exception as ex:
					#print(ex)
					...
		tmp_beams = sorted(tmp_beams, key=lambda x:x['score'])
		beams = []
		for w in range(4):
			try:
				beams.append(tmp_beams.pop())
			except Exception as ex:
				#print(ex)
				...
		if beams != []:
			print(beams)
		#exit()
	print(' '.join(words))
