from __init__ import *

chu_data = open("chuData/music_data.txt", "r", encoding="utf-8").read()


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
            chu_data = file
        with open("chuData/etag.txt", "w") as file:
            file.write(res.headers["etag"])

    if data["user_id"] == "1220332747" and data["raw_message"] == "chu update":
        res = requests.get("https://www.diving-fish.com/api/chunithmprober/music_data")
        with open("chuData/music_data.txt", "w", encoding="utf-8") as file:
            s = str(res.text)
            file.write(s)
            chu_data = file
        print("chu强制更新数据")
        get_msg(data, "chu数据已更新")

    return "update", 200


def chu_search(data):
    chu_update(data)
    songs = json.loads(str(chu_data), strict=False)
    text = "没找到你想要的歌曲呢，注意目前仅支持原名搜索哦"
    name = data["raw_message"].partition(" ")[2].casefold()

    for song in songs:
        if name in song["title"].casefold():
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
                    "Ult "
                    + str(song["ds"][4])
                    + "  ("
                    + str(song["charts"][4]["charter"])
                    + ")"
                )
            text = (
                "歌曲名："
                + str(song["title"])
                + "\n难度：\n"
                + nd
                + "\n作者："
                + str(song["basic_info"]["artist"])
                + "\nBPM："
                + str(song["basic_info"]["bpm"])
                + "\n分类："
                + str(song["basic_info"]["genre"])
                + "\n版本："
                + str(song["basic_info"]["from"])
            )
            break

    debug.print(text)
    msg = {
        "type": "text",
        "data": {"text": text},
    }
    post_msg(data, msg)

    return "search", 200


def chu_random(data):
    diffNum = random.randint(2, 4)
    diffName = ["Basic ", "Advanced ", "Expert ", "Master ", "Ultima ", "Wrold's End "]
    nd = -1
    diff = ["12", "12+", "13", "13+", "14", "14+", "15"]

    info = data["raw_message"].partition(" ")
    if info[0] != data["raw_message"]:
        info = info[2]
        if "红" in info or "红谱" in info:
            diffNum = 2
        if "1" in info:
            num = int(info.partition("1")[2][0])
            nd = (num - 2) * 2
            if "+" in info:
                nd += 1
            if num == 5:
                diffNum = 3
            if num < 3:
                diffNum = random.randint(2, 3)
        if "紫" in info or "紫谱" in info:
            diffNum = 3
        if "黑" in info or "黑谱" in info:
            diffNum = 4
        if (
            "彩" in info
            or "彩谱" in info
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
        "歌曲名："
        + str(song["title"])
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
