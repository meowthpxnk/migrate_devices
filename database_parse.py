from SSHCLI import SshClient
import json
import pandas as pd
from run import (
    SSH_PORT,
    SSH_SUDO_PASS,
    SERVER_MAP_PATH,
)
import sqlite3

DATABASE_PATH = "new_connector.db"
STATUS_ENUM = {
    1: "LOST_REGISTRATION",
    2: "OFFLINE",
    "OFFLINE": "OFFLINE",
    3: "ONLINE",
    4: "STARTING",
    5: "LOST_CONNECT",
    6: "SIGNIN",
}


def restore_data():
    cli = SshClient(
        "192.168.88.32",
        SSH_PORT,
        "connector",
        SSH_SUDO_PASS,
        pkey_path="./private_key.pem",
    )

    db_path = f"/home/connector/whatsapp_connector/app/{DATABASE_PATH}"
    sftp = cli.client.open_sftp()
    sftp.get(db_path, f"./{DATABASE_PATH}")
    sftp.close()


def db_get_data(db_path: str):
    request = "SELECT d.phone, d.server_id, d.port, d.clicker_status FROM devices as d"
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    request_result = list(cursor.execute(request))
    connection.close()
    return request_result


def get_clickers():
    final_data = []
    for clicker in db_get_data(DATABASE_PATH):
        server = (
            f"ws-{clicker[1] if clicker[1] > 9 else '0' + str(clicker[1])}"
        )

        final_data.append(
            {
                "phone": clicker[0],
                "server": server,
                "port": clicker[2],
                "status": STATUS_ENUM[clicker[3]],
            }
        )
    return final_data


def get_server_map():
    data = get_clickers()
    map = {}
    for device in data:
        map.update({device["phone"]: device["server"]})
    return map


def save_map():
    map = get_server_map()
    with open(SERVER_MAP_PATH, "w") as f:
        f.write(json.dumps(map, indent=4))


def save_to_excel(file_name="clickers_data.xlsx"):
    data = get_clickers()
    df = pd.DataFrame(data)
    df.to_excel(file_name, index=False)
    print(f"Data successfully saved to {file_name}")


def update_map():
    restore_data()
    save_map()


def update_table():
    restore_data()
    save_map()
