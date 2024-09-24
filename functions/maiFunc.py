import array

from PIL import Image, ImageDraw, ImageFont

from __init__ import *

mai_data = open("maiData/music_data.txt", "r", encoding="utf-8").read()
mai_alias = json.load(open("maiData/alias.json", "r", encoding="utf-8"))


def mai_update(data):
    mai_etag = open("maiData/etag.txt", "r").read()
    etag = {"If-None-Match": mai_etag}
    res = requests.get(
        "https://www.diving-fish.com/api/maimaidxprober/music_data", headers=etag
    )
    if res.status_code == 200:
        print("mai更新数据")
        with open("maiData/music_data.txt", "w", encoding="utf-8") as file:
            s = str(res.text)
            file.write(s)
            global mai_data
            mai_data = file
        with open("maiData/etag.txt", "w") as file:
            file.write(res.headers["etag"])

    if data["user_id"] == "1220332747" and data["raw_message"] == "mai update":
        print("mai强制更新数据")
        res = requests.get("https://www.diving-fish.com/api/maimaidxprober/music_data")
        with open("maiData/music_data.txt", "w", encoding="utf-8") as file:
            s = str(res.text)
            file.write(s)
            mai_data = file
        nameRes = requests.get("https://download.fanyu.site/maimai/alias.json")
        with open("maiData/alias.json", "w", encoding="utf-8") as file:
            file.write(nameRes.text)
        get_msg(data, "mai数据已更新")

    return "update", 200


def mai_search(data):
    mai_update(data)
    list = []
    id = []
    type = None
    songs = json.loads(str(mai_data), strict=False)
    text = "没找到你想要的歌曲呢"
    name = data["raw_message"].partition(" ")[2].casefold()

    if "dx" in name:
        type = "dx"
        name = name.replace("dx", "")

    if "sd" in name or "st" in name or "标准" in name:
        type = "sd"
        name = name.replace("sd", "").replace("st", "").replace("标准", "")
    if "宴" in name:
        type = "宴会場"
        name = (
            name.replace("宴会場", "")
            .replace("宴会场", "")
            .replace("宴谱", "")
            .replace("宴", "")
        )

    if "id" not in name:
        # 遍历别名数据，查找匹配的别名
        for sID, aliases in mai_alias.items():
            if name in aliases:
                id.append(sID)
    else:
        # 拆分id1145，1145id
        id = id.replace("id", "")

    if type == "宴会場" or len(id[0]) > 5:
        for i in range(len(id)):
            if len(id[i]) <= 5:
                id[i] = id[i].zfill(5)
                id[i] = "1" + id[i]
        songs = songs[::-1]

    for song in songs:
        # id匹配 或 名称匹配
        if song["id"] in id or len(id) == 0 and name in song["title"].casefold():
            if type == "宴会場" or len(id[0]) > 5:
                ndInfo = "Utage " + song["level"][0] + "\n"
            else:
                ndInfo = (
                    "Exp "
                    + str(song["ds"][2])
                    + "  ("
                    + song["charts"][2]["charter"]
                    + ")\nMas "
                    + str(song["ds"][3])
                    + "  ("
                    + song["charts"][3]["charter"]
                    + ")\n"
                )
            if len(song["ds"]) == 5:
                ndInfo += (
                    "ReMas "
                    + str(song["ds"][4])
                    + "  ("
                    + song["charts"][4]["charter"]
                    + ")\n"
                )
            text = (
                song["title"]
                + "  -  ID "
                + str(song["id"])
                + "\n"
                + ndInfo
                + "作者："
                + song["basic_info"]["artist"]
                + "\nBPM："
                + str(song["basic_info"]["bpm"])
                + "\n分类："
                + song["basic_info"]["genre"]
                + "\n版本："
                + song["basic_info"]["from"]
            )
            list.append(song)
            if (
                len(id) == 1
                or (type != "宴会場" or len(id) <= 5 and len(song["id"]) > 5)
                or (type == "宴会場" or len(id) > 5 and len(song["id"] <= 5))
            ):
                break

    if len(list) > 1:
        msg = "查询到多个歌曲，请使用ID查询。可加上“SD”或“DX”区分类型\n"
        for i in range(len(list)):
            msg += (
                list[i]["id"]
                + " - "
                + list[i]["title"]
                + " ("
                + list[i]["type"]
                + ")\n"
            )
        # 切片删换行
        msg = msg[:-1]
        get_msg(data, msg)
        return "多个歌曲", 200

    debug.print(text)

    img = ""
    if len(list) > 0:
        getPic(list[0])
        img = {
            "type": "image",
            "data": {
                "file": "file:///sdcard/Pictures/maiPic/" + list[0]["id"] + ".jpg"
            },
        }
    msg = {
        "type": "text",
        "data": {"text": text},
    }
    post_msg(data, [img, msg])

    return "search", 200


