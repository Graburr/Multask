import discord
from discord.ext import commands

class MyView(discord.ui.View):
    """This class it's used to create views (buttons in this case) when it's needed.

    In this case it put 2 reactions with thumbs up and thumbs down. Each of these reaction,
    has a different functionality.

    Atributes
    ----------
    channel : discord.Message.channel
        The channel where the message (that has the view) was invoked.

    Methods
    --------
    async def first_button_callback(self, interaction: discord.Interaction,
                                     button: discord.ui.Button) -> None:
        Delete the message when the 👍 button is pressed.

    second_button_callback(self, interaction: discord.Interaction, 
                                     button: discord.ui.Button) -> None:
        Send a message when the 👎 button is pressed.
    """
    def __init__(self, *, timeout: float | None = 180, channel: discord.Message.channel):
        # Set the max amount of time that the view is available
        super().__init__(timeout=timeout)
        self.channel = channel

    @discord.ui.button(style=discord.ButtonStyle.primary, emoji="👍")
    async def first_button_callback(self, interaction: discord.Interaction,
                                     button: discord.ui.Button) -> None:
        """Delete the message which is associated with the 👍 in the specific channel
        provided by the attribute.

        Returns
        -------
        None.

        Notes
        ------
        The parameters must be passed because the discord api provided that values
        when the view is pressed. Since I don't use it, I won't comment the purpose of
        them. For more info about the functionality of these parameters see:
        https://discordpy.readthedocs.io/en/latest/interactions/api.html
        https://discordpy.readthedocs.io/en/latest/interactions/api.html?highlight=button#discord.ui.Button
        """
        message = await self.channel.fetch_message(self.channel.last_message_id)
        await message.delete()

    @discord.ui.button(style=discord.ButtonStyle.primary, emoji="👎")
    async def second_button_callback(self, interaction: discord.Interaction, 
                                     button: discord.ui.Button) -> None:
        """Send a message when the 👎 button is pressed in the same channel where the view
        was invoked.

        Parameters
        -----------
        interaction : discord.Interaction
            This is used to send a message in the same channel where the interaction with
            the 👎 happend.

        Returns
        -------
        None.

        Notes
        ------
        For more info about the functionality of interaction and button parameters see:
        https://discordpy.readthedocs.io/en/latest/interactions/api.html
        https://discordpy.readthedocs.io/en/latest/interactions/api.html?highlight=button#discord.ui.Button
        """
        await interaction.response.send_message(content=f"""I can't explain better, for  
                                                more info about a specific feature, type  
                                                the specific command""") # Clear the message