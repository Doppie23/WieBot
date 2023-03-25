import json

def addScoreLaatsteLeave(userID, Username) -> None:
    with open("laatsteleave/laatsteleave.json") as f:
        data: dict = json.load(f)
    if not userID in data:
        data[userID] = {
            "username": Username,
            "score": 1
        }
    else:
        data[userID]["score"] += 1
    with open("laatsteleave/laatsteleave.json", "w") as f:
        json.dump(data, f, indent=2)

def SortJSON():
    with open("laatsteleave/laatsteleave.json") as f:
        data = json.load(f)
    gebruikers = []
    score = []
    for UserID in data:
        gebruikers.append(UserID)
        score.append(data[UserID]["score"])

    score_sorted, userIDS_sorted = (list(t) for t in zip(*sorted(zip(score, gebruikers), reverse=True)))
    return score_sorted, userIDS_sorted

def Leaderboard():
    Leaderboard = {}
    score_sorted, userIDS_sorted = SortJSON()
    for i in range(len(userIDS_sorted)):
        UserID = userIDS_sorted[i]
        Userscore = score_sorted[i]
        Leaderboard[UserID] = Userscore
    return Leaderboard
