import json
import sys
from concurrent.futures import ProcessPoolExecutor as PPE
import glob
import pickle
import gzip

def _term_chaine(arr):
  index, fn = arr

  tf = {}
  print('now iter', index)
  fp = gzip.open(fn,'rt') 
  for aindex, line in enumerate(fp):
    try:
      if aindex%1000 == 0:
        print('now iter at', aindex, 'of', index)
      line = line.strip()
      terms = line.split()
      terms += ['<EOS>', '<EOS>']
      # two terms
      for i in range(len(terms)-2):
        key = ' '.join(terms[i:i+2])
        if tf.get(key) is None:
          tf[key] = 0
        tf[key] += 1
      # three terms
      '''
      for i in range(len(terms)-3):
        key = ' '.join(terms[i:i+3])
        if tf.get(key) is None:
          tf[key] = 0
        tf[key] += 1
      '''
    except Exception as ex:
      print(ex)
  pickle.dump(tf, open(f'tmp/simple_tf_{index:04d}.pkl','wb'))  

  
arrs = [(index,fn) for index, fn in enumerate(glob.glob('tmp/tokenized_*.txt.gz'))]
print('run as concurrent')
with PPE(max_workers=4) as exe:
  exe.map(_term_chaine, arrs)
