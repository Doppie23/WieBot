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

def embedRoulette(interaction: discord.Interaction, outcome, winnings, bet_amount, bet_type_name, nummer):
    embed = discord.Embed(title=f'Roulette', color=discord.Colour.red(), description=f"{interaction.user.display_name} heeft ingezet op ")
    if nummer!=None:
        embed.description += f"nummer {nummer}."
    else:
        embed.description += f"{bet_type_name}."

    if winnings==0:
        value = f"Je hebt {bet_amount} punten verloren"
    else:
        embed.color = discord.Colour.green()
        value = f"Je hebt {winnings} punten gewonnen."
    embed.add_field(name=f"🎲 De uitkomst was {outcome}", value=value, inline=False)
    return embed