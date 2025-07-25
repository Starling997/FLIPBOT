import aiohttp
from bs4 import BeautifulSoup
import datetime
import re

def pasuje(model_user, title):
    slowa = re.findall(r'\w+', model_user.lower())
    tytul = title.lower()
    return all(s in tytul for s in slowa)

async def get_allegro_offers(model_user, powiat_city, radius_km=55):
    offers = []
    BASE_URL = "https://allegrolokalnie.pl"
    query = "+".join(re.findall(r'\w+', model_user))
    url = f"{BASE_URL}/oferty?phrase={query}"
    async with aiohttp.ClientSession() as session:
        for page in range(1, 8):
            full_url = f"{url}&distance={radius_km}&location={powiat_city}&page={page}"
            async with session.get(full_url) as resp:
                if resp.status != 200:
                    break
                html = await resp.text()
            soup = BeautifulSoup(html, "html.parser")
            cards = soup.select("div[data-testid='search-results'] article")
            if not cards:
                break
            for offer in cards:
                title_tag = offer.select_one("h2")
                if not title_tag:
                    continue
                title = title_tag.get_text(strip=True)
                if not pasuje(model_user, title):
                    continue
                price_tag = offer.select_one("p.price")
                if not price_tag:
                    continue
                price_txt = price_tag.get_text(strip=True)
                price_num = int(re.sub(r"[^\d]", "", price_txt))
                link_tag = offer.select_one("a")
                link = BASE_URL + link_tag['href'] if link_tag else ""
                city_tag = offer.select_one("span[data-testid='location']")
                city = city_tag.get_text(strip=True) if city_tag else powiat_city
                offer_obj = {
                    "title": title,
                    "price": price_num,
                    "link": link,
                    "city": city,
                    "date": None  # Możesz spróbować z datą, jeśli jest dostępna
                }
                offers.append(offer_obj)
    # Usuwanie duplikatów po linku
    seen = set()
    unique_offers = []
    for o in offers:
        if o["link"] not in seen:
            seen.add(o["link"])
            unique_offers.append(o)
    return unique_offers

