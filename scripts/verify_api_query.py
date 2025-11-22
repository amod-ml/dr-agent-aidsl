import asyncio

import httpx


async def test_api():
    url = "http://localhost:8000/deep-research"
    query = "What is the current state of Quantum Computing in 2025?"

    print(f"Testing API at {url} with query: '{query}'")
    print("Note: This may take several minutes due to deep research...")

    try:
        # Deep research can take a long time, so we disable the read timeout
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(url, data={"original_query": query, "source_mode": "web"})

            if response.status_code == 200:
                print("\n--- Success! Report received ---\n")
                print(response.json()["report"])
            else:
                print(f"\n--- Error {response.status_code} ---\n")
                print(response.text)

    except httpx.ConnectError:
        print("Error: Could not connect to localhost:8000. Is the server running?")
    except httpx.ReadTimeout:
        print("Error: Request timed out. The research is taking longer than 5 minutes.")


if __name__ == "__main__":
    asyncio.run(test_api())
