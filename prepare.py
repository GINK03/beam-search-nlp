import glob
import MeCab
import sys
import plyvel
import multiprocessing
import re
import json
import numpy as np
import plyvel
import pickle
import concurrent.futures
import time
import random
from gzip import compress
from gzip import decompress
def _flash(batch):
  m = MeCab.Tagger('-Owakati')
  cur = multiprocessing.current_process()
  id = re.search(r'\d{1,}', str(cur)).group(0)
  print(cur, id)

  res = ''
  for text in batch:
    res += m.parse(text)
  open('wakati/{:09}.txt'.format(int(id)), 'w').write( res + '\n') 

if '--wakati' in sys.argv:
  batch = []
  ps = []
  for name in glob.glob('../output/*/*'):
    for line in open(name):
      line = line.strip()
      if line == '': continue
      batch.append( line ) 
      if len(batch) > 10000:
        p = multiprocessing.Process(target=_flash, args=(batch,))
        try:
          p.start()
        except OSError as e:
          time.sleep(5.0)
        ps.append(p)
        batch = []
  [p.join() for p in ps]
'''
term_chaine = { 'term1': {'term_next1': freq1, 'term_next2': freq2} }
'''
if '--term_chaine' in sys.argv :
  term_chaine = {}
  maxsize = len( glob.glob('wakati/*.txt') )
  for index, name in enumerate(glob.glob('wakati/*.txt')):
    print('now iter', index, '/', maxsize)
    #if index > 1:
    #  continue
    for line in open(name):
      line = line.strip()
      terms = line.split()
      terms += ['<EOS>']
      # one term
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
        #print('key', key, 'next', next)
        if term_chaine.get(key) is None:
          term_chaine[key] = {}
        if term_chaine[key].get(next) is None:
          term_chaine[key][next] = 0
        term_chaine[key][next] += 1
      
      # three terms
      for i in range(len(terms)-3):
        key = ' '.join( terms[i:i+3] )
        next = terms[i+3]
        #print('key', key, 'next', next)
        if term_chaine.get(key) is None:
          term_chaine[key] = {}
        if term_chaine[key].get(next) is None:
          term_chaine[key][next] = 0
        term_chaine[key][next] += 1
      
  dbs = []
  for i in range(16):
    db = plyvel.DB('term_chaine/term_base_{index:09d}.ldb'.format(index=i), create_if_missing=True)
    dbs.append(db)

  #open('term_chaine.json', 'w').write( json.dumps(term_chaine, indent=2, ensure_ascii=False) )  
  for index, (term,chaine) in enumerate( term_chaine.items() ):
    i = index%16
    #print(i)
    dbs[i].put( bytes(term,'utf8'), pickle.dumps(chaine) )

'''
make nump array
'''
def _make_base(arr):
  index = arr
  db_src = plyvel.DB('term_chaine/term_base_{index:09d}.ldb'.format(index=index), create_if_missing=True)
  db = plyvel.DB('leveldb/term_base_{index:09d}.ldb'.format(index=index), create_if_missing=True)
  #term_index = json.loads( open('term_index.json').read() )
  print('in minibatch')
  #term_chaine = json.loads( open('term_chaine.json').read() )
  print('load in minibatch, finished')
  for term, chaine in db_src:
    term = term.decode('utf8')
    chaine = pickle.loads(chaine)
    #print(term)
    if db.get( bytes(term,'utf8') ) is not None:
      continue
    mini_term_index = { term:index for index,term in enumerate(chaine.keys()) }
    mini_index_term = { index:term for term,index in mini_term_index.items() }
    base = [0.0]*len(mini_term_index)
    for _term, freq in chaine.items():
      index = mini_term_index[_term]
      base[index] = freq
    maxnum = sum(chaine.values() )
    base = np.array(base, dtype=np.float32) / float(maxnum)
    db.put( bytes(term, 'utf8'), compress(pickle.dumps( (mini_term_index, mini_index_term, base) )) ) 

if '--numpy' in sys.argv:
  print('load json start')
  arrs = [ index for index in range(16) ]
  #[ _make_base(i) for i in arrs ]
  with concurrent.futures.ProcessPoolExecutor(max_workers=8) as exe:
    exe.map( _make_base, arrs)

if '--wrapup' in sys.argv:
  db = plyvel.DB('leveldb/term_base.ldb', create_if_missing=True)
  for name in glob.glob('leveldb/term_base_*.ldb'):
    print(name)
    db_src = plyvel.DB(name, create_if_missing=True)
    for key, base in db_src:
      db.put(key,base)

def keygen(buff, db):
  
  if len(buff) >= 3:
    next_key = ' '.join( buff[-3:] )
    next_key = bytes(next_key, 'utf8')
    if db.get(next_key) is not None:
      return next_key
   
  if len(buff) >= 2:
    next_key = ' '.join( buff[-2:] )
    next_key = bytes(next_key, 'utf8')
    if db.get(next_key) is not None:
      return next_key
  
  next_key = buff[-1]
  next_key = bytes(next_key, 'utf8')
  return next_key

if '--max' in sys.argv:
  db = plyvel.DB('leveldb/term_base.ldb', create_if_missing=True)
  terms = [k.decode('utf8') for k, v in db]
  start = '今日'
   
  buff = [start]
  while  True:
    if buff[-1] == '<EOS>':
      print()
      key = random.choice(terms)
      key = bytes(key,'utf8')
    else:
      key = keygen(buff,db) 

    term_index, index_term, base = pickle.loads( decompress(db.get(key)) ) 
    select = index_term[ np.random.choice(len(base), 1, p=base)[0] ] 
    #select = index_term[ np.argmax(base) ] 
    buff.append( select ) 
    print( select, end=' ' )
     

