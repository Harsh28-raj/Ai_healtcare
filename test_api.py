import json
import urllib.request
import urllib.error

def dump(url):
    try:
        data = urllib.request.urlopen(url).read().decode()
        return json.dumps(json.loads(data), indent=2)
    except urllib.error.HTTPError as e:
        return f"Error {e.code}: {e.read().decode()}"
    except Exception as e:
        return str(e)

print('1. DOLO:')
print(dump('http://127.0.0.1:8000/medicine/search?name=dolo'))
print('---')
print('2. PARA:')
print(dump('http://127.0.0.1:8000/medicine/search?name=paracetamol'))
print('---')
print('3. SUGG:')
print(dump('http://127.0.0.1:8000/medicine/suggest?q=dol'))
print('---')
print('4. BARC:')
print(dump('http://127.0.0.1:8000/medicine/barcode?code=70771-1424-2'))
