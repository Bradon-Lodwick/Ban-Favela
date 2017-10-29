import yaml  # Used to get variables from the configuration file
import psycopg2  # Used to connect to the postgresql database

# Import the config settings from the config file
with open('Config.yaml') as config_yml:
    cfg = yaml.load(config_yml)

host = cfg['database']['host']  # The host address for the database
user = cfg['database']['user']  # The username for the database
password = cfg['database']['password']  # The password for the database
name = cfg['database']['name']  # The name of the database

# Connection to the database using config settings
try:
    conn_string = "dbname='" + name + "' user='" + user + "' host='" + host + "' password='" + password + "'"
    conn = psycopg2.connect(conn_string)
except psycopg2.Error as e:
    print(e)

# Test sql statement
try:
    sql = "SELECT * FROM players"
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    for row in rows:
        print(row)
except psycopg2.Error as e:
    print(e)
