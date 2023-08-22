import discord
from discord.emoji import Emoji
from discord.enums import ButtonStyle
from discord.partial_emoji import PartialEmoji
import asyncio


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
        self.callback = callback


class Summon:
    async def start(self, interaction: discord.Interaction, user_id: discord.User.id) -> None:
        self.original_interaction = interaction
        self.user_id = user_id
        self.timer_still_going = True

        await self.original_interaction.response.send_message("0%")

        asyncio.get_event_loop().create_task(self.timer(100))
        await self.send_message_to_user()

    async def timer(self, seconds=100) -> None:
        await self.original_interaction.edit_original_response(content="1%")
        interval = seconds / 10

        while self.timer_still_going and seconds > 0:
            print(seconds)
            await asyncio.sleep(1)

            seconds -= 1
            if seconds % interval == 0:
                await self.original_interaction.edit_original_response(content=f"{seconds}%")
        print("timer done")
        self.timer_still_going = False

    async def send_message_to_user(self):
        # async def callback(interaction):

        user = self.original_interaction.client.get_user(self.user_id)

        dm_channel = await user.create_dm()
        await dm_channel.send(f"https://tenor.com/view/you-there-you-are-there-car-you-there-cat-you-are-there-gif-18675776", view=self.generate_view())

        # await callback(interaction) -> None:

    async def on_yes(self, interaction: discord.Interaction):
        print("ja", self.timer_still_going)
        self.timer_still_going = False

    async def on_no(self, interaction: discord.Interaction):
        print("no", self.timer_still_going)
        self.timer_still_going = False

    def generate_embed(self, title, description, color, footer):
        embed = discord.Embed(title=title, description=description, color=color, footer=footer)
        return embed

    def generate_view(self):
        view = discord.ui.View()

        yes_button = Button(label="Ja", style=discord.ButtonStyle.primary, callback=self.on_yes)
        no_button = Button(label="Nee", style=discord.ButtonStyle.danger, callback=self.on_no)

        view.add_item(yes_button)
        view.add_item(no_button)
        return view
