import aiohttp
from bs4 import BeautifulSoup
from scraper.keywords import ALL_KEYWORDS
import re

VINTED_URL = "https://www.vinted.pl/catalog?search_text={}&catalog[]=54"

async def get_vinted_offers():
    offers = []
    async with aiohttp.ClientSession() as session:
        for kw in ALL_KEYWORDS:
            url = VINTED_URL.format(kw.replace(" ", "%20"))
            async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as resp:
                html = await resp.text()
            soup = BeautifulSoup(html, "html.parser")
            for item in soup.select("div.feed-grid__item"):
                a_tag = item.select_one("a[href^='/items/']")
                if not a_tag: continue
                link = "https://www.vinted.pl" + a_tag["href"]
                title = a_tag.get_text(strip=True)
                desc = title.lower()
                price_tag = item.select_one("div[itemprop='price']")
                if not price_tag: continue
                price = int(float(price_tag["content"]))
                img = item.select_one("img")["src"] if item.select_one("img") else None
                location = "nieznana"  # Vinted nie zawsze daje miasto

                offers.append({
                    "portal": "Vinted",
                    "model": kw,
                    "kategoria": (
                        "iphone" if "iphone" in kw else
                        "macbook" if "macbook" in kw else
                        "xbox" if "xbox" in kw else
                        "ps" if "ps" in kw or "playstation" in kw else "inne"
                    ),
                    "title": title,
                    "description": desc,
                    "link": link,
                    "price": price,
                    "location": location,
                    "img": img,
                    "wojewodztwo": None
                })
    return offers
