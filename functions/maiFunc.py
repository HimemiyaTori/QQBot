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
        name = re.sub(r"\s*dx\s*", "", name)

    if "sd" in name or "st" in name or "标准" in name:
        type = "sd"
        name = re.sub(r"\s*(sd|st|标准)\s*", "", name)
    if "宴" in name:
        type = "宴会場"
        name = re.sub(r"\s*(宴会場|宴会场|宴谱|宴)\s*", "", name)

    if "id" not in name:
        # 遍历别名数据，查找匹配的别名
        for sID, aliases in mai_alias.items():
            if name in aliases:
                id.append(sID)
    else:
        # 拆分 id1145 与 1145 id
        id = re.sub(r"\s*id\s*", "", name)

    if type == "宴会場" or len(id[0]) > 5 if len(id) > 0 else False:
        for i in range(id):
            if len(id[i]) <= 5:
                id[i] = id[i].zfill(5)
                id[i] = "1" + id[i]
        songs = songs[::-1]

    for song in songs:
        # id匹配 或 名称匹配
        if song["id"] in id or len(id) == 0 and name in song["title"].casefold():
            if type == "宴会場" or len(id[0]) > 5 if len(id) > 0 else False:
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
                list[i]["id"] + ". " + list[i]["title"] + " (" + list[i]["type"] + ")\n"
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
    # 判断后面有无限定条件：等级、难度
    if info[0] != data["raw_message"]:
        info = info[2]
        if "1" in info:
            num = int(info.partition("1")[2][0])
            nd = (num - 2) * 2
            if "+" in info:
                nd += 1
            if num >= 4:
                diffNum = random.randint(3, 4)
        if "红" in info:
            diffNum = 2
        if "紫" in info:
            diffNum = 3
        if "白" in info:
            diffNum = 4
        if "宴" in info:
            diffNum = 0

    if nd == 6:
        song = [
            "PANDORA PARADOXXX  -  ID 834\n难度：Re:Master 15.0  (SD)\n曲师：削除\n谱师：PANDORA PARADOXXX\nBPM：150\n分类：舞萌\n版本：maimai FiNALE",
            "系ぎて - ID 11663\n难度：Re:Master 15.0  (DX)\n曲师：rinto soma\n谱师：to the future\nBPM：88\n分类：舞萌\n版本：maimai Buddies",
        ]
        msg = {
            "type": "text",
            "data": {"text": song[random.randint(0, 1)]},
        }
        post_msg(data, msg)
        return song, 200

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


