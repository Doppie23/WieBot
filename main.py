import os
import random
import re
import traceback
import discord
from discord import app_commands
from dotenv import load_dotenv
from asyncio import sleep
import asyncio
from gtts import gTTS
import json
from TimeoutCommands.Timeout import TimeoutCheck, addTimeoutToCommand
from utils.paarden_utils import Horse, MultiplayerPaarden
from utils.redditpost import randomcopypasta, randomshitpost
from utils.noeputils import totaal_user, meeste_ls, clip_van_gebruiker_met_meeste_ls, add_noep, rem_noep
from utils.summon import Summon
from utils.trackleave import addScoreLaatsteLeave, Leaderboard
from utils.nanogpt_utils import getResponse, getAntwoordzonderPrompt
from utils.scoresUtils import (
    BlackJack,
    RouletteDoubleOrNothingVraag,
    luckywheel,
    steel,
    roulette,
    GenoegPunten,
    Leaderboard_rng,
    getdata,
    getPlayerIDS,
    CheckIfUserExists,
    IedereenDieMeedoetIncall,
    ScoreBijVoorLaatsteLeaven,
    getPunten,
    trinna,
    writedata,
    embedRoulette,
    Donate,
)
from utils.embeds import embedLuckyWheel, embedTrinna, embedOutro
from muziek import muziekspelen

intents = discord.Intents.all()

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
guild = discord.Object(id=659436197457690626)


class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild=guild)
            self.synced = True
        print(f"{self.user} is nu online")
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="You"))


client = aclient()
tree = app_commands.CommandTree(client)
player = muziekspelen()


@tree.command(name="copypasta", description="stuurt een random copypasta van r/copypasta", guild=guild)
async def self(interaction: discord.Interaction):
    copypasta = randomcopypasta()
    leng = len(copypasta)
    while len(copypasta) > 2000:
        print(f"te lange post, reroll {leng}")
        copypasta = randomcopypasta()
    leng = len(copypasta)
    print(f"korte post {leng}")
    await interaction.response.send_message(copypasta)


@tree.command(name="shitpost", description="stuurt een random shitpost van r/shitposting", guild=guild)
async def self(interaction: discord.Interaction):
    shitpost = randomshitpost()
    await interaction.response.send_message(shitpost)


@app_commands.choices(
    choices=[
        app_commands.Choice(name="Crab Rave", value="crabrave"),
        app_commands.Choice(name="Epic Outro", value="outro"),
        app_commands.Choice(name="Royalistiq", value="royalistiq"),
        app_commands.Choice(name="RNG certified", value="rngding"),
    ]
)
@tree.command(name="outro", description="Epic outro", guild=guild)
async def self(interaction: discord.Interaction, choices: app_commands.Choice[str]):
    if choices.value == "crabrave":
        file = "/outro/crab rave kort.wav"
        source = os.getcwd() + file
        bericht = ":crab:"

    elif choices.value == "outro":
        file = "/outro/outro kort.wav"
        source = os.getcwd() + file
        bericht = "SMASH THAT LIKE BUTTON :thumbsup:"

    elif choices.value == "royalistiq":
        file = "/outro/royalistiq.mp3"
        source = os.getcwd() + file
        bericht = "HOOWWH MY DAYS 😱"

    elif choices.value == "rngding":
        voice_channel = interaction.user.voice
        members = voice_channel.channel.members
        incall = []
        for member in members:
            incall.append(str(member.id))

        if IedereenDieMeedoetIncall(incall):
            file = "/outro/royalistiq.mp3"
            source = os.getcwd() + file
            bericht = "RNG Certified 🍀"
        else:
            await interaction.response.send_message("Niet iedereen die meedoet zit in call, dus deze outro kan niet.", ephemeral=True)
            return

    voice_channel = interaction.user.voice
    channel = None
    if voice_channel != None:
        voice_channel = voice_channel.channel
        channel = voice_channel.name
        incall = voice_channel.members
        random.shuffle(incall)
        kick_tasks = []
        member_leave_list = []
        for member in incall:
            kick_tasks.append(kick(member, member_leave_list))
        vc = await voice_channel.connect()
        await interaction.response.send_message(bericht)

        if file == "/outro/outro kort.wav":
            original_message = await interaction.original_response()
            await discord.InteractionMessage.add_reaction(original_message, "👍")
            await discord.InteractionMessage.add_reaction(original_message, "👎")

        vc.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=source))
        while vc.is_playing():
            await sleep(0.1)
        await vc.disconnect(force=True)

        await asyncio.gather(*kick_tasks)

        laatste: discord.Member = member_leave_list[0]
        addScoreLaatsteLeave(str(laatste.id), laatste.name)

        # rng troep score regelen
        if choices.value == "rngding":
            ScoreWaarWeOmspelen = random.randrange(1, 100)
            Positief = random.choices(population=[True, False], weights=[9, 1])[0]
            Multiplier = random.choice(range(10, 100))
            Hoofdprijs = random.choices(population=[False, True], weights=[20, 1])[0]
            if Hoofdprijs:
                Multiplier = 1000
            embed = embedOutro(ScoreWaarWeOmspelen, Positief, Multiplier, laatste)
            await interaction.channel.send(embed=embed)
            ScoreMetMultiplier = ScoreWaarWeOmspelen * Multiplier
            spelers = getPlayerIDS()
            if str(laatste.id) in spelers:
                ScoreBijVoorLaatsteLeaven(str(laatste.id), ScoreMetMultiplier, Positief)
            else:
                await interaction.channel.send(f"{laatste.mention} doet niet mee, niemand krijgt er dus punten bij.")
        else:
            await interaction.channel.send(f"{laatste.mention}")

    else:
        await interaction.response.send_message("Join eerst een spraakkanaal.")


