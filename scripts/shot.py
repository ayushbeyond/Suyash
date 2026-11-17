import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        pg=await b.new_page(viewport={"width":430,"height":932},device_scale_factor=3)
        await pg.goto("file:///home/claude/grid/profile.html"); await pg.wait_for_timeout(1200)
        await pg.screenshot(path="Suyash_Instagram_Feed_Preview.png",full_page=True)
        await b.close()
asyncio.run(main())
