import os
import discord
from discord.ext import commands
from riotwatcher import LolWatcher, ApiError
from dotenv import load_dotenv

# URL to json that contain champs https://ddragon.leagueoflegends.com/cdn/14.23.1/data/en_US/champion.json

class Game(commands.Cog):
    def __init__(self):
        """Constructor to initialize the Game feature"""
        self.number_champs = 0
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
        self.__read_num_champions()
        participants = await self.__get_num_champs(ctx)
        
        me = self.watcher.summoner.by_name(self.region, "Lauriita18")
        print(me)
        # Get riot id of each one in the channel.

        # select for each one randomly champ, runes and summoners

        # Add all of them to an embed message

        # send that embed through channel

    async def __get_num_champs(self, ctx) -> list:
        try:
            participants = ctx.author.voice.channel.members
            assert participants != None
        except Exception:
            print("You have to be connected to a voice channel")
            raise
        else:
            return participants
    
    def __read_num_champions(self) -> None:
        with open(os.path.join(os.getcwd(), "data", "champions_parsed.json")) as f:
            # Get last line of .json which has the number of champs, then split the key-value 
            # and finally take the value
            self.number_champs = f.readlines()[-2:][0].split(":")[1]

    
    def __get_api_key(self) -> str:
        if load_dotenv('./bot.env'):
            return os.getenv('DEV_RIOT_TOKEN')
        else:
            print("Env file couldn't be open")

    

# json_reader = Game()
# json_reader.read_num_champions()