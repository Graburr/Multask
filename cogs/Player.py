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

    voice_channel : discord.context.voice_client
        Refeer to the bot that is connected to the voice channel to reprodue media
        through it.

    task : Optional[asyncio.Task]
        Hold the object task that will be created to cancelled it when bot is disconnected.

    bot_inactivity : Optional[asyncio.Task]
        Hold the object task that will disconnect the bot due to inactivity.
    
    message_def_embed : Optional[discord.Message]
        Get the message where it's going to be updating the embed of the song being reproduced.

    listening_music : bool
        Used to know if bot is reproducing music and avoid to create multiple tasks
        due to that.

    shuffle : bool
        Indicate if choose randomly each song or choose following default order.


    Methods
    -------
    get_desc() -> str
        Get a description with the purpose of this class.

    play(self, ctx, search : str, shuffle : str="n") -> None
        Reproduce a song or playlist where is connected the user who invoke it.
    
    disconnect(self, ctx) -> None
        Disconnect the bot of the channel where is connected.

    async def next_song(self, ctx) -> None
        Skip to the next song.

    __listening_music(self, ctx) -> None:
        Reproduce all the music that is stored in attribute songs.

    __play_song(self, ctx, *, song : wavelink.Playable) -> None:
        Play the song given by parameter.

     __disconect_inactivity(self, ctx, minutes : int = 1) -> None:
        Disconnect bot after certain time of inactivity.
    """
    def __init__(self, bot : commands.Bot) -> None:
        """Constructor of the media player"""
        self.bot = bot
        self.songs : list[wavelink.Playable] = []

        self.voice_channel = None
        self.task : Optional[asyncio.Task] = None
        self.bot_inactivity : Optional[asyncio.Task] = None
        self.message_def_embed : Optional[discord.Message] = None 
        
        self.listening_music = False
        self.shuffle = False


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
        try:
            channel = ctx.author.voice.channel
        except AttributeError:
            await ctx.send(f"{ctx.author.name} you have to be connected to any voice " 
                           "channel in order to use this command")
            return

        if not channel:
            raise ValueError("The user {ctx.author} isn't connected to any voice channel\n")
        
        if not ctx.bot.voice_clients:
            self.voice_channel = typing.cast(wavelink.Player, ctx.voice_client)
            self.voice_channel = await channel.connect(cls=wavelink.Player)
            self.bot_inactivity = asyncio.create_task(self.__disconect_inactivity(ctx))

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
            self.songs.append(song[0])

        if len(self.songs) > 1 and shuffle == "y":
            self.shuffle = True
            
        if not self.listening_music:
            # Create the task to reproduce songs on the background
            self.listening_music = True
            self.task = asyncio.create_task(self.__listening_music(ctx))


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
        vc.cleanup()

        self.listening_music = False
        self.songs.clear()
        self.message_def_embed = None
        self.task.cancel(msg="Disconnecting bot")


    @commands.command()
    async def next_song(self, ctx) -> None: 
        """Reproduce next song.

        Paramteres
        ----------
        ctx : discord.ext.Commands
            Context of the message that invoke this command.

        Returns
        -------
        None
        """ 
        if (self.songs):               
            self.task.cancel(msg="Skipping song")   
            self.task = asyncio.create_task(self.__listening_music(ctx))
        else:
            await ctx.send("You can't skip song, there isn't more songs to reproduce")

    async def __listening_music(self, ctx) -> None:
        """Execute all music that is on songs attribute.

        Execute all music one by one or randomly until songs get empty. When it send a
        song to reproduce, then sleep all the duration time of the song to not overlod
        the task queue and let other coroutines to execute.

        Parameters
        ----------
        ctx : discord.ext.Commands
            Context of the message that invoke this command.

        Returns
        -------
        None.
        """
        try:
            self.bot_inactivity.cancel() # Cancel the countdown to disconnect the bot

            while self.songs:
                index_song = 0
                if self.shuffle:
                    index_song = random.randint(0, len(self.songs) - 1)
                
                song = self.songs.pop(index_song)
                await self.__play_song(ctx, song)

                # suspend the coroutine to not overload the processor during the time
                # that is reproducing the actual song
                await asyncio.sleep(song.length / 1000) 

            # Start again the counter to disconnect the bot when there isn't more songs
            self.bot_inactivity = asyncio.create_task(self.__disconect_inactivity(ctx))
        except asyncio.CancelledError:
            pass


    async def __play_song(self, ctx, song : wavelink.Playable) -> None:
        """Reproduce song specificed by parameter throught the bot. 

        Parameters
        ----------
        ctx : discord.ext.Commands
            Context of the message that invoke this command.

        song : wavelink.Playable
            Song to reproduce.

        Returns
        -------
        None
        """
        from views.PlayerView import PlayerView # Deferred import, first time it will import
                                                # the module, then it will make cache hints
                                                
        # Edit over the same message that has embed of the song, the currently song being
        # reproduced
        if self.message_def_embed:  
            await self.message_def_embed.edit(content=song.uri)
        else: # If no previous message exists, create the message
            self.message_def_embed = await ctx.send(song.uri, view=PlayerView(ctx, self, None))

        await self.voice_channel.play(song)
        

    async def __disconect_inactivity(self, ctx, minutes : int = 1) -> None:
        await asyncio.sleep(minutes * 60)
        await self.disconnect(ctx)  