import random
import asyncio

import typing
import discord
from discord.ext import commands
import wavelink


class Player(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        """Constructor of the media player"""
        self.bot = bot
        self.songs : list[wavelink.Playable]
        self.listening_music = False


    @staticmethod
    def get_desc() -> str:
        return "!player is used to simulate a media player of multiplataform content\n"


    @commands.command()
    async def play(self, ctx, search: str) -> None:
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
        
        if song.playlist:
            self.songs.extend(song.tracks)
        else:
            self.songs.append(song)

        if not self.listening_music:
             self.listening_music = True
             asyncio.create_task(self.__listening_music(ctx, voice_channel, wavelink.Player))

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


    async def __listening_music(self, ctx, channel: discord.VoiceProtocol, 
                                bot_status: discord.voice_client.VoiceClient, 
                                shuffle: bool=False) -> None:
        while self.songs and self.listening_music:
            if not bot_status.is_playing():
                await self.__play_song(ctx, channel=channel, shuffle=shuffle)
            
            # suspend 5sec the coroutine to not overload the processor" 
            await asyncio.sleep(5) 
            

    async def __play_song(self, ctx, *, channel: discord.VoiceProtocol, 
                          shuffle: bool=False) -> None:
        index_song = 0

        if shuffle and isinstance(self.song, wavelink.Playlist):
            index_song = random.randint(0, self.song.length - 1)

        await channel.play(self.song[index_song])
        await ctx.send(f"Playing {self.song[index_song].title}")
        self.song.pop(index_song)
