import os
import yaml
from dotenv import load_dotenv
from benedict import benedict
from MeowthLogger import Logger
import requests
import traceback

logger = Logger(logger_level="INFO", use_uvicorn=True)

load_dotenv()


PHONES_LIST_FILE_PATH = os.getenv("PHONES_LIST_FILE_PATH")
PHONES_FOLDER = os.getenv("PHONES_FOLDER")
MIGRATE_FOLDER_PATH = os.getenv("MIGRATE_FOLDER_PATH")
CLICKER_IMAGE = os.getenv("CLICKER_IMAGE")
CONNECTOR_URL = os.getenv("CONNECTOR_URL")

API_KEY = os.getenv("API_KEY")


PHONES_SETTINGS_FILE_NAME = "clicker_settings.yaml"

SETTINGS_MAP = {
    "DELETE_DIALOGS": "common.nonDeletableChats",
    "CHATS_MAX_COUNT": "common.offsetDeletableChats",
    "DELETE_GROUPS": "common.groupDeletable",
    "DONT_MARK_MESSAGE_READ": "common.dontMarkMessageRead",
    "MESSAGES_DELETION_DAYS_LIMIT": "common.messageDaysLimit",
}

GATEWAY_KEY = "chat2desk.gateway"

CONNECTOR_SERVERS = {}

REQUEST_HEADERS = {"X-API-Key": API_KEY}


class NotExistConnectorServer(Exception):
    def __init__(self):
        super().__init__("Not exist connector server")


def get_connector_server_short_name(url):
    print(url in CONNECTOR_SERVERS)
    print(url)
    print(CONNECTOR_SERVERS)
    if url not in CONNECTOR_SERVERS:
        raise NotExistConnectorServer

    return CONNECTOR_SERVERS[url]


def delete_device(name):
    r = requests.delete(
        f"{CONNECTOR_URL}/device/{name}", headers=REQUEST_HEADERS
    )

    if not r.ok:
        logger.error(r.text)
        exit(1)

    print(r.text)


def create_connector_server(url):
    short_name = input(f"Enter server name for url {url}:\n")
    data = {"short_name": short_name, "url": url}
    r = requests.post(
        f"{CONNECTOR_URL}/server/create", json=data, headers=REQUEST_HEADERS
    )

    if not r.ok:
        logger.error(r.text)
        exit(1)

    print(r.text)
    CONNECTOR_SERVERS.update({url: short_name})
    return short_name


def get_connector_servers():
    r = requests.get(f"{CONNECTOR_URL}/server", headers=REQUEST_HEADERS)
    if not r.ok:
        logger.error(r.text)
        exit(1)
    data = r.json()

    dict_data = {}

    for server in data:
        dict_data.update({server["url"]: server["short_name"]})

    return dict_data


def create_clicker(name, server_name, envs, with_migration):
    data = {
        "name": name,
        "image": CLICKER_IMAGE,
        "server_short_name": server_name,
        "envs": envs,
    }
    if with_migration:
        data.update(
            {
                "with_migration": True,
            }
        )
    r = requests.post(
        f"{CONNECTOR_URL}/device/create", json=data, headers=REQUEST_HEADERS
    )
    if not r.ok:
        logger.error(r.text)
        exit(1)


def read_phones():
    phones = []

    with open(PHONES_LIST_FILE_PATH) as f:
        while True:
            data = f.readline().replace("\n", "")
            if not data:
                break
            phones.append(data)

    return phones


def get_phone_settings(device_name):
    settings_file_path = os.path.join(
        PHONES_FOLDER, device_name, PHONES_SETTINGS_FILE_NAME
    )

    with open(settings_file_path, encoding="utf-8") as f:
        settings_data = f.read()

    settings_data = yaml.safe_load(settings_data)
    settings_data = benedict(settings_data)

    gw = settings_data[GATEWAY_KEY]
    envs = {k: str(settings_data.get(v)) for k, v in SETTINGS_MAP.items()}
    envs = {k: v for k, v in envs.items() if v is not None}

    return gw, envs


def process_create_clicker(device_name, with_migration):
    gw, envs = get_phone_settings(device_name)

    try:
        server_short_name = get_connector_server_short_name(gw)
    except NotExistConnectorServer:
        server_short_name = create_connector_server(gw)

    print(server_short_name, envs)

    create_clicker(device_name, server_short_name, envs, with_migration)


def process_create_devices(with_migration):
    phones = read_phones()
    for phone in phones:
        logger.info(f"Start processing phone, {phone}")

        try:
            process_create_clicker(phone, with_migration)
        except Exception as err:
            logger.error(
                f"Failed processing phone {phone}, reason: {err}, Traceback: {traceback.format_exc()}"
            )


def process_delete_devices():
    phones = read_phones()
    for phone in phones:
        logger.info(f"Start processing deletion phone, {phone}")

        try:
            delete_device(phone)
        except Exception as err:
            logger.error(
                f"Failed processing phone {phone}, reason: {err}, Traceback: {traceback.format_exc()}"
            )


def main(with_migration=True):
    CONNECTOR_SERVERS.update(get_connector_servers())
    process_create_devices(with_migration)


def main_del():
    process_delete_devices()
