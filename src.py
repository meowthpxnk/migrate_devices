from run import main as migrate, main_del as delete
from database_parse import save_map
from file_export import migrate_auth
from run import get_connector_servers as test


def recreate():
    migrate(with_migration=False)
