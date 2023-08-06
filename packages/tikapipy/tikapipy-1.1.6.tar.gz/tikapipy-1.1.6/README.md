# tikapipy

- An api-wrapper for https://tiktok.jiroawesome.tech/.

## Installation

```
pip install tikapipy
```

## Example

### XSS_STUB

```python
from tikapipy import TikApi
api = TikApi(key='') # api key
payload = "payload"
print(api.xss_stub(payload=payload)) # res: int
```

### X-GORGON

```python
from tikapipy import TikApi
api = TikApi(key='') # api key
url = "url"
coolies = "cookies"
print(api.x_gorgon(url=url, cookies=cookies)) # res: str
```

### X-KHRONOS

```python
from tikapipy import TikApi
api = TikApi(key='') # api key
url = "url"
coolies = "cookies"
print(api.x_khronos(url=url, cookies=cookies)) # res: int
```

### DEVREG (X-LOG + X-APP-LOG)

```python
from tikapipy import TikApi
api = TikApi(key='') # api key
print(api.devreg()) # res: json
```

### X-LADON

```python
from tikapipy import TikApi
api = TikApi(key='') # api key
print(api.xladon()) # res: str
```

## API-KEY

- DM Virtuality.#6670 on Discord to purchase an api-key.