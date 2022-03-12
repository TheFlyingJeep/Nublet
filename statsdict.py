import requests
with open("api_key.txt", "r") as apik:
    api_key = apik.read()


async def getstat(val, mode):
    api = requests.get(f"https://api.hypixel.net/player?key={api_key}&uuid={val}").json()["player"]
    stats = {
        "bridge": api["achievements"]["duels_bridge_wins"] if "duels_bridge_wins" in api["achievements"] else 0,
        "sw": api["stats"]["Duels"]["sw_duel_wins"] if "sw_duel_wins" in api["stats"]["Duels"] else 0,
        "sw_doubles": api["stats"]["Duels"]["sw_doubles_wins"] if "sw_doubles_wins" in api["stats"]["Duels"] else 0,
        "bow": api["stats"]["Duels"]["bow_duel_wins"] if "bow_duel_wins" in api["stats"]["Duels"] else 0,
        "op": api["stats"]["Duels"]["op_duel_wins"] if "op_duel_wins" in api["stats"]["Duels"] else 0,
        "bowspleef": api["stats"]["Duels"]["bowspleef_duel_wins"] if "bowspleef_duel_wins" in api["stats"]["Duels"] else 0
    }#FOR FUCKS SAKE JUST ADD AN OVERALL SKYWARS DUELS WINS MODE

    if mode == "sw":
        data = stats["sw"] + stats["sw_doubles"]
    else:
        data = stats[mode]
    return data
