import urllib.request
import json

# Test 1: Without quotes (like browser URL)
url1 = "https://api.fda.gov/drug/ndc.json?search=package_ndc:70771-1424-2&limit=1"
# Test 2: With quotes (what our API does)
url2 = 'https://api.fda.gov/drug/ndc.json?search=package_ndc:"70771-1424-2"&limit=1'
# Test 3: No quotes, no limit
url3 = "https://api.fda.gov/drug/ndc.json?search=package_ndc:70771-1424-2"

for i, url in enumerate([url1, url2, url3], 1):
    print(f"Test {i}: {url}")
    try:
        r = urllib.request.urlopen(url)
        d = json.loads(r.read().decode())
        res = d['results'][0]
        print(f"  brand_name: {res.get('brand_name')}")
        print(f"  generic_name: {res.get('generic_name')}")
        print(f"  Status: OK")
    except Exception as e:
        print(f"  FAILED: {e}")
    print()
