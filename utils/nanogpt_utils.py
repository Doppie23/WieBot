import aiohttp

timeout = aiohttp.ClientTimeout(total=5)
url = "http://192.168.2.30:8000/getresponse"


async def getResponse(prompt: str) -> list:
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, json={"prompt": prompt}) as response:
            antwoord = await response.text()
            antwoord = antwoord.replace('"', "")
            antwoord = antwoord.replace(r"\n", "\n")
            array_antwoorden = antwoord.splitlines()
    return array_antwoorden


def getAntwoordzonderPrompt(prompt: str, antwoorden: list):
    """
    Geeft eerste antwoord als dat verder gaat op prompt anders tweede antwoord
    """
    return antwoorden[1]
    # if antwoorden[0] == prompt:
    #     return antwoorden[1]
    # elif antwoorden[0] == "":
    #     return antwoorden[1]
    # else:
    #     return antwoorden[0]
