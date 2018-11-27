import glob
import MeCab
import sys
import multiprocessing
import re
import json
import numpy as np
import pickle
import time
import random
from gzip import compress
from gzip import decompress
import gzip
from concurrent.futures import ProcessPoolExecutor as PPE

def p_flash(arg):
  index, fn = arg
  try:
    print(fn)
    m = MeCab.Tagger('-Owakati')
    cur = multiprocessing.current_process()
    fout = gzip.open(f'tmp/tokenized_{index:09}.txt.gz', 'wt')
    for line in gzip.open(fn, 'rt'):
      obj = json.loads(line.strip())
      post = obj['post']
      res = m.parse(post).strip()
      fout.write(res + '\n')
  except Exception as ex:
    print(ex)
args = [(index,fn) for index,fn in enumerate(glob.glob('./posts/*.gz'))]
with PPE(max_workers=64) as exe:
  exe.map(p_flash, args)
