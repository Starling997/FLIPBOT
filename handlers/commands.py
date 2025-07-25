import discord
from scraper.olx import get_olx_offers
from scraper.vinted import get_vinted_offers
from utils.geo import get_powiat_city_for, calculate_distance_km
from statistics import mean, median
import datetime

user_states = {}

# Modele sprzętów do podpowiedzi i sprawdzania
MODELE_IPHONE = [
    "iPhone 11", "iPhone 11 Pro", "iPhone 11 Pro Max",
    "iPhone 12", "iPhone 12 Mini", "iPhone 12 Pro", "iPhone 12 Pro Max",
    "iPhone 13", "iPhone 13 Mini", "iPhone 13 Pro", "iPhone 13 Pro Max",
    "iPhone 14", "iPhone 14 Plus", "iPhone 14 Pro", "iPhone 14 Pro Max",
    "iPhone 15", "iPhone 15 Plus", "iPhone 15 Pro", "iPhone 15 Pro Max",
    "iPhone 16", "iPhone 16 Pro", "iPhone 16 Pro Max"
]
MODELE_PS = [
    "PlayStation 3", "PS3", "PlayStation 4", "PS4", "PlayStation 4 Pro", "PS4 Pro",
    "PlayStation 5", "PS5", "PS5 Digital", "PS5 Slim"
]
MODELE_XBOX = [
    "Xbox One", "Xbox One S", "Xbox One X", "Xbox Series S", "Xbox Series X"
]
MODELE_MACBOOK = [
    "MacBook Air 2021", "MacBook Air M1", "MacBook Air 2022", "MacBook Air M2",
    "MacBook Air 2023", "MacBook Air M3", "MacBook Pro 2021", "MacBook Pro M1 Pro",
    "MacBook Pro 2022", "MacBook Pro M2 Pro", "MacBook Pro 2023", "MacBook Pro M3 Pro"
]

SPRZETY = ["iPhone", "PS", "PlayStation", "Xbox", "MacBook"]

EMOJI = {
    "iPhone": "📱",
    "PS": "🎮",
    "PlayStation": "🎮",
    "Xbox": "🎮",
    "MacBook": "💻",
    "money": "💸",
    "plus": "🟢",
    "minus": "🔴",
    "offer": "📰",
    "distance": "🗺️",
    "search": "🔎"
}

class UserState:
    def __init__(self):
        self.step = 0
        self.woj = None
        self.miasto = None
        self.powiat = None
        self.typ = None
        self.model = None
        self.cena = None
        self.miejscowosc_zakupu = None

def reset_user(user_id):
    if user_id in user_states:
        del user_states[user_id]

def get_recent_offers(offers, days=7):
    now = datetime.datetime.now()
    return [
        offer for offer in offers
        if "date" in offer and (now - offer["date"]).days <= days
    ] or offers  # Jeśli brak daty - bierz wszystko

def analiza_ofert(oferty, cena_usera):
    ceny = [o["price"] for o in oferty if isinstance(o["price"], (int, float))]
    if not ceny:
        return None
    sr = mean(ceny)
    mn = min(ceny)
    mx = max(ceny)
    med = median(ceny)
    n = len(ceny)
    zysk = sr - cena_usera
    zwrot = (zysk / cena_usera) * 100 if cena_usera else 0
    return {
        "srednia": sr,
        "min": mn,
        "max": mx,
        "mediana": med,
        "liczba": n,
        "zysk": zysk,
        "zwrot": zwrot
    }

def oferta_embed(state, analiza, oferty, dystans_km):
    typ_emoji = EMOJI.get(state.typ.capitalize(), "")
    msg = f"{typ_emoji} **{state.model}**\n"
    msg += f"{EMOJI['distance']} Odległość: **{dystans_km} km**\n\n"
    msg += f"**Statystyki z ostatnich 7 dni:**\n"
    msg += f"{EMOJI['offer']} Liczba ofert: **{analiza['liczba']}**\n"
    msg += f"{EMOJI['money']} Średnia cena: **{int(analiza['srednia'])} zł**\n"
    msg += f"⬇️ Najniższa: **{int(analiza['min'])} zł**\n"
    msg += f"⬆️ Najwyższa: **{int(analiza['max'])} zł**\n"
    msg += f"📊 Mediana: **{int(analiza['mediana'])} zł**\n\n"
    zysk_emoji = EMOJI['plus'] if analiza['zysk'] >= 0 else EMOJI['minus']
    msg += f"**Twoja cena:** `{int(state.cena)} zł`\n"
    msg += f"**Potencjalny zysk/strata:** {zysk_emoji} `{int(analiza['zysk'])} zł` ({analiza['zwrot']:.1f}%)\n"
    if analiza['zysk'] >= 0:
        msg += "✅ **Opłaca się flipować!**"
    else:
        msg += "⚠️ **Mało opłacalne lub strata!**"

    if oferty:
        msg += "\n\n**Najlepsze oferty:**\n"
        for o in sorted(oferty, key=lambda x: x["price"])[:3]:
            price = int(o["price"])
            msg += f"[{o.get('title', 'Oferta')}]({o.get('link')}) — `{price} zł`\n"
    return msg

def model_podpowiedz(typ):
    if "iphone" in typ.lower():
        return ", ".join(MODELE_IPHONE)
    if "ps" in typ.lower() or "playstation" in typ.lower():
        return ", ".join(MODELE_PS)
    if "xbox" in typ.lower():
        return ", ".join(MODELE_XBOX)
    if "macbook" in typ.lower():
        return ", ".join(MODELE_MACBOOK)
    return ""

