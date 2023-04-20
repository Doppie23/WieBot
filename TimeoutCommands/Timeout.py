from datetime import timedelta, datetime
import json

import discord

def TimeoutCheck():
    def wrap(f):
        async def wrapped_f(*args):
            interaction: discord.Interaction = args[0]
            userID = str(interaction.user.id)
            CommandName = interaction.command.name
            print(CommandName)
            TijdNogTimeout = getTimeNogTimeout(userID, CommandName)
            aantalSecondenTimeout = TijdNogTimeout.total_seconds()
            if aantalSecondenTimeout <= 0:
                RemoveTimeout(userID, CommandName)
                await f(*args)
            else:
                bericht = createMessageTimeString(aantalSecondenTimeout)
                await interaction.response.send_message(bericht, ephemeral=True)                
        return wrapped_f
    return wrap

def addTimeoutToCommand(userID: str, CommandName: str, AantalSeconden: int):
    currTime = GetTime()
    TimeOutVoorbijTijd = currTime + timedelta(seconds=AantalSeconden)
    data = getData()
    if not userID in data:
        data[userID] = {CommandName: TimeOutVoorbijTijd.strftime("%Y-%m-%d %H:%M:%S")}
    elif CommandName in data[userID]:
        return
    else:
        timeouts: object = data[userID]
        timeouts[CommandName] = TimeOutVoorbijTijd.strftime("%Y-%m-%d %H:%M:%S")
    writeData(data)    
    return

# utils
def GetTime():
    return datetime.now()

def getTimeNogTimeout(userID: str, commandNaam: str):
    data = getData()
    if not userID in data:
        return timedelta(seconds=0)    
    elif not commandNaam in data[userID]:
        return timedelta(seconds=0)
    else:
        tijdTimeoutVoorbij = data[userID][commandNaam]
        tijdTimeoutVoorbij = datetime.strptime(tijdTimeoutVoorbij, "%Y-%m-%d %H:%M:%S")
        tijdnu = GetTime()
        print(tijdTimeoutVoorbij, tijdnu)
        return tijdTimeoutVoorbij - tijdnu

def RemoveTimeout(userID: str, CommandName: str):
    data = getData()
    if userID in data:
        if CommandName in data[userID]:
            del data[userID][CommandName]
    writeData(data)
    return

def getData():
    with open("TimeoutCommands/Timeouts.json", "r") as f:
        data = json.load(f)
    return data

def writeData(data):
    with open("TimeoutCommands/Timeouts.json", "w") as f:
        json.dump(data, f, indent=2)
    return

def createMessageTimeString(totalseconds: int):
    hours, remainder = divmod(totalseconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    string = "Je hebt nog een timeout voor:"
    if hours > 0:
        string += f" {round(hours)} uur"
    if minutes > 0:
        string += f" {round(minutes)} minuten"
    if seconds > 0:
        string += f" en {round(seconds)} seconden"
    return string
