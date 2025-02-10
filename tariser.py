from run import read_phones
from get_server import get_clicker_server, SERVERS_MAP


def tarise():
    phones = read_phones()

    for phone in phones:
        server = get_clicker_server(phone)
        address = SERVERS_MAP[server]
