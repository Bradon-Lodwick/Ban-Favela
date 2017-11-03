import yaml  # Used to load the settings from the Config.yaml file
import Database  # Used to load the discord server settings into a dictionary from the database

# Load the config file into a dictionary
with open("""Config.yaml""") as cfg_file:
    cfg = yaml.load(cfg_file)

# Loads all of the database information from the config file
DB_HOST = cfg['database']['host']  # The host address of the database
DB_USER = cfg['database']['user']  # The user of the database
DB_PASS = cfg['database']['password']  # The password of the user connecting to the database
DB_NAME = cfg['database']['name']  # The name of the database being connected to
# The string to be used to connect to the postgres database
DB_CONN_STRING = """dbname={} user={} host={} password={}""".format(
    DB_NAME, DB_USER, DB_HOST, DB_PASS
)

# Loads the discord bot token from the config file
TOKEN = cfg['token']

# The location for the log file loaded from the config file
LOG = cfg['log']

# Loads the discord server settings from the database
SERVER_SETTINGS = Database.get_settings()
