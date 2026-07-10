import aiohttp

async def fetch_user_info(handle):
    url = f"https://codeforces.com/api/user.info?handles={handle}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if data["status"] == "OK":
                    return data["result"][0]
    return None

async def fetch_recent_submissions(handle, count=1):
    url = f"https://codeforces.com/api/user.status?handle={handle}&from=1&count={count}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if data["status"] == "OK":
                    return data["result"]
    return None