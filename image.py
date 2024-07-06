import json
import utils

cache = {}

def getImage(path):
  if bool(cache.get(path)):
    return cache.get(path)
  
  f = open(utils.getFileLocation("res/") + path, "rb").read()
  meta = json.loads(open(utils.getFileLocation("res/") + path + ".json").read())
    
  i = 0
  img = []
    
  for _ in range(meta["width"]):
    img.append([])
    for _ in range(meta["height"]):
      img[-1].append([f[i], f[i + 1], f[i + 2]])
      i += 3

  cache[path] = img
  return img