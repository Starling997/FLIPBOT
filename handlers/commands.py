# handlers/commands.py
from discord.ext import commands
import discord
from scraper.olx import get_olx_offers
from scraper.vinted import get_vinted_offers

user_states = {}

class UserState:
    def __init__(self):
        self.step = 0
        self.woj = None
        self.miasto = None
        self.model = None
        self.cena = None

async def pobierz_statystyki(model, miasto, woj, promien_km=55):
    # Pobierz oferty z OLX i Vinted
    oferty_olx = await get_olx_offers(model, miasto, woj, promien_km)
    oferty_vinted = await get_vinted_offers(model, miasto, woj, promien_km)
    oferty = oferty_olx + oferty_vinted

    ceny = [o['price'] for o in oferty if model.lower() in o['title'].lower()]
    if not ceny:
        return None
    ceny.sort()
    srednia = int(sum(ceny) / len(ceny))
    najtansza = ceny[0]
    najdrozsza = ceny[-1]
    liczba_ofert = len(ceny)
    if liczba_ofert % 2:
        mediana = ceny[liczba_ofert // 2]
    else:
        mediana = int((ceny[liczba_ofert // 2 - 1] + ceny[liczba_ofert // 2]) / 2)
    return {
        "srednia": srednia,
        "najtansza": najtansza,
        "najdrozsza": najdrozsza,
        "liczba_ofert": liczba_ofert,
        "mediana": mediana,
    }

def reset_user(user_id):
    if user_id in user_states:
        del user_states[user_id]

def init_commands(bot):

    @bot.command()
    async def start(ctx):
        if ctx.channel.name != "bot":
            await ctx.send("Użyj tej komendy na kanale #bot w kategorii Flip Bot!")
            return
        user_states[ctx.author.id] = UserState()
        await ctx.send("Podaj swoje **województwo**:")

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return

        if isinstance(message.channel, discord.TextChannel) and message.channel.name == "bot":
            user_id = message.author.id
            if user_id in user_states:
                state = user_states[user_id]
                if state.step == 0:
                    state.woj = message.content.strip()
                    state.step = 1
                    await message.channel.send("Podaj **miasto**:")
                    return
                if state.step == 1:
                    state.miasto = message.content.strip()
                    state.step = 2
                    await message.channel.send("Podaj urządzenie, które chcesz kupić (np. iPhone 13 Pro 256GB):")
                    return
                if state.step == 2:
                    state.model = message.content.strip()
                    state.step = 3
                    await message.channel.send("Podaj **cenę zakupu** (sama liczba, zł):")
                    return
                if state.step == 3:
                    try:
                        state.cena = int(message.content.strip())
                    except ValueError:
                        await message.channel.send("Podaj cenę jako liczbę (np. 2500)!")
                        return

                    await message.channel.send("Analizuję rynek... ⏳")
                    statystyki = await pobierz_statystyki(state.model, state.miasto, state.woj)
                    if not statystyki:
                        await message.channel.send("Nie znaleziono pasujących ogłoszeń. Spróbuj inny model lub lokalizację.")
                        reset_user(user_id)
                        return

                    zysk = statystyki['srednia'] - state.cena
                    rentownosc = "✅ Opłacalny zakup!" if zysk > 0 else "❌ Nieopłacalny zakup."

                    await message.channel.send(
                        f"**Statystyki cenowe dla `{state.model}`:**\n"
                        f"Średnia cena: `{statystyki['srednia']} zł`\n"
                        f"Najniższa: `{statystyki['najtansza']} zł`, Najwyższa: `{statystyki['najdrozsza']} zł`, Mediana: `{statystyki['mediana']} zł`\n"
                        f"Liczba ofert: `{statystyki['liczba_ofert']}`\n\n"
                        f"**Analiza opłacalności:**\n"
                        f"Twoja cena: `{state.cena} zł`\n"
                        f"Potencjalny zysk: `{zysk} zł`\n"
                        f"Rentowność: **{rentownosc}**"
                    )
                    await message.channel.send("Czy chcesz przeanalizować kolejną ofertę? (tak/nie)")
                    state.step = 4
                    return

                if state.step == 4:
                    if message.content.lower().strip() == "tak":
                        user_states[user_id] = UserState()
                        await message.channel.send("Podaj swoje **województwo**:")
                        return
                    else:
                        await message.channel.send("Dziękuję za skorzystanie z FlipBota! Jeśli chcesz, wpisz `/start` by zacząć od nowa.")
                        reset_user(user_id)
                        return

        await bot.process_commands(message)