def mai_random(data):
    diffNum = random.randint(2, 4)
    diffName = ["Utage ", "Advanced ", "Expert ", "Master ", "Re:Master "]
    nd = None
    diff = ["12", "12+", "13", "13+", "14", "14+", "15"]

    info = data["raw_message"].partition(" ")
    # 判断后面有无限定条件（等级、难度
    if info[0] != data["raw_message"]:
        info = info[2]
        if "红" in info:
            diffNum = 2
        if "1" in info:
            num = int(info.partition("1")[2][0])
            nd = (num - 2) * 2
            if "+" in info:
                nd += 1
            if num >= 4:
                diffNum = random.randint(3, 4)
        if "紫" in info:
            diffNum = 3
        if "白" in info:
            diffNum = 4
        if "宴" in info:
            diffNum = 0

    # if nd == 6:
    #     song = "PANDORA PARADOXXX  -  ID 1\n难度：Re:Master 15.0  (SD)\n曲师：削除\n谱师：PANDORA PARADOXXX\nBPM：150\n分类：舞萌\n版本：maimai FiNALE"
    #     msg = {
    #         "type": "text",
    #         "data": {"text": song},
    #     }
    #     post_msg(data, msg)
    #     return song, 200

    mai_update(data)
    songs = json.loads(str(mai_data), strict=False)

    while True:
        song = random.choice(songs)
        debug.print(song)
        # 白谱判断
        if diffNum == 4:
            if len(song["ds"]) == 5:
                break
            else:
                continue
        # 宴谱判断
        elif diffNum == 0 and song["basic_info"]["genre"] == "宴会場":
            break
        # 难度判断
        elif nd != None and song["level"][diffNum] == diff[nd]:
            break
        else:
            break

    if diffNum == 0:
        ndInfo = diffName[diffNum] + song["level"][diffNum]
    else:
        ndInfo = (
            diffName[diffNum] + str(song["ds"][diffNum]) + "  (" + song["type"] + ")"
        )

    img = ""
    text = (
        song["title"]
        + "  -  ID "
        + str(song["id"])
        + "\n"
        + ndInfo
        + "\n作者："
        + song["basic_info"]["artist"]
        + "\n谱师："
        + song["charts"][diffNum]["charter"]
        + "\nBPM："
        + str(song["basic_info"]["bpm"])
        + "\n分类："
        + song["basic_info"]["genre"]
        + "\n版本："
        + song["basic_info"]["from"]
    )

    getPic(song)
    img = {
        "type": "image",
        "data": {"file": "file:///sdcard/Pictures/maiPic/" + song["id"] + ".jpg"},
    }

    msg = {
        "type": "text",
        "data": {"text": text},
    }
    post_msg(data, [img, msg])

    return song, 200


def mai_b50(data):
    # mai_update(data)
    # if " " in data["raw_message"]:
    #     name = data["raw_message"].partition(" ")[2]
    #     res = requests.post(
    #         "https://www.diving-fish.com/api/maimaidxprober/query/player",
    #         json={"username": name, "b50": "1"},
    #     )
    # else:
    #     res = requests.post(
    #         "https://www.diving-fish.com/api/maimaidxprober/query/player",
    #         json={"qq": data["user_id"], "b50": "1"},
    #     )
    # if res.status_code == 400:
    #     get_msg(data, "用户名错误，注意是水鱼网站的用户名，不是游戏的ID哦！")
    #     return "b50", 400
    # if res.status_code == 403:
    #     get_msg(data, "该用户设置了禁止查询哦！")
    #     return "b50", 403
    # userInfo = res.text
    with open("./test.txt", "r", encoding="utf-8") as f:
        testInfo = json.loads(f.read())
    bg = Image.open("C:/Users/12203/Desktop/cut.jpg").resize([900, 2100])
    draw = ImageDraw.Draw(bg)
    songImgs = []
    for s in testInfo["charts"]["sd"]:
        songImgs += [getPic(s)]
    for s in testInfo["charts"]["dx"]:
        songImgs += [getPic(s)]
    songImg = []
    for i in songImgs:
        img = Image.open(i)
        img = img.resize((50, 50))
        songImg.append(img)

    position = []
    # 动态计算位置
    for index, img in enumerate(songImg):
        x = 50 + (index % 5) * 150
        y = 50 + (index // 5) * 150
        position.append((x, y))

    for img, pos, t in zip(songImg, position, testInfo["charts"]["sd"]):
        bg.paste(img, pos)
        draw.text(
            (pos[0] + 55, pos[1]),
            t["title"][:5]
            + "\n"
            + str(t["achievements"])
            + "%\n"
            + str(t["ds"])
            + " "
            + str(t["ra"]),
            fill=(0, 0, 0),
            font=ImageFont.truetype("C:/WINDOWS/FONTS/BIZ-UDMINCHOM.TTC", 20),
        )

    bg.save("C:/Users/12203/Desktop/test111.png")
    return "b50", 200


def mai_alia(data):
    msg = ""
    list = []
    songs = json.loads(str(mai_data), strict=False)
    name = data["raw_message"].partition(" ")[2].casefold()

    if "id" not in name:
        # 遍历别名数据，查找匹配的别名
        for sID, aliases in mai_alias.items():
            if name in aliases:
                list.append({"id": sID})

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
                msg += "ID " + l["id"] + " - " + l["title"] + " (" + l["type"] + ")\n"
            # 切片删换行
            msg = msg[:-1]
            get_msg(data, "查询到多个歌曲，请使用ID查询\n" + msg)
            return "多个别名", 200
    else:
        list.append({"id": name.replace("id", "")})

    for sID, aliases in mai_alias.items():
        if sID == list[0]["id"]:
            for a in aliases:
                msg += a + "，"
            msg = msg[:-1]
            get_msg(data, "ID为" + sID + "的歌曲有以下别名：\n" + msg)
            break

    return "别名", 200
