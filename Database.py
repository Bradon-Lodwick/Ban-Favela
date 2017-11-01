import psycopg2  # Used to connect to the postgresql database
import Settings  # Holds necessary globals such as database connection strings obtained from the Config.yaml file
import logging  # Used to log errors and values in the log file
import datetime  # Used to log times of errors


# Holds the database connection after running connect()
DB = None

# Sets up error logging
logging.basicConfig(filename=Settings.LOG, level=logging.ERROR)


def connect():
    """ Used to open the database connection. Returns whether or not the connection was opened successfully.
    Prints the connection error if an error was occurred.

    :return: Returns whether the database connection was opened successfully via boolean.
    """

    # Accesses the global DB variable
    global DB

    # Tries to access the database
    try:
        # The string used to connect to the database
        conn_string = """dbname={} user={} host={} password={}""".format(
            Settings.DB_NAME, Settings.DB_USER, Settings.DB_HOST, Settings.DB_PASS)
        # Connects to the database
        DB = psycopg2.connect(conn_string)
        # Returns True to signal the connection was successful
        return True
    # Excepts any errors generated while connecting to the database for logging purposes
    except psycopg2.Error as e:
        # Logs the errors
        logging.error(" {}\n{}".format(datetime.datetime.now(), e))
        # Returns False to signal the connection was unsuccessful
        return False


def add_player(server, discord, ign):
    """ Adds a new player to the database.

    :param server: The discord server id that the player is registering in.
    :param discord: The discord id of the player that is registering.
    :param ign: The in-game-name of the player that is registering.
    :return:
    """

    # Accesses the global DB variable
    global DB

    # The sql to be executed, using placeholders for the values to be inserted
    sql = """INSERT INTO "Players"(server, discord, ign) VALUES ('%s', '%s', '%s');"""

    # Executes the sql, filling the placeholders with the arguments
    DB.execute(sql, (server, discord, ign))


connect()
