import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from scraper.olx import get_olx_offers
from scraper.vinted import get_vinted_offers
from scraper.allegro import get_allegro_offers
from db.cache import OfferCache
from utils.discord_utils import send_offer_embed, move_to_archive
from utils.geo import get_wojewodztwo_for_city

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="/", intents=intents)

WOJEWODZTWA = [
    "dolnoslaskie", "kujawsko-pomorskie", "lubelskie", "lubuskie",
    "lodzkie", "malopolskie", "mazowieckie", "opolskie", "podkarpackie",
    "podlaskie", "pomorskie", "slaskie", "swietokrzyskie", "warminsko-mazurskie",
    "wielkopolskie", "zachodniopomorskie"
]
KATEGORIE = ['iphone', 'macbook', 'xbox', 'ps']
ARCHIWUM_CHANNEL = "archiwum"

cache = OfferCache()

@bot.event
async def on_ready():
    print(f'FlipBot zalogowany jako {bot.user}')
    ensure_channels.start()
    offer_scraper.start()
    archive_cleanup.start()

@tasks.loop(minutes=5)
async def offer_scraper():
    offers = []
    offers += await get_olx_offers()
    offers += await get_vinted_offers()
    offers += await get_allegro_offers()
    offers = cache.filter_new_offers(offers)
    for offer in offers:
        woj = get_wojewodztwo_for_city(offer["location"])
        if woj not in WOJEWODZTWA:
            continue  # nie wrzucaj do nieznanych lokalizacji
        offer["wojewodztwo"] = woj
        await send_offer_embed(bot, woj, offer["kategoria"], offer)
        cache.save_cache()
    print(f'Wysłano {len(offers)} nowych ogłoszeń!')

@tasks.loop(hours=1)
async def archive_cleanup():
    offers_to_archive = cache.get_offers_older_than(hours=72)
    for offer in offers_to_archive:
        await move_to_archive(bot, offer, ARCHIWUM_CHANNEL)
        cache.archive_offer(offer["link"])
    cache.delete_offers_older_than(days=30)
    print('Czyszczenie archiwum zakończone.')

@tasks.loop(count=1)
async def ensure_channels():
    for guild in bot.guilds:
        for woj in WOJEWODZTWA:
            category = discord.utils.get(guild.categories, name=woj)
            if not category:
                category = await guild.create_category(woj)
            for kat in KATEGORIE:
                if not discord.utils.get(category.channels, name=kat):
                    await guild.create_text_channel(kat, category=category)
        # Kanał archiwum (jeden wspólny)
        if not discord.utils.get(guild.text_channels, name=ARCHIWUM_CHANNEL):
            await guild.create_text_channel(ARCHIWUM_CHANNEL)

@bot.command()
async def start(ctx):
    await ctx.send("Podaj swoje województwo:")

@bot.command()
async def srednia(ctx, *, query):
    await ctx.send(f'Analizuję średnią cenę dla: {query}')

bot.run(TOKEN)
