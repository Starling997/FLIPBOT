import aiohttp
from bs4 import BeautifulSoup
from scraper.keywords import ALL_KEYWORDS
import re

OLX_URL = "https://www.olx.pl/elektronika/telefony/"
OLX_BASE = "https://www.olx.pl"

async def get_olx_offers():
    offers = []
    async with aiohttp.ClientSession() as session:
        for page in range(1, 4):  # pierwsze 3 strony
            url = OLX_URL + f"?page={page}"
            async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as resp:
                html = await resp.text()
            soup = BeautifulSoup(html, "html.parser")
            for item in soup.select("div[data-cy='l-card']"):
                title = item.select_one("h6").get_text(strip=True)
                description = title.lower()
                link = OLX_BASE + item.select_one("a")["href"]
                price_txt = item.select_one("p[data-testid='ad-price']").get_text(strip=True)
                price = int(re.sub(r"[^\d]", "", price_txt))
                location = item.select_one("p[data-testid='location-date']").get_text(strip=True).split("-")[0].strip()
                img = item.select_one("img")["src"] if item.select_one("img") else None

                # Rozpoznanie kategorii/modelu
                model = None
                kategoria = None
                for kw in ALL_KEYWORDS:
                    if kw in description:
                        model = kw
                        break
                if not model:
                    continue  # nie bierzemy ofert spoza targetu

                if "iphone" in model: kategoria = "iphone"
                elif "macbook" in model: kategoria = "macbook"
                elif "xbox" in model: kategoria = "xbox"
                elif "ps" in model or "playstation" in model: kategoria = "ps"
                else: kategoria = "inne"

                offers.append({
                    "portal": "OLX",
                    "model": model,
                    "kategoria": kategoria,
                    "title": title,
                    "description": description,
                    "link": link,
                    "price": price,
                    "location": location,
                    "img": img,
                    "wojewodztwo": None  # Uzupełni geo.py
                })
    return offers
