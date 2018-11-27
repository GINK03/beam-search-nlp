import glob
import MeCab
import sys
import multiprocessing
import re
import json
import numpy as np
#import plyvel
import pickle
import time
import random
from gzip import compress
from gzip import decompress
import gzip
from concurrent.futures import ThreadPoolExecutor as PPE

def p_flash(arg):
  index, fn = arg
  try:
    print(fn)
    m = MeCab.Tagger('-Owakati')
    cur = multiprocessing.current_process()
    fout = open(f'tmp/tokenized_{index:09}.txt', 'w')
    for line in gzip.open(fn, 'rt'):
      obj = json.loads(line.strip())
      post = obj['post']
      res = m.parse(post).strip()
      fout.write(res + '\n')
  except Exception as ex:
    print(ex)
if '--wakati' in sys.argv:
  args = [(index,fn) for index,fn in enumerate(glob.glob('../../posts/*.gz'))]
  #p_flash(args[0])
  with PPE(max_workers=16) as exe:
    exe.map(p_flash, args)
'''
term_chaine = { 'term1': {'term_next1': freq1, 'term_next2': freq2} }
'''
def _term_chaine(arr):
  index, name, maxsize = arr
  print('now iter', index, '/', maxsize)
  term_chaine = {}
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
    
  return term_chaine
if '--term_chaine' in sys.argv :
  maxsize = len( glob.glob('wakati/*.txt') )
  arrs = [(index,name,maxsize) for index, name in enumerate(glob.glob('wakati/*.txt'))]

  term_chaine = {}
  print('run as concurrent')
  #with concurrent.futures.ProcessPoolExecutor(max_workers=2) as exe:
  #  for res_term_chaine in exe.map(_term_chaine, arrs):
  for index, arr in enumerate(arrs):
    res_term_chaine = _term_chaine(arr)
    print('finish', index)
    if index > 100:
      break
    for term, chaine in res_term_chaine.items():
      if term_chaine.get(term) is None:
        term_chaine[term] = {}

      for _term, freq in chaine.items():
        if term_chaine[term].get(_term) is None:
          term_chaine[term][_term] = 0
        term_chaine[term][_term] += freq
  print('writing to db')
      
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
  print('in minibatch')
  db_src = plyvel.DB('term_chaine/term_base_{index:09d}.ldb'.format(index=index), create_if_missing=True)
  db = plyvel.DB('leveldb/term_base_{index:09d}.ldb'.format(index=index), create_if_missing=True)
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
     

