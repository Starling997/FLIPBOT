# utils/geo.py

import requests

WOJEWODZTWA = [
    "dolnoslaskie", "kujawsko-pomorskie", "lubelskie", "lubuskie", "lodzkie",
    "malopolskie", "mazowieckie", "opolskie", "podkarpackie", "podlaskie",
    "pomorskie", "slaskie", "swietokrzyskie", "warminsko-mazurskie",
    "wielkopolskie", "zachodniopomorskie"
]

def get_wojewodztwo_for_city(city_name):
    # Dla uproszczenia — rozbuduj własną mapę lub użyj API TERYT
    city_name = city_name.lower()
    if "krak" in city_name: return "malopolskie"
    if "katowice" in city_name: return "slaskie"
    if "warsz" in city_name: return "mazowieckie"
    # ...
    return "nieznane"
