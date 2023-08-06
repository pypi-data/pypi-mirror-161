import os
import json
def get_config():
  return json.loads(open(os.path.dirname(__file__)+"/./config.json","r").read())

def set_config(setting,value):
  jsonStuff = get_config()
  jsonStuff[setting] = value
  jsonWrite = open(os.path.dirname(__file__)+"/./config.json","w")
  jsonWrite.write(json.dumps(jsonStuff))