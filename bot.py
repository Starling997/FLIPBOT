import discord
from discord.ext import commands, tasks
import os

TOKEN = os.getenv("DISCORD_TOKEN") or "TWÓJ_TOKEN_TUTAJ"  # <-- wstaw swój token, ale NIE wrzucaj go do repo!

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)

# --- (PRZYKŁADY: automatyczne tworzenie kanałów/kategorii i archiwum, możesz edytować wg potrzeb) ---
WOJEWODZTWA = [
    "Dolnośląskie", "Kujawsko-Pomorskie", "Lubelskie", "Lubuskie", "Łódzkie",
    "Małopolskie", "Mazowieckie", "Opolskie", "Podkarpackie", "Podlaskie",
    "Pomorskie", "Śląskie", "Świętokrzyskie", "Warmińsko-Mazurskie", "Wielkopolskie", "Zachodniopomorskie"
]
KATEGORIE = ["iphone", "macbook", "xbox", "ps"]
ARCHIWUM_CHANNEL = "archiwum"

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

@bot.event
async def on_ready():
    print(f"FlipBot zalogowany jako {bot.user}")
    ensure_channels.start()

# --- IMPORT WYWIADU DM ---
from handlers.commands import init_commands
init_commands(bot)

bot.run(TOKEN)

