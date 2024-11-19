import json
import urllib3
import discord
from discord.ext import commands

# URL to json that contain champs https://ddragon.leagueoflegends.com/cdn/14.23.1/data/en_US/champion.json

class Game(commands.Cog):
    def __init__(self):
        """Constructor to initialize the Game feature"""
        self.champs_pool = []

    @staticmethod
    def get_desc() -> str:
        return ("""$game it's used to select a random champ and runes between all members
                that are in the same voice channel playing League of Legend\n""")
    
    def read_json(self) -> None:
        http = urllib3.PoolManager(1)
        url = "https://ddragon.leagueoflegends.com/cdn/14.23.1/data/en_US/champion.json"

        response = http.request("GET", url)

        if response.status == 200:
            data = json.loads(response.data.decode())

            for data_field in data["data"].values(): 
                    self.champs_pool.append(data_field["name"])


# json_reader = Game()
# json_reader.read_json()