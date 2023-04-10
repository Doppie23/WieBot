import discord
import os

def embedTrinna(interaction: discord.Interaction, bet_winst: int, bet_amount: int, uitkomsten: list):
    if bet_winst > 0:
        embed = discord.Embed(title=f'Lucky Dice', color=discord.Colour.red(), description=f"{interaction.user.display_name} heeft {bet_winst} punten gewonnen.")
    else:
        embed = discord.Embed(title=f'Lucky Dice', color=discord.Colour.red(), description=f"{interaction.user.display_name} heeft {bet_amount} punten verloren.")

    for uitkomst in uitkomsten:
        embed.add_field(name="🎲", value=f"{uitkomst}", inline=True)
    return embed

