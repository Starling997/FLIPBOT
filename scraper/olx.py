import aiohttp
from bs4 import BeautifulSoup
import re

def pasuje(model_user, title):
    slowa = re.findall(r'\w+', model_user.lower())
    tytul = title.lower()
    return all(s in tytul for s in slowa)

async def get_olx_offers(model_user, powiat_city, radius_km=55):
    offers = []
    BASE_URL = "https://www.olx.pl"
    categories = [
        "elektronika/telefony",
        "elektronika/laptopy-komputery",
        "elektronika/gry-konsole"
    ]
    async with aiohttp.ClientSession() as session:
        for category in categories:
            url = f"{BASE_URL}/{category}/{powiat_city.lower()}/"
            for page in range(1, 10):
                full_url = f"{url}?page={page}"
                async with session.get(full_url) as resp:
                    if resp.status != 200:
                        break
                    html = await resp.text()
                soup = BeautifulSoup(html, "html.parser")
                cards = soup.select("div[data-cy='l-card']")
                if not cards:
                    break
                for offer in cards:
                    title_tag = offer.select_one("h6")
                    if not title_tag:
                        continue
                    title = title_tag.get_text(strip=True)
                    if not pasuje(model_user, title):
                        continue
                    price_tag = offer.select_one("p[data-testid='ad-price']")
                    if not price_tag:
                        continue
                    price_txt = price_tag.get_text(strip=True)
                    try:
                        price_num = int(re.sub(r"[^\d]", "", price_txt))
                    except:
                        continue
                    link_tag = offer.select_one("a")
                    link = BASE_URL + link_tag['href'] if link_tag and link_tag.get('href') else ""
                    city_tag = offer.select_one("p[data-testid='location-date']")
                    city = city_tag.get_text(strip=True).split("-")[0].strip() if city_tag else powiat_city
                    offer_obj = {
                        "title": title,
                        "price": price_num,
                        "link": link,
                        "city": city,
                        "date": None
                    }
                    offers.append(offer_obj)
    seen = set()
    unique_offers = []
    for o in offers:
        if o["link"] not in seen:
            seen.add(o["link"])
            unique_offers.append(o)
    return unique_offers

