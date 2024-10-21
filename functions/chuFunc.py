from __init__ import *
from functions.getSongPic import getPic

chu_data = open("chuData/music_data.txt", "r", encoding="utf-8").read()
chu_alias = json.load(open("chuData/alias.json", "r", encoding="utf-8"))
chu_alias = chu_alias["aliases"]


def chu_update(data):
    chu_etag = open("chuData/etag.txt", "r").read()
    etag = {"If-None-Match": chu_etag}
    res = requests.get(
        "https://www.diving-fish.com/api/chunithmprober/music_data", headers=etag
    )
    if res.status_code == 200:
        print("chu更新数据")
        with open("chuData/music_data.txt", "w", encoding="utf-8") as file:
            s = str(res.text)
            file.write(s)
            global chu_data
            chu_data = file.read()
        with open("chuData/etag.txt", "w") as file:
            file.write(res.headers["etag"])

    if data["user_id"] == "1220332747" and data["raw_message"] == "chu update":
        res = requests.get("https://www.diving-fish.com/api/chunithmprober/music_data")
        with open("chuData/music_data.txt", "w", encoding="utf-8") as file:
            s = str(res.text)
            file.write(s)
            chu_data = file.read()
        print("chu强制更新数据")
        get_msg(data, "chu数据已更新")

    return "update", 200


def chu_search(data):
    chu_update(data)
    id = []
    list = []
    songs = json.loads(str(chu_data), strict=False)
    text = "没找到你想要的歌曲呢"
    name = data["raw_message"].partition(" ")[2].casefold()

    if "id" not in name:
        # 遍历别名数据，查找匹配的别名
        for item in chu_alias:
            song_id = item["song_id"]
            aliases = item["aliases"]
            if name in aliases:
                id.append(song_id)
    else:
        # 拆分 id1145 与 1145 id
        id = re.sub(r"\s*id\s*", "", name)

    for song in songs:
        # id匹配 或 名称匹配
        if song["id"] in id or len(id) == 0 and name in song["title"].casefold():
            nd = (
                "Exp "
                + str(song["ds"][2])
                + "  ("
                + str(song["charts"][2]["charter"])
                + ")\nMas "
                + str(song["ds"][3])
                + "  ("
                + str(song["charts"][3]["charter"])
                + ")"
            )
            if len(song["ds"]) == 5:
                nd += (
                    "\nUlt "
                    + str(song["ds"][4])
                    + "  ("
                    + str(song["charts"][4]["charter"])
                    + ")"
                )
            text = (
                str(song["title"])
                + "  -  ID "
                + str(song["id"])
                + "\n"
                + nd
                + "\n作者："
                + str(song["basic_info"]["artist"])
                + "\nBPM："
                + str(song["basic_info"]["bpm"])
                + "\n分类："
                + song["basic_info"]["genre"]
                + "\n版本："
                + song["basic_info"]["from"]
            )
            list.append(song)
            break

    debug.print(text)
    if len(list) > 0:
        getPic(list[0], "chu")
        img = {
            "type": "image",
            "data": {
                "file": "file:///sdcard/Pictures/chuPic/"
                + str(list[0]["id"]).zfill(5)
                + ".png"
            },
        }
    msg = {
        "type": "text",
        "data": {"text": text},
    }
    post_msg(data, [img, msg])

    return "search", 200


def chu_random(data):
    diffNum = random.randint(2, 4)
    diffName = ["Basic ", "Advanced ", "Expert ", "Master ", "Ultima ", "Wrold's End "]
    nd = -1
    diff = ["12", "12+", "13", "13+", "14", "14+", "15"]

    info = data["raw_message"].partition(" ")
    if info[0] != data["raw_message"]:
        info = info[2]
        if "1" in info:
            num = int(info.partition("1")[2][0])
            nd = (num - 2) * 2
            if "+" in info:
                nd += 1
            if num == 5:
                diffNum = 3
            if num < 3:
                diffNum = random.randint(2, 3)
        if "红" in info:
            diffNum = 2
        if "紫" in info:
            diffNum = 3
        if "黑" in info:
            diffNum = 4
        if (
            "彩" in info
            or "worldsend" in info.replace("'", "").replace(" ", "").casefold()
        ):
            diffNum = 5

    chu_update(data)
    songs = json.loads(str(chu_data), strict=False)
    song = random.choice(songs)

    # 黑谱判断
    if diffNum == 4:
        while True:
            if len(song["ds"]) == 5:
                break
            song = random.choice(songs)

    # 彩谱判断
    if diffNum == 5:
        while True:
            if len(song["ds"]) == 6:
                break
            song = random.choice(songs)

    # 难度判断
    if nd != -1 and diffNum != 5:
        while True:
            if diffNum == 4 and len(song["ds"]) != 5:
                song = random.choice(songs)
                continue
            if len(song["ds"]) == 6:
                song = random.choice(songs)
                continue
            if song["level"][diffNum] == diff[nd]:
                break
            song = random.choice(songs)

    ndInfo = diffName[diffNum]
    if diffNum != 5:
        ndInfo += str(song["ds"][diffNum])

    song = (
        str(song["title"])
        + "\n难度："
        + ndInfo
        + "\n作者："
        + str(song["basic_info"]["artist"])
        + "\n谱师："
        + str(song["charts"][diffNum]["charter"])
        + "\nBPM："
        + str(song["basic_info"]["bpm"])
        + "\n分类："
        + str(song["basic_info"]["genre"])
        + "\n版本："
        + str(song["basic_info"]["from"])
    )

    msg = {
        "type": "text",
        "data": {"text": song},
    }
    post_msg(data, msg)

    return song, 200


def chu_alia(data):
    msg = ""
    list = []
    alia = []
    songs = json.loads(str(chu_data), strict=False)
    name = data["raw_message"].partition(" ")[2].casefold()

    if "id" not in name:
        # 遍历别名数据，查找匹配的别名
        for item in chu_alias:
            if name in item["aliases"]:
                list.append({"id": item["song_id"]})
                if len(alia) == 0:
                    alia = item["aliases"]

        if len(list) == 0:
            for song in songs:
                if name == song["title"]:
                    list.append(song)
            if len(list) == 0:
                get_msg(data, "没找到你想要的歌曲呢")
                return "无别名", 200

        if len(list) > 1:
            for song in songs:
                if song["id"] in list["id"]:
                    list.append(song)
            for l in list:
                msg += "ID " + l["id"] + " - " + l["title"] + "\n"
            msg = msg[:-1]  # 切片删换行
            get_msg(data, "查询到多个歌曲，请使用ID查询\n" + msg)
            return "多个别名", 200

        for a in alia:
            msg += a + "，"
        msg = msg[:-1]
        get_msg(data, "ID为" + str(list[0]["id"]) + "的歌曲有以下别名：\n" + msg)
    else:
        list.append({"id": re.sub(r"\s*id\s*", "", name)})

        for item in chu_alias:
            if item["song_id"] == list[0]["id"]:
                for a in item["aliases"]:
                    msg += a + "，"
                msg = msg[:-1]
                get_msg(
                    data, "ID为" + str(item["song_id"]) + "的歌曲有以下别名：\n" + msg
                )
                break

    return "别名", 200
