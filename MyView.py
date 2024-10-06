import discord
from discord.ext import commands

class MyView(discord.ui.View):
    def __init__(self, *, timeout: float | None = 180, bot: commands.Bot, 
                 channel: discord.Message.channel):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.channel = channel

    # FALTA POR SOLUCIONAR ESTO, PROBAR CON LEER EL ÚLTIMO MENSAJE Y BORRARLO
    @discord.ui.button(style=discord.ButtonStyle.primary, emoji="👍")
    async def first_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        message = await self.channel.fetch_message(self.channel.last_message_id)
        await message.delete()

    @discord.ui.button(style=discord.ButtonStyle.primary, emoji="👎")
    async def second_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(content=f"I can't explain better, for more info about \
                                                a specific feature, type the specific command") # Clear the message