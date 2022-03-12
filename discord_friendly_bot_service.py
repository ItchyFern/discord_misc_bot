import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import re
import utils
from survey import survey_cmd
from json import loads

prefix = "$"

# Set all intents
intents = discord.Intents.default()
intents.bans = True  # for logging
intents.guilds = True  
intents.invites = True  # for logging
intents.members = True
intents.presences = True  # for logging
intents.reactions = True  
intents.voice_states = True  # for logging

# initialize the client
client = discord.Client(intents=intents, activity=discord.Activity(type=discord.ActivityType.watching, name=f"for {prefix}help"))

# PROOF OF RUNNING SCRIPT
@client.event
# Print when the program is ready for input
async def on_ready():
    utils.db_build()
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
        print(args)
        
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
            survey_cmd(args, cmd_content, message)
                    
        
        if cmd == "remove_role_msg" and message.author == message.guild.owner:
            # get replied to message
            if message.reference != None:
                #connect to db
                db, cursor = utils.db_connect()
                #remove rows from role_emoji where message id = role_emoji.msg_id
                msg_id = message.reference.message_id 
                cursor.execute(f"DELETE FROM role_emoji WHERE msg_id={msg_id}")

                #commit the deletion
                db.commit()
                await message.channel.send("Deleted msg from database")
                #close the db
                cursor.close()
                db.close()
    
        if "d" in args:
            # delete the command message
            await message.delete()
        
#####################
# Reaction Commands #
#####################
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
    #print(rows)
    # check if payload msg_id is in role_emoji msg_ids 
    for row in rows:
        if payload.message_id == row[0]:
            await change_role(payload)
    # close db
    cursor.close()
    db.close()

async def change_role(payload):
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

##################
# Logging Events #
##################
@client.event
async def on_error(event, *args, **kwargs):
    pass

@client.event
async def on_raw_message_delete(payload):
    pass

@client.event
async def on_raw_message_edit(payload):
    pass

@client.event
async def on_guild_channel_delete(channel):
    pass

@client.event
async def on_guild_channel_create(channel):
    pass

@client.event
async def on_guild_channel_update(before, after):
    pass

@client.event
async def on_member_join(member):
    pass

@client.event
async def on_member_remove(member):
    pass

@client.event
async def on_member_update(before, after):
    pass

@client.event
async def on_guild_role_create(role):
    pass

@client.event
async def on_guild_role_delete(role):
    pass

@client.event
async def on_guild_role_update(before, after):
    pass

@client.event
async def on_voice_state_update(member, before, after):
    pass

@client.event
async def on_member_ban(guild, user):
    pass

@client.event
async def on_member_unban(guild, user):
    pass

@client.event
async def on_invite_create(invite):
    pass

@client.event
async def on_invite_delete(invite):
    pass

# load from .env to get discord token
load_dotenv()
client.run(os.environ['DISCORD_TOKEN'])