async def kick(member: discord.Member, list: list):
    await member.move_to(None)
    list.insert(0, member)


@tree.command(name="outroleaderboard", description="@boodschapjes", guild=guild)
async def self(interaction: discord.Interaction):
    embed = discord.Embed(title="Vaakst het laatste de call verlaten", color=discord.Colour.random())
    Scorebord = Leaderboard()
    nummer = 1
    for UserID in Scorebord:
        Score = Scorebord[UserID]
        User: discord.User = client.get_user(int(UserID))
        if nummer == 1:
            embed.set_thumbnail(url=User.avatar)
        embed.add_field(name=f"{nummer}: {User.display_name}", value=f"{Score} keer", inline=False)
        nummer += 1

    await interaction.response.send_message(embed=embed)


@tree.command(name="sonnet18", description="big hype", guild=guild)
async def self(interaction: discord.Interaction):
    file = "/sonnet/Hardstyle-sonnet.wav"
    source = os.getcwd() + file
    voice_channel = interaction.user.voice
    if voice_channel != None:
        voice_channel = voice_channel.channel
        vc = await voice_channel.connect()
        await interaction.response.send_message(
            """
        Shall I compare thee to a summer's day?
Thou art more lovely and more temperate.
Rough winds do shake the darling buds of May,
And summer's lease hath all too short a date.
Sometime too hot the eye of heaven shines,
And often is his gold complexion dimmed,
And every fair from fair sometime declines,
By chance or nature's changing course untrimmed;

But thy eternal summer shall not fade

Nor lose possession of that fair thou ow'st,
Nor shall death brag thou wander'st in his shade
When in eternal lines to time thou grow'st.
So long as men can breathe or eyes can see,
So long lives this, and this gives life to thee.
https://tenor.com/view/rave-shuffle-hardstyle-gif-26548943
        """
        )
        vc.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=source))
        while vc.is_playing():
            await sleep(0.1)
        await vc.disconnect(force=True)
    else:
        await interaction.response.send_message("Join eerst een spraakkanaal.")


@tree.command(name="tts", description="tts test", guild=guild)
@app_commands.describe(text="text die bot moet zeggen", channel_id="id van kanaal")
async def self(interaction: discord.Interaction, text: str, channel_id: str):
    voice = interaction.guild.voice_client
    if voice == None:
        channel = client.get_channel(int(channel_id))
        # channel = interaction.user.voice.channel
        await channel.connect()
    voice = interaction.guild.voice_client
    audio = gTTS(text=text, lang="nl", slow=False)
    audio.save("text.mp3")
    voice.play(discord.FFmpegPCMAudio(executable="ffmpeg", source="text.mp3"))
    await interaction.response.send_message(f"zegt nu: {text}", ephemeral=True)


