import random
import asyncio

import typing
from typing import Optional
import discord
from discord.ext import commands
import wavelink


class Player(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        """Constructor of the media player"""
        self.bot = bot
        self.songs : list[wavelink.Playable] = []
        self.listening_music = False
        self.task : Optional[asyncio.Task] = None


    @staticmethod
    def get_desc() -> str:
        return "!player is used to simulate a media player of multiplataform content\n"


    @commands.command()
    async def play(self, ctx, search: str, shuffle: str="n") -> None:
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
            self.listening_music = True
            self.task = asyncio.create_task(self.__listening_music
                                             (ctx, voice_channel, wavelink.Player, randomize))

    @commands.command()
    async def disconnect(self, ctx) -> None: 
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


    async def __listening_music(self, ctx, channel : discord.VoiceProtocol, 
                                bot_status : discord.voice_client.VoiceClient, 
                                shuffle : bool) -> None:
        try:
            while self.songs:
                index_song = 0
                if shuffle:
                    index_song = random.randint(0, len(self.songs) - 1)

                song = self.songs[index_song]
                await self.__play_song(ctx, song=song, channel=channel)

                self.songs.pop(index_song)
                # suspend 5sec the coroutine to not overload the processor" 
                await asyncio.sleep(song.length / 1000) 

        except asyncio.CancelledError as e:
            print(f"Bot was disconnected: {e}")


    async def __play_song(self, ctx, *, song : wavelink.Playable,  channel : 
                          discord.VoiceProtocol) -> None:
        await channel.play(song)
        await ctx.send(f"Playing {song.title}")
        