def add_rounded_corners(image, radius):
    # 创建一个与图像大小相同的 alpha 遮罩
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)

    # 画一个圆角矩形
    left_up_point = (0, 0)
    right_down_point = (image.size[0], image.size[1])
    draw.rounded_rectangle([left_up_point, right_down_point], radius, fill=255)

    # 将遮罩应用到图像上
    image.putalpha(mask)
    return image


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
    songs = json.loads(str(mai_data), strict=False)

    with open("./test.txt", "r", encoding="utf-8") as f:
        testInfo = json.loads(f.read())
    bg = (
        Image.open("C:/Users/12203/Desktop/bg/119614191_p0.png")
        .resize([2100, 2100])
        .convert("RGBA")
    )
    draw = ImageDraw.Draw(bg)
    songImgs = []
    for s in testInfo["charts"]["sd"]:
        songImgs += [getPic(s)]
    for s in testInfo["charts"]["dx"]:
        songImgs += [getPic(s)]
    songImg = []
    for i in songImgs:
        img = Image.open(i)
        img = img.resize((120, 120), Image.LANCZOS)
        img = add_rounded_corners(img, 10)  # TODO: 改改角度看看怎么好看
        songImg.append(img)

    # 动态计算位置
    position = []
    for index, img in enumerate(songImg):
        x = 150 + (index % 5) * 330
        y = 500 + (index // 5) * 150
        position.append((x, y))

    cnt = 1
    for img, pos, t in zip(songImg, position, testInfo["charts"]["sd"]):
        bg.paste(img, pos)
        draw.text(
            (pos[0] + 125, pos[1]),
            (
                t["title"][:13]
                + "\n"
                + str(t["achievements"]).split(".")[0]
                + "."
                + (
                    "0000"
                    if "." not in str(t["achievements"])
                    else str(t["achievements"]).split(".")[1].ljust(4, "0")
                )
                + "%\n"
                + str(t["ds"])
                + " -> "
                + str(t["ra"])
            ),
            fill=(0, 0, 0),
            font=ImageFont.truetype("C:/WINDOWS/FONTS/UDDIGIKYOKASHON-B.TTC", 16),
        )
        cnt += 1

    for img, pos, t in zip(songImg[35:], position[35:], testInfo["charts"]["dx"]):
        # 曲绘
        bg.paste(
            img,
            pos,
            mask=img.split()[3],
        )

        # 排名、等级、类型
        draw.text(
            (pos[0], pos[1] - 10),
            "#" + str(cnt),
            font=ImageFont.truetype("C:/WINDOWS/FONTS/UDDIGIKYOKASHON-B.TTC", 10),
        )
        draw.text(
            (pos[0] + 15, pos[1] - 10),
            t["level"],
            font=ImageFont.truetype("C:/WINDOWS/FONTS/UDDIGIKYOKASHON-B.TTC", 10),
        )
        image = Image.open("C:/Users/12203/Desktop/music_" + t["type"] + ".png").resize(
            (35, 10), Image.LANCZOS
        )
        bg.paste(
            image,
            (pos[0] + 30 + image.width, pos[1] - 10 + image.height),
            # mask=img.split()[3],  因为在上面，会越界
        )

        # 达成率处理
        font_large = ImageFont.truetype("C:/WINDOWS/FONTS/UDDIGIKYOKASHON-B.TTC", 25)
        font_small = ImageFont.truetype("C:/WINDOWS/FONTS/UDDIGIKYOKASHON-B.TTC", 16)
        main_part = str(t["achievements"]).split(".")[0]
        decimal_part = "." + (
            "0000"
            if "." not in str(t["achievements"])
            else str(t["achievements"]).split(".")[1].ljust(4, "0")
        )
        # bbox (left, top, right, bottom)
        mainBox = draw.textbbox(
            (pos[0] + img.width + 5, pos[1]), main_part, font=font_large
        )
        main_width = mainBox[2] - mainBox[0]
        main_height = mainBox[3] - mainBox[1]
        decimalBox = draw.textbbox(
            (pos[0] + img.width + 5 + main_width, pos[1]), decimal_part, font=font_large
        )
        smallBox = draw.textbbox(
            (pos[0] + img.width + 5, pos[1]), t["title"][:16], font=font_small
        )
        decimal_width = decimalBox[2] - decimalBox[0]
        small_height = smallBox[3] - smallBox[1]

        draw.text(
            (pos[0] + img.width + 5, pos[1]),
            t["title"][:16],
            fill=(0, 0, 0),
            font=font_small,
        )
        draw.text(
            (pos[0] + img.width + 5, pos[1] + small_height + 4),
            main_part,
            fill=(0, 0, 0),
            font=font_large,
        )
        draw.text(
            (pos[0] + img.width + 5 + main_width, pos[1] + small_height + 4),
            decimal_part,
            fill=(0, 0, 0),
            font=font_large,
        )
        draw.text(
            (
                pos[0] + img.width + 5 + main_width + decimal_width,
                pos[1] + small_height + 10,
            ),
            "%",
            fill=(0, 0, 0),
            font=font_small,
        )
        image = Image.open("C:/Users/12203/Desktop/" + t["rate"] + ".png").resize(
            (80, 31), Image.LANCZOS
        )
        bg.paste(
            image,
            (
                pos[0] + img.width + 12 + main_width + decimal_width,
                pos[1] + small_height + 4,
            ),
            mask=image.split()[3],
        )

        # 定数与rating
        draw.text(
            (pos[0] + img.width + 5, pos[1] + small_height + main_height + 6),
            (str(t["ds"]) + " → " + str(t["ra"])),
            fill=(0, 0, 0),
            font=ImageFont.truetype("C:/WINDOWS/FONTS/UDDIGIKYOKASHON-B.TTC", 21),
        )

        # dx星处理
        dxScore = 0
        for s in songs:
            if int(s["id"]) == int(t["song_id"]):
                note = s["charts"][t["level_index"]]["notes"]
                for n in note:
                    dxScore += n
                break
        dxScore = t["dxScore"] / (dxScore * 3)
        if dxScore >= 0.97:
            dxScore = 5
        elif dxScore >= 0.95:
            dxScore = 4
        elif dxScore >= 0.93:
            dxScore = 3
        elif dxScore >= 0.9:
            dxScore = 2
        elif dxScore >= 0.85:
            dxScore = 1
        else:
            dxScore = 0
        if dxScore != 0:
            image = Image.open(
                "C:/Users/12203/Desktop/music_icon_dxstar_detail_"
                + str(dxScore)
                + ".png"
            ).resize((120, 23), Image.LANCZOS)

            # 用贴图
            bg.paste(
                image,
                (pos[0] + 125, pos[1] + 95),
                mask=image.split()[3],
            )
            # 用字符 ✦    5：FFD700   4: FFA500  2: 008000 找不到字体，润了
            # draw.text(
            #     (pos[0] + 125, pos[1] + 40),
            #     "✦" * dxScore,
            #     fill=(
            #         "#FFD700"
            #         if dxScore == 5
            #         else "#FFA500" if (dxScore == 4 or dxScore == 3) else "#008000"
            #     ),
            #     font=ImageFont.truetype("", 23),
            # )

        # fc与fs
        if t["fc"] != "":
            image = Image.open("C:/Users/12203/Desktop/" + t["fc"] + ".png").resize(
                (30, 34), Image.LANCZOS
            )
            bg.paste(
                image,
                (pos[0] + 245, pos[1] + 90),
                mask=image.split()[3],
            )

        if t["fs"] != "":
            image = Image.open("C:/Users/12203/Desktop/" + t["fs"] + ".png").resize(
                (30, 34), Image.LANCZOS
            )
            bg.paste(
                image,
                (pos[0] + 275, pos[1] + 90),
                mask=image.split()[3],
            )
        cnt += 1

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
        list.append({"id": name.replace("id", "").replace(" ", "")})

    for sID, aliases in mai_alias.items():
        if sID == list[0]["id"]:
            for a in aliases:
                msg += a + "，"
            msg = msg[:-1]
            get_msg(data, "ID为" + sID + "的歌曲有以下别名：\n" + msg)
            break

    return "别名", 200