@tree.command(name="vrienden", description="!vrienden", guild=guild)
async def self(interaction: discord.Interaction):
    voice_channel = interaction.user.voice
    channel = None
    if voice_channel != None:
        voice_channel = voice_channel.channel
        channel = voice_channel.name
        incall = voice_channel.members
        vc = await voice_channel.connect()
        await interaction.response.send_message(f"{voice_channel} gejoind", ephemeral=True)
    else:
        await interaction.response.send_message("Join eerst een spraakkanaal.", ephemeral=True)


@tree.command(name="leave", description="leave call", guild=guild)
async def self(interaction: discord.Interaction):
    voice_channel = interaction.guild.voice_client
    if voice_channel != None or voice_channel.is_connected():
        await voice_channel.disconnect(force=True)
        await interaction.response.send_message(":wave:", ephemeral=True)
    else:
        await interaction.response.send_message("Bot zit niet in een kanaal.", ephemeral=True)


@tree.command(name="muziek-quiz", description="Start een muziek quiz.", guild=guild)
@app_commands.describe(
    url="Link naar Spotify playlist. Werkt alleen met een playlist, niet met albums of blends.",
    aantal_nummers="Aantal nummers waar de quiz uit moet bestaan (max 10).",
)
async def self(interaction: discord.Interaction, url: str, aantal_nummers: int):
    if aantal_nummers > 10:
        aantal_nummers = 10
    player.initquiz(interaction, client, url, aantal_nummers)
    voice_channel = interaction.guild.voice_client
    if voice_channel == None or voice_channel.is_connected() != True:
        await player.join()
    await player.start()


@tree.command(name="stop-quiz", description="stopt quiz", guild=guild)
async def self(interaction: discord.Interaction):
    await player.force_quit_quiz(interaction)


def check_if_is_admin(interaction: discord.Interaction) -> bool:
    return interaction.user.id == 327038629585223690


@tree.command(name="add_noep", description="voeg een /noep toe", guild=guild)
@app_commands.check(check_if_is_admin)
async def self(interaction: discord.Interaction, link: str, userid: str):
    add_noep(link, int(userid))
    await interaction.response.send_message(f"{link} is nu een /noep", ephemeral=True)


@tree.command(name="rem_noep", description="remove een /noep toe", guild=guild)
@app_commands.check(check_if_is_admin)
async def self(interaction: discord.Interaction, link: str):
    rem_noep(link)
    await interaction.response.send_message(f"{link} is nu niet meer een /noep", ephemeral=True)


@tree.command(name="noep", description="!noep", guild=guild)
async def self(interaction: discord.Interaction):
    f = open(r"noeps/noep.json")
    noeps = json.load(f)
    clip, user_vote = random.choice(list(noeps.items()))
    user = user_vote[1]
    vote = user_vote[0]
    totaal_l = totaal_user(str(user))
    await interaction.response.send_message(f"{user} heeft al {vote} L's gepakt met deze clip. In totaal heeft {user} al {totaal_l} L's gepakt. {clip}")
    original_message = await interaction.original_response()
    await discord.InteractionMessage.add_reaction(original_message, "🇱")
    f.close()


@tree.command(name="grootste-noep", description="De grootste noeps van iedereen.", guild=guild)
async def self(interaction: discord.Interaction):
    embed = discord.Embed(title="De grootste noeps", color=discord.Colour.random())
    meeste_l_list, meeste_l_list_gebruiker = meeste_ls()
    for i in range(3):
        totaal_ls = meeste_l_list[i]
        totaal_ls_gebruiker = meeste_l_list_gebruiker[i]
        clip, ls_clip = clip_van_gebruiker_met_meeste_ls(totaal_ls_gebruiker)
        userid = totaal_ls_gebruiker[2:-1]
        userob = client.get_user(int(userid))
        if i == 0:
            embed.set_thumbnail(url=userob.avatar)
        nummer = i + 1
        embed.add_field(
            name=f"{nummer}: {userob.display_name} met {totaal_ls} L's in totaal", value=f"De clip met de meeste L's ({ls_clip}) is: {clip}", inline=False
        )

    await interaction.response.send_message(embed=embed)


