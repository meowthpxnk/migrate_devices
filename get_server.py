from run import SERVER_MAP_PATH
import json

SERVERS_MAP = {
    "ws-01": "101",
    "ws-02": "102",
    "ws-03": "103",
    "ws-04": "104",
    "ws-05": "105",
    "ws-06": "106",
    "ws-07": "107",
    "ws-08": "108",
    "ws-09": "109",
    "ws-10": "110",
}


def get_clicker_server(phone):
    with open(SERVER_MAP_PATH) as f:
        data = json.loads(f.read())
    server = data[phone]
    return server[SERVERS_MAP]
