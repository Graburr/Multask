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
from MyView import MyView



class Bot():

    def __init__(self, game: Game, message: Message, player: Player,
                 ppv: Ppv, spotify: Spotify, youtube: Youtube):
        """Constructor to initialize the bot class"""
        self.game = game
        self.message = message
        self.player = player
        self.ppv = ppv
        self.spotify = spotify
        self.youtube = youtube
        self.file = discord.File(f"{os.path.dirname(__file__)}/images/icon_dc.png", 
                                 filename="icon_dc.png")
        self.bot = self.run_bot()
        self.register_events()
        self.register_commands()
        

    def run_bot(self):
            intents = discord.Intents.all()
            bot = commands.Bot(command_prefix='$', intents=intents, help_command=None)
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

    

    def register_commands(self, *args):
        """Register the commands that the user types."""
        

        @self.bot.command()
        async def help(ctx):
            embed = discord.Embed(
                 title="Use of commands",
                 description="Show all types of commands that you have",
                 color=discord.Colour(value=0x8170EE),
            )
            embed.add_field(name="Help commands",
                            value=f"\n**!game:** {self.game.get_desc()}\n\
                                    **!player:** {self.player.get_desc()}\n\
                                    **!message:** {self.message.get_desc()}")

            embed.set_author(name="Multask info", 
                             icon_url=f"attachment://{self.file.filename}")
            embed.set_thumbnail(url=f"attachment://{self.file.filename}")
            embed.set_footer(text="© Multask")
            await ctx.send(file=self.file, embed=embed, view=MyView(bot=self.bot, 
                           channel=ctx.channel))


        @self.bot.command(name="create-pool")
        @commands.has_role('Admin')
        async def create_draw(ctx, title: str, description: str):
            await self.message.create_draw(ctx, title=title, description=description, 
                                           icon=self.file)
        

        @self.bot.command(name="get-winner")
        @commands.has_role('Admin')
        async def get_winner(ctx):
            await self.message.get_winner(ctx)

        @self.bot.command(name="clear")
        @commands.has_role('Admin')
        async def remove_messages(ctx, number: int):
            await self.message.remove_messages(ctx, number)

if __name__=='__main__':
    if os.name == 'nt': 
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Read the token of the discord server
    load_dotenv('./bot.env')
    TOKEN = os.getenv('DISCORD_TOKEN')

    bot = Bot(Game(), Message(), Player(), Ppv(), Spotify(), Youtube())
    bot.start_bot(TOKEN)
