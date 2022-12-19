import discord
import os
from discord import app_commands
from dotenv import load_dotenv
load_dotenv()
from muziek import muziekspelen

intents = discord.Intents.all()
# TOKEN = os.getenv(sys.argv[1])
TOKEN = os.getenv('DISCORD_TOKEN')
# guild = discord.Object(id=690215022957559942)

class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync()
            self.synced=True
        print(f'{self.user} is nu online')
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='You'))

client = aclient()
tree = app_commands.CommandTree(client)
player = muziekspelen()

@tree.command(name="muziek-quiz", description="Start een muziek quiz. Werkt alleen met een Spotify playlist, niet met albums of een blend.")
async def self(interaction: discord.Interaction, url: str, aantal_nummers: int):
    if aantal_nummers > 10:
        aantal_nummers = 10
    player.initquiz(interaction, client, url, aantal_nummers)
    voice_channel = interaction.guild.voice_client
    if voice_channel == None or voice_channel.is_connected() != True:
        await player.join()
    await player.start()

@tree.command(name="leave", description="leave")
async def self(interaction: discord.Interaction):
    await player.leave()

@tree.command(name="stop-quiz", description="stopt quiz")
async def self(interaction: discord.Interaction):
    await player.force_quit_quiz(interaction)

@client.event
async def on_message(message: discord.Message):
    await player.message_handler(message)

client.run(TOKEN)