import json
from time import sleep
def totaal_user(usermention: str) -> int:
    '''
    Geeft de totale l's van een gebruiker
    '''
    with open('noeps/noep.json') as f:
        data = json.load(f)
    totaal = 0
    user = usermention
    for i in data:
        if data[i][1] == user:
            totaal = totaal + data[i][0]
    return totaal

def meeste_ls():
    '''
    Geeft een list van de gebruikers gesorteerd van meeste naar minste l's en een list met de l's
    '''
    with open('noeps/noep.json') as f:
        data = json.load(f)
    iedereen = []
    for i in data:
        user = data[i][1]
        if user not in iedereen:
            iedereen.append(user)

    gerbruikers = []
    ls = []
    for i in iedereen:
        totaal = totaal_user(i)
        gerbruikers.append(i)
        ls.append(totaal)

    ls_sorted, user_sorted = (list(t) for t in zip(*sorted(zip(ls, gerbruikers), reverse=True)))
    return ls_sorted, user_sorted

def list_alle_gebruikers() -> list:
    with open('noeps/noep.json') as f:
        data = json.load(f)
    iedereen = []
    for i in data:
        user = data[i][1]
        if user not in iedereen:
            iedereen.append(user)
    return iedereen

def clip_van_gebruiker_met_meeste_ls(user):
    '''
    Geeft van een gebruiker de clip met de meeste l's
    '''
    with open('noeps/noep.json') as f:
        data = json.load(f)
    clips_user = []
    ls_clips = []
    for i in data:
        user_data = data[i][1]
        if user_data == user:
            ls = data[i][0]
            clips_user.append(i)
            ls_clips.append(ls)
    ls_sorted, clips_sorted = (list(t) for t in zip(*sorted(zip(ls_clips, clips_user), reverse=True)))
    return clips_sorted[0], ls_sorted[0]

def add_noep(Link: str, userID: int):
    with open('noeps/noep.json') as f:
        data = json.load(f)
    UserTag = f"<@{userID}>"
    data[Link] = [0, UserTag]
    with open('noeps/noep.json', "w") as f:
        json.dump(data, f, indent=4)

def rem_noep(Link: str):
    with open('noeps/noep.json') as f:
        data: dict = json.load(f)
    data.pop(Link)
    with open('noeps/noep.json', "w") as f:
        json.dump(data, f, indent=4)