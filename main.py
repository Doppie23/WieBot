import os

import discord
from dotenv import load_dotenv

intents = discord.Intents.all()

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    # print(message.content)
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')
        print('bericht')
client.run(TOKEN)