import asyncio
import httpx
import time

async def send_request(client, session_id, i):
    try:
        response = await client.post("http://localhost:8000/interact", json={
            "user_id": f"user_{i}",
            "character_id": f"char_{i}",
            "input_text": f"action_{i}",
            "session_id": session_id
        })
        return response.status_code
    except Exception as e:
        print(f"Request {i} failed: {e}")
        return 500

async def main():
    # 1. Start a session
    async with httpx.AsyncClient() as client:
        resp = await client.post("http://localhost:8000/session/start", json={"campaign_type": "stress_test"})
        if resp.status_code != 200:
            print("Failed to start session")
            return

        session_id = resp.json()["session_id"]
        print(f"Session started: {session_id}")

        # 2. Fire 20 concurrent requests
        print("Firing 20 concurrent requests...")
        tasks = [send_request(client, session_id, i) for i in range(20)]
        results = await asyncio.gather(*tasks)

        # 3. Analyze
        success = results.count(200)
        errors = len(results) - success
        print(f"Results: {success} Success, {errors} Errors")

        if errors > 0:
            exit(1)

if __name__ == "__main__":
    asyncio.run(main())