def czy_poprawny_model(typ, model):
    if "iphone" in typ.lower():
        return any(m.lower() in model.lower() for m in MODELE_IPHONE)
    if "ps" in typ.lower() or "playstation" in typ.lower():
        return any(m.lower() in model.lower() for m in MODELE_PS)
    if "xbox" in typ.lower():
        return any(m.lower() in model.lower() for m in MODELE_XBOX)
    if "macbook" in typ.lower():
        return any(m.lower() in model.lower() for m in MODELE_MACBOOK)
    return False

def init_commands(bot):
    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return

        # KOMENDA /help
        if message.content.strip().lower() in ["/help", "!help", "help"]:
            help_text = (
                "**Komendy FlipBot:**\n"
                "`/start` - Rozpocznij analizę opłacalności flipu.\n"
                "`/help` - Wyświetl tę pomoc.\n"
                "\nPrzebieg wywiadu krok po kroku:\n"
                "1. Podaj województwo\n"
                "2. Podaj miejscowość\n"
                "3. Wybierz typ sprzętu (iPhone, PS, Xbox, MacBook)\n"
                "4. Podaj dokładny model\n"
                "5. Podaj cenę zakupu\n"
                "6. Podaj miejscowość zakupu\n"
                "7. Otrzymasz analizę opłacalności flipu (średnie ceny, zysk, dystans)\n"
                "\nMożesz przerwać w dowolnym momencie, rozpoczynając od nowa komendą `/start` na serwerze."
            )
            await message.channel.send(help_text)
            return

        # START tylko na publicznym kanale
        if message.guild and message.content.strip().lower() == "/start":
            await message.author.send("Podaj swoje województwo:")
            user_states[message.author.id] = UserState()
            await message.channel.send(
                f"{message.author.mention}, wywiad przeniesiony do DM! Sprawdź prywatną wiadomość."
            )
            return

        # DM - kolejne kroki wywiadu
        if isinstance(message.channel, discord.DMChannel):
            user_id = message.author.id
            if user_id in user_states:
                state = user_states[user_id]

                if state.step == 0:
                    state.woj = message.content.strip()
                    state.step += 1
                    await message.channel.send("Podaj swoją miejscowość:")
                    return

                if state.step == 1:
                    state.miasto = message.content.strip()
                    powiat = get_powiat_city_for(state.miasto, state.woj)
                    if powiat:
                        state.powiat = powiat
                        await message.channel.send(
                            f"Analiza będzie prowadzona od miasta powiatowego: **{powiat}** (promień 55 km)."
                        )
                    else:
                        state.powiat = state.miasto
                    state.step += 1
                    await message.channel.send(
                        "Co chcesz kupić? (iPhone, PS, Xbox, MacBook)"
                    )
                    return

                if state.step == 2:
                    typ = message.content.strip().lower()
                    if any(t.lower() in typ for t in SPRZETY):
                        state.typ = typ
                        state.step += 1
                        podpowiedz = model_podpowiedz(typ)
                        await message.channel.send(
                            f"Podaj dokładny model ({typ}) (np. iPhone 13 Pro 256GB, PS5 Digital, MacBook Air M2, Xbox Series X):\n"
                            f"*Dostępne modele:*\n{podpowiedz}"
                        )
                        return
                    else:
                        await message.channel.send(
                            "Podaj tylko jeden z typów: iPhone, PS, Xbox, MacBook."
                        )
                        return

                if state.step == 3:
                    state.model = message.content.strip()
                    if not czy_poprawny_model(state.typ, state.model):
                        podpowiedz = model_podpowiedz(state.typ)
                        await message.channel.send(
                            f"Nie rozpoznano modelu! Podaj jeden z dostępnych:\n{podpowiedz}"
                        )
                        return
                    state.step += 1
                    await message.channel.send("Podaj cenę zakupu (liczba, zł):")
                    return

                if state.step == 4:
                    try:
                        state.cena = int(message.content.strip())
                        state.step += 1
                        await message.channel.send(
                            "Podaj miejscowość, w której chcesz dokonać zakupu (skąd jest sprzedający):"
                        )
                    except ValueError:
                        await message.channel.send("Podaj cenę jako liczbę, np. 1200!")
                    return

                if state.step == 5:
                    state.miejscowosc_zakupu = message.content.strip()
                    dystans_km = calculate_distance_km(state.miasto, state.miejscowosc_zakupu)
                    await message.channel.send(
                        f"{EMOJI['distance']} Odległość od Ciebie do sprzedającego: **{dystans_km} km**"
                    )

                    # -- ANALIZA CEN --
                    await message.channel.send(f"{EMOJI['search']} Analizuję rynek... To może potrwać chwilę.")

                    # Pobierz oferty z OLX i Vinted
                    olx_offers = await get_olx_offers(state.model, state.powiat, radius_km=55)
                    vinted_offers = await get_vinted_offers(state.model, state.powiat, radius_km=55)
                    all_offers = (olx_offers or []) + (vinted_offers or [])

                    # Filtruj z ostatnich 7 dni
                    recent_offers = get_recent_offers(all_offers, days=7)

                    if not recent_offers:
                        await message.channel.send("Brak świeżych ofert z ostatnich 7 dni dla tego modelu w okolicy.")
                        reset_user(user_id)
                        return

                    analiza = analiza_ofert(recent_offers, state.cena)
                    if not analiza:
                        await message.channel.send("Nie udało się policzyć statystyk — brak cen.")
                        reset_user(user_id)
                        return

                    msg = oferta_embed(state, analiza, recent_offers, dystans_km)
                    await message.channel.send(msg)

                    await message.channel.send(
                        "Dziękuję za skorzystanie z FlipBot!\nJeśli chcesz przeprowadzić kolejną analizę, wpisz `/start` na serwerze.\nAby zobaczyć listę komend, wpisz `/help`."
                    )
                    reset_user(user_id)
                    return

        await bot.process_commands(message)

