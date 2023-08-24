import random
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
        self.user = self.original_interaction.client.get_user(user_id)
        self.timer_still_going = True
        self.user_responed = False
        self.user_responed_yes = False

        await self.original_interaction.response.send_message(
            embed=self.generate_embed("/summon", f"Started summoning {self.user.name}.", "STARTED", color=discord.Colour.blurple())
        )

        await self.send_pm_to_user()
        # asyncio.get_event_loop().create_task(self.timer(100))
        await self.timer(60)
        if not self.user_responed_yes and self.user_responed:
            await self.original_interaction.edit_original_response(
                embed=self.generate_embed("/summon", f"{self.user.name} doesn't want to get summoned...", "SUMMON FAILED", discord.Color.orange())
            )
        elif self.user_responed_yes:
            await self.original_interaction.edit_original_response(
                embed=self.generate_embed("/summon", f"Succesfully summoned {self.user.name}.", "SUMMONED USER", discord.Colour.green())
            )
        else:
            await self.original_interaction.edit_original_response(
                embed=self.generate_embed("/summon", f"Failed to summon {self.user.name}.", "SUMMON FAILED", discord.Colour.red())
            )

    async def timer(self, seconds=60) -> None:
        max_seconds = int(seconds)
        interval = seconds / 10

        while self.timer_still_going and seconds > 0:
            await asyncio.sleep(1)
            seconds -= 1

            if (seconds % interval == 0) or seconds == max_seconds - 1:
                percentage = round((((max_seconds - seconds) / (max_seconds)) * 100) + random.randint(0, 9))
                # await self.original_interaction.edit_original_response(content=f"{max_seconds - seconds + random.randint(0, 9)}%")
                await self.original_interaction.edit_original_response(
                    embed=self.generate_embed(
                        "/summon",
                        f"Trying to find {self.user.name}...",
                        f"{percentage if percentage < 100 else 100}%",
                        progress=percentage / 100,
                    )
                )
        self.timer_still_going = False

    async def send_pm_to_user(self):
        dm_channel = await self.user.create_dm()
        gifs = [
            "https://tenor.com/view/you-there-you-are-there-car-you-there-cat-you-are-there-gif-18675776",
            "https://tenor.com/view/dory-are-you-there-where-you-at-gif-12631596",
            "https://tenor.com/view/up-dog-dug-waiting-patient-gif-14540614",
            "https://tenor.com/view/hey-marmot-me-calling-my-friends-squirrel-are-you-alive-gif-15790032",
        ]
        await dm_channel.send(f"{self.user.mention}")
        await dm_channel.send(random.choice(gifs), view=self.generate_view())

    async def on_yes(self, interaction: discord.Interaction):
        self.timer_still_going = False
        self.user_responed = True
        self.user_responed_yes = True
        await interaction.response.defer()
        await interaction.message.edit(content="https://tenor.com/view/aight-bet-aight-bet-cat-gif-25610485", view=None)

    async def on_no(self, interaction: discord.Interaction):
        self.timer_still_going = False
        self.user_responed = True
        await interaction.response.defer()
        await interaction.message.edit(content="https://tenor.com/view/sad-face-ok-cute-baby-gif-14541209", view=None)

    def generate_embed(self, title: str, description: str, footer: str, color: discord.Colour = discord.Colour.blue(), progress: float = None):
        def generate_loadbar():
            empty_emoji = "🔳"
            full_emoji = "🟦"
            arrow_emoji = ""

            progress_bar = ""
            for i in range(0, 10):
                if i < (progress * 10):
                    progress_bar += full_emoji
                else:
                    progress_bar += empty_emoji
            progress_bar = progress_bar.replace(empty_emoji, arrow_emoji, 1)
            return progress_bar

        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_footer(text=footer)
        if progress is not None:
            embed.add_field(name="Progress:", value=generate_loadbar())
        embed.set_thumbnail(url=self.user.avatar.url)
        return embed

    def generate_view(self):
        view = discord.ui.View()

        yes_button = Button(label="Ja", style=discord.ButtonStyle.primary, callback=self.on_yes)
        no_button = Button(label="Nee", style=discord.ButtonStyle.danger, callback=self.on_no)

        view.add_item(yes_button)
        view.add_item(no_button)
        return view
