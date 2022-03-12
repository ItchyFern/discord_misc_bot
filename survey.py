from json import loads
import utils


async def survey_cmd(args, cmd_content, message):
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
            # build payload set, check for errors, then add if no errors
            payload_set = []
            error_set = []
            for emoji in msg_json["options"]:
                payload = {}
                payload["msg_id"] = int(msg_send.id)
                payload["emoji"] = emoji.strip()
                payload["role_id"] = int(utils.get_role_id(message.guild.roles, msg_json["options"][emoji]))
                if payload["role_id"] == -1:
                    error_set.append(f"{len(error_set) + 1}. Error with role: {msg_json['options'][emoji]}")
                payload_set.append(payload)

            # if there are no errors
            if error_set == []:
                # add role msg entries for each emote in the payload
                for payload in payload_set: 
                    utils.db_add_role_msg(payload)
            
            # if there are errors, do not add any roles, print errors
            else:
                await message.channel.send("####ERROR####\n Command prevented.\n" + "\n".join(error_set))
                await msg_send.delete()