import asyncio
import json
import random
import discord


# standaard json functies
def getdata() -> object:
    with open("scores/scores.json") as f:
        data = json.load(f)
    return data


def writedata(data: object) -> None:
    with open("scores/scores.json", "w") as f:
        json.dump(data, f, indent=2)


def getPunten(userID: str) -> int:
    data = getdata()
    return data[userID]


def setPunten(userID: str, punten: int) -> None:
    data = getdata()
    data[userID] = punten
    writedata(data)


def GenoegPunten(userID: str, puntenNodig: int) -> bool:
    punten = getPunten(userID)
    if punten >= puntenNodig:
        return True
    else:
        return False


def ScoreBijVoorLaatsteLeaven(UserID, score: int, Positief: bool) -> None:
    data = getdata()
    oudescore = data[UserID]
    if Positief:
        data[UserID] = oudescore + score
    elif not Positief:
        data[UserID] = oudescore - score
    writedata(data)


def CheckIfUserExists(UserID: str) -> bool:
    data = getdata()
    if UserID in data:
        return True
    else:
        return False


def Leaderboard_rng():
    def SortJSON():
        data = getdata()
        gebruikers = []
        score = []
        for UserID in data:
            gebruikers.append(UserID)
            score.append(data[UserID])

        score_sorted, userIDS_sorted = (
            list(t) for t in zip(*sorted(zip(score, gebruikers), reverse=True))
        )
        return score_sorted, userIDS_sorted

    Leaderboard = {}
    score_sorted, userIDS_sorted = SortJSON()
    for i in range(len(userIDS_sorted)):
        UserID = userIDS_sorted[i]
        Userscore = score_sorted[i]
        Leaderboard[UserID] = Userscore
    return Leaderboard


def getPlayerIDS() -> list[str]:
    data = getdata()
    playerids = []
    for playerid in data:
        playerids.append(playerid)
    return playerids


def IedereenDieMeedoetIncall(UserIDSincall: list) -> bool:
    gameSpelers = getPlayerIDS()
    for gameSpeler in gameSpelers:
        if gameSpeler in UserIDSincall:
            continue
        else:
            return False
    return True


# spel functies
def steel(userID: str, TargetID: str) -> bool:
    data = getdata()

    userpunten = data[userID]
    targetpunten = data[TargetID]
    if userpunten < 0:
        userpunten = 0
    if targetpunten < 0:
        targetpunten = 0

    winnaarID = random.choices(
        population=[userID, TargetID],
        weights=[
            targetpunten,
            userpunten,
        ],  # bij weinig punten heb je nu meer kans om te winnen
    )[0]

    if userpunten >= targetpunten:
        puntenFraction = round(targetpunten / userpunten, 2)
    else:
        puntenFraction = round(userpunten / targetpunten, 2)
    puntenFraction = (
        1 - puntenFraction
    )  # om het systeem om te draaien, als je veel punten heb steel je minder van kleine spelers

    puntenErbij = round(data[TargetID] * puntenFraction)
    puntenErbij = round(puntenErbij * 0.3)

    if winnaarID == userID:  # steel gelukt
        setPunten(winnaarID, data[winnaarID] + puntenErbij)
        setPunten(TargetID, data[TargetID] - puntenErbij)
        return True, puntenErbij
    else:  # steel mislukt, en dus als boete 2x wat je zou hebben gestolen
        boete = puntenErbij * 2
        setPunten(userID, data[userID] - boete)
        return False, boete


def embedRoulette(
    interaction: discord.Interaction,
    outcome,
    winnings,
    bet_amount,
    bet_type_name,
    nummer,
):
    embed = discord.Embed(
        title=f"Roulette",
        color=discord.Colour.red(),
        description=f"{interaction.user.display_name} heeft ingezet op ",
    )
    if nummer != None:
        embed.description += f"nummer {nummer}."
    else:
        embed.description += f"{bet_type_name}."

    if winnings == 0:
        value = f"Je hebt {bet_amount} punten verloren"
    else:
        embed.color = discord.Colour.green()
        value = f"Je hebt {winnings} punten gewonnen."
    embed.add_field(name=f"🎲 De uitkomst was {outcome}", value=value, inline=False)
    return embed