@tree.command(name="say", description="zeg iets als wiebot", guild=guild)
async def self(interaction: discord.Interaction, say: str):
    await interaction.response.send_message(f"Bericht: {say}", ephemeral=True)
    channel = interaction.channel
    await channel.send(say)


async def users_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    userIDS = getPlayerIDS()
    users = []
    for userID in userIDS:
        user = client.get_user(int(userID))
        if not user == interaction.user:
            users.append(user)
    return [app_commands.Choice(name=user.name, value=str(user.id)) for user in users if current.lower() in user.name.lower()]


@tree.command(name="steel", description="steel punten van iemand anders", guild=guild)
@app_commands.autocomplete(target=users_autocomplete)
async def self(interaction: discord.Interaction, target: str):
    if not json.load(open("scores/gamebezig.json"))["bezig"]:
        await interaction.response.send_message("Spel is niet bezig.", ephemeral=True)
        return
    if await TimeoutCheck(interaction):
        return
    if not CheckIfUserExists(str(interaction.user.id)):
        await interaction.response.send_message(f"Je doet niet mee aan het spel.", ephemeral=True)
        return
    if CheckIfUserExists(target):
        if getPunten(str(target)) <= 0:
            await interaction.response.send_message(f"Je kan niet stelen van iemand met nul of minder punten.", ephemeral=True)
            return

        isGelukt, puntenerbij = steel(str(interaction.user.id), str(target))
        if isGelukt:
            await interaction.response.send_message(
                f"{interaction.user.mention} heeft zojuist {puntenerbij} punten gestolen van {client.get_user(int(target)).mention}."
            )
        elif not isGelukt:
            await interaction.response.send_message(
                f"{interaction.user.mention} probeerde zojuist te stelen van {client.get_user(int(target)).mention}, maar heeft gefaald. Nu moet hij een boete betalen van {puntenerbij} punten."
            )
        addTimeoutToCommand(str(interaction.user.id), interaction.command.name, 43200)
    else:
        await interaction.response.send_message(f"{target} doet niet mee...", ephemeral=True)


@app_commands.choices(
    bet_type=[
        app_commands.Choice(name="Even", value="even"),
        app_commands.Choice(name="Oneven", value="odd"),
        app_commands.Choice(name="Getal", value="number"),
    ]
)
@tree.command(name="roulette", description="rng certified", guild=guild)
async def self(interaction: discord.Interaction, bet_amount: int, bet_type: app_commands.Choice[str], nummer: int = None):
    if not json.load(open("scores/gamebezig.json"))["bezig"]:
        await interaction.response.send_message("Spel is niet bezig.", ephemeral=True)
        return
    # if await TimeoutCheck(interaction):
    #     return
    if bet_amount <= 0:
        await interaction.response.send_message("Je kan niet een negatief aantal of nul punten inzetten.", ephemeral=True)
        return

    # check if wel genoeg punten
    data = getdata()
    if str(interaction.user.id) in data:
        if not GenoegPunten(str(interaction.user.id), bet_amount):
            await interaction.response.send_message("Niet genoeg punten.", ephemeral=True)
            return
    else:
        await interaction.response.send_message("Je doet niet mee aan het spel.", ephemeral=True)
        return
    if bet_type.value != "number" and nummer != None:
        await interaction.response.send_message("Je kan niet een nummer opgeven als je niet op een nummer in wil zetten.", ephemeral=True)
        return
    if bet_type.value == "number" and nummer == None:
        await interaction.response.send_message("Geef ook een nummer op als je op een nummer in wil zetten.", ephemeral=True)
        return

    outcome, winnings = roulette(str(interaction.user.id), bet_amount, bet_type.value, nummer)
    embed = embedRoulette(interaction, outcome, winnings, bet_amount, bet_type.name, nummer)
    await interaction.response.send_message(embed=embed)
    addTimeoutToCommand(str(interaction.user.id), interaction.command.name, 1800)
    if winnings != 0:
        bet_amount += winnings
        DoubleRouletteVraag = RouletteDoubleOrNothingVraag(interaction=interaction, bet_amount=bet_amount)
        await interaction.channel.send(f"Double or nothing met {bet_amount} punten?", view=DoubleRouletteVraag)


