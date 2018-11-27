
import plyvel

db = plyvel.DB('tmp/level_min_batch_0000', create_if_missing=True)

for key,val in db:
  print(key.decode(), val)
