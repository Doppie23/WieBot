import re
from colorama import Fore
import discord
import youtube_dl
import asyncio
import difflib
from spotifynaaryoutubelinks import spotify_naar_youtubeid

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio',
    # 'restrictfilenames': True,
    'noplaylist': True,
    # 'nocheckcertificate': True,
    # 'ignoreerrors': False,
    # 'logtostderr': False,
    # 'quiet': True,
    # 'no_warnings': True,
    # 'default_search': 'auto',
    # 'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

class muziekspelen(object):    
    def __init__(self) -> None:
        self.quizbezig = False

    def initquiz(self, interaction: discord.Interaction, client: discord.Client, url: str, aantal_nummers: int):
        self.quizbezig = True
        self.url = url
        self.aantal_nummers = aantal_nummers

        self.interaction = interaction
        self.client = client
        self.name = ''
        self.artist = ''
        self.all_geraden = []
        self.name_geraden = False
        self.voteskips = 0

    async def join(self):
        voice_channel = self.interaction.user.voice
        if voice_channel != None:
            voice_channel = voice_channel.channel
            self.id = voice_channel.id
            self.vc = await voice_channel.connect()
            await self.interaction.response.send_message(f'{voice_channel} gejoind')
        else:
            await self.interaction.response.send_message("Join eerst een spraakkanaal.")

    async def leave(self):
        voice_channel = self.interaction.guild.voice_client
        if voice_channel != None or voice_channel.is_connected():
            await voice_channel.disconnect()
            self.vc.cleanup()
        else:
            await self.interaction.response.send_message("Bot zit niet in een kanaal.", ephemeral=True)

    async def play(self, id: str):
        url = 'https://www.youtube.com/watch?v=' + id
        channel = self.interaction.channel
        server = self.interaction.guild
        voice_channel = server.voice_client
        voice_channel.stop()
        vc = voice_channel
        await asyncio.sleep(5) # pauze tussen nummers door
        with youtube_dl.YoutubeDL(ytdl_format_options) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            vc.play(discord.FFmpegPCMAudio(executable='ffmpeg', source=url2))
        await channel.send(f'🎵 Nieuwe ronde start met raden 🎵')
        if vc.is_playing() != True:
            await channel.send(f'🚩 Error -> dit nummer wordt geskipt')
            self.nummer_speel_tijd.cancel()

    async def start(self):
        channel = self.interaction.channel
        spel_uitleg = self.speluitleg()
        await channel.send(embed=spel_uitleg)
        self.playlist = spotify_naar_youtubeid(self.url, self.aantal_nummers)
        self.scorebord_create()
        for i in self.playlist:
            ytid = i[0]
            self.name = i[1]
            self.artist = i[2]
            self.all_geraden = []
            self.name_geraden = False
            self.voteskips = 0
            print(Fore.MAGENTA + f'nummer: {self.name}\nartiest: {self.artist}')
            asyncio.ensure_future(self.play(ytid))
            self.nummer_speel_tijd = asyncio.create_task(self.cancelable_sleep(45)) # tijd per nummer
            await self.nummer_speel_tijd
            await channel.send(f'🛑 Het antwoord was: {self.name} - {self.artist}')
            embed_score = self.embed_scorebord()
            await channel.send(embed=embed_score)
            continue
        await self.leave()
        embed = discord.Embed(title='Einde spel', color=discord.Colour.red())
        await channel.send(embed=embed)
        self.quizbezig = False

    def scorebord_create(self):
        self.scorebord = {}
        channel = self.client.get_channel(self.id)
        members = channel.members
        for member in members:
            if member == self.client.user:
                continue
            name = member.name
            score = 0
            self.scorebord[name] = score

    def scorebord_sort(self) -> dict:
        sorted_score = sorted(self.scorebord, key=self.scorebord.get, reverse=True)
        sorted_scorebord = {}
        for name in sorted_score:
            sorted_scorebord[name] = self.scorebord[name]
        return sorted_scorebord

    def embed_scorebord(self):
        embed = discord.Embed(title='Scorebord', color=discord.Colour.random())
        sorted_scorebord = self.scorebord_sort()
        nummer = 1
        for name in sorted_scorebord:
            score = sorted_scorebord[name]
            embed.add_field(name=f"{nummer}: {name}", value=score, inline=False)
            nummer += 1
        return embed

    def speluitleg(self):
        embed = discord.Embed(title='Regels', color=discord.Colour.gold())
        embed.add_field(name='Het spel', value='Elke ronde komt er weer een nieuw nummer voor een bepaalde tijd, typ in de chat hoe jij denkt dat het nummer heet en wie de artiest is.', inline=False)
        embed.add_field(name='Score', value='Voor elk goede antwoord krijg je een punt, het hoeft niet helemaal goed getypt te zijn.\
             Let wel op, alles moet wel apart in de chat. Dus alle artiesten en de naam van het nummer in aparte berichten.', inline=False)
        embed.add_field(name='?skip', value='Gebruik dit om het huidige nummer over te slaan. 1/2 van iedereen die aan de quiz mee doet moet skippen.', inline=False)
        embed.add_field(name='Ik hoor niks?', value='Kan gebeuren, skip het nummer en meestal werkt het dan weer.', inline=False)
        return embed

    async def message_handler(self, message: discord.Message):
        if self.quizbezig == False:
            return
        print('message_handler')
        if message.author == self.client.user:
            return
        if message.content.startswith('?skip'):
            self.voteskips += 1
            votes_nodig = round(0.5*len(self.scorebord))
            await message.channel.send(f'{self.voteskips}/{votes_nodig} votes voor skip')
            if self.voteskips >= votes_nodig:
                self.nummer_speel_tijd.cancel()

        artist_list = re.split(', ', self.artist)

        bericht = message.content.lower()
        low_name = self.name.lower()

        artist_lower = []
        for artist in artist_list:
            artist_lower.append(artist.lower())

        # print(Fore.YELLOW + f'Controle:\nnummer: {bericht} - {low_name}\nartiest: {bericht} - {artist_lower}')

        name_match = difflib.SequenceMatcher(None, low_name, bericht).ratio()
        if name_match >= 0.6 and self.name_geraden == False:
            print(Fore.GREEN + 'name goed')
            await message.add_reaction('✅')
            self.name_geraden = True
            self.scorebord[message.author.name] += 1

        for artist in artist_lower:
            if artist in self.all_geraden:
                continue
            artist_match = difflib.SequenceMatcher(None, artist, bericht).ratio()
            if artist_match >= 0.6:
                print(Fore.GREEN + 'artist goed')
                await message.add_reaction('✅')
                self.all_geraden.append(artist)
                self.scorebord[message.author.name] += 1

        if set(self.all_geraden) == set(artist_lower) and self.name_geraden == True:
            print(Fore.BLUE + 'alles geraden')
            self.nummer_speel_tijd.cancel()

    async def cancelable_sleep(self, time):
        try:
            # sleep
            await asyncio.sleep(time)
        except asyncio.CancelledError:
            print(Fore.CYAN + 'Nummer geskipt')
            raise
        finally:
            return