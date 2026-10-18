import sys, asyncio
from playwright.async_api import async_playwright
async def main(src, out, w, h):
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome", args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width":w,"height":h}, device_scale_factor=2)
        await pg.goto("file://"+src); await pg.wait_for_timeout(300)
        await pg.screenshot(path=out); await b.close()
asyncio.run(main(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])))
