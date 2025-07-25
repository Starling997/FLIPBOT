import discord

async def send_offer_embed(bot, woj, kategoria, offer):
    for guild in bot.guilds:
        category = discord.utils.get(guild.categories, name=woj)
        if not category: continue
        channel = discord.utils.get(category.channels, name=kategoria)
        if not channel: continue
        embed = discord.Embed(
            title=offer["title"],
            description=f'{offer["portal"]}\nCena: {offer["price"]} zł\n{offer["link"]}',
            color=discord.Color.blue()
        )
        if offer["img"]:
            embed.set_thumbnail(url=offer["img"])
        embed.add_field(name="Miasto", value=offer["location"])
        await channel.send(embed=embed)

async def move_to_archive(bot, offer, archive_channel_name):
    for guild in bot.guilds:
        channel = discord.utils.get(guild.text_channels, name=archive_channel_name)
        if not channel: continue
        embed = discord.Embed(
            title="[ARCHIWUM] " + offer["title"],
            description=f'{offer["portal"]}\nCena: {offer["price"]} zł\n{offer["link"]}',
            color=discord.Color.dark_grey()
        )
        if offer["img"]:
            embed.set_thumbnail(url=offer["img"])
        embed.add_field(name="Miasto", value=offer["location"])
        await channel.send(embed=embed)
