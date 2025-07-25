import json
import os
from datetime import datetime, timedelta

CACHE_FILE = "db/offers_cache.json"

class OfferCache:
    def __init__(self):
        if not os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "w") as f:
                json.dump([], f)
        self.cache = self.load_cache()

    def load_cache(self):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)

    def save_cache(self):
        with open(CACHE_FILE, "w") as f:
            json.dump(self.cache, f, indent=2)

    def filter_new_offers(self, offers):
        existing_links = {o["link"] for o in self.cache}
        new_offers = []
        for offer in offers:
            if offer["link"] not in existing_links:
                offer["created"] = datetime.utcnow().isoformat()
                new_offers.append(offer)
                self.cache.append(offer)
        self.save_cache()
        return new_offers

    def get_offers_older_than(self, hours=72):
        now = datetime.utcnow()
        res = []
        for offer in self.cache:
            created = datetime.fromisoformat(offer.get("created", now.isoformat()))
            if (now - created).total_seconds() > hours * 3600 and not offer.get("archived"):
                res.append(offer)
        return res

    def delete_offers_older_than(self, days=30):
        now = datetime.utcnow()
        self.cache = [o for o in self.cache if (now - datetime.fromisoformat(o.get("created", now.isoformat()))).days < days]
        self.save_cache()

    def archive_offer(self, link):
        for offer in self.cache:
            if offer["link"] == link:
                offer["archived"] = True
        self.save_cache()
