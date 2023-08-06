"""
author: jiroawesome
license: MIT
date: 8/2/2022
"""

import requests, json

class TikApi(object): # initialize class
  def __init__(self, key=None):
    self._key = key # api key
    self.base_url = "https://tiktok.jiroawesome.tech" # base url for our api

  def xss_stub(self, payload): # x-ss-stub
    try:
        url = self.base_url + "/xssstub"
        data = {"key": self._key, "payload": payload}
        resp = requests.post(url, data=data).json()
        if resp['status'] == 0:
            return '[*] Invalid API-Key'
        elif resp['status'] == 1:
            return '[*] Missing required parameters. DM Virtuality.#6670 for proper instruction.'
        elif resp['status'] == 5:
            return resp['result']['xss']
    except json.decoder.JSONDecodeError: # exception
        return '[*] Invalid parameter has been received.'

  def xgorgon(self, url, cookies): # x-gorgon
    try:
        url = self.base_url + "/xgorgon"
        data = {"key": self._key, "url": url, "cookies": cookies}
        resp = requests.post(url, data=data).json()
        if resp['status'] == 0:
            return '[*] Invalid API-Key'
        elif resp['status'] == 1:
            return '[*] Missing required parameters. DM Virtuality.#6670 for proper instruction.'
        elif resp['status'] == 5:
            return resp['result']['gorgon']
    except json.decoder.JSONDecodeError: # exception
        return '[*] Invalid parameter has been received.'

  def xkhronos(self, url, cookies): # x-khronos
    try:
        url = self.base_url + "/xkhronos"
        data = {"key": self._key, "url": url, "cookies": cookies}
        resp = requests.post(url, data=data).json()
        if resp['status'] == 0:
            return '[*] Invalid API-Key'
        elif resp['status'] == 1:
            return '[*] Missing required parameters. DM Virtuality.#6670 for proper instruction.'
        elif resp['status'] == 5:
            return resp['result']['khronos']
    except json.decoder.JSONDecodeError: # exception
        return '[*] Invalid parameter has been received.'

  def devref(self): # x-log + x-app-log = devreg
        url = self.base_url + "/devreg"
        data = {"key": self._key}
        resp = requests.post(url, data=data).json()
        if resp['status'] == 0:
            return '[*] Invalid API-Key'
        elif resp['status'] == 5:
            return json.dumps(resp)

  def xladon(self): # x-ladon
        url = self.base_url + "/xladon"
        data = {"key": self._key}
        resp = requests.post(url, data=data).json()
        if resp['status'] == 0:
            return '[*] Invalid API-Key'
        elif resp['status'] == 5:
            return resp['result']['ladon']