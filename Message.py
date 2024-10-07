import random

import discord
from discord.ext import commands

class Message:
    def __init__(self) -> None:
        """Constructor of message"""
        self.__surveys = dict()
        self.reaction = "✅"

    def get_desc(self) -> str:
        return "!message is used to interact using messages with the bot\n"
    
    def __get_msg_id(self, ctx) -> int:
        return self.__surveys[ctx.guild][ctx.channel][1]

    async def create_pool(self, ctx, *, title: str, description: str, icon: discord.File):
        """Create a pool for a draw"""
        if ctx.guild not in self.__surveys:
            embed = discord.Embed(
                    title=title,
                    description=description,
                    color=discord.Colour(value=0x8170EE),
                    )
            embed.set_thumbnail(url=f"attachment://{icon.filename}")
            msg = await ctx.send(file=icon, embed=embed)
            
            await msg.add_reaction(self.reaction)
            self.__surveys[ctx.guild] = {
                ctx.channel: [embed, msg.id]
            }
        
    async def get_winner(self, ctx):
        """get participants of the draw specified by draw_id"""
        if ctx.channel not in self.__surveys[ctx.guild]:
            raise ValueError("This draw doesn't exist in this channel.")
        
        msg = await ctx.fetch_message(self.__get_msg_id(ctx))
        # msg.reactions return a list of reactions. Since it's just one reaction to the 
        # draw, get the first element of the list and iterate over all the members that
        # react there.
        participants = [participant async for participant in msg.reactions[0].users()]
        winner = random.choice(participants)
        await ctx.send(f"{winner} has won the prize")


    async def remove_messages(self, ctx, number="10"):
        """Remove the number of messages (from newest to older) specified by number """
        number = int(number)
        async for msg in ctx.channel.history(limit=number, oldest_first=False):
           await msg.delete()



