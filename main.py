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
    msg = str(data["raw_message"])

    if "raw_message" not in data:
        return "nothing", 200

    if "[CQ:at,qq=3937926418] " in msg:
        data["raw_message"] = msg.replace("[CQ:at,qq=3937926418] ", "")
        if msg == "":
            return (
                get_msg(
                    data,
                    "功能列表如下<必填参数>(选填参数)[替代参数]：\n"
                    "1. arc b30 <cookie>：根据给定的cookie查询arcaea官网的b30分表\n"
                    "2. bot退群\n"
                    "3. mai[chu] update\n"
                    "4. mai[chu]找歌 <歌名[id114514]>：根据歌名或id查询歌曲信息\n"
                    "5. mai[chu]别名 <歌名[id114514]>：根据歌名或id查询歌曲别名\n"
                    "6. mai[chu]随机 (紫[白][宴]13+)\n"
                    "7. b30[b50] (用户名)：生成成绩图，不输用户名则用QQ号查询\n",
                    "8. @bot bv号[av号]：查询bilibili视频信息",
                ),
                200,
            )
        data["raw_message"] = msg[:2].lower() + msg[2:]
        if msg.startswith("bv") or msg.startswith("av"):
            return bilibili_search(data)

    msg = msg.lower()
    if msg.startswith("arc b30"):
        return arc_b30(data)

    if msg == "bot退群":
        return bot_exit(data)

    if msg.startswith("b50"):
        return mai_b50(data)
    if msg == "mai update":
        return mai_update(data)
    if msg.startswith("mai别名"):
        return mai_alia(data)
    if msg.startswith(any(["mai找歌", "mai查歌", "mai搜索", "mai查找", "mai查询"])):
        return mai_search(data)
    if msg.startswith(
        any(["mai随机", "mai随歌", "mai随个歌", "mai随首歌", "mai随机歌曲"])
    ):
        return mai_random(data)

    if msg.startswith("b30"):
        redirect(url_for("process_image"))
        reply = [
            {
                "type": "reply",
                "data": {"id": data["message_id"]},
            }
        ] + [
            {
                "type": "image",
                "data": {"file": "http://localhost:8889/image"},
            }
        ]
        return get_msg(data, reply), 200
        # return chu_b30(data)
    if msg == "chu update":
        return chu_update(data)
    if msg.startswith("chu别名"):
        return chu_alia(data)
    if msg.startswith(any(["chu找歌", "chu查歌", "chu搜索", "chu查找", "chu查询"])):
        return chu_search(data)
    if msg.startswith(
        any(["chu随机", "chu随歌", "chu随个歌", "chu随首歌", "chu随机歌曲"])
    ):
        return chu_random(data)

    return "nothing", 200


@app.route("/image")
def process_image():
    buffer = chu_b30(data)
    # reply = [{
    #     "type": "reply",
    #     "data": {"id": data["message_id"]},
    # }]+[msg]+[{
    #     "type": "image",
    #     "data": {"file": "http://localhost:8889/image"},
    # }]
    return send_file(buffer, mimetype="image/png")
    # # 假设这里是图片处理逻辑
    # img = Image.new('RGB', (100, 100), color='blue')  # 示例生成蓝色图片
    # img = img.rotate(45)  # 进行图片处理，如旋转图片

    # # 将图片保存到字节流中
    # img_io = io.BytesIO()
    # img.save(img_io, 'JPEG')  # 可以改成其他格式
    # img_io.seek(0)

    # 返回处理后的图片
    # return send_file(img_io, mimetype='image/jpeg')


if __name__ == "__main__":
    app.run(debug=True, port=8889, host="localhost")
