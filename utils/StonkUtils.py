import aiohttp
import discord
from utils.scoresUtils import getPunten, setPunten
import json

link = "http://192.168.2.48:8000"


async def getPrice(bedrijf) -> int:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{link}/CurrentPrice", json={"bedrijf": bedrijf}) as response:
            htmltext = await response.text()
    return int(htmltext)


async def getBedrijven() -> list:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{link}/bedrijven") as response:
            htmltext = await response.json()
    return htmltext


async def getLaatsteUur(bedrijf) -> list:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{link}/LaatsteUur", json={"bedrijf": bedrijf}) as response:
            htmltext = await response.json()
    return htmltext


async def getLaatsteDag(bedrijf) -> list:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{link}/LaatsteDag", json={"bedrijf": bedrijf}) as response:
            htmltext = await response.json()
    return htmltext


def GenoegGeld(userID: str, TotalePrijs: int) -> bool:
    punten = getPunten(userID)
    if punten >= TotalePrijs:
        return True
    else:
        return False


def AddToPortemonnee(userID: str, bedrijf: str, amount: int):
    with open("stonks/stonks.json") as f:
        data = json.load(f)
    if bedrijf in data["bedrijven"]:
        data["bedrijven"][bedrijf] -= amount
    else:
        data["bedrijven"][bedrijf] = 100 - amount

    if userID in data["portemonnees"]:
        if bedrijf in data["portemonnees"][userID]:
            data["portemonnees"][userID][bedrijf] += amount
        else:
            data["portemonnees"][userID][bedrijf] = amount
    else:
        data["portemonnees"][userID] = {bedrijf: amount}

    if data["portemonnees"][userID][bedrijf] == 0:
        del data["portemonnees"][userID][bedrijf]

    with open("stonks/stonks.json", "w") as f:
        json.dump(data, f, indent=2)


def Stonkbeschikbaar(bedrijf: str, amount: int) -> bool:
    with open("stonks/stonks.json") as f:
        data = json.load(f)
    if not bedrijf in data["bedrijven"]:
        data["bedrijven"][bedrijf] = 100
        return True
    else:
        hoeveelheid = data["bedrijven"][bedrijf]
        if amount > hoeveelheid:
            return False
        else:
            return True


async def BuyStonks(userID: str, bedrijf: str, amount: int):
    if not bedrijf in await getBedrijven():
        return False, None
    prijs = await getPrice(bedrijf)
    if not GenoegGeld(userID, prijs * amount):
        return False, None
    if not Stonkbeschikbaar(bedrijf, amount):
        return False, None

    AddToPortemonnee(userID, bedrijf, amount)
    setPunten(userID, getPunten(userID) - prijs * amount)
    return True, prijs * amount


def getPortemonnee(userID: str) -> dict:
    with open("stonks/stonks.json") as f:
        data = json.load(f)
    return data["portemonnees"][userID]


async def SellStonks(userID: str, bedrijf: str, amount: int) -> bool:
    if not bedrijf in await getBedrijven():
        return False, None
    prijs = await getPrice(bedrijf)
    if not bedrijf in getPortemonnee(userID):
        return False, None
    if not amount <= getPortemonnee(userID)[bedrijf]:
        return False, None
    AddToPortemonnee(userID, bedrijf, -amount)
    setPunten(userID, getPunten(userID) + prijs * amount)
    return True, prijs * amount


# embeds
async def embedPortemonnee(userID: str) -> discord.Embed:
    embed = discord.Embed(title=f"Portomonnee", color=discord.Colour.blue())
    portomonnee = getPortemonnee(userID)
    if len(portomonnee) == 0:
        return embed
    totalewaarde = 0
    for bedrijf in portomonnee:
        if portomonnee[bedrijf] == 0:
            continue
        prijs = await getPrice(bedrijf)
        embed.add_field(name=bedrijf, value=f"{portomonnee[bedrijf]} aandelen | Huidige prijs: {prijs}", inline=False)
        totalewaarde += portomonnee[bedrijf] * prijs
    embed.title = f"Portomonnee | Totale waarde: {totalewaarde}"
    return embed


def createStringfromList(list):
    return ", ".join(map(str, list))


def getData(bedrijf):
    with open("stonks/stonks.json") as f:
        data = json.load(f)
    if not bedrijf in data["bedrijven"]:
        data["bedrijven"][bedrijf] = 100
        with open("stonks/stonks.json", "w") as f:
            json.dump(data, f, indent=2)
    return data


async def embedCurrentPrice(bedrijf: str):
    embed = discord.Embed(title=f"{bedrijf} | Info", color=discord.Colour.blue())
    embed.add_field(name="Prijs per aandeel momenteel", value=f"{await getPrice(bedrijf)}", inline=False)
    data = getData(bedrijf)
    aandelenbesackibaar = data["bedrijven"][bedrijf]
    embed.add_field(name="Aantal aandelen beschikbaar", value=f"{aandelenbesackibaar}", inline=False)
    embed.add_field(
        name="Spreadsheet", value="https://docs.google.com/spreadsheets/d/14glUJeNNB-EiyI9fsyGGpX6CWwfgVWTlAcO0qf4JdDI/edit?usp=sharing", inline=False
    )
    # prijsuur = createStringfromList(await getLaatsteUur(bedrijf))
    # embed.add_field(name="Prijs laatste uur", value=f"{prijsuur}", inline=False)
    # prijsdag = createStringfromList(await getLaatsteDag(bedrijf))
    # embed.add_field(name="Prijs laatste 24 uur", value=f"{prijsdag}", inline=False)
    return embed


async def embedKoers():
    embed = discord.Embed(title="Koers", color=discord.Colour.blue())
    bedrijven = await getBedrijven()
    for bedrijf in bedrijven:
        data = getData(bedrijf)
        embed.add_field(name=bedrijf, value=f"Prijs: {await getPrice(bedrijf)} | Aandelen beschikbaar: {data['bedrijven'][bedrijf]}", inline=False)
    return embed


async def SellAllButtonView(userID: str):
    async def SellAll(interaction: discord.Interaction):
        if str(interaction.user.id) != userID:
            await interaction.response.send_message("gsat is niet jouw knop", ephemeral=True)
            return
        portomonnee = getPortemonnee(userID)
        for bedrijf in portomonnee:
            await SellStonks(userID, bedrijf, portomonnee[bedrijf])
        await interaction.response.defer()

    view = discord.ui.View()
    button = discord.ui.Button(label="Verkoop alles", style=discord.ButtonStyle.red)
    button.callback = SellAll
    view.add_item(button)
    return view
