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
    :return: Returns whether the player was added successfully to the database via boolean.
    """

    # Accesses the global DB variable
    global DB

    # Tries to add the player into the database
    try:
        # The sql to be executed, using placeholders for the values to be inserted
        sql = """INSERT INTO "Players"(server, discord, ign) VALUES (%s, %s, %s);"""
        # Cursor to execute the sql insertion
        cur = DB.cursor()
        # Executes the sql, filling the placeholders with the arguments
        cur.execute(sql, (server, discord, ign))
        # Commits the execution
        DB.commit()
        # Close the cursor
        cur.close()
        # Returns True to signal the connection was successful
        return True
    # Excepts any errors generated while adding the player to the database
    except psycopg2.Error as e:
        # Logs the errors
        logging.error(" {}\n{}".format(datetime.datetime.now(), e))
        # Returns False to signal adding the player was unsuccessful
        return False


def set_team(server, player, team):
    """ Sets a player's team in the database.

    :param server: The dicsord server id of the player.
    :param player: The discord id of the player to have their team set to.
    :param team: The discord id of the team to have the player set to.
    :return: Returns whether setting the team of the player was successful via boolean.
    """

    # Accesses the global DB variable
    global DB

    # Tries to change the team of the player in the database
    try:
        # The sql to be executed, using placeholders for the values to be inserted
        sql = """Update "Players" p
            SET team = t.id
            FROM "Teams" t
            WHERE
                p.server = %s AND
                t.server = p.server AND
                p.discord = %s AND
                t.discord = %s;"""
        # Cursor to execute the sql insertion
        cur = DB.cursor()
        # Executes the sql that changes the player's team
        cur.execute(sql, (server, player, team))
        # Commits the execution
        DB.commit()
        # Close the cursor
        cur.close()
        # Returns True to signal changing the player's team was successful
        return True
    # Excepts any errors generated while changing the player's team in the database
    except psycopg2.Error as e:
        # Logs the errors
        logging.error(" {}\n{}".format(datetime.datetime.now(), e))
        # Returns False to signal changing the player's team was unsuccessful
        return False
