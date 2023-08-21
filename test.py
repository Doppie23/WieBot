import discord
import os
from discord import app_commands
from dotenv import load_dotenv
from utils.summon import summon

load_dotenv()

intents = discord.Intents.all()
# TOKEN = os.getenv(sys.argv[1])
TOKEN = os.getenv("DISCORD_TOKEN_TEST_BOT")
guild = discord.Object(id=690215022957559942)


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


async def users_autocomplete(
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


@tree.command(name="test", description="test", guild=guild)
@app_commands.autocomplete(user_id=users_autocomplete)
async def self(interaction: discord.Interaction, user_id: str):
    await summon(interaction, int(user_id))


client.run(TOKEN)