@tree.command(name="trinna", description="trinna is altijd goed", guild=guild)
async def self(interaction: discord.Interaction, bet_amount: int):
    if not json.load(open("scores/gamebezig.json"))["bezig"]:
        await interaction.response.send_message("Spel is niet bezig.", ephemeral=True)
        return
    # if await TimeoutCheck(interaction):
    #     return
    if bet_amount <= 0:
        await interaction.response.send_message("Je kan niet een negatief aantal of nul punten inzetten.", ephemeral=True)
        return
    data = getdata()
    if str(interaction.user.id) in data:
        if not GenoegPunten(str(interaction.user.id), bet_amount):
            await interaction.response.send_message("Niet genoeg punten.", ephemeral=True)
            return
    else:
        await interaction.response.send_message("Je doet niet mee aan het spel.", ephemeral=True)
        return

    uitkomsten, bet_winst = trinna(str(interaction.user.id), bet_amount)
    embed = embedTrinna(interaction, bet_winst, bet_amount, uitkomsten)
    await interaction.response.send_message(embed=embed)
    addTimeoutToCommand(str(interaction.user.id), interaction.command.name, 1800)


@tree.command(name="luckywheel", description="Altijd prijs!!!", guild=guild)
async def self(interaction: discord.Interaction):
    if not json.load(open("scores/gamebezig.json"))["bezig"]:
        await interaction.response.send_message("Spel is niet bezig.", ephemeral=True)
        return
    if await TimeoutCheck(interaction):
        return
    data = getdata()
    if str(interaction.user.id) in data:
        wheel = luckywheel([5, 100])
        embed = embedLuckyWheel(wheel)
        await interaction.response.send_message(embed=embed)
        sleeptime = 0.1
        for _ in range(8):
            await asyncio.sleep(sleeptime)
            embed = embedLuckyWheel(wheel)
            message = await interaction.original_response()
            await message.edit(embed=embed)
            sleeptime += 0.05
        punten = wheel.getPunten()
        await interaction.channel.send(f"Je hebt {punten} punten gewonnen.")
        data = getdata()
        userid = str(interaction.user.id)
        data[userid] += punten
        writedata(data)
        addTimeoutToCommand(str(interaction.user.id), interaction.command.name, 43200)
    else:
        await interaction.response.send_message("Je doet niet mee aan het spel.", ephemeral=True)
        return


@tree.command(name="blackjack", description="Unlimited Money Glitch 100% WORKING!!1!", guild=guild)
async def self(interaction: discord.Interaction, bet_amount: int):
    if not json.load(open("scores/gamebezig.json"))["bezig"]:
        await interaction.response.send_message("Spel is niet bezig.", ephemeral=True)
        return
    # if await TimeoutCheck(interaction):
    #     return
    if bet_amount <= 0:
        await interaction.response.send_message("Je kan niet een negatief aantal of nul punten inzetten.", ephemeral=True)
        return
    data = getdata()
    if str(interaction.user.id) in data:
        if not GenoegPunten(str(interaction.user.id), bet_amount):
            await interaction.response.send_message("Niet genoeg punten.", ephemeral=True)
            return
    else:
        await interaction.response.send_message("Je doet niet mee aan het spel.", ephemeral=True)
        return
    blackjack = BlackJack(inzet=bet_amount, interaction=interaction)
    await interaction.response.send_message(view=blackjack.view)
    await blackjack.UpdateBericht("Hit of stand?")
    addTimeoutToCommand(str(interaction.user.id), interaction.command.name, 300)


paarden: list[Horse] = [
    Horse([1, 4], "Rappe Riko"),
    Horse([1, 2], "Leunie(Mike)"),
    Horse([1, 8], "Bartholomeus"),
    Horse([1, 6], "Trappelende Titus"),
    Horse([1, 10], "Karel Galop"),
]
PaardenRace = MultiplayerPaarden(paarden)


