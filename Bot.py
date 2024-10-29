import os

import asyncio
import discord
from dotenv import load_dotenv
from discord.ext import commands
import wavelink

from cogs.Game import Game
from cogs.Message import Message
from cogs.Player import Player
from cogs.Ppv import Ppv
from MyView import MyView



class Bot():
    """ This class is used to create the bot on the guild where it's added.

    The purpose of this class is create the bot run it on a server discord and then
    manage all the functionality that is implemented in different classes. It also handles
    some errors that can occur and has a help command to show all the features that exists.

    Attributes:
    -----------
    icon : discord.File
        It has the default image of the icon that the bot will use

    bot : commands.Bot
        Instance of the class that has the configuration to run the bot
    
        
    Methods:
    --------
    run_bot(self) -> commands.Bot:
        Create the bot and initialize all the cogs of the differents object with different
        functionality

    start_bot(self, TOKEN: str) -> None:
        Run the bot on the guild specified by the parameter.

    register_events(self) -> None:
        Send a message with the error in the same channel where it was being invoked.

    register_commands(self) -> None:
        Manage to print all functionality of the bot when te user types $help.
    """

    def __init__(self):
        """Constructor to initialize the bot class"""
        self.icon = discord.File(f"{os.path.dirname(__file__)}/images/icon_dc.png", 
                                 filename="icon_dc.png")
        self.bot = self.run_bot()
        self.register_events()
        self.register_commands()
        

    def run_bot(self) -> commands.Bot:
        """ Set up the bot and the cogs that the bot will has.

        Set up the bot with the intents that it has (all privileges). Then select the
        keyword to invoke the commands ($) and finally, add all the cogs of the bot.

        Return:
        -------
        commands.Bot
            Instance of the class with the bot set up to use his functionality.
        """
        intents = discord.Intents.all()
        bot = commands.Bot(command_prefix='$', intents=intents, help_command=None)

        asyncio.run(bot.add_cog(Message()))
        asyncio.run(bot.add_cog(Player(bot)))

        return bot
            
    
    def start_bot(self, TOKEN: str) -> None:
        self.bot.run(TOKEN)

            

    def register_events(self) -> None:
        """Register error events after the bot was created.
        
        The error events must be created inside this method because I couldn't use the
        decorator of the bot. Due to that, I had to encapsulate the method to manage errors.

        Return:
        -------
        None.
        """    
        @self.bot.event
        async def on_command_error(ctx, *args, **kwargs):
            """Show on the same chat the message where the error occured."""
            msg = args[0]
            await ctx.send(msg)

        @self.bot.event
        async def on_ready() -> None:
            """Execute this function automatically when bot is set up.
            
            This create a node of a public server of Lavalink to reproduce songs

            Returns
            -------
            None
            """
            await self.bot.wait_until_ready()
            
            # Public server
            nodes = [
                wavelink.Node(
                identifier="Node1", # This identifier must be unique for all the nodes you are going to use
                uri="https://lavalinkv4-id.serenetia.com:443", # Protocol (http/s) is required, port must be 443 as it is the one lavalink uses
                password="BatuManaBisa",
                )       
            ]

            await wavelink.Pool.connect(client=self.bot, nodes=nodes)
            print("Conexion stablized")
    

    def register_commands(self) -> None:
        """Register the commands that the user types.
        
        I have to use this to encapsulate the help functionality because I couldn't use 
        the decorator. Therefore, I used that way to could use the help command.
        """
        

        @self.bot.command()
        async def help(ctx) -> None:
            """When $help is typed. It shows a brief of the different functionality
            the bot has.

            It show the functionality using the embed messages and algo calling each class
            method get_desc() with a brief description of it functionality.

            Return:
            -------
            None
            """
            embed = discord.Embed(
                 title="Use of commands",
                 description="Show all types of commands that you have",
                 color=discord.Colour(value=0x8170EE),
            )
            embed.add_field(name="Help commands",
                            value=f"\n**!game:** {Game.get_desc()}\n\
                                    **!player:** {Player.get_desc()}\n\
                                    **!message:** {Message.get_desc()}")

            embed.set_author(name="Multask info", 
                             icon_url=f"attachment://{self.icon.filename}")
            embed.set_thumbnail(url=f"attachment://{self.icon.filename}")
            embed.set_footer(text="© Multask")

            await ctx.send(file=self.icon, embed=embed, view=MyView(channel=ctx.channel))
        

    


if __name__=='__main__':
    if os.name == 'nt': # Set up the event loop if it's running on windows
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Read the token of the discord server
    load_dotenv('./bot.env')
    TOKEN = os.getenv('DISCORD_TOKEN')
    
    # Initialize the bot.
    bot = Bot()
    bot.start_bot(TOKEN)
