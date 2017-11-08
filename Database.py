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

    :except psycopg2.DatabaseError: Writes database errors to the error log defined in Settings.py

    :param conn_string: The string to be used to connect to the database.
    Should specify the databases name, user, password, and host address.
    Defaults to the DB_CONN_STRING in the Settings.py file.
    :type conn_string: str

    :param commit: Used to say if the cursor is to be committed to the database.
    Defaults to False so accidental commits are avoided.
    :type commit: bool

    :return: Returns None if an exception occurs, doesn't return anything otherwise.
    :rtype: None
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
        logging.error(" {}\n{}".format(error, datetime.datetime.now))
        # Returns False to signal that the connection failed.
        return False
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

    :return: Returns the server settings as a dictionary, or returns false if the query didn't result in what was
    expected.  If an error occurs in the connect loop, it will return None
    :rtype: dict, bool, None
    """

    # Opens a database connection where commits cannot occur, with a cursor object to use in that connection
    with connect() as cursor:
        # The SQL code to get all of the server settings that are in the Settings table of the database.
        sql = """SELECT server, c_symbol, game_type, current_season, current_round, admin_role, team_size
            FROM "Settings";"""
        # Executes the sql query with the given parameters
        cursor.execute(sql)
        # Checks to make sure the status message is what was expected.
        if cursor.statusmessage == 'SELECT {}'.format(cursor.rowcount):
            # Gets all of the rows obtained from the sql query
            rows = cursor.fetchall()
            # The settings dictionary
            server_settings = dict()
            # Loops through all of the rows in the query
            for row in rows:
                # The server id to be used as the key in the dictionary
                server_id = row[0]
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
                # Assigns the settings of the server into the server_settings dictionary using the server's
                # discord id as the key
                server_settings[server_id] = sub_dictionary
            # Returns the server settings dictionary
            return server_settings
        # Returns false if there was an error getting the settings.
        else:
            return False


def update_settings(server, setting_type, setting_val):
    """ Updates the server settings in the Settings.py file as well as the database.

    :param server: The discord server id of the server to be added.
    :type server: str

    :param setting_type: The setting to be changed in the server.
    :type setting_type: str

    :param setting_val: The value to have the setting changed to.
    :type setting_val: int, str, etc

    :return: Returns whether or not the settings were updated properly.  Returns None if an error occurs in connect
    :rtype: bool, None
    """

    # Opens a database connection where commits can occur, with a cursor object to use in that connection
    # to update the setting in the database
    with connect(commit=True) as cursor:
        # The sql to be executed, using placeholders for the values to be inserted
        sql = """Update "Settings" SET {} = %s WHERE server = %s""".format(setting_type)
        # Executes the sql query with the given parameters
        cursor.execute(sql, (setting_val, server))
        # Checks if the update was executed as expected using the cursor status message
        if cursor.statusmessage == 'UPDATE 1':
            # Updates the settings in the server settings dictionary
            Settings.SERVER_SETTINGS[server][setting_type] = setting_val
            # Returns True stating that the settings was set properly
            return True
        # If the update wasn't executed properly
        else:
            # Returns False if the setting wasn't set properly.
            return False


def check_team_size(server, team):
    """ Gets the current number of players that are on the given team.

    :param server: The discord server id of the server the team belongs to.
    :type server: str

    :param team: The discord id of the team to be checked.
    :type team: str

    :return: The number of players on the team, or false if the settings were grabbed incorrectly.
    Returns None if an error occurs in connect
    :rtype: int, bool, None
    """

    # Opens a database connection where commits can occur, with a cursor object to use in that connection
    with connect() as cursor:
        # SQL code to check the number of players on the team
        sql = """SELECT COUNT(p.id) FROM "Players" p, "Teams" t 
            WHERE t.server=%s AND p.server=t.server AND t.discord=%s AND p.team=t.id"""
        # Executes the sql query with the given parameters
        cursor.execute(sql, (server, team))
        # Checks if the status message is what was expected
        if cursor.statusmessage == 'SELECT 1':
            # Fetches the result of the query that represents the number of people on the given team
            number_of_players = cursor.fetchone()[0]
            # Returns the number of players
            return number_of_players
        # Returns False if there was an error getting the team size
        else:
            return False


def add_player(server, discord, ign):
    """ Adds a player to the database. Uses the cursor object to do any queries.

    :param server: The discord server id of the server to have the player added into.
    :type server: str

    :param discord: The discord id of the player to be added.
    :type discord: str

    :param ign: The in-game-name of the player to be added.
    :type ign: str

    :return: Whether adding the player was successful or not. If an error occurs in connect, returns None.
    :rtype: bool, None
    """

    # Opens a database connection where commits can occur, with a cursor object to use in that connection
    with connect(commit=True) as cursor:
        # SQL code to insert the new player into the database without assigning them a team
        sql = """INSERT INTO "Players"(server, discord, ign) VALUES (%s, %s, %s);"""
        # Executes the sql query with the given parameters
        cursor.execute(sql, (server, discord, ign))
        # Checks to see if the message is as expected
        if cursor.statusmessage == 'INSERT 0 1':
            # Returns True since the status message was as expected
            return True
        # If the proper status message wasn't returned, return False
        else:
            return False


def change_ign(server, discord, ign):
    """ Changes the ign of the given player.

    :param server: The discord server id that the player's ign is to be changed in.
    :type server: str

    :param discord: The discord id of the player you want to change the ign of.
    :type discord: str

    :param ign: The new ign of the player.
    :type ign: str

    :return: Whether the ign of the player was changed successfully or not.
    Returns None if an error occurs in connect.
    :rtype: bool, None
    """

    # Opens a database connection where commits can occur, with a cursor object to use in that connection
    with connect(commit=True) as cursor:
        # SQL code to change the ign of the player in the database
        sql = """UPDATE "Players" SET ign=%s WHERE server=%s AND discord=%s"""
        # Executes the sql query with the given parameters
        cursor.execute(sql, (ign, server, discord))
        # Checks if the status message was as expected
        if cursor.statusmessage == 'UPDATE 1':
            # Returns that the player's ign has been successfully changed
            return True
        # If the status was not as expected, return False
        else:
            return False


def set_team(server, player, team):
    """ Sets a player's team in the database.

    :param server: The discord server id of the player.
    :type server: str

    :param player: The discord id of the player to have their team set to.
    :type player: str

    :param team: The discord id of the team to have the player set to.
    :type team: str

    :return: Whether or not the team was set successfully.  Returns None if an error occurs in connect.
    :rtype: bool, None
    """

    # Opens a database connection where commits can occur, with a cursor object to use in that connection
    with connect(commit=True) as cursor:
        # The sql to be executed, using placeholders for the values to be inserted
        sql = """Update "Players" p SET team = t.id FROM "Teams" t 
        WHERE p.server = %s AND t.server = p.server AND p.discord = %s AND t.discord = %s;"""
        # Executes the sql query with the given parameters
        cursor.execute(sql, (server, player, team))
        # Checks if the status message is as expected
        if cursor.statusmessage == 'UPDATE 1':
            # Returns a message saying the team was added successfully
            return True
        # If the status message is not as expected, return False
        else:
            return False


def get_players(server, team, ign=False):
    """ Gets a string that mentions all the team members of the given team.  Can also get the ign of the players.

    :param server: The discord server id of the server the team exists in.
    :type server: str

    :param team: The discord role id of the team to have the list of players obtained from.
    :type team: str

    :param ign: Flag that decides whether or not the ign of the players should be retrieved as well.
    :type ign: bool

    :return: A list of tuples that contain the discord id's of the players.  Will contain discord id's and the ign
    of the players if the ign flag is True.  Returns False if there is a problem getting the player names.
    Returns None if an error occurs in connect.
    :rtype: list, bool, None
    """

    # Opens a database connection where commits cannot occur, with a cursor object to use in that connection
    with connect() as cursor:
        # If the ign was desired
        if ign:
            # The sql to be executed, using placeholders for the values to be inserted
            sql = """SELECT p.discord, p.ign FROM "Players" p, "Teams" t\n""" \
                """\tWHERE p.server=%s AND t.server=p.server AND t.discord=%s AND p.team=t.id;"""
        # If the ign was not desired
        else:
            # The sql to be executed, using placeholders for the values to be inserted
            sql = """SELECT p.discord FROM "Players" p, "Teams" t\n""" \
                """\tWHERE p.server=%s AND t.server=p.server AND t.discord=%s AND p.team=t.id;"""
        # Executes the sql query with the given parameters
        cursor.execute(sql, (server, team))
        # Checks if the status message is as expected
        if cursor.statusmessage == 'SELECT {}'.format(cursor.rowcount):
            # Gets all of the players from the cursor and returns the list
            return cursor.fetchall()
        # If the status message was not as expected
        else:
            return False


def update_game_scores(server, match_round, team_given, given_team_score, other_team_score):
    """ Update the scores of the given team's game in the given round.  Only needs 1 team to update the proper game.

    :param server: The discord id of the server the game is in.
    :type server: str

    :param match_round: The round to change the score for.
    :type match_round: int

    :param team_given: The discord id of the given team.
    :type team_given: str

    :param given_team_score: The score of the given team.
    :type given_team_score: int

    :param other_team_score: The score of the other team.
    :type other_team_score: int

    :return: Returns the success of updating the game scores.
    :rtype: bool
    """

    # Opens a database connection where commits cannot occur, with a cursor object to use in that connection
    with connect(commit=True) as cursor:
        # The sql to be executed to update the score of the game
        sql = """UPDATE "Matches" m\n\tSET team_1_score=(CASE WHEN m.team_1=t.id THEN %s ELSE %s END), 
            team_2_score=(CASE WHEN m.team_2=t.id THEN %s ELSE %s END) FROM "Teams" t\n\tWHERE m.round=%s AND 
            t.discord=%s AND (m.team_1=t.id OR m.team_2=t.id) AND m.server=%s AND m.team_1_score IS NULL 
            AND m.team_2_score IS NULL"""
        # Attempts to execute the sql to update the game results
        cursor.execute(sql, (given_team_score, other_team_score, given_team_score, other_team_score, match_round,
                             team_given, server))
        # Checks if the status message is as expected
        if cursor.statusmessage == 'UPDATE 1':
            # Returns a message saying the team was added successfully
            return True
        # If the status message is not as expected, return False
        else:
            return False
