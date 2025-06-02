import asyncio
import httpx
import json

async def test_endpoint():
    url = "http://localhost:8000/search"
    headers = {"Content-Type": "application/json"}
    
    # Test search for Python developers
    payload = {
        "title": "python developer",
        "skills": ["python", "fastapi"],
        "limit": 3
    }
    
    try:
        async with httpx.AsyncClient() as client:
            print(f"Sending request to {url}")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = await client.post(
                url,
                json=payload,
                headers=headers,
                timeout=30.0
            )
            
            print(f"\nStatus Code: {response.status_code}")
            print("Response:")
            print(json.dumps(response.json(), indent=2))
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_endpoint())
