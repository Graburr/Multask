import os

import asyncio
import discord
from dotenv import load_dotenv
from discord.ext import commands
import wavelink

from src.Game import Game
from src.Message import Message
from src.Player import Player
from views.MyView import MyView


class Bot():
    """ This class is used to create the bot on the guild where it's added.

    The purpose of this class is create the bot run it on a server discord and then
    manage all the functionality that is implemented in different classes. It also handles
    some errors that can occur and has a help command to show all the features that exists.

    Attributes
    ----------
    icon : discord.File
        It has the default image of the icon that the bot will use

    bot : commands.Bot
        Instance of the class that has the configuration to run the bot
    
        
    Methods
    -------
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
        self.icon = discord.File(os.path.join(os.path.dirname(__file__),"assets",
                                "icon_dc.png"), filename="icon_dc.png")
        self.bot = self.run_bot()
        self.register_events()
        self.register_commands()
        

    def run_bot(self) -> commands.Bot:
        """ Set up the bot and the cogs that the bot will has.

        Set up the bot with the intents that it has (all privileges). Then select the
        keyword to invoke the commands ($) and finally, add all the cogs of the bot.

        Returns
        -------
        commands.Bot
            Instance of the class with the bot set up to use his functionality.
        """
        intents = discord.Intents.all()
        bot = commands.Bot(command_prefix='$', intents=intents, help_command=None)

        asyncio.run(bot.add_cog(Message()))
        asyncio.run(bot.add_cog(Player()))
        asyncio.run(bot.add_cog(Game()))

        return bot
            
    
    def start_bot(self, TOKEN: str) -> None:
        self.bot.run(TOKEN)


    def register_events(self) -> None:
        """Register error events after the bot was created.
        
        The error events must be created inside this method because I couldn't use the
        decorator of the bot. Due to that, I had to encapsulate the method to manage errors.

        Returns
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
            
            This create a node to a public server of Lavalink to reproduce songs

            Returns
            -------
            None
            """
            await self.bot.wait_until_ready()

            urls = {"https://lava-all.ajieblogs.eu.org:443" : "https://dsc.gg/ajidevserver",
                    "https://lava-v4.ajieblogs.eu.org:443" : "https://dsc.gg/ajidevserver",
                    "https://lavalinkv3-id.serenetia.com:443" : "BatuManaBisa"}
            
            for uri, psswd in urls.items():
                # Public server
                node = wavelink.Node(uri=uri, password=psswd)
                try:
                    await asyncio.wait_for(wavelink.Pool.connect(client=self.bot, 
                                            nodes=[node]), timeout=4.0)
                    print("Conexion establish")
                    break
                except asyncio.TimeoutError:
                    print(f"{uri} --> conexion wasn't able to be stablished.\n"
                          "trying next option...")
    

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

            Returns
            -------
            None
            """
            # Create an embed to show the info of help command
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