def rouletteGame(bet_amount: int, bet_type: str, bet_value, outcome=None):
    # Define the possible outcomes and their corresponding odds
    # fmt: off
    outcomes = ['0', '00', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36']
    # fmt: off
    odds = [1, 1, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35]
    
    # Get a random outcome based on the odds
    if outcome == None:
        outcome = random.choices(outcomes, weights=odds)[0]

    # Determine the payout based on the bet type and value
    payout = 0
    if bet_type == "number" and str(bet_value) == outcome:
        payout = 35
    elif (
        bet_type == "even"
        and outcome != "0"
        and outcome != "00"
        and int(outcome) % 2 == 0
    ):
        payout = 1
    elif (
        bet_type == "odd"
        and outcome != "0"
        and outcome != "00"
        and int(outcome) % 2 != 0
    ):
        payout = 1

    # Calculate the winnings and return the outcome and winnings
    winnings = bet_amount * payout
    return (outcome, winnings)


def roulette(userID: str, bet_amount: int, bet_type: str, bet_value, outcome=None):
    data = getdata()

    outcome, winnings = rouletteGame(bet_amount, bet_type, bet_value, outcome)
    if winnings > 0:
        score = data[userID] + winnings
        data[userID] = score
    elif winnings == 0:
        score = data[userID] - bet_amount
        data[userID] = score
    writedata(data)
    return outcome, winnings


class RouletteDoubleOrNothing(discord.ui.Modal, title="Double or Nothing"):
    bet_type = discord.ui.TextInput(
        label="Inzet",
        placeholder='Waar zet je op in? type: "Even", "Oneven" of "Getal"',
        style=discord.TextStyle.short,
        required=True,
    )
    getal = discord.ui.TextInput(
        label="Getal",
        placeholder="Als je op een getal inzet geef dat getal dan hier op.",
        style=discord.TextStyle.short,
        required=False,
    )
    bet_amount = 0
    outcome = None

    async def on_submit(self, interaction: discord.Interaction):
        bet_type = self.bet_type.value
        nummer = None
        if bet_type.lower() == "getal":
            bet_type = "number"
            bet_type_name = "Nummer"
            nummer = self.getal.value
        elif bet_type.lower() == "even":
            bet_type = "even"
            bet_type_name = "Even"
        elif bet_type.lower() == "oneven":
            bet_type = "odd"
            bet_type_name = "Oneven"
        else:
            await interaction.response.send_message(
                f"{bet_type} is geen optie.", ephemeral=True
            )
            return

        outcome, winnings = roulette(
            str(interaction.user.id), self.bet_amount, bet_type, nummer, self.outcome
        )
        embed = embedRoulette(
            interaction, outcome, winnings, self.bet_amount, bet_type_name, nummer
        )
        await interaction.response.send_message(embed=embed)
        if winnings != 0:
            self.bet_amount *= 2
            DoubleRouletteVraag = RouletteDoubleOrNothingVraag(
                interaction=interaction, bet_amount=self.bet_amount
            )
            await interaction.channel.send(
                f"Double or nothing met {self.bet_amount} punten?",
                view=DoubleRouletteVraag,
            )


class RouletteDoubleOrNothingVraag(discord.ui.View):
    def __init__(self, *, timeout=180, interaction: discord.Interaction, bet_amount):
        super().__init__(timeout=timeout)
        self.interaction = interaction
        self.Spelernaam = interaction.user.display_name
        self.bet_amount = bet_amount

    @discord.ui.button(label="Ja", style=discord.ButtonStyle.primary)
    async def Ja(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.display_name == self.Spelernaam:
            outcome, _ = rouletteGame(0, "even", None, None)
            print("uitkomst:", outcome)
            uiopties = RouletteDoubleOrNothing()
            uiopties.bet_amount = self.bet_amount
            uiopties.outcome = outcome
            await interaction.response.send_modal(uiopties)
            await interaction.message.delete()
        else:
            await interaction.response.send_message("Gsat rot op", ephemeral=True)

    @discord.ui.button(label="Nee", style=discord.ButtonStyle.secondary)
    async def Nee(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.display_name == self.Spelernaam:
            await interaction.response.defer()
            await interaction.message.delete()
        else:
            await interaction.response.send_message("Gsat rot op", ephemeral=True)


def trinna(UserID: str, bet_amount: int):
    data = getdata()
    # punten eraf
    data[UserID] -= bet_amount

    dobbel_opties = ["🚂", "🚿", "💡", "🛂", "🚗", "💍"]

    uitkomsten = []
    for _ in range(3):
        uitkomst = random.choice(dobbel_opties)
        uitkomsten.append(uitkomst)

    aantalKeerTrein = uitkomsten.count("🚂")
    if aantalKeerTrein > 0:
        bet_winst = bet_amount * (2 * aantalKeerTrein)
        data[UserID] += bet_winst
    else:
        bet_winst = 0
    writedata(data)
    return uitkomsten, bet_winst


class luckywheel:
    def __init__(self, RangeGetallen) -> None:
        self.hoofprijsbeschikbaar = True
        self.begin, self.eind = RangeGetallen
        self.opties = self._geneRandomArray()

    def _geneRandomArray(self):
        array = []
        for _ in range(3):
            nummer = self._RandomNieuweGetal()
            array.append(nummer)
        return array

    def _randomnegatief(self, getal):
        Positief = random.choices(population=[True, False], weights=[9, 1])[0]
        if Positief:
            pass
        else:
            getal = getal - 2 * getal  # getal negatief maken
        return getal

    def _RandomNieuweGetal(self):
        if self.hoofprijsbeschikbaar:
            Hoofdprijs = random.choices(population=[False, True], weights=[9, 1])[0]
            if Hoofdprijs:
                self.hoofprijsbeschikbaar = False
                return 500
        getal = random.randrange(self.begin, self.eind, step=5)
        getal = self._randomnegatief(getal)
        return getal

    def VoegGetalToe(self):
        getal = self._RandomNieuweGetal()
        self.opties.insert(0, getal)

    def getDrieNummers(self):
        nummer1 = self.opties[0]
        nummer2 = self.opties[1]
        nummer3 = self.opties[2]
        self.VoegGetalToe()
        return nummer1, nummer2, nummer3

    def getPunten(self) -> int:
        return self.opties[2]


class BlackJack(discord.ui.View):
    def __init__(self, *, timeout=180, inzet, interaction: discord.Interaction):
        super().__init__(timeout=timeout)
        self.inzet = inzet
        self.knopBeschikbaar = True
        self.interaction = interaction

        self.Spelernaam = interaction.user.display_name

        # initialize deck
        suits = ["♥️", "♦️", "♣️", "♠️"]
        values = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        self.deck = [value + suit for suit in suits for value in values]
        random.shuffle(self.deck)

        # initialize player and dealer hands
        self.player_hand = [self.deck.pop(), self.deck.pop()]
        self.dealer_hand = [self.deck.pop(), self.deck.pop()]

        self.DealerHandHidden = [self.dealer_hand[0]]

        self.winner = None

    async def PlayerTurn(self, action: str):
        self.knopBeschikbaar = False
        if action.lower() == "hit":
            self.player_hand.append(self.deck.pop())
            await self.UpdateBericht(f"{self.Spelernaam} hits.")
            if self.sum_card_values(self.player_hand) > 21:
                self.winner = "Dealer"
                await self.UpdateBericht(f"{self.Spelernaam} is gebust. Dealer wint.")
                self.RegelPunten()
                return
            await self.UpdateBericht("Hit of stand?")
            self.knopBeschikbaar = True
        elif action.lower() == "stand":
            await self.UpdateBericht(f"{self.Spelernaam} stands.")
            await self.DealerTurn()
            await self.DetermineWinner()

    async def DealerTurn(self):
        while self.sum_card_values(self.dealer_hand) < 17:
            self.dealer_hand.append(self.deck.pop())
            self.DealerHandHidden = self.dealer_hand
            await self.UpdateBericht("Dealer hits.")
            if self.sum_card_values(self.dealer_hand) > 21:
                self.winner = "Player"
                await self.UpdateBericht(f"Dealer is gebust. {self.Spelernaam} wint.")
                self.RegelPunten()
                return
            await asyncio.sleep(1)

    async def DetermineWinner(self):
        player_score = self.sum_card_values(self.player_hand)
        dealer_score = self.sum_card_values(self.dealer_hand)
        if self.winner == None:  # nog niemand gebust
            if player_score > dealer_score:
                self.winner = "Player"
                await self.UpdateBericht(f"{self.Spelernaam} wint!")
            elif player_score < dealer_score:
                self.winner = "Dealer"
                await self.UpdateBericht("Dealer wint!")
            else:
                self.winner = "niemand"
                await self.UpdateBericht("Het is een gelijkspel!")
            self.RegelPunten()

    def RegelPunten(self):
        data = getdata()
        if self.winner == "Player":
            data[str(self.interaction.user.id)] += self.inzet
        elif self.winner == "niemand":
            pass
        else:
            data[str(self.interaction.user.id)] -= self.inzet
        writedata(data)

    def sum_card_values(self, hand):
        # fmt: off
        values = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "J": 10, "Q": 10, "K": 10, "A": 11}
        total = 0
        num_aces = 0
        for card in hand:
            value = card[:-2]
            if value == "A":
                num_aces += 1
            total += values[value]
        while total > 21 and num_aces > 0:
            total -= 10
            num_aces -= 1
        return total

    async def UpdateBericht(self, actie: str):
        embed = self.GenerateEmbed()
        embed.add_field(name="", value=actie, inline=False)
        message = await self.interaction.original_response()
        await message.edit(embed=embed)

    def GenerateEmbed(self):
        def HandToString(hand):
            string = ""
            i = 0
            while i <= len(hand) - 1:
                if i == (len(hand) - 1):
                    string += f"{hand[i]}"
                else:
                    string += f"{hand[i]},⠀"
                i += 1
            return string

        embed = discord.Embed(
            title=f"Blackjack",
            description=f"{self.interaction.user.display_name} heeft {self.inzet} punten ingezet.",
            color=discord.Colour.brand_red(),
        )
        embed.add_field(
            name="Player hand", value=HandToString(self.player_hand), inline=False
        )
        if self.winner == None:
            Dealerhand = self.DealerHandHidden
        else:
            Dealerhand = self.dealer_hand
        embed.add_field(
            name="Dealer hand", value=HandToString(Dealerhand), inline=False
        )

        return embed

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.primary)
    async def Hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.display_name == self.Spelernaam:
            if self.knopBeschikbaar:
                await self.PlayerTurn("hit")
            await interaction.response.defer()
        else:
            await interaction.channel.send("Gsat rot op", ephemeral=True)

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.secondary)
    async def Stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.display_name == self.Spelernaam:
            if self.knopBeschikbaar:
                await self.PlayerTurn("stand")
            await interaction.response.defer()
        else:
            await interaction.channel.send("Gsat rot op", ephemeral=True)
