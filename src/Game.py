import json
import os
import random
import discord
from discord.ext import commands
from itertools import islice
from riotwatcher import LolWatcher, ApiError
from dotenv import load_dotenv

# URL to json that contain champs https://ddragon.leagueoflegends.com/cdn/14.23.1/data/en_US/champion.json

class Game(commands.Cog):
    def __init__(self):
        """Constructor to initialize the Game feature"""
        self.data_assets = self.__get_files(os.path.join(os.getcwd(), "assets"), ["champion"])
        self.__TOKEN_RIOT = self.__get_api_key()
        self.watcher = LolWatcher(self.__TOKEN_RIOT)
        assert self.watcher != None, "Chek the Riot token again, it might be disable"
        self.region = "euw1"


    @staticmethod
    def get_desc() -> str:
        return ("""$game it's used to select a random champ and runes between all members
                that are in the same voice channel playing League of Legend\n""")
    
    @commands.command()
    async def randomize_champs(self, ctx) -> None:
        """Return all members that are in the same channel who typed this functionality
        """
        
        participants = await self.__get_num_champs(ctx)
        
        
        # me = self.watcher.summoner.by_name(self.region, "Lauriita18")
        
        # Get riot id of each one in the channel.



        # select for each one randomly champ, runes and summoners
        with open(os.path.join(os.getcwd(), "data", "champions_parsed.json")) as f:
            champs = json.load(f)
            for player in participants:
                player_slection = dict()
                champ_name, champ_image = random.choice(list(champs.items()))
                player_slection[champ_name] = champ_image
                runes_selected = False

                for key in self.data_assets:
                    if runes_selected:
                        break

                    limit = 4
                    if key == "item":
                        limit = 3
                    elif key == "summoner":
                        limit = 2
                    else:
                        rune_selection = [rune for rune in self.data_assets 
                                          if rune not in ["item", "summoner"]]
                        key = random.choice(rune_selection)
                        runes_selected = True

                    key_values = []
                    while len(key_values) < limit:
                        value = random.choice(self.data_assets[key])

                        if value not in key_values:
                            key_values.append(value) 
                    
                    player_slection[key] = key_values
                
                print(f"{player.name} has to choose the following:\n{player_slection}")
                

        # Add all of them to an embed message

        # send that embed through channel




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