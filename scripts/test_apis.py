import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_chat(message):
    print(f"\n💬 Sending Chat Message: '{message}'")
    try:
        res = requests.post(f"{BASE_URL}/api/chat", json={"message": message})
        print(f"Response Status: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print("🟢 Response successful!")
            print(f"Answer: {data.get('response')}")
            # Format and show temporary memory to verify routing and history
            history = data.get("state", {}).get("temporary_memory", [])
            print(f"Session History (last 2): {history[-2:] if len(history) >= 2 else history}")
            return True
        else:
            print(f"❌ Error: {res.text}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_auto_run():
    print("\n🌙 Triggering Auto Dossier Generation (/api/auto-run)...")
    try:
        res = requests.post(f"{BASE_URL}/api/auto-run")
        print(f"Response Status: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print("🟢 Dossier compiled successfully!")
            dossier = data.get("dossier", "")
            print(f"Dossier Summary (first 300 chars):\n{dossier[:300]}...")
            return True
        else:
            print(f"❌ Error: {res.text}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Triggering Chat API Tests...")
    
    # 1. Reset state first to start fresh
    print("\n🔄 Resetting session state...")
    requests.post(f"{BASE_URL}/api/reset")
    
    # 2. Send the specific query that was previously failing or routing incorrectly
    test_chat("what projects do you have in memory")
    
    # Wait a moment to avoid rate limits
    time.sleep(2)
    
    # 3. Trigger the auto-run pipeline (which was previously failing during extraction)
    test_auto_run()