@tree.command(name="paardenrace", description="Start de paardenrace.", guild=guild)
async def self(interaction: discord.Interaction):
    if not json.load(open("scores/gamebezig.json"))["bezig"]:
        await interaction.response.send_message("Spel is niet bezig.", ephemeral=True)
        return
    if PaardenRace.RaceJoinable:
        await interaction.response.send_message("Er is al een race gestart!", ephemeral=True)
        return
    PaardenRace.initRace(interaction)
    await PaardenRace.UpdateWachtenOpSpelersScherm()


async def paarden_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    return [app_commands.Choice(name=paard.getNaamMetKansen(), value=paard.naam) for paard in paarden if current.lower() in paard.naam.lower()]


@app_commands.autocomplete(paard=paarden_autocomplete)
@tree.command(name="join-paardenrace", description="join een paardenrace", guild=guild)
async def self(interaction: discord.Interaction, paard: str, inzet: int):
    if not json.load(open("scores/gamebezig.json"))["bezig"]:
        await interaction.response.send_message("Spel is niet bezig.", ephemeral=True)
        return
    if inzet <= 0:
        await interaction.response.send_message("Je kan niet een negatief aantal of nul punten inzetten.", ephemeral=True)
        return
    data = getdata()
    if str(interaction.user.id) in data:
        if not GenoegPunten(str(interaction.user.id), inzet):
            await interaction.response.send_message("Niet genoeg punten.", ephemeral=True)
            return
    if not PaardenRace.RaceJoinable:
        await interaction.response.send_message("Je kan nu geen race joinen...", ephemeral=True)
        return
    if not str(interaction.user.id) in PaardenRace.SpelersNodigVoorStart:
        await interaction.response.send_message("Je kan niet meedoen...", ephemeral=True)
        return
    if str(interaction.user.id) in PaardenRace.SpelersInSpel:
        await interaction.response.send_message("Je doet al mee...", ephemeral=True)
        return
    if paard not in [paard.naam for paard in paarden]:
        await interaction.response.send_message("Dat paard bestaat niet...", ephemeral=True)
        return
    await interaction.response.send_message("Je doet mee!", ephemeral=True)
    await PaardenRace.JoinSpeler(str(interaction.user.id), paard, inzet)


@tree.command(name="scorebord_rng_certified", description="rng certified", guild=guild)
async def self(interaction: discord.Interaction):
    embed = discord.Embed(title="Beste RNG", color=discord.Colour.random())
    Scorebord = Leaderboard_rng()
    nummer = 1
    for UserID in Scorebord:
        Score = Scorebord[UserID]
        User: discord.User = client.get_user(int(UserID))
        if nummer == 1:
            embed.set_thumbnail(url=User.avatar)
        embed.add_field(name=f"{nummer}: {User.display_name}", value=f"{Score} punten", inline=False)
        nummer += 1

    await interaction.response.send_message(embed=embed)


@tree.command(name="donate", description="doneer punten aan iemand anders.", guild=guild)
@app_commands.autocomplete(target=users_autocomplete)
async def self(interaction: discord.Interaction, target: str, amount: int):
    if not json.load(open("scores/gamebezig.json"))["bezig"]:
        await interaction.response.send_message("Spel is niet bezig.", ephemeral=True)
        return
    if amount <= 0:
        await interaction.response.send_message("Je kan niet een negatief aantal of nul punten doneren.", ephemeral=True)
        return
    data = getdata()
    if str(interaction.user.id) in data:
        if not GenoegPunten(str(interaction.user.id), amount):
            await interaction.response.send_message("Niet genoeg punten.", ephemeral=True)
            return
    else:
        await interaction.response.send_message("Je doet niet mee aan het spel.", ephemeral=True)
        return

    Donate(str(interaction.user.id), str(target), amount)
    targetMember: discord.Member = client.get_user(int(target))
    await interaction.response.send_message(f"{interaction.user.mention} hebt {amount} punten gedoneerd aan {targetMember.mention}.")


