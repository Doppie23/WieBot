import asyncio
import random

import discord

from utils.scoresUtils import getPlayerIDS, getPunten, setPunten


class Horse:
    def __init__(self, probability: list[int], naam: str) -> None:
        self.ratioProbs = probability
        self.PercentageDone = 0
        self.finished = False
        self.naam = naam

    def MoveForward(self) -> None:
        rand_distance = random.random()
        distance = rand_distance*10 + self._randomBonus()
        self.PercentageDone = round((self.PercentageDone + distance), 1)
        self._CheckFinished()

    def _randomBonus(self):
        ratio = self.ratioProbs
        kans = [False]*ratio[1]
        for i in range(ratio[0]):
            kans[i-1] = True
        isBonus = random.choice(kans)
        if isBonus:
            return ratio[1]*0.1
        else:
            return 0.0

    def _CheckFinished(self) -> None:
        if self.PercentageDone >= 100:
            self.PercentageDone = 100
            self.finished = True
        else:
            pass

    def getNaamMetKansen(self) -> str:
        # "🐴 Rappe Riko | 1/3"
        return f"🐴 {self.naam} | {self.ratioProbs[0]}/{self.ratioProbs[1]}"

class MultiplayerPaarden:
    def __init__(self, paarden: list[Horse]) -> None:
        self.RaceJoinable = False
        self.paarden = paarden
        pass

    def initRace(self, interaction: discord.Interaction):
        self.RaceJoinable = True
        self._reinithorses()

        self.SpelersNodigVoorStart = getPlayerIDS()
        self.SpelersInSpel = {} # {"PlayerID": "[Inzet: Horse, punten]"}
        self.RaceBericht: discord.Message | None = None

        self.InitInteraction = interaction
        self.timerTask = asyncio.create_task(self.TimerVoorStartBericht())

    def _reinithorses(self):
        for paard in self.paarden:
            paard.__init__(paard.ratioProbs, paard.naam)

    async def TimerVoorStartBericht(self):
        def geefpuntenterug():
            for playerID in self.SpelersInSpel:
                setPunten(playerID, getPunten(playerID) + self.SpelersInSpel[playerID][1])

        await asyncio.sleep(180)
        await self.UpdateWachtenOpSpelersScherm(discord.Colour.blue(), "Niet genoeg spelers om de race te starten.")
        self.RaceJoinable = False
        await asyncio.sleep(4)
        await self.InitInteraction.delete_original_response()
        geefpuntenterug()
        self.timerTask.cancel()


    async def UpdateWachtenOpSpelersScherm(self, kleur: discord.Colour | None = None, description = "Wachten tot iedereen is gejoined..."):
        def GenerateWachtEmbed(kleur, description) -> discord.Embed:
            if kleur == None:
                kleur = discord.Colour.red()
            embed = discord.Embed(title=f'Paarden Race | {len(self.SpelersInSpel)}/{len(self.SpelersNodigVoorStart)} spelers', description=description, color=kleur)
            for spelerID in self.SpelersInSpel:
                PLayerName = self.InitInteraction.client.get_user(int(spelerID)).display_name
                inzetPaard, InzetPunten = self.SpelersInSpel[spelerID]
                ratio = inzetPaard.ratioProbs
                embed.add_field(name=PLayerName, value=f"🐴 {inzetPaard.naam} | {ratio[0]}/{ratio[1]} - {InzetPunten} punten", inline=False)
            return embed
        embed = GenerateWachtEmbed(kleur, description)
        if not self.InitInteraction.response.is_done():
            self.SpelerJoinBericht = await self.InitInteraction.response.send_message(embed=embed)
        else:
            bericht = await self.InitInteraction.original_response()
            await bericht.edit(embed=embed)

    async def JoinSpeler(self, PlayerID: str, PaardNaam, inzet):
        def GetPaardObject(PaardNaam):
            for paard in self.paarden:
                if paard.naam == PaardNaam:
                    return paard
                
        setPunten(PlayerID, getPunten(PlayerID) - inzet)
        self.SpelersInSpel[PlayerID] = [GetPaardObject(PaardNaam), inzet]
        await self.UpdateWachtenOpSpelersScherm()
        if self.CheckIfSpelKanStarten():
            self.RaceJoinable = False
            for i in [3,2,1,0]:
                if i == 0:
                    description = "Race is begonnen!"
                else:
                    description = f"Race start in {i} seconden"
                await self.UpdateWachtenOpSpelersScherm(discord.Colour.green(), description)
                if i != 0:
                    await asyncio.sleep(1)
            await self.StartSpel()

    def CheckIfSpelKanStarten(self) -> bool:
        for spelerIDNodig in self.SpelersNodigVoorStart:
            if not spelerIDNodig in self.SpelersInSpel:
                return False
        return True
    
    async def StartSpel(self):
        self.timerTask.cancel()

        embed = self.GenPaardenEmbed()
        self.RaceBericht = await self.InitInteraction.channel.send(embed=embed)
        winnendepaard = await self.HorseGame()
        await self.RegelWinnerPunten(winnendepaard)

    async def RegelWinnerPunten(self, winnendePaard: Horse):
        for SpelerID in self.SpelersInSpel:
            paard = self.SpelersInSpel[SpelerID][0]
            inzet = self.SpelersInSpel[SpelerID][1]
            if paard.naam == winnendePaard.naam:
                ratio = paard.ratioProbs[1]
                puntenerbij = inzet*ratio
                setPunten(SpelerID, getPunten(SpelerID) + puntenerbij)
                spelertag = self.InitInteraction.client.get_user(int(SpelerID)).mention
                await self.InitInteraction.channel.send(f"{spelertag} heeft {puntenerbij - inzet} gewonnen!")

    async def HorseGame(self):
        message = self.RaceBericht
        while True:
            for paard in self.paarden:
                paard.MoveForward()
                if paard.finished:
                    embed = self.GenPaardenEmbed()
                    await message.edit(embed=embed)
                    return paard
            embed = self.GenPaardenEmbed()
            await message.edit(embed=embed)
            await asyncio.sleep(1)

    def GenPaardenEmbed(self):
        embed = discord.Embed(title=f'Paarden Race', color=discord.Colour.dark_green())
        self.paarden.sort(key=lambda x: x.PercentageDone, reverse=True)
        positie = 1
        for paard in self.paarden:
            value = f"{paard.PercentageDone}%"
            if paard.finished:
                value += " 🏁"
            ratio = paard.ratioProbs
            name = f"{positie} - 🐴 {paard.naam} | {ratio[0]}/{ratio[1]}"
            positie +=1
            embed.add_field(name=name, value=value, inline=False)
        return embed
    