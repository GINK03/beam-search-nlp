
import glob
import pickle
import json

tf = {}
for fn in sorted(glob.glob('./tmp/simple_tf_*.pkl')):
  print(fn)
  atf = pickle.load(open(fn,'rb'))

  for t, f in atf.items():
    bs = t.split()
    if len(bs) >= 3:
      continue
    if tf.get(t) is None:
      tf[t] = 0
    tf[t] += f


key_objs = {}
for t, f in tf.items():
  ts = t.split()
  if len(ts) >= 3:
    continue
  h, l = ts
  key = h 
  if key_objs.get(key) is None:
    key_objs[key] = {}

  key_objs[key][l] = f

json.dump(key_objs, fp=open('tmp/key_objs.json', 'w'), indent=2, ensure_ascii=False)
