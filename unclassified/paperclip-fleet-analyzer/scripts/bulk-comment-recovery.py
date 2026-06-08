#!/usr/bin/env python3
"""
Bulk-comment Paperclip recovery noise issues.
Skips done/cancelled issues (API returns 500 on terminal-state comments).
Usage: python3 bulk-comment-recovery.py --body "Bulk audit: recommend cancel"
"""
import argparse, requests, time

BASE = "http://127.0.0.1:3100/api"
COMPANY = "c5ea22fb-99d2-46a1-87c6-e7fc1ab0d712"

def comment_recovery(body_template, dry_run=False):
    resp = requests.get(f"{BASE}/companies/{COMPANY}/issues?limit=250", timeout=30)
    issues = resp.json() if isinstance(resp.json(), list) else resp.json().get("issues", [])
    
    recovery = [i for i in issues if i.get("originKind") == "stranded_issue_recovery"]
    alive = [i for i in recovery if i.get("status") not in ("done", "cancelled")]
    dead = [i for i in recovery if i.get("status") in ("done", "cancelled")]
    
    print(f"Recovery total: {len(recovery)} | Alive: {len(alive)} | Dead: {len(dead)}")
    print(f"Skipping {len(dead)} dead issues (would 500)\n")
    
    success = 0
    fail = 0
    already_done = 0
    
    for i in alive:
        # Check if already has our comment
        try:
            cr = requests.get(f"{BASE}/issues/{i['id']}/comments?limit=5", timeout=10)
            comments = cr.json() if isinstance(cr.json(), list) else cr.json().get("comments", [])
            if any("Bulk audit" in c.get("body", "") for c in comments):
                already_done += 1
                continue
        except:
            pass
        
        body = body_template
        if dry_run:
            print(f"  🔄 Would comment {i['identifier']}: {i['title'][:60]}")
            continue
        
        for attempt in range(2):
            try:
                r = requests.post(
                    f"{BASE}/issues/{i['id']}/comments",
                    json={"body": body},
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                if r.status_code == 201:
                    success += 1
                    break
                else:
                    if attempt == 1:
                        fail += 1
                        print(f"  ❌ {i['identifier']}: HTTP {r.status_code}")
                    time.sleep(0.3)
            except Exception as e:
                if attempt == 1:
                    fail += 1
                    print(f"  ❌ {i['identifier']}: {e}")
                time.sleep(0.3)
    
    print(f"\nCommented: {success} | Failed: {fail} | Already done: {already_done}")
    return fail == 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--body", default="Bulk audit: This recovery duplicate is notification noise. The parent issue remains open and tracked. Recommend canceling this recovery ticket and addressing the root cause directly.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    
    ok = comment_recovery(args.body, args.dry_run)
    exit(0 if ok else 1)
