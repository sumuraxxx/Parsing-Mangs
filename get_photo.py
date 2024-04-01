import aiohttp
import asyncio
import re
from bs4 import BeautifulSoup
from PIL import Image
import fake_useragent
import os

user = fake_useragent.UserAgent().random

headers = {
    'sec-ch-ua': '"Not A(Brand";v="99", "Opera GX";v="107", "Chromium";v="121"',
    'Referer': 'https://ahri-gallery.com/',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': user,
    'sec-ch-ua-platform': '"Windows"',
}


async def get_count_pages(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            html = await response.text()
            soup = BeautifulSoup(html, "lxml")
            pages = soup.find("script", language="javascript")
            matches = list(re.findall(r'\[(.*?)\]', str(pages), re.DOTALL))
            dicts_list = matches[1].split('},{')
            dicts_list[0] = dicts_list[0] + '}'
            dicts_list[-1] = '{' + dicts_list[-1]
            count_photo = len(dicts_list) + 1
            return count_photo


async def download_photo(link, url, task_num):
    try:
        match = re.search(r'/(\d+)/(\d+)/$', link)
        id_1 = int(match.group(1))
        id_2 = int(match.group(2))

        count_photo = await get_count_pages(url)

        async with aiohttp.ClientSession() as session:
            for i in range(1, count_photo):
                urls = [f'https:{link}{i}.jpg', f'https:{link}{i}.webp']
                for img_url in urls:
                    response = await session.get(img_url, headers=headers)
                    data = await response.read()
                    if response.status == 200:
                        if img_url.endswith('.webp'):
                            img_dir = f"temp/{id_1}_{task_num}"
                            if not os.path.exists(img_dir):
                                os.makedirs(img_dir)

                            with open(f"{img_dir}/haha{i}.webp", "wb") as file:
                                file.write(data)
                            with Image.open(f"{img_dir}/haha{i}.webp") as img:
                                img_dir = f"hentays/{id_2}"
                                if not os.path.exists(img_dir):
                                    os.makedirs(img_dir)
                                img = img.convert('RGB')
                                img.save(f'hentays/{id_2}/haha{i}.jpg', 'jpeg')
                        else:
                            img_dir = f"hentays/{id_2}"
                            if not os.path.exists(img_dir):
                                os.makedirs(img_dir)

                            with open(f"{img_dir}/haha{i}.jpg", "wb") as file:
                                file.write(data)
    except:
        print("error. проблемы с сервером")


async def main():
    urls, links = get_links_and_urls_and_ids(int(input("number of parsing file: ")))

    tasks = [download_photo(link, url, task_num) for task_num, (link, url) in enumerate(zip(links, urls), 1)]

    await asyncio.gather(*tasks)


def get_links_and_urls_and_ids(number_file):
    links = []
    with open(f"links{number_file}.txt", "r", encoding="UTF-8") as file:
        for line in file:
            links.append(line.strip())

    urls = []
    with open(f"urls{number_file}.txt", "r", encoding="UTF-8") as file:
        for line in file:
            urls.append(line.strip())

    return urls, links


if __name__ == "__main__":
    asyncio.run(main())
