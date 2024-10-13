import os, random

import asyncio
import discord
from discord.ext import commands


class Message(commands.Cog):
    """ A class used to manage all messages send by the bot.

    This class is created to manage all the messages that the bot send to each channel
    of a guild (server) as well as private messages
    Some of the messages are also developed using discord.Embed to make them have a 
    better presentation.


    Attributes:
    -----------
    reaction : str
        Default emoji reaction to participate on draws.

    file : discord.File
        File location of the avatar used by the bot.

    __draws : Dict
        Private dictionary to store all the differents draws in differents guilds.


    Methods:
    --------
    get_desc(self) -> str:
        Give a general description of the purpose of this class for the help command
        of class Bot.

    create_draw(self, ctx, *, title: str, description: str, 
                icon: discord.File) -> None:
        Create a draw in the specific channel that it's invoked.

    get_winner(self, ctx) -> None:
        Get the winner (choosed randomly) of the draw created in the same channel
        where this method is called.

    remove_messages(self, ctx, number: int) -> None:
        Remove an specific amount of messages where this method is invoked using the
        order newest -> oldest.

    __send_priv_msg(self, member: discord.Member, title: str, text: str, 
                              embed: discord.Embed=None) -> None:
        Send a private message to someone with an specific text.

    __get_title(self, ctx) -> str:
        Return the title of the draw that was created in the same channel where this
        method is invoked.

    __get_embed(self, ctx) -> discord.Embed:    
        Return the embed used in the draw that was created in the same channel where
        this method is invoked.

    __get_msg_id(self, ctx) -> int:
        Return the id of the draw msg that was created in the same channel where this
        method is invoked.

    __create_embed(self, title: str, desciption: str, icon: discord.File, 
                       color: int=0x8170EE, text_fileds: dict[str, str]=dict(), 
                       inline: bool=False) -> discord.Embed:
        Create an embed and set the necesary information.

    __set_field(self, embed: discord.Embed, values: dict[str, str], 
                    inline: bool=False ) -> None:
        Set a new field to an existant embed.
    """

    def __init__(self) -> None:
        self.reaction = "✅"
        self.file = discord.File(f"{os.path.dirname(__file__)}/../images/icon_dc.png",
                                filename="icon_dc.png")
        self.__draws = dict()

    @staticmethod
    def get_desc() -> str:
        """Returns a message summaraising the purpose of message class commands.
        
        Return:
        -------
        str
            Containing the message for class Bot.

        Note:
        -----
        See the $help command of Bot.py.
        """
        return f"""!message is used to interact using messages in the chat
                 with the bot as well as making some tasks like create draws,
                 delete some messages, etc.\n"""

    @commands.command()
    async def create_draw(self, ctx, title: str, description: str, 
                          icon: discord.File=None, reaction: str=None) -> None:
        """Create a draw in the current channel.

        Create a draw in the same channel where the command was invoked.

        Parameters:
        -----------
        ctx : discord.ext.commands.Context
            Represent the context (information) where the command is being invoked 
            under.

        title : str
            The title that will be used in the draw.

        description : str
            Some description about how participate and when the winners will be 
            gived.

        icon : discord.File, optional
            Image that is setted at the top right of the draw message. If no value 
            is given, the default icon will be assigned.

        reaction: str, optional
            Emoji to set the reaction button for participate on the draw. If no value
            is given, it's used the default value (atribute self.reaction).

        Returns:
        --------
        None.
        """
        if ctx.guild not in self.__draws:
            if not icon:
                icon = self.file

            embed = self.__create_embed(title, description, icon)
            msg = await ctx.send(file=icon, embed=embed)
            
            if not reaction: # If no value of reaction was given, use default reaction
                reaction = self.reaction

            await msg.add_reaction(reaction)
            self.__draws[ctx.guild] = {
                ctx.channel: [embed, msg.id]
            }
        else:
            await ctx.send("There is alredy a draw in this channel")
    
    @commands.command()
    async def get_winner(self, ctx) -> None:
        """get the winner of the draw created before.

        Get a winner slected randomly of the draw that was created in the same
        channel where this is being invoked under.

        Parameter:
        ----------
         ctx : discord.ext.commands.Context
            Represent the context (information) where the command is being invoked 
            under.

        Raises:
        -------
        ValueError
            If there isn't currently a draw in the channel.

        Returns:
        --------
        None.
        """
        if ctx.channel not in self.__draws[ctx.guild]:
            raise ValueError("This draw doesn't exist in this channel.")
        
        msg = await ctx.fetch_message(self.__get_msg_id(ctx))
        # msg.reactions return a list of reactions. Since it's just one reaction to the 
        # draw, get the first element of the list and iterate over all the members that
        # react there.
        participants = [participant async for participant in msg.reactions[0].users()
                        if isinstance(participant, discord.Member) and 
                        participant != ctx.bot.user]
        
        if not participants:
            await ctx.send("No valid participants that are members is found")

        winner = random.choice(participants)

        title = self.__get_title(ctx)
        text = {f"Result of draw: {title}" : f"{winner.display_name} has won the prize"}
        embed = self.__create_embed(title, "", self.file, text_fileds=text)
        await ctx.send(embed=embed)


        priv_msg = f"""You: {winner.display_name}, have won the draw, put in contact
                     with a moderator"""
        embed.remove_field(0)
        await self.__send_priv_msg(winner, title, priv_msg, embed)
        await msg.delete()
        
    @commands.command()
    async def remove_messages(self, ctx, number: int=None) -> None:
        """Remove the number of messages (from newest to oldest).
        
        Paraeters:
        ----------
        ctx : discord.ext.commands.Context
            Represent the context (information) where the command is being invoked 
            under.
        
        number : int
            The amount of messages to delete. If no number if passed, it will print
            a message asking for that number in order to use this function.

        Return:
        -------
        None.
        """
        seconds_sleep = 0.5

        if not number:
            await ctx.send("Expected $remove_messages <number> where number is the "
                           "quantity of messages that will be deleted")
            return

        if number >= 50:
            time_stimate = number * seconds_sleep
            await ctx.send(f"""This will take around {time_stimate}s to delete the
                           {number} messages""")
            await asyncio.sleep(3)

        async for msg in ctx.channel.history(limit=number+1):
            await msg.delete()
            # Used to don't overload the server discord and dimiss delete some messages
            await asyncio.sleep(seconds_sleep)

    
    async def __send_priv_msg(self, member: discord.Member, title: str, text: str, 
                              embed: discord.Embed=None) -> None:
        """Send a private message to the user specified by the parameter member.
        
        Send a private message to a member with the title, text and if it's provided,
        the bot uses the embed object to send it with a personalized presentation.

        Parameters:
        -----------
        member : discord.Member
            The member who the message is going to be send.

        title : str
            Title of the message.

        text : str
            Text to send.

        embed : discord.Embed, optional
            embed object to give a personalization to the message.

        Return:
        -------
        None.
        """
        await member.create_dm()

        if embed:
            kwargs = {f"Winner of the draw {title}" : text}
            # Here it's not checked if the exception that could be thrown by 
            # __set_field() is called because there is an if-else that checks it.
            self.__set_field(embed, kwargs)
            await member.dm_channel.send(embed=embed)
        else:
            await member.dm_channel.send(text)
            
    
    def __get_title(self, ctx) -> str:
        """Get the title of the draw.
        
        Get the title of the draw where is being invoked under through the embed
        object stored in self.__draws.

        Paraeters:
        ----------
        ctx : discord.ext.commands.Context
            Represent the context (information) where the command is being invoked 
            under.

        Return:
        -------
        str
            containing the title.
        """
        return self.__draws[ctx.guild][ctx.channel][0].title


    def __get_embed(self, ctx) -> discord.Embed:
        """Get the embed object used in the draw.
        
        Get the embed object used where is being invoked under through the embed 
        object stored in self.__draws.

        Paraeters:
        ----------
        ctx : discord.ext.commands.Context
            Represent the context (information) where the command is being invoked 
            under.
        
        Return:
        -------
        discord.Embed
            embed object used by the draw.
        """
        return self.__draws[ctx.guild][ctx.channel][0]


    def __get_msg_id(self, ctx) -> int:
        """Get the embed object used in the draw.
        
        Get the embed object used where is being invoked under through the embed 
        object stored in self.__draws.

        Paraeters:
        ----------
        ctx : discord.ext.commands.Context
            Represent the context (information) where the command is being invoked 
            under.
        
        Return:
        -------
        int
            with the id of the draw message.
        """
        return self.__draws[ctx.guild][ctx.channel][1]
    

    def __create_embed(self, title: str, desciption: str, icon: discord.File, 
                       color: int=0x8170EE, text_fileds: dict[str, str]=dict(), 
                       inline: bool=False) -> discord.Embed:  
        """ Create an embed object using the class discord.Embed.

        This method is used to avoid DRY. See the documentation of discord.Embed() at:
        https://discordpy.readthedocs.io/en/latest/api.html?highlight=embed#discord.Embed
        """    
        embed = discord.Embed(
            title=title,
            description=desciption,
            color=discord.Colour(value=color)
        )
        embed.set_thumbnail(url=f"attachment://{icon.filename}")

        for name, text in text_fileds.items():
            embed.add_field(name=name, value=text, inline=inline)

        return embed
    
    
    def __set_field(self, embed: discord.Embed, values: dict[str, str], 
                    inline: bool=False ) -> None:
        """ Set new field/s in the existant embed object.

        Set a new field/s using the differents functions of discord.Embed with the 
        different configuration that could be given to each function.

        Parameters:
        -----------
        embed : discord.Embed
            The embed object where it will added new fields.

        values : dict[str, str]
            The key indicate which parameter set on add_field() and value, has the
            value asociated to that parameter.

        inline : bool, optional
            Indicate if the new text of add_field should go in the same line (default
            if False).

        Raises:
        -------
        ValueError
            If the embed doesn't exist. 

        Return:
        -------
        None.
        """
        if not embed:
            raise ValueError("Expected an object embed previously created, "
                             "but got None instead\n") 

        for name, value in values.items():
            if name == "Thumbnail" or name == "thumbnail":
                 embed.set_thumbnail(url=f"attachment://{value}")
            elif name == "Color" or name == "color":
                c_value = int(value)
                embed.color = discord.Colour(value=c_value)
            else:
                embed.add_field(name=name, value=value, inline=inline)




