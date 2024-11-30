import json
import urllib3
import os

def write_reduce_champs():
    file_name = "data/champions_red.json"
    champ = dict()
    relative_path = os.path.relpath((os.path.join(os.path.dirname(__file__), "assets", 
                                    "game_images", "champion")), "C:\\Users\\Dani\\Desktop\\Python Bot")
    http = urllib3.PoolManager(1)
    url = "https://ddragon.leagueoflegends.com/cdn/14.23.1/data/en_US/champion.json"

    response = http.request("GET", url)

    if response.status == 200:
        data = json.loads(response.data.decode())
        
        
        for values in data["data"].values():
            # The name is the same as the image associated to this champ
            champ_name = values["name"]

            if champ_name:
                champ_image = f"{champ_name.replace(' ', '')}.png" 
                image_path = f"{relative_path}\\{champ_image}"
            
                champ[champ_name] = image_path

    try: 
        with open(file_name, "x", encoding="utf-8") as out_file:
            json.dump(champ, out_file, indent=4)

    except FileExistsError:
        print(f"{file_name} alredy exists")


def remove_runes_duplicated(parent : str, grand_parent : str, depth : int):
    with os.scandir(parent) as direc:
        num_files = 0

        for sub_dirs in direc:
            parent_child = os.path.join(parent, sub_dirs.name)

            if sub_dirs.is_dir():
                remove_runes_duplicated(parent_child, parent+"\\", depth + 1)
            elif depth > 1:
                os.system(f'move "{parent_child}" "{grand_parent}"')
                num_files = num_files + 1

        if num_files <= 1 and depth > 1: 
            os.removedirs(parent)


def create_json_dirs(parent : str, depth : int) -> dict[str, str] | None: 
    with os.scandir(parent) as direc:
        dict_json = {}

        for file in direc:
            parent_child = os.path.join(parent, file.name)
            
            if file.is_dir():
               dict_json[parent_child] = create_json_dirs(parent_child, depth + 1)
            else:
                rel_path_values = os.path.relpath(os.path.join(parent_child, file),
                                                  os.getcwd()) 
                rel_path_key = os.path.relpath(file, os.getcwd())
                dict_json[file.name] = rel_path_values

        if depth == 1:
            try: 
                new_json_file = os.path.join(os.getcwd(), "data", parent.split("\\")[-1])
                                
                with open(new_json_file+".json", "w", encoding="utf-8") as out_file:
                    json.dump(dict_json, out_file, indent=4)

            except (IOError, OSError):
                print(f"An unexpected error ocurred when writing on: {new_json_file}")
        else: 
            return dict_json
                




if __name__ == "__main__":
    # write_reduce_champs()
    def_route = os.path.join(os.path.dirname(__file__), "assets", "game_images")
    create_json_dirs(def_route, 0)