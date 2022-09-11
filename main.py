import os
from redditpost import randomcopypasta, randomshitpost
import discord
from discord import app_commands
from dotenv import load_dotenv
from asyncio import sleep

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

@tree.command(name="outro", description="outro", guild=guild)
async def self(interaction: discord.Interaction):
    voice_channel = interaction.user.voice
    channel = None
    if voice_channel != None:
        voice_channel = voice_channel.channel
        channel = voice_channel.name
        incall = voice_channel.members
        vc = await voice_channel.connect()
        await interaction.response.send_message("SMASH THAT LIKE BUTTON :thumbsup:")
        vc.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source="D:\.onedrive bestanden\creatief\Code\Dsicord bot\wiebot\outro\outro kort.wav"))
        while vc.is_playing():
            await sleep(0.1)
        await vc.disconnect()
        for member in incall:
            await member.move_to(None)
    else:
        await interaction.response.send_message("Join eerst een spraakkanaal.")

@tree.command(name="crabrave", description="Epic traditie", guild=guild)
async def self(interaction: discord.Interaction):
    voice_channel = interaction.user.voice
    channel = None
    if voice_channel != None:
        voice_channel = voice_channel.channel
        channel = voice_channel.name
        incall = voice_channel.members
        vc = await voice_channel.connect()
        await interaction.response.send_message(":crab: ")
        vc.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source="D:\.onedrive bestanden\creatief\Code\Dsicord bot\wiebot\outro\crab rave kort.wav"))
        while vc.is_playing():
            await sleep(0.1)
        await vc.disconnect()
        for member in incall:
            await member.move_to(None)
    else:
        await interaction.response.send_message("Join eerst een spraakkanaal.")

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

client.run(TOKEN)