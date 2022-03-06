import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import re
import utils
from json import loads

prefix = "$"

intents = discord.Intents.default()
intents.members = True
intents.reactions = True
intents.presences = True
client = discord.Client(intents=intents, activity=discord.Activity(type=discord.ActivityType.watching, name=f"for {prefix}help"))

# PROOF OF RUNNING SCRIPT
@client.event
# Print when the program is ready for input
async def on_ready():
    # connect to db
    db, cursor = utils.db_connect()
    # check if table is created for role_emoji
    try: 
        cursor.execute("CREATE TABLE role_emoji ( \
	                        msg_id INT NOT NULL, \
   	                        emoji TEXT NOT NULL, \
                            role_id INT NOT NULL);")
        print("role_emoji table created")
        db.commit()
        print("role_emoji committed")
    except Exception as e:
        print(e)

    # close db connection
    cursor.close()
    db.close()
    print("We have logged in as {0.user}".format(client))

@client.event
async def on_member_join(member):
    # if the author of the message is a bot, do not respond
    if member.bot:
        return
    await client.get_channel(928331889641656322).send(f"Welcome to Friends and Friends of Friends, <@{member.id}>!\nCheck out <#{928335763811213323}> for information about the server such as roles, and <#{928406434285252688}> to suggest changes!")

@client.event
async def on_message(message):
    # if it is a bot messaging, skip
    if message.author.bot:
        return
    
    # check if command symbol is presented
    if str(message.content).startswith(prefix):
        # get the command from the message
        cmd = message.content[1:].split(" ")[0]

        # get command args
        # ex: survey -dr
        args = utils.get_args(message.content)
        
        # get command content
        # start by assuming you will just need to cut the command out
        array_index = 1
        # if arguments is not empty, cut the first two array elements instead (command and args)
        if not args == []:
            array_index = 2
        # remove the first one or two elements of the message (command and potentially args)
        # then rejoin the command using a space
        cmd_content = " ".join(str(message.content).split(" ")[array_index:])



        # if command is help
        if cmd == "help":
            await message.channel.send(f"Use {prefix}survey help\nTo try out the survey builder!")
        # if command is survey command
        if cmd == "survey":
            if cmd_content.strip() == "help":
                await message.channel.send('Use the message below as a template for your survey!\n{"title": "Title message goes here","options": {"emoji1": "option1", "emoji2": "option2" #add more options here if you want, comma separated },"info": "End message goes here"}')
            else:
                
                # convert message to json
                print(cmd_content)
                msg_json = loads(cmd_content)
                print(msg_json)
                msg_send = await message.channel.send(utils.build_message(msg_json))
                for emote in msg_json["options"]:
                    await msg_send.add_reaction(emote.strip())
                
                # if role call in survey
                # build db entry
                # Guild table
                # only owner of the guild can do this message
                if "r" in args and message.author == message.guild.owner:
                    for emoji in msg_json["options"]:
                        payload = {}
                        payload["msg_id"] = int(msg_send.id)
                        payload["emoji"] = emoji
                        payload["role_id"] = int(utils.get_role_id(message.guild.roles, msg_json["options"][emoji]))
                        utils.add_role_msg(payload)


        
        if cmd == "drop_table":
            db, cursor = utils.db_connect()
            print(cursor.execute("DROP TABLE role_emoji;").fetchall())
            cursor.close()
            db.close()

    
        if "d" in args:
            # delete the command message
            await message.delete()
        
                

@client.event
async def on_raw_reaction_add(payload):
    await reaction_helper(payload)
    # Check if the reaction is to the role message
    if payload.message_id == 945682836768309338:
        await change_role(payload)

@client.event
async def on_raw_reaction_remove(payload):
    await reaction_helper(payload)
    # Check if the reaction is to the role message
    if payload.message_id == 945682836768309338:
        await change_role(payload)

async def reaction_helper(payload):
    # connect to db
    db, cursor = utils.db_connect()
    # get all role_emoji msg_ids 
    rows = cursor.execute("SELECT DISTINCT msg_id FROM role_emoji").fetchall()
    print(rows)
    # check if payload msg_id is in role_emoji msg_ids 
    for row in rows:
        if payload.message_id == row[0]:
            await change_role(payload)
    # close db
    cursor.close()
    db.close()
        

async def change_role(payload):
    """
    print(payload.user_id)
    print(payload.event_type)
    # get guild object
    guild = client.get_guild(payload.guild_id)
    print(guild)
    
    # convert emoji to unicode
    e_str = str(payload.emoji)

    # check contents of emoji
    if e_str == "🎊":
        role_id = 928333529161535619
    elif e_str == "🎲":
        role_id = 928333059751821333
    elif e_str == "🔫":
        role_id = 928333452166696980
    elif e_str == "🎵":
        role_id = 928339820957278289
    elif e_str == "📼":
        role_id = 928339868839473192
    elif e_str == "🧐":
        role_id = 928341159808499793
    elif e_str == "🖥️":
        role_id = 928342309182005308
    else:
        print("fail")
        return

    # get member and role objects
    member = guild.get_member(payload.user_id)
    print(member)
    role = guild.get_role(role_id)
    print(role)
    """
    # connect to db
    db, cursor = utils.db_connect()
    # get rows where the payload message id is
    rows = cursor.execute(f"SELECT emoji, role_id FROM role_emoji WHERE msg_id={payload.message_id}").fetchall()
    print(rows)
    role_id = -1

    # loop through all role emojis for that message id
    for row in rows:
        # if payload emoji is equal to the role emoji for that message id
        if str(payload.emoji) == str(row[0].strip()):
            # set role_id to the role id for the emoji for that message id
            role_id = row[1]
    
    # close db connection 
    cursor.close()
    db.close()
    
    if role_id == -1:
        print("role not found in message")
        return False

    # get guild, member, and role
    guild = client.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    role = guild.get_role(role_id)
    if payload.event_type == "REACTION_ADD":
        await member.add_roles(role, reason="React role add")
    else:
        try:
            await member.remove_roles(role, reason="React role remove")
        except:
            print("didn't have the role already")


load_dotenv()
client.run(os.environ['DISCORD_TOKEN'])
