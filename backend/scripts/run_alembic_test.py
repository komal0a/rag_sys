from alembic.config import Config
from alembic import command
import os

cfg = Config(r'C:/Users/Komal/OneDrive/Desktop/rag_sys/backend/alembic.ini')
script_location = os.path.abspath(r'C:/Users/Komal/OneDrive/Desktop/rag_sys/backend/alembic')
cfg.set_main_option('script_location', script_location)
cfg.set_main_option('sqlalchemy.url', 'sqlite:///C:/Users/Komal/OneDrive/Desktop/rag_sys/backend/dev_migration.db')
# Fresh upgrade to head
command.upgrade(cfg, 'head')
print('upgrade head applied')
# Now simulate upgrade from 0001: create a DB with only 0001 applied
cfg2 = Config(r'C:/Users/Komal/OneDrive/Desktop/rag_sys/backend/alembic.ini')
cfg2.set_main_option('script_location', script_location)
cfg2.set_main_option('sqlalchemy.url', 'sqlite:///C:/Users/Komal/OneDrive/Desktop/rag_sys/backend/dev_migration_from_0001.db')
# Apply only first revision
command.upgrade(cfg2, '0001_initial')
print('applied 0001 only')
# Now upgrade to head (should apply 0002)
command.upgrade(cfg2, 'head')
print('upgraded from 0001 to head')
