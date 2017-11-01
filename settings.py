import yaml  # Used to load the settings from the Config.yaml file

# Load the config file into a dictionary
with open("""Config.yaml""") as cfg_file:
    cfg = yaml.load(cfg_file)

# Loads all of the database information
DB_HOST = cfg['database']['host']  # The host address of the database
DB_USER = cfg['database']['user']  # The user of the database
DB_PASS = cfg['database']['password']  # The password of the user connecting to the database
DB_NAME = cfg['database']['name']  # The name of the database being connected to

# Loads the discord bot token
TOKEN = cfg['token']

# The location for the log file
LOG = cfg['log']
