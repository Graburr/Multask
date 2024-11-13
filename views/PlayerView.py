import discord

from cogs.Player import Player


class PlayerView(discord.ui.View):
    """Create 2 buttons to skip songs and disconnect bot from voice channel

    Atributes
    ----------
    ctx : discord.ext.Commands
            Context of the message that invoke this command.

    player : Player
        Current instance of object Player to skip song and disconnect bots.

    Methods
    --------
    async def first_button_callback(self, interaction: discord.Interaction,
                                     button: discord.ui.Button) -> None:
        Skip the song and reproduce another song.

    second_button_callback(self, interaction: discord.Interaction, 
                                     button: discord.ui.Button) -> None:
        Disconnect the bot from voice channel.
    """
    def __init__(self, ctx, player : Player, timeout: float | None = 180):
        # Set the max amount of time that the view is available
        super().__init__(timeout=timeout)
        self.__ctx = ctx
        self.__player = player
        

    @discord.ui.button(label="Skip song",style=discord.ButtonStyle.primary, emoji="⏭️")
    async def first_button_callback(self, interaction: discord.Interaction,
                                     button: discord.ui.Button) -> None:
        """Skip the song to reproduce another song.

        When the button with ⏭️ is pressed, it will execute an aknowledge that the button
        was pressed and it will execute a skip of the song instead of response with a message
        to that interaction.

        Returns
        -------
        None.

        Notes
        ------
        The parameters must be passed because the discord api provided that values
        when the button is pressed. Since I don't use it, I won't comment the purpose of
        them. For more info about the functionality of these parameters see:
        https://discordpy.readthedocs.io/en/latest/interactions/api.html
        https://discordpy.readthedocs.io/en/latest/interactions/api.html?highlight=button#discord.ui.Button
        """
        await interaction.response.defer()
        await self.__player.next_song(self.__ctx)
        

    @discord.ui.button(label="Disconnect bot", style=discord.ButtonStyle.danger, emoji="🔌")
    async def second_button_callback(self, interaction: discord.Interaction, 
                                     button: discord.ui.Button) -> None:
        """Disconnect the bot from the channel where it is.

         When the button with 🔌 is pressed, it will execute an aknowledge that the button
        was pressed and it will execute a disconnection of bot instead of response with a 
        message to that interaction.

        Returns
        -------
        None.

        Notes
        ------
        For more info about the functionality of interaction and button parameters see:
        https://discordpy.readthedocs.io/en/latest/interactions/api.html
        https://discordpy.readthedocs.io/en/latest/interactions/api.html?highlight=button#discord.ui.Button
        """
        await interaction.response.defer()
        await self.__player.disconnect(self.__ctx)