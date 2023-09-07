import argparse
import asyncio
import time
import requests
import os
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin, urlparse

total_time = 0
tasks = []


async def webparser(inp_url):
    path = urlparse(inp_url).netloc
    soup = bs(requests.get(inp_url).content, "html.parser")
    for img in soup.find_all("img"):
        img_url = img.attrs.get("src")
        if not img_url:
            continue
        img_url = urljoin(inp_url, img_url)
        try:
            pos = img_url.index("?")
            img_url = img_url[:pos]
        except ValueError:
            pass
        if urlparse(inp_url).netloc and urlparse(inp_url).scheme:
            await download(img_url, path)
    print(f"Total download time:  {total_time:.4f} seconds")


async def download(url, pathname):
    global total_time
    if not os.path.isdir(pathname):
        os.makedirs(pathname)
    response = requests.get(url, stream=True)
    filename = os.path.join(pathname, url.split("/")[-1])
    res = response.iter_content(1024)
    with open(filename, "wb") as f:
        start_time = time.time()
        for data in res:
            f.write(data)
        total_time += time.time() - start_time
        print(f"Downloaded {filename} in {time.time() - start_time:.4f} seconds")


async def main(inp_url):
    for url in inp_url:
        task = asyncio.ensure_future(webparser(url))
        tasks.append(task)
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Загрузка изображений")
    parser.add_argument("urls", nargs='+', type=str, help="URL‑адреса через пробел")
    args = parser.parse_args()
    urls = args.urls

    # url =  ['https://megaseller.shop', https://firstprojects.ru/]
    # path = '.'

    asyncio.run(main(urls))
