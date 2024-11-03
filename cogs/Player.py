import random
import asyncio

import typing
from typing import Optional
import discord
from discord.ext import commands
import wavelink


class Player(commands.Cog):
    """A class used to reproduce songs and videos.

    This class is used to reproduce songs from youtube or spotify. You can reproduce one 
    song or a playlist, if you pass a playlist you can randomize it. In spite of that, is
    capable of live stream a video of youtube in a current channel.

    
    Attributes
    ----------
    bot : commands.Bot
        The object that has been used to initialize the bot.

    songs : list[wavelink.Playable]
        List used to store all the songs that is going to be reproduced.

    listening_music : bool
        Used to know if bot is reproducing music and avoid to create multiple tasks
        due to that.

    task : Optional[asyncio.Task]
        Hold the object task that will be created to cancelled it when bot is disconnected.


    Methods
    -------
    get_desc() -> str
        Get a description with the purpose of this class.

    play(self, ctx, search : str, shuffle : str="n") -> None
        Reproduce a song or playlist where is connected the user who invoke it.
    
    disconnect(self, ctx) -> None
        Disconnect the bot of the channel where is connected.

    __listening_music(self, ctx, channel : discord.VoiceProtocol, 
                      shuffle : bool) -> None:
        Reproduce all the music that is stored in attribute songs.

    __play_song(self, ctx, *, song : wavelink.Playable,  channel : 
                          discord.VoiceProtocol) -> None:
        Play the song given by parameter.
    """
    def __init__(self, bot : commands.Bot) -> None:
        """Constructor of the media player"""
        self.bot = bot
        self.songs : list[wavelink.Playable] = []
        self.listening_music = False
        self.task : Optional[asyncio.Task] = None


    @staticmethod
    def get_desc() -> str:
        """Get a brief description of the purpose of this class.
        
        Returns
        -------
        str
            Message with the purpose of class player
        """
        return "!player is used to simulate a media player of multiplataform content\n"


    @commands.command()
    async def play(self, ctx, search : str, shuffle : str="n") -> None:
        """Reproduce the song given by parameter.

        Connect the bot to the same channel where is connected who invoke this command.
        Then when the song or playlist given by search is parsed, invoke a task to reproduce
        all songs that were found in the parameter search on background until the songs 
        attribute gets empty.

        Parameters
        ----------
        ctx : discord.ext.Commands
            Context of the message that invoke this command.

        search : str
            URL of specific song or playlist to search on youtube or spotify.

        shuffle : str, optional
            Indicate if the shongs will be random or reproduce them in order. By default "n".

        Returns
        -------
        None.

        Raises
        ------
        ValueError
            The user who invoke this command isnt connected to any voice channel.
        """
        channel = ctx.author.voice.channel

        if not channel:
            raise ValueError("The user {ctx.author} isn't connected to any voice channel\n")
        
        voice_channel = typing.cast(wavelink.Player, ctx.voice_client)

        if not ctx.bot.voice_clients:
            voice_channel = await channel.connect(cls=wavelink.Player)

        song = await wavelink.Playable.search(search)

        if not song:
            await ctx.send("No song found");
            return
        
        if isinstance(song, wavelink.Playlist):
            # Add all songs of the playlist to the attribute songs.
            # Decided to add the songs that are in attribute to the songs which where
            # parsed by search. If songs has 10 songs and the playlist has 500 songs, 
            # it will be more efficient.
            temp_songs = self.songs
            self.songs = song.tracks

            if not temp_songs:
                self.songs.extend(temp_songs)
        else:
            self.songs.append(song)

        randomize = False

        if len(self.songs) > 1 and shuffle == "y":
            randomize = True
            
        if not self.listening_music:
            # Create the task to reproduce songs on the background
            self.listening_music = True
            self.task = asyncio.create_task(self.__listening_music
                                             (ctx, voice_channel, wavelink.Player, randomize))

    @commands.command()
    async def disconnect(self, ctx) -> None: 
        """Disconnect the bot of the voice channel where is connected.

        Parameters
        ----------
        ctx : discord.ext.Commands
            Context of the message that invoke this command.

        Raises
        ------
        ValueError
            The bot isn't connected to any channel.
        """
        vc = ctx.voice_client

        if not vc:
            raise ValueError("The bot isn't connected to any channel\n")
        
        await vc.disconnect()
        try:
            await vc.cleanup()
        except TypeError as te:
            print(f"An error occured when cleaning up the voice data of bot: {te}\n")

        self.listening_music = False
        self.task.cancel()


    async def __listening_music(self, ctx, bot : discord.VoiceProtocol,  
                                shuffle : bool) -> None:
        """Execute all music that is on songs attribute.

        Execute all music one by one or randomly until songs get empty. When it send a
        song to reproduce, then sleep all the duration time of the song to not overlod
        the task queue and let other coroutines to execute.

        Parameters
        ----------
        ctx : discord.ext.Commands
            Context of the message that invoke this command.

        bot : discord.VoiceProtocol
            Bot with the voice protocol that enable him to reproduce song on it.

        shuffle : bool
            Randomize the order which song are going to be reproduced. By default None.

        Returns
        -------
        None.
        """
        try:
            while self.songs:
                index_song = 0
                if shuffle:
                    index_song = random.randint(0, len(self.songs) - 1)

                song = self.songs[index_song]
                await self.__play_song(ctx, song=song, bot=bot)

                self.songs.pop(index_song)
                # suspend 5sec the coroutine to not overload the processor" 
                await asyncio.sleep(song.length / 1000) 

        except asyncio.CancelledError as e:
            print(f"Bot was disconnected: {e}")


    async def __play_song(self, ctx, *, song : wavelink.Playable, bot : 
                          discord.VoiceProtocol) -> None:
        """Reproduce song specificed by parameter throught the bot. 

        Parameters
        ----------
        ctx : discord.ext.Commands
            Context of the message that invoke this command.

        song : wavelink.Playable
            Song to reproduce.

        bot : discord.VoiceProtocol
            Bot where reproduce the song.

        Returns
        -------
        None.
        """
        await bot.play(song)
        await ctx.send(f"Playing {song.title}")
        
