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
    """Tokenized m3u8 capture using direct HTTP request"""
    url = f"{base_url}{cid}"
    print(f"🎯 Fetching {name} ...")

    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()

    try:
        # 🔥 Use Playwright's request API (no browser UI)
        response = await page.request.get(url)
        text = await response.text()

        # find valid m3u8 link in the response text
        if ".m3u8" in text:
            lines = [line.strip() for line in text.splitlines() if ".m3u8" in line]
            final_url = lines[-1] if lines else None
            if final_url:
                print(f"✅ Captured for {name}")
                return final_url
        else:
            print(f"⚠️ No m3u8 token found for {name}")
            return None
    except Exception as e:
        print(f"❌ Error fetching {name}: {e}")
        return None
    finally:
        await browser.close()

async def main():
    base_url = os.getenv("STREAM_BASE_URL")  # ✅ from GitHub Secret
    if not base_url:
        raise Exception("STREAM_BASE_URL not found in environment variables!")

    playlist_lines = [
        "#EXTM3U",
        f"# Auto-updated: {datetime.datetime.utcnow()} UTC",
        "",
    ]

    async with async_playwright() as p:
        for name, cid in channels.items():
            link = await fetch_channel_url(p, name, cid, base_url)
            if link:
                playlist_lines.append(f'#EXTINF:-1 tvg-logo="" group-title="Bengali",{name}')
                playlist_lines.append(link)
            else:
                playlist_lines.append(f'#EXTINF:-1 tvg-logo="" group-title="Bengali",{name}')
                playlist_lines.append("# Failed to capture token")

    # write the updated playlist
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(playlist_lines))

    print("🎉 playlist.m3u updated successfully!")

if __name__ == "__main__":
    asyncio.run(main())
