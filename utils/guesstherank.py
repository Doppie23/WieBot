import aiohttp
import asyncio


class GuessTheRank:
    async def __init__(self, spelers) -> None:
        self.videoList = await getVideos()


async def getVideos() -> list[list]:
    async with aiohttp.ClientSession() as session:
        async with session.get("https://guesstherank.org/rocketleague") as response:
            htmltext = await response.text()
            htmllines = htmltext.splitlines()
            for index, line in enumerate(htmllines):
                if "var videoLinks" in line:
                    IndexVideosList = index + 1
                    break
            videoList = htmllines[IndexVideosList][:-2]
            videoList = eval(videoList)  # lijst met dit soort lijsten erin: ['https://youtu.be/XVTvh6jgYoU', '6', 'Sheik', '19268', '6.2105']
            return videoList


asyncio.run(getVideos())
