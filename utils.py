import json
sample_string = '{"title": "Currently available fan clubs:","options": {":confetti_ball:": "Pokemon Fan",":game_dice:": "DnD Fan",":gun:": "Competitive Gaming Fan",":musical_note:": "Music Fan",":vhs:": "Movie Fan",":face_with_monocle:": "Meme Fan",":desktop:": "Programming Fan" },"info": "React using the corresponding emote to be given the role!"}'

sample_json = json.loads(sample_string)

def save():
    pass


def build_message(j):
    sep = j.get("separator", "|")
    message = []
    # message.append("```")
    message.append(j["title"])
    for key in j["options"]:
        message.append(f"  {key.strip()} {sep} {j['options'][key]}")
    message.append(j["info"])
    # message.append("```")
    return "\n".join(message)
