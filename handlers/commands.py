import discord
from scraper.olx import get_olx_offers
from scraper.vinted import get_vinted_offers
from utils.geo import get_powiat_city_for, calculate_distance_km

user_states = {}

SPRZETY = ["iPhone", "PS", "Xbox", "MacBook"]

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
                        await message.channel.send(
                            f"Podaj dokładny model ({typ}) (np. iPhone 13 Pro 256GB, PS5 Digital, MacBook Air M2, Xbox Series X):"
                        )
                        return
                    else:
                        await message.channel.send(
                            "Podaj tylko jeden z typów: iPhone, PS, Xbox, MacBook."
                        )
                        return

                if state.step == 3:
                    state.model = message.content.strip()
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
                        f"Odległość od Ciebie do sprzedającego: **{dystans_km} km**"
                    )
                    await message.channel.send(
                        "Dziękuję za skorzystanie z FlipBot!\nJeśli chcesz przeprowadzić kolejną analizę, wpisz `/start` na serwerze.\nAby zobaczyć listę komend, wpisz `/help`."
                    )
                    reset_user(user_id)
                    return

        await bot.process_commands(message)

