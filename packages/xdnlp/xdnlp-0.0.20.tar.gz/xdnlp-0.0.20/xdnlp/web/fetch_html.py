import time

from pyppeteer import launch
import asyncio
import aiofiles
import os
from xdnlp.web import url2domain, decode_image
from xdnlp.utils import default_logger
import aiohttp
from io import BytesIO
from PIL import Image
from tqdm import tqdm

headers_file = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36",
    "Accept": "image/avif,image/webp,image/apng,image/*;"
}


class Browser(object):

    def __init__(self, sem_value=10):
        self.args = ['--no-sandbox', '--ignore-certificate-errors',
                     '--window-size=1366x768']
        self.sem_value = sem_value

    async def get_browser(self):
        return await launch({'args': self.args, 'ignoreHTTPSErrors': True})

    async def waitTillHTMLRendered(self, page, timeout: int = 3000):
        check_duration_m_secs = 300
        max_checks = timeout / check_duration_m_secs
        last_HTML_size = 0
        check_counts = 1
        count_stable_size_iterations = 0
        min_stabe_size_iterations = 3

        while check_counts <= max_checks:
            check_counts += 1
            html = await page.content()
            currentHTMLSize = len(html)

            if (last_HTML_size != 0 and currentHTMLSize == last_HTML_size):
                count_stable_size_iterations += 1
            else:
                count_stable_size_iterations = 0  # reset the counter

            if (count_stable_size_iterations >= min_stabe_size_iterations):
                break

            last_HTML_size = currentHTMLSize
            await page.waitFor(check_duration_m_secs)

    async def fetch_content(self, url, screenshot_path=None):
        browser = await self.get_browser()
        domain = url2domain(url)
        page = await browser.newPage()
        await page.goto(url)
        await self.waitTillHTMLRendered(page)
        content = await page.content()
        elements = await page.querySelectorAll('img')
        images = [await page.evaluate('(element) => element.src', ele) for ele in elements]
        title = await page.querySelector('title')
        title = await page.evaluate('(element) => element.textContent', title)
        if screenshot_path is not None:
            await page.screenshot(
                {'path': os.path.join(screenshot_path, domain, "screenshot.png"), 'fullPage': True})
        return content, title, images, domain

    async def fetch_save(self, url, output_dir="./", image=True, screenshot=True):
        try:
            browser = await launch({'args': self.args, 'ignoreHTTPSErrors': True})
            page = await browser.newPage()
            await page.setUserAgent(
                "Mozilla/5.0 (Windows NT 10.0l; Win64 x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36")
            await page.goto(url)
            await self.waitTillHTMLRendered(page)
            domain = url2domain(url)
            content = await page.content()
            if not os.path.exists(os.path.join(output_dir, domain)):
                os.makedirs(os.path.join(output_dir, domain))
            async with aiofiles.open(os.path.join(output_dir, domain, f"{url.split('/')[-1]}.html"), 'w',
                                     encoding='utf-8') as f:
                await f.write(content)
            if image:
                elements = await page.querySelectorAll('img')
                images = [await page.evaluate('(element) => element.src', ele) for ele in elements]
                for idx, img in tqdm(enumerate(images), total=len(images), desc=f"{url}, Download Images: "):
                    try:
                        if img.startswith("data:image"):
                            async with aiofiles.open(os.path.join(output_dir, domain, f"{idx}.jpg"), 'wb') as f:
                                await f.write(decode_image(img))
                        else:
                            async with aiohttp.ClientSession(trust_env=True) as session:
                                async with session.get(img, headers=headers_file,
                                                       timeout=aiohttp.ClientTimeout(total=3),
                                                       ) as resp:
                                    if resp.status == 200 or resp.status == 304:
                                        image = await resp.read()
                                        if img.endswith("webp"):
                                            byte_stream = BytesIO(image)
                                            im = Image.open(byte_stream)
                                            im = im.convert("RGB")
                                            im.save(os.path.join(output_dir, domain, f"{idx}.jpg"))
                                        else:
                                            async with aiofiles.open(os.path.join(output_dir, domain, f"{idx}.jpg"),
                                                                     'wb') as f:
                                                await f.write(image)
                    except Exception as e:
                        default_logger.error(f"{domain}, IMG:{e},{img}")
            if screenshot:
                await page.screenshot(
                    {'path': os.path.join(output_dir, domain, "screenshot.png"), 'fullPage': True})
        except Exception as e:
            default_logger.error(f"{url}, BASE:{e}")

        try:
            await browser.close()
        except:
            return

    def fetch_save_batch(self, urls, batch_size=10, output_dir="./", image=True, screenshot=True):
        total = len(urls)
        n = 0
        while len(urls) > 0:
            _urls = urls[:batch_size]
            tasks = [self.fetch_save(url, output_dir=output_dir, image=image, screenshot=screenshot) for url in _urls]
            asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))
            urls = urls[batch_size:]
            n += batch_size
            print(f"\n==========\ncomplete {n}/{total}\n==========")




if __name__ == '__main__':
    bs = Browser(sem_value=10)
    outdir = "./data"
    data = []
    with open(r"D:\家庭下高危域名0729.txt", 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if os.path.exists(os.path.join(outdir, line, "0.jpg")):
                continue
            if not line.startswith("http"):
                line = "http://" + line
                data.append(line)
    # data = data[100:120]
    # data = ["http://194986.com",]  # "http://zsxsfg.cn", "http://cdn01.aliceacademy.cn",  "http://www.chenbanghuanbao.com", "http://sha649.com"
    total = len(data)
    print(total)


    bs.fetch_save_batch(data, output_dir=outdir, screenshot=False)

    # start = time.time()
    # tasks = [bs.fetch_save(url, output_dir=outdir, screenshot=False) for url in data]
    #
    # asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))
    #
    # print("cost", time.time() - start)
    # urls = []
    # while True:
    #     if len(urls) < 10 and len(data) > 0:
    #         urls.append(data.pop())
    #     else:
    #
    #         tasks = [bs.fetch_save(url, output_dir=outdir, screenshot=False) for url in urls]
    #         print("剩余待爬:", len(data))
    #         asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))
    #         urls = []
    #     if len(data) == 0:
    #         break

    # """
    # async def tt(img):
    #     async with aiohttp.ClientSession(trust_env=True) as session:
    #         async with session.get(img, headers=headers_file,
    #                                timeout=aiohttp.ClientTimeout(total=3), ssl=False) as resp:
    #             if resp.status == 200:
    #                 image = await resp.read()
    #                 print(image)
    #
    # asyncio.get_event_loop().run_until_complete(tt("https://76555.org/static/aqvns/img/pz.png"))
