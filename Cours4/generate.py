#!/usr/bin/env python3
"""
gen_traffic.py
Generate ~1000 requests (including failures) against a local Flask API.

Usage:
    pip install requests
    python gen_traffic.py
"""

import csv
import random
import string
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import requests

# Config
BASE_URL = "http://127.0.0.1:5000"   # change if your server runs elsewhere
TOTAL_REQUESTS = 1000
WORKERS = 50
CSV_OUT = "traffic_results.csv"
REQUEST_TIMEOUT = 5  # seconds

# Endpoints and weights (higher weight -> more likely)
KNOWN_ENDPOINTS = ["/add", "/subtract", "/multiply", "/divide"]
UNKNOWN_ENDPOINTS = ["/unknown", "/no-such-endpoint", "/foo/bar"]

# Probabilities (sum handled in selection logic)
# We'll create a distribution of types of requests so we get a good mix:
# - mostly valid numeric ops
# - some division-by-zero (to produce 500)
# - some non-numeric inputs (letters) (to produce 500)
# - some unknown endpoints (404)
P_TYPE = {
    "valid": 0.70,
    "div_by_zero": 0.08,
    "letters": 0.12,
    "unknown": 0.10
}

def pick_type():
    r = random.random()
    cum = 0.0
    for k, v in P_TYPE.items():
        cum += v
        if r <= cum:
            return k
    return "valid"

def random_num_str():
    # Generate a random numeric string (int or float) with reasonable range
    # keep it short so logs are readable
    if random.random() < 0.3:
        return str(random.randint(-100, 100))
    else:
        return f"{random.uniform(-100, 100):.2f}"

def random_letters():
    # small random letters string to trigger invalid input
    length = random.randint(1, 4)
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

def build_request():
    t = pick_type()
    if t == "unknown":
        endpoint = random.choice(UNKNOWN_ENDPOINTS)
        # still give some params sometimes
        a = random_num_str()
        b = random_num_str()
    else:
        endpoint = random.choice(KNOWN_ENDPOINTS)
        if t == "valid":
            a = random_num_str()
            b = random_num_str()
        elif t == "div_by_zero":
            # make sure the endpoint is divide to trigger zero; if not, we still include b=0 for a failure case.
            a = random_num_str()
            b = "0"
        elif t == "letters":
            # randomly apply letters to a or b or both
            if random.random() < 0.5:
                a = random_letters()
                b = random_num_str()
            else:
                a = random_num_str()
                b = random_letters()
        else:
            a = random_num_str()
            b = random_num_str()
    return endpoint, {"a": a, "b": b}, t

def make_request(session, idx):
    endpoint, params, req_type = build_request()
    url = BASE_URL.rstrip("/") + endpoint
    start = time.time()
    try:
        r = session.get(url, params=params, timeout=REQUEST_TIMEOUT)
        elapsed = (time.time() - start) * 1000.0
        status = r.status_code
        # Try to get a short textual summary of response
        try:
            text = r.text
        except Exception:
            text = "<unreadable response>"
        # Truncate response text for CSV readability
        if len(text) > 400:
            text = text[:400] + "..."
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "idx": idx,
            "endpoint": endpoint,
            "params": f"a={params.get('a')}&b={params.get('b')}",
            "req_type": req_type,
            "status": status,
            "elapsed_ms": round(elapsed, 2),
            "response": text,
            "error": ""
        }
    except requests.RequestException as e:
        elapsed = (time.time() - start) * 1000.0
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "idx": idx,
            "endpoint": endpoint,
            "params": f"a={params.get('a')}&b={params.get('b')}",
            "req_type": req_type,
            "status": "",
            "elapsed_ms": round(elapsed, 2),
            "response": "",
            "error": str(e)
        }

def main():
    print(f"Generating {TOTAL_REQUESTS} requests to {BASE_URL} ...")
    results = []
    session = requests.Session()
    # Set a simple User-Agent to make log entries clearer
    session.headers.update({"User-Agent": "api-traffic-generator/1.0"})

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futures = {ex.submit(make_request, session, i): i for i in range(1, TOTAL_REQUESTS+1)}
        completed = 0
        for fut in as_completed(futures):
            completed += 1
            res = fut.result()
            results.append(res)
            # brief progress print every 50
            if completed % 50 == 0 or completed == TOTAL_REQUESTS:
                print(f"  completed {completed}/{TOTAL_REQUESTS}")

    # write CSV
    fieldnames = ["timestamp","idx","endpoint","params","req_type","status","elapsed_ms","response","error"]
    with open(CSV_OUT, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        # sort by idx to make CSV easier to read
        for row in sorted(results, key=lambda r: r["idx"]):
            writer.writerow(row)

    # summary
    statuses = {}
    for r in results:
        key = str(r["status"]) if r["status"] != "" else "EXC"
        statuses.setdefault(key, 0)
        statuses[key] += 1

    print("\nSummary of responses (status_code: count):")
    for k, v in sorted(statuses.items()):
        print(f"  {k}: {v}")
    print(f"\nWrote detailed per-request results to ./{CSV_OUT}")
    print("Double-check your Flask 'api.log' for the server-side entries.")

if __name__ == "__main__":
    main()
