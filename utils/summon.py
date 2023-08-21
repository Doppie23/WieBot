from typing import Optional, Union
import discord
from discord.emoji import Emoji
from discord.enums import ButtonStyle
from discord.partial_emoji import PartialEmoji


def generate_embed(title, description, color, footer):
    embed = discord.Embed(title=title, description=description, color=color, footer=footer)
    return embed


def generate_view():
    def on_yes(interaction: discord.Interaction):
        print("ja")

    def on_no(interaction: discord.Interaction):
        print("no")

    view = discord.ui.View()

    yes_button = discord.ui.Button(label="Ja", style=discord.ButtonStyle.primary)
    yes_button.callback = on_yes
    no_button = discord.ui.Button(label="Nee", style=discord.ButtonStyle.danger)
    no_button.callback = on_no

    view.add_item(yes_button)
    view.add_item(no_button)
    return view


async def summon(interaction: discord.Interaction, user_id: discord.User.id):
    # async def callback(interaction):
    await interaction.response.send_message("test")

    user = interaction.client.get_user(user_id)

    dm_channel = await user.create_dm()
    await dm_channel.send(f"Hallo {user.name}, ik ben Wiebot", view=generate_view())

    # await callback(interaction) -> None:


class Button(discord.ui.Button):
    def __init__(
        self,
        *,
        callback,
        style: ButtonStyle = ButtonStyle.secondary,
        label: str | None = None,
        disabled: bool = False,
        custom_id: str | None = None,
        url: str | None = None,
        emoji: str | Emoji | PartialEmoji | None = None,
        row: int | None = None,
    ):
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)
        # todo ipv callback manier nu
        self.callback = callback
