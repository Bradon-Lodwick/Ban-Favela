import discord
import asyncio
import yaml
import queue

# Import the config settings from the config file
with open('Config.yaml') as config_yml:
    cfg = yaml.load(config_yml)

token = cfg['token']

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as %s' % client.user.name)
    print('With id %s' % client.user.id)

check_list = []

@client.event
async def on_message(message):
    if message.content.startswith('!test1'):
        await client.send_message(message.channel, 'you will have 3 seconds to confirm this action using !confirm')
        check_list.append((message.channel, message.author, False))
        await asyncio.sleep(5)
        if any((message.channel, message.author, False) for x in check_list):
            index = check_list.index((message.channel, message.author, False))
        else:
            index = check_list.index((message.channel, message.author, True))
        if check_list[index][2]:
            await client.send_message(message.channel, 'doing the action now')
        else:
            await client.send_message(message.channel, 'you did not confirm this action')
        check_list.pop(index)

    elif message.content.startswith('!test2'):
        if any((message.channel, message.author, False) for x in check_list):
            index = check_list.index((message.channel, message.author, False))
            check_list[index] = (message.channel, message.author, True)
            await client.send_message(message.channel, 'Action confirmed')

client.run(token)
