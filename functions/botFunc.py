from __init__ import *


def post_msg(data, msg):
    if data["message_type"] == "private":
        requests.post(
            "http://localhost:3939/send_private_msg",
            json={"user_id": data["target_id"], "message": msg},
        )
    if data["message_type"] == "group":
        requests.post(
            "http://localhost:3939/send_group_msg",
            json={"group_id": data["group_id"], "message": msg},
        )
    return


def get_msg(data, msg):
    if data["message_type"] == "private":
        requests.get(
            "http://localhost:3939/send_private_msg",
            params={"user_id": data["target_id"], "message": msg},
        )
    if data["message_type"] == "group":
        requests.get(
            "http://localhost:3939/send_group_msg",
            params={"group_id": data["group_id"], "message": msg},
        )
    return


def bot_exit(data):
    if data["message_type"] == "group":
        if data["user_id"] == "1220332747":
            get_msg("哼，那我走了")
            requests.get(
                "http://localhost:3939/set_group_leave",
                params={"group_id": data["group_id"]},
            )
        else:
            get_msg("哼，你不是我的主人，我才不听你的呢")
    else:
        get_msg("憋憋")
    return "exit", 200
