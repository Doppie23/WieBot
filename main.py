import os
from redditpost import randomcopypasta, randomshitpost
import discord
from discord import app_commands
from dotenv import load_dotenv
from asyncio import sleep
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
        for member in incall:
            await member.move_to(None)
    else:
        await interaction.response.send_message("Join eerst een spraakkanaal.")

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
        f.close()

        channel = client.get_channel(690215022961754121)
        await channel.send(f'<@{member.id}> zat {tijd_in_call} in {kanaal}')

        f = open('calltimer\leaderboard.json')
        leaderboard = json.load(f)

        try:
            oudetijd = datetime.strptime(leaderboard[str(before.channel)]['tijd'], '%H:%M:%S.%f')
            print(oudetijd)
            nieuwetijd = datetime.strptime(str(tijd_in_call), '%H:%M:%S.%f')

            if (oudetijd < nieuwetijd) == True:
                print('betere tijd')
                leaderboard[str(before.channel)] = {'tijd': str(tijd_in_call), 'member': str(member.id)}
                with open('calltimer\leaderboard.json', 'w') as f:
                    json.dump(leaderboard, f)
                f.close()
            else:
                print('geen beter tijd')

        except KeyError:
            leaderboard[str(before.channel)] = {'tijd': str(tijd_in_call), 'member': str(member.id)}
            with open('calltimer\leaderboard.json', 'w') as f:
                json.dump(leaderboard, f)
            f.close()

client.run(TOKEN)