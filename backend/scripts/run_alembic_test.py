from alembic.config import Config
from alembic import command
from pathlib import Path

# Portable script to run alembic against local backend directory.
BASE = Path(__file__).resolve().parents[1]  # repository root/backend
ALEMBIC_INI = BASE / 'alembic.ini'
SCRIPT_LOC = str((BASE / 'alembic').resolve())

def _make_cfg(db_path: Path):
	cfg = Config(str(ALEMBIC_INI))
	cfg.set_main_option('script_location', SCRIPT_LOC)
	cfg.set_main_option('sqlalchemy.url', f'sqlite:///{str(db_path)}')
	return cfg

def main():
	db1 = BASE / 'dev_migration.db'
	cfg = _make_cfg(db1)
	# Fresh upgrade to head
	command.upgrade(cfg, 'head')
	print('upgrade head applied (to', db1, ')')

	# simulate upgrade from 0001
	db2 = BASE / 'dev_migration_from_0001.db'
	cfg2 = _make_cfg(db2)
	command.upgrade(cfg2, '0001_initial')
	print('applied 0001 only (to', db2, ')')
	command.upgrade(cfg2, 'head')
	print('upgraded from 0001 to head (on', db2, ')')


if __name__ == '__main__':
	main()
