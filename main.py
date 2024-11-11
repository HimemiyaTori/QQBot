from __init__ import *


def arc_b30(data):
    get_msg(data, "正在获取B30，需要约20秒，请稍等。注意撤回你的cookie哦！")
    parts = data["raw_message"].split(" ", 2)
    cookie = parts[2] if len(parts) > 2 else ""

    try:
        b30(cookie)
    except:
        get_msg(data, "获取失败，请稍后重试或提供新的cookie")
        debug.print(cookie)
        return "nothing", 200

    atImage = [
        {"type": "reply", "data": {"id": data["message_id"]}},
        {
            "type": "image",
            "data": {"file": "file:///sdcard/Pictures/image.jpg"},
        },
    ]
    post_msg(data, atImage)
    return atImage, 200


app = Flask(__name__)


@app.route("/", methods=["POST"])
def post_data():
    # 获取请求体中的数据
    global data
    data = request.get_json(force=True)
    # 调试，原样返回数据
    jsonify(data)
    debug.print(data)

    if "raw_message" not in data:
        return "nothing", 200

    if "[CQ:at,qq=3937926418] " in data["raw_message"]:
        data["raw_message"] = data["raw_message"].replace("[CQ:at,qq=3937926418] ", "")
        if data["raw_message"] == "":
            return (
                get_msg(
                    data,
                    "功能列表如下<必填参数>(选填参数)[替代参数]：\n"
                    "1. arc b30 <cookie>：根据给定的cookie查询arcaea官网的b30分表\n"
                    "2. bot退群\n"
                    "3. mai update\n"
                    "4. mai[chu]找歌 <歌名[id114514]>：根据歌名或id查询歌曲信息\n"
                    "5. mai别名 <歌名[id114514]>：根据歌名或id查询歌曲别名\n"
                    "6. mai[chu]随机 (紫[白][宴]13+)\n"
                    "7. b30[b50] (用户名)：生成成绩图",
                ),
                200,
            )
        data["raw_message"] = (
            str(data["raw_message"])[:2].lower() + str(data["raw_message"])[2:]
        )
        if data["raw_message"].startswith("bv") or data["raw_message"].startswith("av"):
            return bilibili_search(data)

    if data["raw_message"].startswith("arc b30"):
        return arc_b30(data)

    if data["raw_message"] == "bot退群":
        return bot_exit(data)

    if data["raw_message"].startswith("b50") or data["raw_message"].startswith("B50"):
        return mai_b50(data)
    if data["raw_message"] == "mai update":
        return mai_update(data)
    if data["raw_message"].startswith("mai别名"):
        return mai_alia(data)
    if data["raw_message"].startswith("mai查歌") or data["raw_message"].startswith(
        "mai找歌"
    ):
        return mai_search(data)
    if (
        data["raw_message"].startswith("mai随机")
        or data["raw_message"].startswith("mai随歌")
        or data["raw_message"].startswith("mai随个歌")
        or data["raw_message"].startswith("mai随首歌")
        or data["raw_message"].startswith("mai随机歌曲")
    ):
        return mai_random(data)

    if data["raw_message"].startswith("b30") or data["raw_message"].startswith("B30"):
        return chu_b30(data)
    if data["raw_message"] == "chu update":
        return chu_update(data)
    if data["raw_message"].startswith("chu查歌") or data["raw_message"].startswith(
        "chu找歌"
    ):
        return chu_search(data)
    if (
        data["raw_message"].startswith("chu随机")
        or data["raw_message"].startswith("chu随歌")
        or data["raw_message"].startswith("chu随个歌")
        or data["raw_message"].startswith("chu随首歌")
        or data["raw_message"].startswith("chu随机歌曲")
    ):
        return chu_random(data)
    if data["raw_message"].startswith("chu别名"):
        return chu_alia(data)

    return "nothing", 200


if __name__ == "__main__":
    app.run(debug=True, port=8889, host="localhost")