@tree.command(name="stopspel", description="Stop het gokspel.", guild=guild)
@app_commands.check(check_if_is_admin)
async def self(interaction: discord.Interaction):
    with open("scores/gamebezig.json") as f:
        data = json.load(f)
    data["bezig"] = False
    with open("scores/gamebezig.json", "w") as f:
        json.dump(data, f, indent=2)
    await interaction.response.send_message("Gokspel gestopt.", ephemeral=True)


async def guild_users_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    guild = interaction.guild
    users = guild.members
    return [
        app_commands.Choice(name=user.name, value=str(user.id))
        for user in users
        if current.lower() in user.name.lower() and not user.bot and user.id != client.user.id
    ]


@tree.command(name="summon", description="Summon iemand", guild=guild)
@app_commands.autocomplete(user=users_autocomplete)
async def self(interaction: discord.Interaction, user: str):
    await Summon().start(interaction, int(user))


@client.event
async def on_raw_reaction_add(payload):
    if client.user.id == payload.user_id:
        return
    if payload.emoji.name == "🇱":
        # print(payload)
        channel_id = payload.channel_id
        msg_id = payload.message_id
        channel = client.get_channel(channel_id)
        msg = await channel.fetch_message(msg_id)
        if msg.author == client.user:
            msg_content = msg.content
            link = re.search("(?P<url>https?://[^\s]+)", msg_content).group("url")
            with open(r"noeps/noep.json") as f:
                data = json.load(f)
            data[link][0] += 1
            print(f"+1 vote voor {link}")
            with open(r"noeps/noep.json", "w") as f:
                json.dump(data, f, indent=4)
    else:
        return


@client.event
async def on_raw_reaction_remove(payload: discord.Reaction):
    if client.user.id == payload.user_id:
        return
    if payload.emoji.name == "🇱":
        # print(payload)
        channel_id = payload.channel_id
        msg_id = payload.message_id
        channel = client.get_channel(channel_id)
        msg = await channel.fetch_message(msg_id)
        if msg.author == client.user:
            msg_content = msg.content
            link = re.search("(?P<url>https?://[^\s]+)", msg_content).group("url")
            with open(r"noeps/noep.json") as f:
                data = json.load(f)
            data[link][0] -= 1
            print(f"-1 vote voor {link}")
            with open(r"noeps/noep.json", "w") as f:
                json.dump(data, f, indent=4)
    else:
        return


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        # print('eigen bericht')
        return
    await player.message_handler(message)

    # print(message.content)
    if message.content.lower().startswith("wie"):
        user = message.author.id
        await message.channel.send(f"<@{user}> wie vroeg?")
        # print('bericht')

    # gpt troep
    if message.content.startswith(client.user.mention):
        bericht = message.content.removeprefix(client.user.mention)
        if bericht == "":
            bericht = "\n"
        try:
            async with message.channel.typing():
                antwoorden = await getResponse(bericht)
                antwoord = getAntwoordzonderPrompt(bericht, antwoorden)
            await message.channel.send(antwoord)
        except Exception as e:
            print("ai troep werkt niet")
            print(e)
            error_message = await message.channel.send("AI doet het nu ff niet")
            await error_message.delete(delay=2)


@client.event
async def on_voice_state_update(member: discord.User, before: discord.VoiceState, after: discord.VoiceState):
    if after.channel == None:
        return
    if before.channel == after.channel:
        return
    if before.channel != after.channel:
        source = random_nummer()
        voice_channel = after.channel
        vc = await voice_channel.connect()
        vc.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=source))
        while vc.is_playing():
            await asyncio.sleep(0.1)
        await vc.disconnect(force=True)
        vc.cleanup()


def random_nummer():
    dir = os.path.join(os.getcwd(), "joinsounds")
    randomnummer = random.choice(os.listdir(dir))
    path = os.path.join(dir, randomnummer)
    return path


@tree.error
async def on_test_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        cooldownTijd = int(re.search(r"\d+", str(error)).group())
        await interaction.response.send_message(f"Command is op cooldown. Probeer nog een keer in {cooldownTijd} seconden.", ephemeral=True)
    else:
        print(error)
        traceback.print_exc()


client.run(TOKEN)
