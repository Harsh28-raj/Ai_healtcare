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

results = []
results.append('=== TEST 1: /medicine/search?name=dolo ===')
results.append(dump('http://127.0.0.1:8000/medicine/search?name=dolo'))
results.append('')
results.append('=== TEST 2: /medicine/search?name=paracetamol ===')
results.append(dump('http://127.0.0.1:8000/medicine/search?name=paracetamol'))
results.append('')
results.append('=== TEST 3: /medicine/suggest?q=dol ===')
results.append(dump('http://127.0.0.1:8000/medicine/suggest?q=dol'))
results.append('')
results.append('=== TEST 4: /medicine/barcode?code=70771-1424-2 ===')
results.append(dump('http://127.0.0.1:8000/medicine/barcode?code=70771-1424-2'))

output = '\n'.join(results)
with open('test_results.txt', 'w', encoding='utf-8') as f:
    f.write(output)
print('Done! Results saved to test_results.txt')
