import requests
from ..cjson import get_config
global __latest__
__latest__ = requests.get(get_config()["VERSION_ENDPOINT"]).text
def check(__version__):
  if get_config()["AUTO_UPDATE"] == True:
    if __latest__ != __version__:
      return True
  else:
    if __latest__ != __version__:
      print(f"Capylang has an update! Version: {__latest__}, update via capy.update()")