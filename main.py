import os
import random
import re
from redditpost import randomcopypasta, randomshitpost
import discord
from discord import app_commands
from dotenv import load_dotenv
from asyncio import sleep
import asyncio
from datetime import datetime, timedelta
import json

intents = discord.Intents.all()

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
guild = discord.Object(id=659436197457690626)

class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild=guild)
            self.synced=True
        print(f'{self.user} is nu online')
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='You'))

client = aclient()
tree = app_commands.CommandTree(client)

@tree.command(name="copypasta", description="stuurt een random copypasta van r/copypasta", guild=guild)
async def self(interaction: discord.Interaction):
    copypasta = randomcopypasta()
    leng = len(copypasta)
    while len(copypasta) > 2000:
        print(f'te lange post, reroll {leng}')
        copypasta = randomcopypasta()
    leng = len(copypasta)
    print(f'korte post {leng}')
    await interaction.response.send_message(copypasta)

@tree.command(name="shitpost", description="stuurt een random shitpost van r/shitposting", guild=guild)
async def self(interaction: discord.Interaction):
    shitpost = randomshitpost()
    await interaction.response.send_message(shitpost)

@app_commands.choices(choices=[
        app_commands.Choice(name="Crab Rave", value="crabrave"),
        app_commands.Choice(name="Epic Outro", value="outro"),
        ])

@tree.command(name="outro", description="Epic outro", guild=guild)
async def self(interaction: discord.Interaction, choices: app_commands.Choice[str]):   
    if (choices.value == 'crabrave'):
        file = '\outro\crab rave kort.wav'
        source = os.getcwd()+file
        bericht = ":crab:"

    elif (choices.value == 'outro'):
        file = '\outro\outro kort.wav'
        source = os.getcwd()+file
        bericht = "SMASH THAT LIKE BUTTON :thumbsup:"

    voice_channel = interaction.user.voice
    channel = None
    if voice_channel != None:
        voice_channel = voice_channel.channel
        channel = voice_channel.name
        incall = voice_channel.members
        vc = await voice_channel.connect()
        await interaction.response.send_message(bericht)
        if file == '\outro\outro kort.wav':
            original_message = await interaction.original_response()
            await discord.InteractionMessage.add_reaction(original_message, "👍")
            await discord.InteractionMessage.add_reaction(original_message, "👎")
        vc.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source=source))
        while vc.is_playing():
            await sleep(0.1)
        await vc.disconnect()

        await asyncio.wait([
        asyncio.create_task(kick(incall[i]))
        for i in range(len(incall))
        ])
    else:
        await interaction.response.send_message("Join eerst een spraakkanaal.")

async def kick(member):
    await member.move_to(None)

@tree.command(name="vrienden", description="!vrienden", guild=guild)
async def self(interaction: discord.Interaction):
    voice_channel = interaction.user.voice
    channel = None
    if voice_channel != None:
        voice_channel = voice_channel.channel
        channel = voice_channel.name
        incall = voice_channel.members
        vc = await voice_channel.connect()
        await interaction.response.send_message(f'{voice_channel} gejoind', ephemeral=True)
    else:
        await interaction.response.send_message("Join eerst een spraakkanaal.", ephemeral=True)

@tree.command(name="leave", description="leave call", guild=guild)
async def self(interaction: discord.Interaction):
    voice_channel = interaction.user.voice
    channel = None
    if voice_channel != None:
        voice_channel = voice_channel.channel
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message(':wave:', ephemeral=True)
    else:
        await interaction.response.send_message("Join eerst een spraakkanaal.", ephemeral=True)

@tree.command(name="leaderboard", description="leaderboard van wie het langst in elke call heeft gezeten", guild=guild)
async def self(interaction: discord.Interaction, kanaal: str):
    f = open('calltimer\leaderboard.json')
    data = json.load(f)
    try:
        tijd = data[str(kanaal).lower()]['tijd']
        memberid = data[str(kanaal).lower()]['member']
        await interaction.response.send_message(f"De persoon die het langst in {kanaal} heeft gezeten is <@{memberid}> met een tijd van: {tijd}")
    except KeyError:
        await interaction.response.send_message(f"Het kanaal {kanaal} heeft nog geen beste tijd.")
    
@tree.command(name="noep", description="!noep", guild=guild)
async def self(interaction: discord.Interaction):
    f = open(r'noeps\noep.json')
    noeps = json.load(f)
    clip, user_vote = random.choice(list(noeps.items()))
    user = user_vote[1]
    vote = user_vote[0]
    await interaction.response.send_message(f'gerbuiker: {user}, {vote} {clip}')
    original_message = await interaction.original_response()
    await discord.InteractionMessage.add_reaction(original_message, "🇱")
    f.close()

@tree.command(name="grootste-noep", description="De grootste noep van iedereen.", guild=guild)
async def self(interaction: discord.Interaction):
    with open(r'noeps\noep.json') as f:
        alles = []
        data = json.load(f)
        for i in data:
            getal = data[i]
            alles.append([data, getal])
    alles.sort(reverse=True)
    user = alles[0][1]
    hoevaak = alles[0][0]
    await interaction.response.send_message(f'gerbuiker: {user}, {hoevaak}')
    


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
            with open(r'noeps\noep.json') as f:
                data = json.load(f)
            data[link][0] += 1
            with open(r'noeps\noep.json', 'w') as f:
                json.dump(data, f, indent=4)            
    else:
        return

@client.event
async def on_message(message):
    if message.author == client.user:
        # print('eigen bericht')
        return

        # print(message.content)
    if message.content.lower().startswith('wie'):
        user = message.author.id
        await message.channel.send(f"<@{user}> wie vroeg?")
        # print('bericht')

@client.event
async def on_voice_state_update(member, before, after):
    print(after.channel)
    if after.channel != None:
        f = open('calltimer\data.json')
        data = json.load(f)

        starttijd = str(datetime.now())
        data[str(member.id)] = {'starttijd': starttijd, 'kanaal': str(after.channel)}

        with open('calltimer\data.json', 'w') as f:
            json.dump(data, f)

        f.close()

    elif after.channel == None:
        f = open('calltimer\data.json')
        data = json.load(f)

        eindtijd = datetime.now()

        starttijd = datetime.strptime(data[str(member.id)]['starttijd'], '%Y-%m-%d %H:%M:%S.%f')
        kanaal = data[str(member.id)]['kanaal']

        tijd_in_call = eindtijd - starttijd
        minutenincall = int(tijd_in_call.total_seconds()/60)
        f.close()

        channel = client.get_channel(1033786185719500850)
        await channel.send(f'<@{member.id}> zat {minutenincall} minuten in {kanaal}')

        f = open('calltimer\leaderboard.json')
        leaderboard = json.load(f)

        try:
            oudetijd = int(leaderboard[str(before.channel).lower()]['tijd'])
            print(oudetijd)
            nieuwetijd = minutenincall

            if nieuwetijd > oudetijd:
                print('betere tijd')
                leaderboard[str(before.channel).lower()] = {'tijd': str(minutenincall), 'member': str(member.id)}
                with open('calltimer\leaderboard.json', 'w') as f:
                    json.dump(leaderboard, f)
                f.close()
            else:
                print('geen beter tijd')

        except KeyError:
            leaderboard[str(before.channel).lower()] = {'tijd': str(minutenincall), 'member': str(member.id)}
            with open('calltimer\leaderboard.json', 'w') as f:
                json.dump(leaderboard, f)
            f.close()

client.run(TOKEN)