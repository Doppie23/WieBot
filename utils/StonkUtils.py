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


async def BuyStonks(userID: str, bedrijf: str, amount: int) -> bool:
    if not bedrijf in await getBedrijven():
        return False
    prijs = await getPrice(bedrijf)
    if not GenoegGeld(userID, prijs * amount):
        return False
    if not Stonkbeschikbaar(bedrijf, amount):
        return False

    AddToPortemonnee(userID, bedrijf, amount)
    setPunten(userID, getPunten(userID) - prijs * amount)
    return True


def getPortemonnee(userID: str) -> dict:
    with open("stonks/stonks.json") as f:
        data = json.load(f)
    return data["portemonnees"][userID]


async def SellStonks(userID: str, bedrijf: str, amount: int) -> bool:
    if not bedrijf in await getBedrijven():
        return False
    prijs = await getPrice(bedrijf)
    if not bedrijf in getPortemonnee(userID):
        return False
    if not amount <= getPortemonnee(userID)[bedrijf]:
        return False
    AddToPortemonnee(userID, bedrijf, -amount)
    setPunten(userID, getPunten(userID) + prijs * amount)
    return True


# embeds
async def embedPortemonnee(userID: str) -> discord.Embed:
    embed = discord.Embed(title=f"Portomonnee", color=discord.Colour.blue())
    portomonnee = getPortemonnee(userID)
    for bedrijf in portomonnee:
        embed.add_field(name=bedrijf, value=f"{portomonnee[bedrijf]} aandelen", inline=False)
    return embed


def createStringfromList(list):
    return ", ".join(map(str, list))


async def embedCurrentPrice(bedrijf: str):
    embed = discord.Embed(title=f"{bedrijf} | Info", color=discord.Colour.blue())
    embed.add_field(name="Prijs per aandeel momenteel", value=f"{await getPrice(bedrijf)}", inline=False)
    with open("stonks/stonks.json") as f:
        data = json.load(f)
    aandelenbesackibaar = data["bedrijven"][bedrijf]
    embed.add_field(name="Aantal aandelen beschikbaar", value=f"{aandelenbesackibaar}", inline=False)
    prijsuur = createStringfromList(await getLaatsteUur(bedrijf))
    embed.add_field(name="Prijs laatste uur", value=f"{prijsuur}", inline=False)
    prijsdag = createStringfromList(await getLaatsteDag(bedrijf))
    embed.add_field(name="Prijs laatste 24 uur", value=f"{prijsdag}", inline=False)
    return embed
