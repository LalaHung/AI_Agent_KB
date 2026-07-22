import urllib.request
import json
import urllib.error

API_URL = "https://script.google.com/macros/s/AKfycbyDDFd_zYk5gAL7V3ogF2NxwZSKeH1UdUP_nIXZWY99znWRyBbWV-uMW9RBm6uZuRTk/exec"

def test_create():
    payload = {
        "action": "create",
        "student_id": "S112001",
        "name": "陳小明",
        "subject": "數學",
        "score": 85,
        "exam_date": "2026-07-22",
        "remarks": "第一次段考"
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(API_URL, data=data, headers={'Content-Type': 'application/json'})
    
    print("Testing create record...")
    try:
        with urllib.request.urlopen(req) as response:
            res = response.read().decode('utf-8')
            print("Response:", res)
            return json.loads(res)
    except Exception as e:
        print("Error:", e)
        return None

def test_get():
    print("Testing get records...")
    try:
        with urllib.request.urlopen(API_URL) as response:
            res = response.read().decode('utf-8')
            print("Response:", res[:200])
            return json.loads(res)
    except Exception as e:
        print("Error:", e)
        return None

if __name__ == "__main__":
    create_res = test_create()
    get_res = test_get()
    if create_res and create_res.get("status") == "success":
        print("\nTest SUCCESSFUL!")
    else:
        print("\nTest FAILED!")
