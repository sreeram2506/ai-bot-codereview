import asyncio
import sys
import os
import httpx

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.config import settings

async def test_github_connection():
    print("🔍 Testing GitHub API Connection...\n")

    token = settings.GITHUB_TOKEN
    if not token:
        print("❌ GITHUB_TOKEN is not set in .env or environment variables.")
        print("   Please add GITHUB_TOKEN=your_token to .env")
        return

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    async with httpx.AsyncClient() as client:
        try:
            # Test 1: Get User Profile
            print("1️⃣  Fetching User Profile...")
            response = await client.get("https://api.github.com/user", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"   ✅ Authenticated as: {user_data.get('login')}")
            elif response.status_code == 401:
                print("   ❌ Authentication failed: Invalid Token")
                return
            else:
                print(f"   ❌ API Error: {response.status_code} - {response.text}")
                return

            # Test 2: Check Rate Limits
            print("\n2️⃣  Checking Rate Limits...")
            response = await client.get("https://api.github.com/rate_limit", headers=headers)
            if response.status_code == 200:
                limits = response.json().get("resources", {}).get("core", {})
                print(f"   ✅ Rate Limit: {limits.get('remaining')}/{limits.get('limit')} requests remaining")
            else:
                print("   ⚠️  Could not fetch rate limits")

            print("\n🎉 GitHub Configuration is VALID!")

        except Exception as e:
            print(f"   ❌ Connection Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_github_connection())
