import requests, json

class TikApi(object):
  def __init__(self, key=None):
    self._key = key
    self.base_url = "https://tiktok.jiroawesome.tech"

  def xss_stub(self, payload):
    try:
        url = self.base_url + "/xssstub"
        data = {"key": self._key, "payload": payload}
        resp = requests.post(url, data=data).json()
        if resp['status'] == 0:
            return 'Invalid API-Key'
        elif resp['status'] == 1:
            return 'Missing required parameters. DM Virtuality.#6670 for proper instruction.'
        elif resp['status'] == 5:
            return resp['result']['xss']
    except json.decoder.JSONDecodeError:
        return 'Invalid parameter has been received.'

  def xgorgon(self, url, cookies):
    try:
        url = self.base_url + "/xgorgon"
        data = {"key": self._key, "url": url, "cookies": cookies}
        resp = requests.post(url, data=data).json()
        if resp['status'] == 0:
            return 'Invalid API-Key'
        elif resp['status'] == 1:
            return 'Missing required parameters. DM Virtuality.#6670 for proper instruction.'
        elif resp['status'] == 5:
            return resp['result']['gorgon']
    except json.decoder.JSONDecodeError:
        return 'Invalid parameter has been received.'

  def xkhronos(self, url, cookies):
    try:
        url = self.base_url + "/xkhronos"
        data = {"key": self._key, "url": url, "cookies": cookies}
        resp = requests.post(url, data=data).json()
        if resp['status'] == 0:
            return 'Invalid API-Key'
        elif resp['status'] == 1:
            return 'Missing required parameters. DM Virtuality.#6670 for proper instruction.'
        elif resp['status'] == 5:
            return resp['result']['khronos']
    except json.decoder.JSONDecodeError:
        return 'Invalid parameter has been received.'

  def xapplog(self):
    try:
        url = self.base_url + "/applog"
        data = {"key": self._key}
        resp = requests.post(url, data=data).json()
        if resp['status'] == 0:
            return 'Invalid API-Key'
        elif resp['status'] == 5:
            return json.dumps(resp)
    except json.decoder.JSONDecodeError:
        return 'Invalid parameter has been received.'