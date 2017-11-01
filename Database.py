import psycopg2  # Used to connect to the postgresql database
import settings  # Holds necessary globals such as database connection strings obtained from the Config.yaml file
import logging  # Used to log errors and values in the log file
import datetime  # Used to get the date and time

def connect():
    """ Used to open the database connection. Returns whether or not the connection was opened successfully.
    Prints the connection error if an error was occurred.
    :return: Returns whether the database connection was opened successfully via boolean.
    """
    try:
        conn_string = """dbname={} user={} host={} password={}""".format(
        settings.DB_NAME, settings.DB_USER, settings.DB_HOST, settings.DB_PASS)
        conn = psycopg2.connect(conn_string)
        return True
    except psycopg2.Error as e:
        print(e)
        return False


def add_player(server, discord, ign):
    """ Adds a new player to the database.

    :param server: The discord server id that the player is registering in.
    :param discord: The discord id of the player that is registering.
    :param ign: The in-game-name of the player that is registering.
    :return:
    """

    # The sql to be executed, using placeholders for the values to be inserted
    sql = """INSERT INTO "Players"(server, discord, ign) VALUES ('%s', '%s', '%s');"""

    # Executes the sql, filling the placeholders with the arguments
    conn.execute(sql, (server, discord, ign))

# Test sql statement
try:
    sql = """SELECT * FROM "Teams";"""
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    for row in rows:
        print(row)
except psycopg2.Error as e:
    print(e)
