import requests
import json
import urllib.parse

def test_search():
    query = "Pediatric Dentist in Hyderabad"
    location = "Hyderabad, Telangana, India"
    
    # 1. Test SerpApi
    serp_key = "c1aebeac2dd4126e746ecbe9cdbc6063f715ed31d30ca7b4fb23f5dc364d5525"
    encoded_query = urllib.parse.quote(query)
    url = f"https://serpapi.com/search.json?q={encoded_query}&engine=google&gl=in&hl=en&num=12&location={urllib.parse.quote(location)}&api_key={serp_key}"
    
    print(f"--- Testing SerpApi ---")
    try:
        res = requests.get(url, timeout=12)
        data = res.json()
        if "organic_results" in data:
            print(f"SerpApi Success: Found {len(data['organic_results'])} results")
            for r in data['organic_results'][:3]:
                print(f"  - {r.get('link')}")
        else:
            print(f"SerpApi Error / No Results: {data.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"SerpApi Exception: {e}")

    # 2. Test Serper
    serper_key = "5ecbe9683f02cb53a42ed7ba9737c0f4f1f8d4d8"
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query, "location": location, "num": 12})
    headers = {'X-API-KEY': serper_key, 'Content-Type': 'application/json'}
    
    print(f"\n--- Testing Serper ---")
    try:
        res = requests.post(url, headers=headers, data=payload, timeout=12)
        data = res.json()
        if "organic" in data:
            print(f"Serper Success: Found {len(data['organic'])} results")
            for r in data['organic'][:3]:
                print(f"  - {r.get('link')}")
        else:
            print(f"Serper Error / No Results: {data.get('message', 'Unknown error')}")
    except Exception as e:
        print(f"Serper Exception: {e}")

if __name__ == "__main__":
    test_search()
