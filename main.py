import os
from redditpost import randomcopypasta
import discord
from dotenv import load_dotenv

intents = discord.Intents.all()

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} is nu online')

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
    
    if message.content.startswith('!reddit'):
        copypasta = randomcopypasta()
        leng = len(copypasta)
        while len(copypasta) > 2000:
            print(f'te lange post, reroll {leng}')
            copypasta = randomcopypasta()
        leng = len(copypasta)
        await message.channel.send(copypasta)
        print(f'korte post {leng}')

client.run(TOKEN)