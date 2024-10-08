import os, random

import discord
from discord.ext import commands

class Message:
    def __init__(self) -> None:
        """Constructor of message"""
        self.__draws = dict()
        self.reaction = "✅"
        self.file = discord.File(f"{os.path.dirname(__file__)}/images/icon_dc.png",
                                filename="icon_dc.png")

    def get_desc(self) -> str:
        return "!message is used to interact using messages with the bot\n"

    async def create_pool(self, ctx, *, title: str, description: str, 
                          icon: discord.File) -> None:
        """Create a pool for a draw"""
        if ctx.guild not in self.__draws:
            embed = self.__create_embed(title, description, icon)
            msg = await ctx.send(file=icon, embed=embed)
            
            await msg.add_reaction(self.reaction)
            self.__draws[ctx.guild] = {
                ctx.channel: [embed, msg.id, title]
            }
        
    async def get_winner(self, ctx) -> None:
        """get participants of the draw specified by draw_id"""
        if ctx.channel not in self.__draws[ctx.guild]:
            raise ValueError("This draw doesn't exist in this channel.")
        
        msg = await ctx.fetch_message(self.__get_msg_id(ctx))
        # msg.reactions return a list of reactions. Since it's just one reaction to the 
        # draw, get the first element of the list and iterate over all the members that
        # react there.
        participants = [participant async for participant in msg.reactions[0].users()
                        if isinstance(participant, discord.Member) and participant != ctx.bot.user]
        
        if not participants:
            await ctx.send("No valid participants that are members is found")

        winner = random.choice(participants)

        title = self.__get_title(ctx)
        text = {f"Result of draw: {title}" : f"{winner.display_name} has won the prize"}
        embed = self.__create_embed(title, "", self.file, text_fileds=text)
        await ctx.send(embed=embed)


        priv_msg = f"You: {winner.display_name}, have won the draw, put in contact with a moderator"
        embed.remove_field(0)
        await self.__send_priv_msg(winner, title, priv_msg, embed)
        

    async def __send_priv_msg(self, member: discord.Member, title: str, text: str, 
                              embed: discord.Embed=None) -> None:
        """The bot send a private mesagge to a member that is given by parameter"""
        await member.create_dm()

        if embed:
            kwargs = {f"Winner of the draw {title}" : text}
            # Here it's not checked if the exception is called because there is an if-else
            # that checks it.
            self.__set_field(embed, kwargs)
            await member.dm_channel.send(embed=embed)
        else:
            await member.dm_channel.send(text)


    async def remove_messages(self, ctx, number="10") -> None:
        """Remove the number of messages (from newest to older) specified by number """
        number = int(number)

        async for msg in ctx.channel.history(limit=number, oldest_first=False):
           await msg.delete()

    
    def __get_title(self, ctx) -> str:
        return self.__draws[ctx.guild][ctx.channel][2]


    def __get_embed(self, ctx) -> discord.Embed:
        return self.__draws[ctx.guild][ctx.channel][0]


    def __get_msg_id(self, ctx) -> int:
        return self.__draws[ctx.guild][ctx.channel][1]
    

    def __create_embed(self, title: str, desciption: str, icon: discord.File, color: int=0x8170EE,  
                       text_fileds: dict[str, str]=dict(), inline: bool=False) -> discord.Embed:  
        """ Create an embed object from the class discord.Embed().
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
        """ Set a new field in the existant embed object
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




