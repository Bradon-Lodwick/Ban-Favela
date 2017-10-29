import yaml  # Used to get variables from the configuration file
import psycopg2  # Used to connect to the postgresql database

# Import the config settings from the config file
with open('Config.yaml') as config_yml:
    cfg = yaml.load(config_yml)

host = cfg['database']['host']  # The host address for the database
user = cfg['database']['user']  # The username for the database
password = cfg['database']['password']  # The password for the database
