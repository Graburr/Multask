import json
import os
import random
import discord
from discord.ext import commands
from itertools import islice
from riotwatcher import LolWatcher, ApiError
from dotenv import load_dotenv

# Select differents colors for the embed in function of the runes used
colors_runes = {
    "Domination" : (215,65,67),
    "Precision" : (206,174,123),
    "Inspiration" : (66,167,172),
    "Resolve" : (157,214,132),
    "Sorcery" : (156,167,246)
}

class Game(commands.Cog):
    """Select a randomized champ, items, summoners and runes for the game League of Legends.

    This read all the members that exists in a class, then for each player, select a random
    champ, items, summoners and runes. The purpose it's just to have fun playing differents
    compos as it's normal playing.

    Attributes
    ----------
    __TOKEN_RIOT : str
        The token of the riot games API.

    watcher : LolWatcher
        Class that provide functions to make call to the riot API in a eassly way.

    region : str
        Region where to make the calls on the Riot Games API.

    __rune_used : str
        Hold which main category of runes has been choose for the current player.

    Methods
    -------
    def get_desc() -> str:
        Gives a description of the use of the command $game.

    async def randomize_champs(self, ctx) -> None:
        Randomize the selections of the different items for each player.    
    """
    def __init__(self):
        """Constructor to initialize the Game feature"""
        self.__TOKEN_RIOT = self.__get_api_key()
        self.watcher = LolWatcher(self.__TOKEN_RIOT)
        assert self.watcher != None, "Chek the Riot token again, it might be disable"
        self.region = "euw1"
        self.__rune_used = ""


    @staticmethod
    def get_desc() -> str:
        """ Return a description of the use of this command.

        Returns
        -------
        str
            Message that will be given to the user.
        """
        return ("""$game it's used to select a random champ, runes, items, summoners, etc.
                to each player that is in the same voice channel playing League of Legend\n""")
    
    @commands.command()
    async def randomize_champs(self, ctx) -> None:
        """Generate all randomizations needed for each player on the same voice channel.

        First get all participants in a voice channel, then select in a random way everything
        each player shoud pick. Finally all this info is given to __embed_msg(), this 
        function will create the embed that will be send to each user with the items that
        has to choose.

        Parameters
        ----------
        ctx : discord.ext.Commands
            Context of the message that invoke this command.

        Returns
        -------
        None
        """
        
        participants = await self.__get_participants(ctx)
        
        # me = self.watcher.summoner.by_name(self.region, "Lauriita18")
        # Get riot id of each one in the channel.

        champs_file = open(os.path.join(os.getcwd(), "data", "1champion.json"))
        summoners_file = open(os.path.join(os.getcwd(), "data", "2summoner.json")) 
        items_file = open(os.path.join(os.getcwd(), "data", "3item.json")) 
        runes_file = open(os.path.join(os.getcwd(), "data", "4runes.json"))  

        selections = [champs_file, summoners_file, items_file, runes_file]
        sections = ["champ", "summoners", "items", "runes"]

        for player in participants:
            player_selection = self.__choose_random__items(selections, sections)
            await self.__embed_msg(ctx, player.name, player_selection)

        champs_file.close()
        summoners_file.close()
        items_file.close()
        runes_file.close()


    def __choose_random__items(self, selections : list, sections : str) -> dict:
        """Select all random items for each player.

        This start selecting the champ that must play, then the spells, items to buy and
        finally the runes. 

        Parameters
        ----------
        selections : list
            Json files opened to select randomly the values.
        sections : str
            Names of each category to slect values.

        Returns
        -------
        dict
            All sections with the random values respectively, for each player.
        """
        
        player_slection = dict()
        limit = 1 # number of random choice to do
        
        while limit < 5:
            list_values = []
            file_dumped = json.load(selections[limit - 1])
            
            j = limit
            # Store which category was randomly choosed on this attribute to choose
            # the runes inside this category.
            if limit == 4:
                self.__rune_used = random.choice(list(file_dumped.keys()))
            main_rune_selected = False

            while j > 0:
                if limit == 4: # logic to select only runes
                    rune = ""
                    if not main_rune_selected:
                        rune = self.__choose_main_rune(file_dumped)
                        main_rune_selected = True
                    else:
                        rune = self.__select_runes(file_dumped, list_values)
                        
                    list_values.append(rune)

                else:
                    item_choose = self.__select_item(file_dumped, list_values)
                    list_values.append(item_choose)

                j -= 1

            # Add all items selected of the actual category
            player_slection[sections[limit - 1]] = list_values
            limit += 1   

        return player_slection    

    def __choose_main_rune(self, file_dumped : dict) -> str:
        """Select the main rune of the actual category choosed.

        Parameters
        ----------
        file_dumped : dict
            JSON file of runes dumped.

        Returns
        -------
        str
            Path of the image of the rune choose.
        """
        key_main_rune = random.choice(list(file_dumped[self.__rune_used]["mainRunes"].keys()))
        value_main_rune = file_dumped[self.__rune_used]["mainRunes"][key_main_rune]
        return value_main_rune
    

    def __select_runes(self, file_dumped : dict, list_values : list) -> str:
        """Select other 3 runes that aren't the main rune.

        Parameters
        ----------
        file_dumped : dict
            JSON file of runes dumped.
        list_values : list
            Runes alredy choosed

        Returns
        -------
        str
            Path of the image of the rune choose.
        """
        rune_selected = ""
        # Select a new rune that wasn't chose before.
        while True:
            key_specific_rune = random.choice(list(file_dumped[self.__rune_used].keys()))
            rune_selected = file_dumped[self.__rune_used][key_specific_rune]
            if rune_selected not in list_values:
                break
            print("Executed runes")
        
        return rune_selected
    

    def __select_item(self, file_dumped : dict, list_values : list) -> str:
        """Select all the remaining items that aren't the runes.

        Parameters
        ----------
        file_dumped : dict
            JSON file where choose randomly the items.
        list_values : list
            Values of the JSON file alredy choosed.

        Returns
        -------
        str
            Path of the item choose.
        """
        # Select new item that wasn't choose before
        value_selected = ""
        while True:
            random_key = random.choice(list(file_dumped.keys()))
            value_selected = file_dumped[random_key]
            if value_selected not in list_values:
                break
            print("Executed item")

        return value_selected
    

    async def __embed_msg(self, ctx, user : str, player_selection : dict):
        """Create the embed message for each category.

        Parameters
        ----------
        ctx : discord.ext.Commands
            Context of the message that invoke this command.
        user : str
            Name of the actual user that has to choose the items.
        player_selection : dict
            Contains all randomizations of each category.

        Raises
        ------
        FileNotFoundError
            Path that contains the image wasn't found.
        """
        iteration = 0
        image_file : discord.File = None
        category = ["champion -->", "summoners -->", "items -->", "runes -->"]
        pool_embeds = []
        files_images = []

        for values in player_selection.values():
            embed = discord.Embed(
                title=f"{category[iteration]} {user}",
                color=discord.Colour.from_rgb(*colors_runes[self.__rune_used])
            )      

            try:
                for path_item in values:
                    image_file = discord.File(path_item, filename=path_item.split("\\")[-1])
                    files_images.append(image_file)
                    
                pool_embeds.append(embed)
                iteration += 1

            except FileNotFoundError:
                raise FileNotFoundError(f"route of file {path_item} wasn't found")
        
        init = 0
        fin = 1
        increase = 2
        # Extract images from each category, group all of them in an embed and send the 
        # embed
        for emb in pool_embeds:
            if init == 0:
                await ctx.send(embed=emb, file=files_images[0])
            else:
                await ctx.send(embed=emb, files=files_images[init:fin])
            
            init = fin
            fin += increase
            increase += 1


    async def __get_participants(self, ctx) -> list[discord.Member]:
        """Get all members in the same voice channel as the person who invoke this randomization.

        Parameters
        ----------
        ctx : discord.ext.Commands
            Context of the message that invoke this command.

        Returns
        -------
        list[discord.Member]
            All members in a voice channel.

        Raises
        ------
        Exception
            The person who invokes randomize_champs() isn't connected to any voice channel.
        """
        try:
            participants = ctx.author.voice.channel.members
            assert participants != None
        except Exception:
            raise Exception("You have to be connected to a voice channel")
        else:
            return participants

    
    def __get_api_key(self) -> str:
        """Get API key of Riot Games API

        Returns
        -------
        str
            Key of the API.
        """
        if load_dotenv('./bot.env'):
            return os.getenv('DEV_RIOT_TOKEN')
        else:
            print("Env file couldn't be open")