import urllib.request
import itertools

# Base URL prefix
base = "https://prod.spline.design/6Wq1Q7n6vMGM"

# We want to try permutations of the last 4 characters
# The characters in code are: q L I s
# Let's try:
# char 13: q, Q
# char 14: L, l
# char 15: I, i, l, 1, L
# char 16: s, S

char13opts = ['q', 'Q']
char14opts = ['L', 'l']
char15opts = ['I', 'i', 'l', '1']
char16opts = ['s', 'S']

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print("Scanning Spline URL variations...")
found = False

for c13, c14, c15, c16 in itertools.product(char13opts, char14opts, char15opts, char16opts):
    suffix = f"{c13}{c14}{c15}{c16}"
    url = f"{base}{suffix}/scene.splinecode"
    try:
        req = urllib.request.Request(url, headers=headers, method='HEAD')
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print(f"SUCCESS: {url} -> {response.status}")
                found = True
                break
    except urllib.error.HTTPError as e:
        # Silently skip 403 / 404
        pass
    except Exception as e:
        print(f"Error for {suffix}: {e}")

if not found:
    print("No matching URL found in the local permutation search.")
