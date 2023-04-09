import json
import random

# standaard json functies
def getdata() -> object:
    with open("scores/scores.json") as f:
        data = json.load(f)
    return data

def writedata(data: object) -> None:
    with open("scores/scores.json", "w") as f:
        json.dump(data, f, indent=2)

def getPunten(userID: str) -> int:
    data = getdata()
    return data[userID]

def setPunten(userID: str, punten: int) -> None:
    data = getdata()
    data[userID] = punten
    writedata(data)

def GenoegPunten(userID: str, puntenNodig: int) -> bool:
    punten = getPunten(userID)
    if punten >= puntenNodig:
        return True
    else:
        return False
    
def CheckIfUserExists(UserID: str) -> bool:
    data = getdata()
    if UserID in data:
        return True
    else:
        return False
    
def Leaderboard_rng():
    def SortJSON():
        data = getdata()
        gebruikers = []
        score = []
        for UserID in data:
            gebruikers.append(UserID)
            score.append(data[UserID])

        score_sorted, userIDS_sorted = (list(t) for t in zip(*sorted(zip(score, gebruikers), reverse=True)))
        return score_sorted, userIDS_sorted
    Leaderboard = {}
    score_sorted, userIDS_sorted = SortJSON()
    for i in range(len(userIDS_sorted)):
        UserID = userIDS_sorted[i]
        Userscore = score_sorted[i]
        Leaderboard[UserID] = Userscore
    return Leaderboard

def getPlayerIDS() -> list[str]:
    data = getdata()
    playerids = []
    for playerid in data:
        playerids.append(playerid)
    return playerids        

# spel functies
def steel(userID: str, TargetID: str) -> bool:
    data = getdata()

    userpunten = data[userID]
    targetpunten = data[TargetID]

    winnaarID = random.choices(
        population=[userID, TargetID],
        weights=[targetpunten, userpunten] # bij weinig punten heb je nu meer kans om te winnen
    )[0]
    
    if userpunten>=targetpunten:
        puntenFraction = round(targetpunten/userpunten, 2)
    else:
        puntenFraction = round(userpunten/targetpunten, 2)
    puntenFraction = 1 - puntenFraction # om het systeem om te draaien, als je veel punten heb steel je minder van kleine spelers

    puntenErbij = round(data[TargetID]*puntenFraction)
    puntenErbij = round(puntenErbij * 0.3)

    if winnaarID == userID: # steel gelukt
        setPunten(winnaarID, data[winnaarID]+puntenErbij)
        setPunten(TargetID, data[TargetID]-puntenErbij)
        return True, puntenErbij
    else: # steel mislukt, en dus als boete 2x wat je zou hebben gestolen
        boete = puntenErbij * 2
        setPunten(userID, data[userID]-boete)
        return False, boete
    
def roulette(userID: str, bet_amount: int, bet_type: str, bet_value):
    def rouletteGame(bet_amount: int, bet_type: str, bet_value):
        # Define the possible outcomes and their corresponding odds
        outcomes = ['0', '00', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36']
        odds = [1, 1, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35]
        
        # Get a random outcome based on the odds
        outcome = random.choices(outcomes, weights=odds)[0]
        
        # Determine the payout based on the bet type and value
        payout = 0
        if bet_type == 'number' and str(bet_value) == outcome:
            payout = 35
        elif bet_type == 'even' and outcome != '0' and outcome != '00' and int(outcome) % 2 == 0:
            payout = 1
        elif bet_type == 'odd' and outcome != '0' and outcome != '00' and int(outcome) % 2 != 0:
            payout = 1
        
        # Calculate the winnings and return the outcome and winnings
        winnings = bet_amount * payout
        return (outcome, winnings)
    
    data = getdata()

    outcome, winnings = rouletteGame(bet_amount, bet_type, bet_value)
    if winnings>0:
        score = data[userID] + winnings
        data[userID] = score
    elif winnings==0:
        score = data[userID] - bet_amount
        data[userID] = score
    writedata(data)
    return outcome, winnings

def IedereenDieMeedoetIncall(UserIDSincall: list) -> bool:
    gameSpelers = getPlayerIDS()
    for gameSpeler in gameSpelers:
        if gameSpeler in UserIDSincall:
            continue
        else:
            return False
    return True

def ScoreBijVoorLaatsteLeaven(UserID, score: int, Positief: bool) -> None:
    data = getdata()
    oudescore = data[UserID]
    if Positief:
        data[UserID] = oudescore + score
    elif not Positief:
        data[UserID] = oudescore - score
    writedata(data)