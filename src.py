from run import main as migrate, main_del as delete
from database_parse import save_map
from file_export import migrate_auth


def recreate():
    migrate(with_migration=False)
