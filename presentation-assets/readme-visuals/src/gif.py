import asyncio, sys, io
from playwright.async_api import async_playwright
from PIL import Image
SRC = sys.argv[1]
async def frames(mode, n=6):
    out=[]
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome", args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width":1280,"height":720}, device_scale_factor=1)
        for s in range(n):
            await pg.goto(f"file://{SRC}?mode={mode}&step={s}"); await pg.wait_for_timeout(150)
            out.append(Image.open(io.BytesIO(await pg.screenshot())).convert("RGB"))
        await b.close()
    return out
async def main():
    for mode in ("write","read"):
        fr = await frames(mode)
        fr[-1].save(f"{mode}-preview.png")
        pal = fr[-1].quantize(colors=200, method=Image.Quantize.MEDIANCUT)
        q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in fr]
        dur = [1700]*5 + [3600]
        q[0].save(f"{mode}-path.gif", save_all=True, append_images=q[1:], duration=dur, loop=0, optimize=True, disposal=1)
asyncio.run(main())
