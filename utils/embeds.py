import discord

def embedTrinna(interaction: discord.Interaction, bet_winst: int, bet_amount: int, uitkomsten: list):
    if bet_winst > 0:
        embed = discord.Embed(title=f'Lucky Dice', color=discord.Colour.green(), description=f"{interaction.user.display_name} heeft {bet_winst-bet_amount} punten gewonnen.")
    else:
        embed = discord.Embed(title=f'Lucky Dice', color=discord.Colour.red(), description=f"{interaction.user.display_name} heeft {bet_amount} punten verloren.")

    for uitkomst in uitkomsten:
        embed.add_field(name="🎲", value=f"{uitkomst}", inline=True)
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
