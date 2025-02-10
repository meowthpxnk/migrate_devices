import os
import tarfile
import shutil
from SSHCLI import SshClient

from run import (
    SSH_PORT,
    SSH_SUDO_PASS,
    SSH_USERNAME,
    SSH_IP,
    PHONES_FOLDER,
    logger,
    read_phones,
)
from get_server import get_clicker_server


def tarise(phone):
    # init ssh cli
    server = get_clicker_server(phone)
    cli = SshClient(
        SSH_IP + server,
        SSH_PORT,
        SSH_USERNAME,
        SSH_SUDO_PASS,
        pkey_path="./private_key.pem",
    )

    # --- required params
    root_path = "/clicker"
    m_path = f"{root_path}/migration_data"
    m_phone_path = f"{m_path}/{phone}"
    m_tmp_path = f"{m_phone_path}/tmp"

    curr_path = f"{root_path}/users/{phone}"

    copy_auth_name = "file_auth"
    copy_settings_name = "clicker_settings.yaml"

    tar_name = f"{phone}.tar.gz"
    tar_path = f"{m_phone_path}/{tar_name}"

    migrate_tar_path = f"{PHONES_FOLDER}/{tar_name}"
    migrate_folder_path = f"{PHONES_FOLDER}/{phone}"
    # ---

    # make directories
    cli.execute(f"mkdir {m_path}")
    cli.execute(f"rm -rf {m_phone_path}")

    cli.execute(f"mkdir {m_phone_path}")
    cli.execute(f"mkdir {m_tmp_path}")

    def copy(items):
        for item in items:
            command = f"cp -r {curr_path}/{item} {m_tmp_path}/{item}"
            cli.execute(command)

    def taritase(items):

        command = f"tar -czpf {tar_path} " + " ".join(
            [f"-C {m_tmp_path} {item}" for item in items]
        )
        cli.execute(command)

    copied = [copy_auth_name, copy_settings_name]

    copy(copied)
    taritase(copied)

    cli.execute(f"chown clicker:clicker {tar_path}")

    try:
        shutil.rmtree(migrate_folder_path)
    except:
        pass
    try:
        os.remove(migrate_tar_path)
    except:
        pass

    sftp = cli.client.open_sftp()
    sftp.get(tar_path, migrate_tar_path)
    sftp.close()
    cli.execute(f"rm -rf {m_phone_path}")

    with tarfile.open(migrate_tar_path, "r:gz") as tar:
        tar.extractall(path=migrate_folder_path)

    cli.execute(f"rm -rf {m_phone_path}")
    logger.info(f"Copied {phone} auth folder")
    os.remove(migrate_tar_path)


def migrate_auth():
    phones = read_phones()
    for phone in phones:
        tarise(phone)
