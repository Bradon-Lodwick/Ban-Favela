"""
todo: don't think I can have Settings.py and Database.py import each other
"""

import psycopg2  # Used to connect to the postgresql database
import Settings  # Holds necessary globals such as database connection strings obtained from the Config.yaml file
import logging  # Used to log errors and values in the log file
import datetime  # Used to log times of errors
from contextlib import contextmanager  # Used to make connecting to the database and logging errors easier

# Sets up error logging
logging.basicConfig(filename=Settings.LOG, level=logging.ERROR)  # Sets errors to be written to


@contextmanager
def connect(conn_string=Settings.DB_CONN_STRING, commit=False):
    """ Used to connect to the database. Use the cursor object to do any queries.

    :param conn_string: The string to be used to connect to the database.
    Should specify the databases name, user, password, and host address.
    Defaults to the DB_CONN_STRING in the Settings.py file.
    :type conn_string: str

    :param commit: Used to say if the cursor is to be committed to the database.
    Defaults to False so accidental commits are avoided.
    :type commit: bool
    """

    try:
        # Connects to the database
        db = psycopg2.connect(conn_string)
        # Cursor to be used when interacting with the database
        cursor = db.cursor()
        # Yield the cursor so it can be used in other functions
        yield cursor
    # Excepts any database errors so they can be handled and logged
    except psycopg2.DatabaseError as e:
        # Gets the argument variables
        error, = e.args
        # Logs the error and the time of the error
        logging.error(" {}\n{}".format(error.message, datetime.datetime.now))
        # Changes the return_val to False so False will be returned in the finally clause.
        return_val = False
    # If an error doesn't occur, determines whether a commit is to be made
    else:
        # If a commit was to be made
        if commit:
            # Commits the database
            db.commit()
        # If a commit wasn't to be made
        else:
            # Rolls the database back
            db.rollback()
    # Finally the database connection will be closed
    finally:
        # Closes the database
        db.close()


def get_settings():
    """ Gets the server settings from the database.

    :return: Returns the server settings
    :rtype: dict
    """

    # Opens a database connection where commits cannot occur, with a cursor object to use in that connection
    with connect() as cursor:
        # The SQL code to get all of the server settings that are in the Settings table of the database.
        sql = """SELECT server, c_symbol, game_type, current_season, current_round, admin_role, team_size
            FROM "Settings";"""
        # Executes the sql query with the given parameters
        cursor.execute(sql)
        # Gets all of the rows obtained from the sql query
        rows = cursor.fetchall()
        # The settings dictionary
        server_settings = dict()
        # Loops through all of the rows in the query
        for row in rows:
            # The server id to be used as the key in the dictionary
            id = row[0]
            # The sub-dictionary that will hold all the settings for the current server
            sub_dictionary = dict()
            # Assigns the command symbol of the server
            sub_dictionary['c_symbol'] = row[1]
            # Assigns the game type of the server
            sub_dictionary['game_type'] = row[2]
            # Assigns the current season of the server
            sub_dictionary['current_season'] = row[3]
            # Assigns the current round of the server
            sub_dictionary['current_round'] = row[4]
            # Assigns the admin role of the server
            sub_dictionary['admin_role'] = row[5]
            # Assigns the team size of the server
            sub_dictionary['team_size'] = row[6]
            # Assigns the settings of the server into the server_settings dictionary using the server's discord id as
            # they key
            server_settings[id] = sub_dictionary
        # Returns the server settings dictionary
        return server_settings


def update_settings(server, setting_type, setting_val):
    """ Updates the server settings in the Settings.py file as well as the database.

    :param server: The discord server id of the server to be added.
    :type server: str

    :param setting_type: The setting to be changed in the server.
    :type setting_type: str

    :param setting_val: The value to have the setting changed to.
    :type setting_val: int, str, etc
    """
    # Opens a database connection where commits can occur, with a cursor object to use in that connection
    # to update the setting in the database
    with connect(commit=True) as cursor:
        # The sql to be executed, using placeholders for the values to be inserted
        sql = """Update "Settings" SET %s = $s WHERE p.server = %s"""
        # Executes the sql query with the given parameters
        cursor.execute(sql, (setting_type, setting_val, server))

    # Changes the value of the setting in the Settings.py dictionary
    Settings.SERVER_SETTINGS[server][setting_type] = setting_val


def add_player(server, discord, ign):
    """ Adds a player to the database. Uses the cursor object to do any queries.

    :param server: The discord server id of the server to have the player added into.
    :type server: str

    :param discord: The discord id of the player to be added.
    :type discord: str

    :param ign: The in-game-name of the player to be added.
    :type ign: str
    """

    # Opens a database connection where commits can occur, with a cursor object to use in that connection
    with connect(commit=True) as cursor:
        # SQL code to insert the new player into the database without assigning them a team
        sql = """INSERT INTO "Players"(server, discord, ign) VALUES (%s, %s, %s);"""
        # Executes the sql query with the given parameters
        cursor.execute(sql, (server, discord, ign))


def set_team(server, player, team):
    """ Sets a player's team in the database.

    :param server: The discord server id of the player.
    :type server: str

    :param player: The discord id of the player to have their team set to.
    :type player: str

    :param team: The discord id of the team to have the player set to.
    :type team: str
    """

    # Opens a database connection where commits can occur, with a cursor object to use in that connection
    with connect(commit=True) as cursor:
        # The sql to be executed, using placeholders for the values to be inserted
        sql = """Update "Players" p SET team = t.id FROM "Teams" t 
        WHERE p.server = %s AND t.server = p.server AND p.discord = %s AND t.discord = %s;"""
        # Executes the sql query with the given parameters
        cursor.execute(sql, (server, player, team))


#get_settings()
#update_settings('360201172851621890', 'c_symbol', '@')
print('temp')
