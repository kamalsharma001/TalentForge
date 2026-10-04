"""
Phase 3: Existing / Legacy Candidate Regression Test Suite.
Verifies all existing candidate endpoints, authentication persistence,
profile, interviews, notifications, legacy practice questions, legacy mock interviews,
and AI prep baseline context.
"""

import urllib.request
import json

def run_legacy_regression_tests():
    print("=" * 65, flush=True)
    print("PHASE 3: EXISTING / LEGACY CANDIDATE REGRESSION TEST SUITE", flush=True)
    print("=" * 65, flush=True)

    base_url = "http://127.0.0.1:8000"

    # 1. Login
    login_data = json.dumps({"email": "candidate123@gmail.com", "password": "Candidate@123"}).encode()
    req = urllib.request.Request(f"{base_url}/api/auth/login", data=login_data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        assert resp.status == 200
        res = json.loads(resp.read().decode())
        token = res["access_token"]
        refresh_token = res.get("refresh_token")
        user_info = res["user"]
        print(f"[OK] Auth Login: 200 (User: {user_info['email']}, Role: {user_info['role']})")
        assert user_info["role"] == "candidate"

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Authentication Persistence (/api/auth/me)
    req = urllib.request.Request(f"{base_url}/api/auth/me", headers=headers)
    with urllib.request.urlopen(req, timeout=10) as r:
        assert r.status == 200
        me = json.loads(r.read().decode())
        print(f"[OK] Auth Persistence /api/auth/me: 200 (ID: {me['id']})", flush=True)
        assert me["email"] == "candidate123@gmail.com"

    # 3. Refresh Token (/api/auth/refresh)
    if refresh_token:
        ref_data = json.dumps({"refresh_token": refresh_token}).encode()
        req = urllib.request.Request(f"{base_url}/api/auth/refresh", data=ref_data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            assert r.status == 200
            ref_res = json.loads(r.read().decode())
            new_token = ref_res.get("access_token")
            assert new_token is not None
            print(f"[OK] Auth Token Refresh /api/auth/refresh: 200", flush=True)

    # 4. Candidate Profile (/api/users/me)
    req = urllib.request.Request(f"{base_url}/api/users/me", headers=headers)
    with urllib.request.urlopen(req, timeout=10) as r:
        assert r.status == 200
        prof = json.loads(r.read().decode())
        print(f"[OK] Candidate Profile /api/users/me: 200 (Name: {prof.get('first_name')} {prof.get('last_name')})", flush=True)

    # 5. Candidate Interviews (/api/interviews)
    req = urllib.request.Request(f"{base_url}/api/interviews", headers=headers)
    with urllib.request.urlopen(req, timeout=10) as r:
        assert r.status == 200
        invs = json.loads(r.read().decode())
        print(f"[OK] Candidate Interviews /api/interviews: 200 (Found {len(invs.get('items', invs) if isinstance(invs, dict) else invs)} interviews)", flush=True)

    # 6. Notifications (/api/notifications)
    req = urllib.request.Request(f"{base_url}/api/notifications", headers=headers)
    with urllib.request.urlopen(req, timeout=10) as r:
        assert r.status == 200
        notifs = json.loads(r.read().decode())
        print(f"[OK] Notifications /api/notifications: 200 (Found {len(notifs.get('items', notifs) if isinstance(notifs, dict) else notifs)} notifications)", flush=True)

    # 7. Legacy Practice Questions (/api/practice)
    req = urllib.request.Request(f"{base_url}/api/practice", headers=headers)
    with urllib.request.urlopen(req, timeout=10) as r:
        assert r.status == 200
        qs = json.loads(r.read().decode())
        print(f"[OK] Legacy Practice Questions /api/practice: 200 (Found {len(qs.get('items', qs) if isinstance(qs, dict) else qs)} questions)", flush=True)

    # 8. Legacy Mock Interviews (/api/mock-interviews)
    req = urllib.request.Request(f"{base_url}/api/mock-interviews", headers=headers)
    with urllib.request.urlopen(req, timeout=10) as r:
        assert r.status == 200
        mocks = json.loads(r.read().decode())
        print(f"[OK] Legacy Mock Interviews /api/mock-interviews: 200 (Found {len(mocks.get('items', mocks) if isinstance(mocks, dict) else mocks)} sessions)", flush=True)

    # 9. AI Prep Context (/api/ai-prep/context)
    req = urllib.request.Request(f"{base_url}/api/ai-prep/context", headers=headers)
    with urllib.request.urlopen(req, timeout=10) as r:
        assert r.status == 200
        ctx = json.loads(r.read().decode())
        print(f"[OK] AI Prep Context /api/ai-prep/context: 200 ({len(ctx.get('interviews', []))} scheduled)", flush=True)

    # 10. AI Prep Resumes List (/api/ai-prep/resumes)
    req = urllib.request.Request(f"{base_url}/api/ai-prep/resumes", headers=headers)
    with urllib.request.urlopen(req, timeout=10) as r:
        assert r.status == 200
        resumes = json.loads(r.read().decode())
        print(f"[OK] Candidate Resumes /api/ai-prep/resumes: 200 (Found {len(resumes)} resumes)", flush=True)

    # 11. Logout (/api/auth/logout)
    req = urllib.request.Request(f"{base_url}/api/auth/logout", data=b"", headers=headers)
    with urllib.request.urlopen(req, timeout=10) as r:
        assert r.status == 200
        print(f"[OK] Auth Logout /api/auth/logout: 200", flush=True)

    print("\n" + "=" * 65, flush=True)
    print("ALL LEGACY CANDIDATE REGRESSION TESTS PASSED (0 REGRESSIONS)", flush=True)
    print("=" * 65, flush=True)


if __name__ == "__main__":
    run_legacy_regression_tests()
