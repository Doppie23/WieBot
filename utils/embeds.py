import discord

def embedTrinna(interaction: discord.Interaction, bet_winst: int, bet_amount: int, uitkomsten: list):
    if bet_winst > 0:
        embed = discord.Embed(title=f'Lucky Dice', color=discord.Colour.green(), description=f"{interaction.user.display_name} heeft {bet_winst-bet_amount} punten gewonnen.")
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

def embedLuckyWheel(Luckywheel):
    embed = discord.Embed(title=f'Lucky Wheel', color=discord.Colour.blue())
    nummers = Luckywheel.getDrieNummers()
    for i in range(3):
        if i == 1:# midden
            value = "⬆"
        else:
            value = "🔹"
        embed.add_field(name=f"{nummers[i]}", value=value, inline=True)
    return embed
