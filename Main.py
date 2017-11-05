# TODO Change the message listeners to use the new return values in Database.py
import discord  # Used to connect to discord
import Settings  # Used to get server settings from the bot
import Database  # Used to initialize the server settings from the bot


# The client that connects the bot to discord
client = discord.Client()


@client.event
async def on_ready():
    """ Is ran when the client is started
    """
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('--------------------')

    # Loads the settings from the database into the Settings.py server settings dictionary.
    Settings.SERVER_SETTINGS = Database.get_settings()


def check_c_symbol(server):
    """ Gets the server symbol from the discord server.

    :param server: The discord id of the server to have the setting checked for.
    :type server: str

    :return: Returns the given server's command symbol/command prefix for messages.
    :rtype: str
    """
    return Settings.SERVER_SETTINGS[server]['c_symbol']


def get_args(message):
    """ Takes a string and separates it into a list of it's arguments.  Arguments are separated by spaces, and
    multi-word arguments are contained within a string.  If the message string starts with the command that was used,
    then the first item in the list will be the command used.

    :param message: The message that you would like to have split into a list of arguments.
    :type message: str

    :return: The list of arguments.
    :rtype: list
    """
    # A tuple that will hold the arguments given in the message
    message_args = list()
    # The temporary argument string used when characters are being read
    temp_arg = ''
    # Says if a quote has been reached once already, so that multi-word arguments can be read
    quote_already_seen = False
    # Loops through all the characters in the message
    for c in message:
        # Reads in the character to temp_arg if it isn't a space or a "
        if ((c != ' ' and c != '"') and not quote_already_seen) or (c != '"' and quote_already_seen):
            # Appends the current character to the temp_arg
            temp_arg += c
        # If the char is the second quote or a space, adds the temp_arg to the args list
        elif ((c == '"' and quote_already_seen) or (c == ' ' and not quote_already_seen)) and len(temp_arg) > 0:
            # Appends the temp arg to the list
            message_args.append(temp_arg)
            # Clears the temp arg for the next loop
            temp_arg = ''
            # Resets the quote_already_seen bool to False for the next iteration of the loop
            quote_already_seen = False
        # If it is the first quote seen, sets quote_already_seen to True
        elif c == '"' and not quote_already_seen:
            # Sets the quote_already_seen value to True
            quote_already_seen = True
    # Adds the last word to the args list
    if len(message_args) != 0 and len(temp_arg) > 0:
        message_args.append(temp_arg)
    # Returns the args list
    return message_args


@client.event
async def on_message(message):
    # Checks to make sure the message was not sent as a private message
    if message.server is not None:
        # Gets the command symbol of the server
        c_symbol = check_c_symbol(message.server.id)
        # Gets the message arguments as a list
        args = get_args(message.content)
        # The number of arguments given
        number_of_args = len(args)
        # Sends the user a private message with a list of the commands that the bot has
        if message.content.startswith("{}help".format(c_symbol)):
            # Sends the user a list of commands that the bot has
            help_string = "The bot has the following commands that it uses. The ***{1}*** server uses `{0}` as its" \
                " command symbol, but beware as other servers may use a different symbol.\n" \
                "`{0}help` - used to send a private message with a list of the commands that the bot has." \
                .format(c_symbol, message.server.name)
            # Sends the help string to the user through private message
            await client.send_message(message.author, help_string)

        # Adds a player to the database. They won't have a team until it is set. Requires the user to give their ign
        elif message.content.startswith("{}addplayer".format(c_symbol)):
            # Checks to see if the user provided the proper number of arguments
            if number_of_args == 2:
                # Add the user to the database
                new_message = Database.add_player(message.server.id, message.author.id, args[1])
                await client.send_message(message.channel, new_message)
            # If the person didn't provide the correct number of arguments
            else:
                # Output the proper use of the command
                await client.send_message(message.channel,
                                          '<@{}> did not use the command properly.  '
                                          'To use, use the following format:\n`{}addplayer your-ign`'
                                          '\nIf your ign is multiple words, place it in quotes, '
                                          'for example `"your-ign"`'.format(message.author.id, c_symbol))

        # Changes the ign of the player in the Database to the given ign.
        elif message.content.startswith("{}changeign".format(c_symbol)):
            # Checks to see if the user provided the proper number of arguments
            if number_of_args == 2:
                # Change the player's ign
                new_message = Database.change_ign(message.server.id, message.author.id, args[1])
            # If the person didn't provide the correct number of arguments
            else:
                # The error message to be outputted.
                new_message = '<@{}> did not use the command properly.  To use, use the following format:\n' \
                              '`{}changeign your-ign`\nIf your ign is multiple words, place it in quotes, for example' \
                              '`"your-ign"`'.format(message.author.id, c_symbol)
            # Outputs the new message through a discord message
            await client.send_message(message.channel, new_message)

        # Mention the players on a given team
        elif message.content.startswith("{}mentionteam".format(c_symbol)):
            # Gets a list of roles mentioned in the message
            roles = message.raw_role_mentions
            # If the correct number of args  was used, including mentioning the role
            if number_of_args == 2 and len(roles) == 1:
                new_message = Database.get_players(message.server.id, roles[0])
            # If the correct number of args wasn't used, output how to use the command
            else:
                new_message = '<@{}> did not use the command properly.  To use, use the following format:\n' \
                              '`{}mentionteam @team-role` where @team-role is the mention of the team\n' \
                              .format(message.author.id, c_symbol)
            # Outputs the new message through a discord message
            await client.send_message(message.channel, new_message)

        # Adds a player to the given team
        # TODO Set privilege of command to be only so captains or admins can do it
        elif message.content.startswith("{}setteam".format(c_symbol)):
            # Gets a list of roles mentioned in the message
            roles = message.raw_role_mentions
            # If the correct number of args  was used, including mentioning the role
            if number_of_args == 2 and len(roles) == 1:
                new_message = Database.set_team(message.server.id, message.author.id, roles[0])
            # If the correct number of args wasn't used, output how to use the command
            else:
                new_message = '<@{}> did not use the command properly.  To use, use the following format:\n' \
                              '`{}setteam @team-role` where @team-role is the mention of the team\n' \
                              .format(message.author.id, c_symbol)
            # Outputs the new message through a discord message
            await client.send_message(message.channel, new_message)


# Runs the discord bot
client.run(Settings.TOKEN)
