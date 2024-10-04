import os

import asyncio
import discord
from dotenv import load_dotenv
from discord.ext import commands

from Game import Game
from Message import Message
from Player import Player
from Ppv import Ppv
from Spotify import Spotify
from Youtube import Youtube



class Bot:

    def __init__(self, game: Game, message: Message, player: Player,
                 ppv: Ppv, spotify: Spotify, youtube: Youtube):
        """Constructor to initialize the bot class"""
        self.game = game
        self.message = message
        self.player = player
        self.ppv = ppv
        self.spotify = spotify
        self.youtube = youtube
        self.bot = self.run_bot()
        self.register_events()
        self.register_commands()
        

    def run_bot(self):
            intents = discord.Intents.all()
            bot = commands.Bot(command_prefix='$', intents=intents)
            return bot
            
    
    def start_bot(self, TOKEN: str):
         self.bot.run(TOKEN)
            

    def register_events(self):
        """Register events after the bot was created"""    
        @self.bot.event
        async def on_command_error(ctx, *args, **kwargs):
            """Show on the chat the error that trigered this"""
            msg = args[0]
            await ctx.send(msg)

    def register_commands(self):
        """Register the commands that the user types."""
        @self.bot.command(name='h')
        async def help_command(ctx):
            await ctx.send(f"Esto es una prueba de que funciona:\n"
                           f"{self.game.get_desc()}{self.player.get_desc()}"
                           f"{self.message.get_desc()}")
         


if __name__=='__main__':
    if os.name == 'nt': 
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Read the token of the discord server
    load_dotenv('./bot.env')
    TOKEN = os.getenv('DISCORD_TOKEN')

    bot = Bot(Game(), Message(), Player(), Ppv(), Spotify(), Youtube())
    bot.start_bot(TOKEN)
