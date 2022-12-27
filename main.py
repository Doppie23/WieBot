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
from gtts import gTTS
import json
from func import totaal_user, meeste_ls, clip_van_gebruiker_met_meeste_ls
from muziek import muziekspelen

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
player = muziekspelen()

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
        file = '/outro/crab rave kort.wav'
        source = os.getcwd()+file
        bericht = ":crab:"

    elif (choices.value == 'outro'):
        file = '/outro/outro kort.wav'
        source = os.getcwd()+file
        bericht = "SMASH THAT LIKE BUTTON :thumbsup:"

    voice_channel = interaction.user.voice
    channel = None
    if voice_channel != None:
        voice_channel = voice_channel.channel
        channel = voice_channel.name
        incall = voice_channel.members
        vc = await voice_channel.connect()
        member_leave_list = []
        await interaction.response.send_message(bericht)
        if file == '/outro/outro kort.wav':
            original_message = await interaction.original_response()
            await discord.InteractionMessage.add_reaction(original_message, "👍")
            await discord.InteractionMessage.add_reaction(original_message, "👎")
        vc.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=source))
        while vc.is_playing():
            await sleep(0.1)
        await vc.disconnect()

        await asyncio.wait([
        asyncio.create_task(kick(incall[i], member_leave_list))
        for i in range(len(incall))
        ])
        laatste: discord.Member = member_leave_list[0]
        await interaction.channel.send(f'{laatste.mention}')
    else:
        await interaction.response.send_message("Join eerst een spraakkanaal.")

async def kick(member: discord.Member, list: list):
    await member.move_to(None)
    list.insert(0, member)

@tree.command(name="tts", description="tts test" , guild=guild)
@app_commands.describe(text='text die bot moet zeggen', channel_id='id van kanaal')
async def self(interaction: discord.Interaction, text: str, channel_id: str):
    voice = interaction.guild.voice_client
    if voice == None:
        channel = client.get_channel(int(channel_id))
        # channel = interaction.user.voice.channel
        await channel.connect()
    voice = interaction.guild.voice_client
    audio = gTTS(text=text, lang="nl", slow=False)
    audio.save("text.mp3")
    voice.play(discord.FFmpegPCMAudio(executable='ffmpeg', source='text.mp3'))
    await interaction.response.send_message(f'zegt nu: {text}', ephemeral=True)

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
    voice_channel = interaction.guild.voice_client
    if voice_channel != None or voice_channel.is_connected():
        await voice_channel.disconnect()
        await interaction.response.send_message(':wave:', ephemeral=True)
    else:
        await interaction.response.send_message("Bot zit niet in een kanaal.", ephemeral=True)

@tree.command(name="muziek-quiz", description="Start een muziek quiz.", guild=guild)
@app_commands.describe(url='Link naar Spotify playlist. Werkt alleen met een playlist, niet met albums of blends.', aantal_nummers='Aantal nummers waar de quiz uit moet bestaan (max 10).')
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
    
@tree.command(name="noep", description="!noep", guild=guild)
async def self(interaction: discord.Interaction):
    f = open(r'noeps/noep.json')
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
    embed = discord.Embed(title='De grootste noeps', color=discord.Colour.random())
    meeste_l_list, meeste_l_list_gebruiker = meeste_ls()
    for i in range(3):
        totaal_ls = meeste_l_list[i]
        totaal_ls_gebruiker = meeste_l_list_gebruiker[i]
        clip, ls_clip = clip_van_gebruiker_met_meeste_ls(totaal_ls_gebruiker)
        userid = totaal_ls_gebruiker[2:-1]
        userob = client.get_user(int(userid))
        if i == 0:
            embed.set_thumbnail(url=userob.avatar)
        nummer = i+1
        embed.add_field(name=f"{nummer}: {userob.display_name} met {totaal_ls} L's in totaal", value=f"De clip met de meeste L's ({ls_clip}) is: {clip}", inline=False)

    await interaction.response.send_message(embed=embed)

@tree.command(name="say", description="zeg iets als wiebot", guild=guild)
async def self(interaction: discord.Interaction, say: str):
    await interaction.response.send_message(f"Bericht: {say}", ephemeral=True)
    channel = interaction.channel
    await channel.send(say)

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
            with open(r'noeps/noep.json') as f:
                data = json.load(f)
            data[link][0] += 1
            print(f'+1 vote voor {link}')
            with open(r'noeps/noep.json', 'w') as f:
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
            with open(r'noeps/noep.json') as f:
                data = json.load(f)
            data[link][0] -= 1
            print(f'-1 vote voor {link}')
            with open(r'noeps/noep.json', 'w') as f:
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
    if message.content.lower().startswith('wie'):
        user = message.author.id
        await message.channel.send(f"<@{user}> wie vroeg?")
        # print('bericht')

client.run(TOKEN)