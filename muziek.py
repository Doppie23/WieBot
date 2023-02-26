import re
from colorama import Fore
import discord
import yt_dlp as youtube_dl
import asyncio
import difflib
from spotifynaaryoutubelinks import spotify_naar_youtubeid
import requests
import datetime

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

class muziekspelen(object):    
    def __init__(self) -> None:
        self.quizbezig = False

    def initquiz(self, interaction: discord.Interaction, client: discord.Client, url: str, aantal_nummers: int):
        self.quizbezig = True
        self.url = url
        self.aantal_nummers = aantal_nummers
        self.ronde = 0

        self.interaction = interaction
        self.client = client
        self.name = ''
        self.artist = ''
        self.all_geraden = []
        self.skip_gebruikt = []
        self.name_geraden = False
        self.voteskips = 0

        self.force_quit_quiz_bool = False

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
            self.quizbezig = False
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
        starttijd = self.startpunt_get(id)
        if self.ronde != 1:
            await asyncio.sleep(5) # pauze tussen nummers door
        with youtube_dl.YoutubeDL(ytdl_format_options) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info["url"]
            print(url2)
            vc.play(discord.FFmpegPCMAudio(executable='ffmpeg', source=url2, before_options=starttijd))
        await channel.send(f'🎵 Nieuwe ronde start met raden 🎵')
        if vc.is_playing() != True:
            await channel.send(f'🚩 Error -> dit nummer wordt geskipt')
            self.nummer_speel_tijd.cancel()

    async def start(self):
        channel = self.interaction.channel
        spel_uitleg = self.speluitleg()
        await channel.send(embed=spel_uitleg)
        try:
            self.playlist = spotify_naar_youtubeid(self.url, self.aantal_nummers)
        except:
            await channel.send("geen goede spotify link")
            await self.leave()
            return
        self.scorebord_create()

        for i in self.playlist:
            if self.force_quit_quiz_bool == True:
                continue
            #init ronde
            ytid = i[0]
            self.skip_gebruikt = []
            self.voteskips = 0
            self.ronde += 1
            
            print(Fore.MAGENTA + f'nummer: {self.name}\nartiest: {self.artist}')
            asyncio.ensure_future(self.play(ytid))

            self.all_geraden = []
            self.name_geraden = False
            self.name = i[1]
            self.artist = i[2]

            self.nummer_speel_tijd = asyncio.create_task(self.cancelable_sleep(60)) # tijd per nummer
            await self.nummer_speel_tijd
            await channel.send(f'🛑 Het antwoord was: {self.name} - {self.artist}')
            embed_score = self.embed_scorebord()
            await channel.send(embed=embed_score)
            continue
        await self.leave()
        embed = discord.Embed(title='Einde spel', color=discord.Colour.red())
        await channel.send(embed=embed)

    async def force_quit_quiz(self, interaction: discord.Interaction):
        if self.quizbezig == True:
            self.force_quit_quiz_bool = True
            try:
                self.nummer_speel_tijd.cancel()
            finally:
                await interaction.response.send_message('Stopt quiz')
        else:
            await interaction.response.send_message('geen quiz bezig', ephemeral=True)

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
        embed = discord.Embed(title=f'Scorebord - Ronde {self.ronde}/{self.aantal_nummers}', color=discord.Colour.random())
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
             Let wel op, alles moet apart in de chat. Dus alle artiesten en de naam van het nummer in aparte berichten.', inline=False)
        embed.add_field(name='?skip', value='Gebruik dit om het huidige nummer over te slaan. De helft van iedereen die aan de quiz mee doet moet skippen.', inline=False)
        embed.add_field(name='Ik hoor niks?', value='Kan gebeuren, als het niet goed gaat skipt de bot het nummer zelf. Bij sommige nummers duurt het wat langer voordat ze beginnen.', inline=False)
        return embed

    async def message_handler(self, message: discord.Message):
        if self.quizbezig == False:
            return
        print('message_handler')
        if message.author == self.client.user:
            return
        if message.content.startswith('?skip'):
            if message.author in self.skip_gebruikt:
                return
            self.voteskips += 1
            self.skip_gebruikt.append(message.author)
            votes_nodig = round(1.0*len(self.scorebord))
            await message.channel.send(f'{self.voteskips}/{votes_nodig} votes voor skip')
            if self.voteskips >= votes_nodig:
                self.nummer_speel_tijd.cancel()
            return

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

    def startpunt_get(self, id):
        url = 'https://sponsor.ajay.app/api/skipSegments'

        params = {
        'videoID': id,  
        'category': 'music_offtopic'
        }

        r = requests.get(url, params)
        if r.status_code == 200:
            data = r.json()

            tijd = data[0]['segment'][1]
            tijd = round(int(tijd))

            tijd = str(datetime.timedelta(seconds=tijd))
            tijd = f'-ss {tijd}'
            return tijd
        else:
            return None