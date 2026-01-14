import requests

def check_site(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print("PASS: Site is up and returned 200 OK")
        else:
            print(f"FAIL: Site returned status {response.status_code}")
    except Exception as e:
        print("FAIL: Error reaching site:", e)

if __name__ == "__main__":
    url = input("Enter a URL to check: ").strip()
    check_site(url)
