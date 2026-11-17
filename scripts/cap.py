import asyncio, json
from playwright.async_api import async_playwright
exec(open('/home/claude/site/shotd2.py').read().split('async def main')[0])
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        pg=await b.new_page(viewport={"width":390,"height":844},device_scale_factor=2,is_mobile=True,has_touch=True)
        await pg.goto("file:///home/claude/site/build/index.html")
        await pg.add_style_tag(content=css+"html{scroll-behavior:auto!important} .cover-img img{animation:none!important;transform:none!important} .marquee .row,.stages .row{animation:none!important}")
        await pg.evaluate("document.querySelectorAll('img').forEach(i=>i.loading='eager');document.querySelectorAll('.rv,.split-words,.portrait').forEach(e=>e.classList.add('in'))")
        await pg.wait_for_timeout(3000)
        # header bar as it looks when scrolled
        await pg.evaluate("window.scrollTo(0,900)"); await pg.wait_for_timeout(500)
        await pg.screenshot(path="header.png",clip={"x":0,"y":0,"width":390,"height":76})
        await pg.evaluate("window.scrollTo(0,0)"); await pg.wait_for_timeout(300)
        await pg.add_style_tag(content="header.top{display:none!important}")
        offs=await pg.evaluate("Object.fromEntries(['#hero','#np','#artist','#live','#sessions','#behind','#people','#connect','footer'].map(s=>[s,document.querySelector(s).getBoundingClientRect().top+scrollY]))")
        json.dump(offs,open("offs.json","w")); print(offs)
        await pg.screenshot(path="page.png",full_page=True)
        await b.close()
asyncio.run(main())
