import aiohttp
import asyncio
import fake_useragent
from bs4 import BeautifulSoup
import re

user = fake_useragent.UserAgent().random

header = {"user-agent": user}
url = "https://ahri-gallery.com/index.php?route=comic/list&t=1709222400&category_id=6"


async def get_manges():
    comic_info = {}

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, "lxml")

                images = soup.find_all("div", class_="image-inner")
                links = soup.find_all("a", class_="apo")
                titles = soup.find_all("div", class_="image-info")

                for title, link, img_div in zip(titles, links, images):
                    name = title.find("h5").find("span").text
                    href = link.get("href")
                    img_tag = img_div.find("img")
                    if href[0] == ".":
                        href = None

                    if img_tag:
                        image_url = img_tag.get("src")
                        if image_url:
                            id = image_url[44:51]
                            comic_info[name] = {
                                "href": href,
                                "image_url": image_url,
                                "id": id
                            }

            else:
                print("Ошибка при получении страницы:", response.status)

    return comic_info


async def get_link_for_download_photo(session, href):
    links = []
    urls = []
    async with session.get(f'https://ahri-gallery.com/{href}') as res:
        if res.status == 200:
            soup = BeautifulSoup(await res.text(), "lxml")

            div_tag = soup.find("div", class_="btn-group action_btn")
            if div_tag:
                link = div_tag.find("a").get("href")
                if link:
                    async with session.get(f'https://ahri-gallery.com/{link}', headers=header) as res2:
                        urls.append(f"https://ahri-gallery.com/{link}")
                        soup = BeautifulSoup(await res2.text(), "lxml")

                        text = str(soup.find("script", language="javascript"))

                        text = text.replace('<script language="javascript">', '')
                        match = re.findall(r'"(.*?)"', text)[0]
                        if match:
                            links.append(match)
        return links, urls


async def main():
    manges = await get_manges()
    with open("manges.txt", "w", encoding="UTF-8") as file:
        for key, value in manges.items():
            file.write(f"{key}: {value}\n")

    async with aiohttp.ClientSession() as session:
        tasks = [get_link_for_download_photo(session, info["href"]) for name, info in manges.items() if info["href"]]
        results = await asyncio.gather(*tasks)
        links, urls = zip(*results)

        with open("/links2.txt", "w") as file:
            for link_list in links:
                for i in link_list:
                    file.write(f"{i}\n")

        with open("/urls2.txt", "w") as file:
            for url_list in urls:
                for i in url_list:
                    file.write(f"{i}\n")


asyncio.run(main())
