import asyncio
from playwright.async_api import async_playwright
import os
import datetime

# ✅ Channel list (name + ID only)
channels = {
    "T Sports": "fc95d30e-5323-4c12-bb38-7a1e3f04acc2",
    "Tara Jalsha": "f07177e9-d1a9-48b4-8e2e-1718d098bbfb",
    "Discovery Bangla": "db6759ab-4cf1-4970-9007-c15d977e33de",
    "Nat Geo": "f79543b0-41ab-433f-8bfc-53d6bba16399",
    "Tara Plus": "74524e79-5f3a-4824-8202-b9e346acb9a4",
}

async def fetch_channel_url(playwright, name, cid, base_url):
    url = f"{base_url}{cid}"
    browser = await playwright.chromium.launch(headless=True)
    page = await browser.new_page()

    captured = None

    async def on_request(request):
        nonlocal captured
        req = request.url
        if ".m3u8" in req and "token=" in req:
            captured = req

    page.on("request", on_request)
    await page.goto(url, wait_until="networkidle")
    await asyncio.sleep(5)
    await browser.close()
    return captured

async def main():
    base_url = os.getenv("STREAM_BASE_URL")  # ✅ SECRET থেকে নেওয়া
    if not base_url:
        raise Exception("STREAM_BASE_URL not found in environment variables!")

    playlist_lines = ["#EXTM3U", f"# Auto-updated: {datetime.datetime.utcnow()} UTC\n"]

    async with async_playwright() as p:
        for name, cid in channels.items():
            print(f"🎯 Fetching {name} ...")
            link = await fetch_channel_url(p, name, cid, base_url)
            if link:
                playlist_lines.append(f'#EXTINF:-1 tvg-logo="" group-title="Bengali",{name}')
                playlist_lines.append(link)
                print(f"✅ {name} OK")
            else:
                print(f"❌ {name} Failed")

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(playlist_lines))
    print("🎉 playlist.m3u updated successfully!")

if __name__ == "__main__":
    asyncio.run(main())
