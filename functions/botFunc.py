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
        if data["user_id"] == 1:
            get_msg(data, "哼，那我走了")
            requests.get(
                "http://localhost:3939/set_group_leave",
                params={"group_id": data["group_id"]},
            )
        else:
            get_msg(data, "哼，你不是我的主人，我才不听你的呢")
    else:
        get_msg(data, "憋憋")
    return "exit", 200


def bilibili_search(data):
    av = None
    vid = str(data["raw_message"])
    debug.print(vid)
    if vid.startswith("bv"):
        av = "bv"
        vid = "BV" + vid[2:]
    if vid.startswith("av"):
        av = "a"
        vid = vid[2:]
    if av == None:
        return get_msg(data, "参数错误！使用av号请以av开头"), 200
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Accept": "*/*",
        "Host": "api.bilibili.com",
        "Connection": "keep-alive",
    }
    res = requests.get(
        f"https://api.bilibili.com/x/web-interface/view?{av}id={vid}",
        headers=headers,
    )
    if res.status_code == 200:
        res = json.loads(res.text)
        debug.print(res["code"])
        # 0：成功 -400：请求错误 -403：权限不足 -404：无视频 62002：稿件不可见 62004：稿件审核中 62012：仅UP主自己可见
        # if res["code"] == -400:
        #     return get_msg(data, "B站服务器有问题呢，请稍后再试"), 200
        if res["code"] != 0:
            return get_msg(data, "视频不存在呢"), 200

        pic = {"type": "image", "data": {"file": res["data"]["pic"]}}
        localtime = time.localtime(res["data"]["pubdate"])
        pubdate = time.strftime("%y-%m-%d  %H:%M:%S", localtime)
        desc = str(res["data"]["desc"])
        if len(desc) > 85:
            desc = desc[:80] + "……"
        txt = res["data"]["title"] + (
            f"（共{res["data"]["videos"]}P）\n" if res["data"]["videos"] > 1 else "\n"
        )
        txt += (
            f"{res["data"]["bvid"]}  [AV{res["data"]["aid"]}]\n"
            f"https://b23.tv/{res["data"]["bvid"]}\n"
            f"分区：{res["data"]["tname"]}\n"
            f"发布时间：{pubdate}\n"
        )
        txt += f"简介：\n{desc}\n" if desc != "" else ""
        txt += (
            f"UP主：{res["data"]["owner"]["name"]}（https://space.bilibili.com/{res["data"]["owner"]["mid"]}）\n"
            f"播放：{res["data"]["stat"]["view"]} | 点赞：{res["data"]["stat"]["like"]}\n"
            f"投币：{res["data"]["stat"]["coin"]} | 收藏：{res["data"]["stat"]["favorite"]}\n"
            f"回复：{res["data"]["stat"]["reply"]} | 分享：{res["data"]["stat"]["share"]}"
        )
        # 弹幕danmaku
    else:
        return get_msg(data, "bot被玩坏了╥﹏╥，请稍后再试"), 400

    reply = [
        {"type": "reply", "data": {"id": data["message_id"]}},
        pic,
        {
            "type": "text",
            "data": {"text": txt},
        },
    ]
    post_msg(data, reply)
    return "bilibili", 200
