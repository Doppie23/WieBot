from code import interact
from http import client
import os
from redditpost import randomcopypasta
import discord
from discord import app_commands
from dotenv import load_dotenv

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

client = aclient()
tree = app_commands.CommandTree(client)

@tree.command(name="test", description="test2", guild=guild)
async def self(interaction: discord.Interaction):
    await interaction.response.send_message('test')

@tree.command(name="reddit", description="stuurt een random copypasta van r/copypasta", guild=guild)
async def self(interaction: discord.Interaction):
    copypasta = randomcopypasta()
    leng = len(copypasta)
    while len(copypasta) > 2000:
        print(f'te lange post, reroll {leng}')
        copypasta = randomcopypasta()
    leng = len(copypasta)
    print(f'korte post {leng}')
    await interaction.response.send_message(copypasta)

@client.event
async def on_message(message):
    if message.author == client.user:
        # print('eigen bericht')
        return

        # print(message.content)
    if message.content.startswith('wie'):
        user = message.author.id
        await message.channel.send(f"<@{user}> wie vroeg?")
        # print('bericht')

client.run(TOKEN)