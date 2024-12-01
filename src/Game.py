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
    data_assets : dict[str : list]
        Have all the champions, items, runes, etc that exists in the game to select it
        in a random way.

    __TOKEN_RIOT : str
        The token of the riot games API.

    watcher : LolWatcher
        Class that provide functions to make call to the riot API in a eassly way.

    region : str
        Region where to make the calls on the Riot Games API.
    """
    def __init__(self):
        """Constructor to initialize the Game feature"""
        self.data_assets = self.__get_files(os.path.join(os.getcwd(), "assets"), ["champion"])
        self.__TOKEN_RIOT = self.__get_api_key()
        self.watcher = LolWatcher(self.__TOKEN_RIOT)
        assert self.watcher != None, "Chek the Riot token again, it might be disable"
        self.region = "euw1"


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
        """Generate all randomizations needed to each player on the same voice channel.

        This first get all participants in a voice channel, then select in a random way
        what each player shoud pick. Finally all this info is given to __embed_msg(), this 
        function will create the embed that will be send to each user with the picks that
        has to choose.

        Parameters
        ----------
        ctx : discord.ext.Commands
            Context of the message that invoke this command.

        Returns
        -------
        None
        """
        
        participants = await self.__get_num_champs(ctx)
        
        # me = self.watcher.summoner.by_name(self.region, "Lauriita18")
        # Get riot id of each one in the channel.
        champs_file = open(os.path.join(os.getcwd(), "data", "1champion.json"))
        summoners_file = open(os.path.join(os.getcwd(), "data", "2summoner.json")) 
        items_file = open(os.path.join(os.getcwd(), "data", "3item.json")) 
        runes_file = open(os.path.join(os.getcwd(), "data", "4runes.json"))  

        selections = ["champs", "summoners", "items", "runes"]
        for player in participants:
            player_selection = self.__choose_random__items(selections)
            await self.__embed_msg(ctx, player.name, player_selection)

        champs_file.close()
        summoners_file.close()
        items_file.close()
        runes_file.close()

        # # Read the json with champs name and the path with the image of the champs
        # with open(os.path.join(os.getcwd(), "data", "champions_red.json")) as f:
        #     champs = json.load(f)

        #     for player in participants:
        #         player_slection = dict()
                
        #         runes_selected = False

        #         # Iterate over each random stuff to choose
        #         for key in self.data_assets:
        #             if runes_selected:
        #                 break

                     
        #             path = os.path.join(os.getcwd(), "assets", "game_images")
                    
        #             if key == "1champion":
        #                 _, champ_image = random.choice(list(champs.items()))
        #                 player_slection[key] = champ_image
        #                 limit = 1
        #                 continue

        #             elif key == "2summoner":
        #                 limit = 2
        #                 path = os.path.join(path, "2summoner")

        #             elif key == "3item":
        #                 limit = 3
        #                 path = os.path.join(path, "3item")

        #             else:
        #                 rune_selection = [rune for rune in self.data_assets 
        #                                   if rune not in ["3item", "2summoner"]]
        #                 key = random.choice(rune_selection)
        #                 runes_selected = True
        #                 path = path = os.path.join(path, "4runes", key)

        #             path = os.path.relpath(path, os.getcwd())
        #             key_values = []

        #             # Store each random choice until reach the limits of stuff to store
        #             while len(key_values) < limit:
        #                 value = os.path.join(path, random.choice(self.data_assets[key]))

        #                 if value not in key_values:
        #                     key_values.append(value) 

        #             player_slection[key] = key_values

        #         # Create embed messages and send it throgh the same text channel where
        #         # this command was invoked.

    def __choose_random__items(self, selections : list) -> dict:
        player_slection = dict()
        limit = 1 # number of random choice to do
        
        for _ in range (limit):
            list_values = []
            file_dumped = json.load(selections[limit - 1]+"_file")
            
            j = limit
            key_selected = random.choice(list(file_dumped.keys()))
            main_rune_selected = False

            while j > 0:
                repeated_value = False

                if limit == 4:
                    rune_path = self.__select_runes(file_dumped, list_values, 
                                                    key_selected, main_rune_selected)
                    if rune_path is not None:
                        list_values.append(rune_path)
                    else:
                        repeated_value = True
                else:
                    item_choose = self.__select_item(file_dumped, list_values)

                    if item_choose is not None:
                        list_values.append(item_choose)
                    else:
                        repeated_value = True

                if not repeated_value:
                    j -= 1

            player_slection[selections[limit - 1]] = list_values
            limit += 1   

        return player_slection    

                
    def __select_runes(self, file_dumped : dict, list_values : list, 
                       key_selected : str, main_rune_selected : bool) -> str | None:
        # Select a random rune of an specific type of rune.
        key_specific_rune = random.choice(list(file_dumped[key_selected].keys()))
        rune_selected = file_dumped[key_selected][key_specific_rune]
        
        # Insert runes that are not the main runes
        if (rune_selected not in list_values) and (not isinstance(rune_selected, dict)):
            # If main rune wasn't choose and the 3 subrunes were choosen, 
            # force to choose the main rune
            if len(list_values) == 3 and not main_rune_selected:
                return self.__choose_main_rune(file_dumped, key_selected)
            else:
                return rune_selected
        # main rune was choosen by random and main rune wasn't added yet
        elif isinstance(rune_selected, dict) and not main_rune_selected:
            # here rune_selected is a list because it was accesed the values
            # of the pair that holds the main runes
            main_rune_selected = True
            return self.__choose_main_rune(file_dumped, key_selected)
            
        return
    

    def __choose_main_rune(self, file_dumped : dict, type_rune : str):
        key_main_rune = random.choice(list(file_dumped[type_rune]["mainRunes"]).keys())
        value_main_rune = file_dumped[type_rune]["mainRunes"][key_main_rune]
        return value_main_rune
    

    def __select_item(self, file_dumped : dict, list_values : list) -> str | None:
        random_key = random.choice(list(file_dumped.keys()))
        values_selected = file_dumped[random_key]

        if values_selected not in list_values:
            return values_selected
        
        return
    

    async def __embed_msg(self, ctx, user : str, player_selection : dict):
        iteration = 0
        image_file : discord.File = None
        category = ["champion -->", "items -->", "summoners -->", "runes -->"]
        pool_embeds = []
        files_images = []

        for key, values in player_selection.items():
            embed = discord.Embed(
                title=f"{category[iteration]} {user}",
                color=discord.Colour.from_rgb(*colors_runes[list(player_selection)[-1]])
            )      

            try:
                if not isinstance(values, list):
                    values = [values]
                    values[0] = os.path.abspath(values[0])

                for i in range (0, len(values)):
                    path_image = values[i]
                    image_file = discord.File(path_image, filename=path_image.split("\\")[-1])
                    #! CHECK ALL IMAGES ARE INCLUDE IN THE ORDER NEEDED FOR THE FINAL LOOP
                    files_images.append(image_file)
                    
                pool_embeds.append(embed)
                iteration += 1

            except FileNotFoundError:
                raise FileNotFoundError(f"route of file {path_image} wasn't found")
        
        init = 0
        fin = 1
        aumento = 2
        #! CHECK THAT IS ONLY GETTING THE NECESARY IMAGES ON EACH ITERATION
        for emb in pool_embeds:
            if init == 0:
                await ctx.send(embed=emb, file=files_images[0])
            else:
                await ctx.send(embed=emb, files=files_images[init:fin])
            
            init = fin
            fin += aumento
            aumento += 1



    def __get_files(self, path : str, discard_dir : list[str] = None) -> dict[str, list]:
        for parent_dir, sub_dirs, files in os.walk(path):
            if discard_dir is not None:
                sub_dirs = [sub_dir for sub_dir in sub_dirs if os.path.basename(sub_dir) not in discard_dir]
            
            if len(sub_dirs) == 0:
                    return {os.path.basename(parent_dir) : files}
            else:
                files_subdir = dict()

                for directory in sub_dirs:
                    new_path = os.path.join(path, directory)
                    value = self.__get_files(new_path, discard_dir)
                    files_subdir.update(value)
                        
                return files_subdir


    async def __get_num_champs(self, ctx) -> list[discord.Member]:
        try:
            participants = ctx.author.voice.channel.members
            assert participants != None
        except Exception:
            raise Exception("You have to be connected to a voice channel")
        else:
            return participants
    
    
    def __read_num_champions(self) -> int:
        with open(os.path.join(os.getcwd(), "data", "champions_parsed.json")) as f:
            # Get last line of .json which has the number of champs, then split the key-value 
            # and finally take the value. Minus 1 to do not take the possibility of take
            # the pair number_champs : value (it's at the final of the json file)
            return int(f.readlines()[-2:][0].split(":")[1]) - 1

    
    def __get_api_key(self) -> str:
        if load_dotenv('./bot.env'):
            return os.getenv('DEV_RIOT_TOKEN')
        else:
            print("Env file couldn't be open")

    
    def __read_line(self, file : str, line : int) -> str:
        with open(file) as f:
            return next(islice(f, None, line - 1, line), None)


    
json_reader = Game()
#json_reader.randomize_champs()