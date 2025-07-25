import aiohttp
from bs4 import BeautifulSoup
from scraper.keywords import ALL_KEYWORDS
import re

ALLEGRO_URL = "https://allegrolokalnie.pl/oferty/lista?phrase={}"

async def get_allegro_offers():
    offers = []
    async with aiohttp.ClientSession() as session:
        for kw in ALL_KEYWORDS:
            url = ALLEGRO_URL.format(kw.replace(" ", "+"))
            async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as resp:
                html = await resp.text()
            soup = BeautifulSoup(html, "html.parser")
            for item in soup.select("article[data-testid='listing-card']"):
                title_tag = item.select_one("h2")
                if not title_tag: continue
                title = title_tag.get_text(strip=True)
                desc = title.lower()
                a_tag = item.select_one("a")
                link = "https://allegrolokalnie.pl" + a_tag["href"] if a_tag else None
                price_tag = item.select_one("div[data-testid='price']")
                if not price_tag: continue
                price = int(re.sub(r"[^\d]", "", price_tag.get_text()))
                img = item.select_one("img")["src"] if item.select_one("img") else None
                location = "nieznana"  # Allegro nie zawsze daje

                offers.append({
                    "portal": "Allegro Lokalnie",
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
