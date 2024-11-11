from __init__ import *
from functions.getSongPic import getPic

chu_data = open("chuData/music_data.txt", "r", encoding="utf-8").read()
chu_alias = json.load(open("chuData/alias.json", "r", encoding="utf-8"))
chu_alias = chu_alias["aliases"]
asset = "asset/chu/"


def chu_update(data):
    etag = open("chuData/etag.txt", "r").read()
    etag = {"If-None-Match": etag}
    res = requests.get(
        "https://www.diving-fish.com/api/chunithmprober/music_data", headers=etag
    )
    if res.status_code == 200:
        print("chu更新数据")
        with open("chuData/music_data.txt", "w", encoding="utf-8") as file:
            file.write(str(res.text))
        with open("chuData/etag.txt", "w") as file:
            file.write(res.headers["etag"])
        global chu_data
        chu_data = open("chuData/music_data.txt", "r", encoding="utf-8").read()

    if data["user_id"] == "1220332747" and data["raw_message"] == "chu update":
        print("chu强制更新数据")
        res = requests.get("https://www.diving-fish.com/api/chunithmprober/music_data")
        with open("chuData/music_data.txt", "w", encoding="utf-8") as file:
            file.write(str(res.text))
        chu_data = open("chuData/music_data.txt", "r", encoding="utf-8").read()
        get_msg(data, "chu数据已更新")

    return "update", 200


def chu_search(data):
    chu_update(data)
    id = []
    list = []
    songs = json.loads(str(chu_data), strict=False)
    img = ""
    text = "没找到你想要的歌曲呢"
    name = str(data["raw_message"]).partition(" ")[2].lower()

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
        if song["id"] in id or len(id) == 0 and name in str(song["title"]).lower():
            nd = (
                f"Exp {song["ds"][2]}  ({song["charts"][2]["charter"]})\n"
                f"Mas {song["ds"][3]}  ({song["charts"][3]["charter"]})"
            )
            if len(song["ds"]) == 5:
                nd += f"\nUlt {song["ds"][4]}  ({song["charts"][4]["charter"]})"
            text = (
                f"{song["title"]}  -  ID {song["id"]}\n{nd}\n"
                f"作者：{song["basic_info"]["artist"]}\n"
                f"BPM：{song["basic_info"]["bpm"]}\n"
                f"分类：{song["basic_info"]["genre"]}\n"
                f"版本：{song["basic_info"]["from"]}"
            )
            list.append(song)
            break

    debug.print(text)
    if len(list) > 0:
        getPic(list[0], "chu")
        img = {
            "type": "image",
            "data": {"file": f"file:///sdcard/Pictures/chuPic/{list[0]["id"]}.png"},
        }
    msg = {
        "type": "text",
        "data": {"text": text},
    }
    post_msg(data, [img, msg])

    return "search", 200


def chu_random(data):
    diffNum = random.randint(2, 4)  # 下面name的索引
    diffName = ["Basic ", "Advanced ", "Expert ", "Master ", "Ultima ", "Wrold's End "]
    nd = -1  # 难度。处理指定等级，若存在处理后为下面level的索引
    diff = ["12", "12+", "13", "13+", "14", "14+", "15"]

    # 判断后面有无限定条件：等级、难度
    info = str(data["raw_message"]).partition(" ")
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
            or "worldsend" in info.replace("'", "").replace(" ", "").lower()
        ):
            diffNum = 5

    chu_update(data)
    songs = json.loads(str(chu_data), strict=False)
    song = random.choice(songs)
    # 难度判断
    while nd != -1 and diffNum != 5:
        if diffNum == 4 and len(song["ds"]) != 5:
            song = random.choice(songs)
            continue
        if len(song["ds"]) == 6:
            song = random.choice(songs)
            continue
        if song["level"][diffNum] == diff[nd]:
            break
        song = random.choice(songs)
    # 黑谱判断
    while diffNum == 4:
        if len(song["ds"]) == 5:
            break
        song = random.choice(songs)
    # 彩谱判断
    while diffNum == 5:
        if len(song["ds"]) == 6:
            break
        song = random.choice(songs)

    ndInfo = diffName[diffNum]
    if diffNum != 5:
        ndInfo += str(song["ds"][diffNum])

    getPic(song, "chu")
    img = {
        "type": "image",
        "data": {"file": f"file:///sdcard/Pictures/chuPic/{song["id"]}.png"},
    }

    song = (
        f"{song["title"]}  -  ID {song["id"]}\n"
        f"难度：{ndInfo} ({song["charts"][diffNum]["charter"]})\n"
        f"作者：{song["basic_info"]["artist"]}\n"
        f"BPM：{song["basic_info"]["bpm"]}\n"
        f"分类：{song["basic_info"]["genre"]}\n"
        f"版本：{song["basic_info"]["from"]}"
    )

    msg = {
        "type": "text",
        "data": {"text": song},
    }
    post_msg(data, [img, msg])

    return song, 200


def chu_alia(data):
    msg = ""
    list = []
    alia = []
    songs = json.loads(str(chu_data), strict=False)
    name = str(data["raw_message"]).partition(" ")[2].lower()

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


def cut_title(title, len):
    text = ""
    is_cut = False
    draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    for word in title:
        title_bbox = draw.textbbox(
            (0, 0),
            text.replace("°", ""),
            font=ImageFont.truetype("C:/WINDOWS/FONTS/UDDIGIKYOKASHON-B.TTC", 16),
        )
        title_width = title_bbox[2] - title_bbox[0]
        text += word
        if title_width > len:
            is_cut = True
            break
    return text, is_cut


def txt_faded(txt, width):
    width += 13  # 文字切掉的有点多，补正一下

    # 创建一个单独的图层用于绘制文字
    layer = Image.new("RGBA", (width, 18), (255, 255, 255, 0))  # 完全透明背景
    draw = ImageDraw.Draw(layer)
    draw.text(
        (0, 0),
        txt,
        font=ImageFont.truetype("C:/WINDOWS/FONTS/UDDIGIKYOKASHON-B.TTC", 16),
        fill=(255, 255, 255),
    )

    # 创建渐变蒙版，控制右侧逐渐透明
    gradient = Image.new("L", layer.size, 255)  # 单通道（L），全白
    for x in range(width):
        transparency = int(
            max(0, 255 - (x - width + 20) * 12.75)
        )  # 渐变从最后20px开始，最后的因子由255/x得到
        for y in range(18):
            gradient.putpixel((x, y), transparency)

    # 将渐变蒙版应用到文字图层
    fade = Image.composite(
        layer,
        Image.new("RGBA", layer.size, (255, 255, 255, 0)),
        gradient,
    )

    return fade


def chu_b30(data):
    chu_update(data)
    name = None
    if data["raw_message"] == "b30" or data["raw_message"] == "B30":
        res = requests.post(
            "https://www.diving-fish.com/api/chunithmprober/query/player",
            json={"qq": data["user_id"]},
        )
    elif " " in data["raw_message"]:
        name = data["raw_message"].partition(" ")[2]
        res = requests.post(
            "https://www.diving-fish.com/api/chunithmprober/query/player",
            json={"username": name},
        )
    else:
        return "nothing", 200
    if res.status_code == 400:
        if name != None:
            get_msg(data, "用户名错误，注意是水鱼网站的用户名，不是游戏ID哦！")
        else:
            get_msg(data, "你还没有绑定QQ号呢，请前往水鱼网站绑定或使用用户名查询。")
        return "b30", 400
    if res.status_code == 403:
        get_msg(data, "该用户设置了禁止查询哦！")
        return "b30", 403
    get_msg(data, "生成B30中，请稍等")
    user_info = json.loads(res.text)

    margin_x = 200
    margin_y = 50
    font = "C:/WINDOWS/FONTS/UDDIGIKYOKASHON-B.TTC"
    font_xxl = ImageFont.truetype(font, 50)
    font_xl = ImageFont.truetype(font, 40)
    font_large = ImageFont.truetype(font, 25)
    font_small = ImageFont.truetype(font, 16)
    font_xs = ImageFont.truetype(font, 13)

    bg = Image.open("C:/Users/12203/Desktop/bg/121522032_p0.jpg")
    if bg.width != bg.height:
        len = min(bg.width, bg.height)
        bg = bg.crop((0, 0, len, len))
    bg = bg.resize([2100, 2100], Image.LANCZOS).convert("RGBA")
    bg = bg.filter(ImageFilter.GaussianBlur(5))
    draw = ImageDraw.Draw(bg)

    # 用户名与rt
    rt_img = "rating_"
    user_rt = user_info["rating"]
    if user_rt < 4.0:
        rt_img += "green_"
    elif user_rt < 7.0:
        rt_img += "orange_"
    elif user_rt < 10.0:
        rt_img += "red_"
    elif user_rt < 12.0:
        rt_img += "purple_"
    elif user_rt < 13.25:
        rt_img += "bronze_"
    elif user_rt < 14.5:
        rt_img += "silver_"
    elif user_rt < 15.25:
        rt_img += "gold_"
    elif user_rt < 16.0:
        rt_img += "platinum_"
    else:
        rt_img += "rainbow_"

    name_bg = (
        Image.open("asset/256001.png")
        .resize([1055, 170], Image.LANCZOS)
        .convert("RGBA")
    )
    # 生成圆角alpha遮罩
    rounded_mask = Image.new("L", name_bg.size, 0)
    rounded_draw = ImageDraw.Draw(rounded_mask)
    rounded_draw.rounded_rectangle([(0, 0), name_bg.size], 6, fill=255)  # 圆角半径3
    name_bg.putalpha(rounded_mask)
    bg.paste(name_bg, (margin_x, margin_y), name_bg)
    margin_y += 20
    draw.text(
        (margin_x + 180, margin_y),
        user_info["username"],
        "black",
        font=font_xxl,
    )
    margin_y += 75

    rt_pos = (margin_x + 180, margin_y)
    rt_param = {
        "xy": rt_pos,
        "text": "Rating",
        "font": ImageFont.truetype(font, 43),
    }
    draw.text(**rt_param, fill="black")
    rt_bbox = draw.textbbox(**rt_param)
    rt_len = rt_bbox[2] - rt_bbox[0]
    rt_pos = (rt_pos[0] + rt_len + 15, rt_pos[1] + 13)
    user_rt = str(math.floor(user_rt * 100) / 100.0)
    space = 20
    for char in user_rt:
        if char == ".":
            rt = rt_img + "comma.png"
            rt = Image.open(asset + rt)
            bg.paste(
                rt,
                (rt_pos[0], rt_pos[1] + 15),
                rt,
            )
            rt_pos = (rt_pos[0] - 5, rt_pos[1])
        else:
            rt = rt_img + f"0{char}.png"
            rt = Image.open(asset + rt)
            bg.paste(
                rt,
                rt_pos,
                rt,
            )
        rt_pos = (rt_pos[0] + space, rt_pos[1])

    # logo
    logo_pos = (margin_x + 1150, 0)
    # size 1024x576
    logo = Image.open("asset/CHUNITHM_LUMINOUS.png").resize([717, 403])
    bg.paste(
        logo,
        logo_pos,
        logo,
    )

    # 分数统计 & 曲绘准备
    b30_tot = b30_lv = b30_score = r10_tot = r10_lv = r10_score = 0
    img_paths = []
    for s in user_info["records"]["b30"]:
        img_paths.append(getPic(s, "chu"))  # mid 歌曲id；cid 谱面id
        b30_tot += s["ra"]
        b30_lv += s["ds"]
        b30_score += s["score"]
    for s in user_info["records"]["r10"]:
        img_paths.append(getPic(s, "chu"))
        r10_tot += s["ra"]
        r10_lv += s["ds"]
        r10_score += s["score"]
    song_imgs = []
    for i in img_paths:
        img = Image.open(i).resize((120, 120), Image.LANCZOS)
        # 生成圆角alpha遮罩
        rounded_mask = Image.new("L", img.size, 0)
        rounded_draw = ImageDraw.Draw(rounded_mask)
        rounded_draw.rounded_rectangle([(0, 0), img.size], 15, fill=255)  # 圆角半径15
        img.putalpha(rounded_mask)
        song_imgs.append(img)

    b30_avg = f"{b30_tot/30:.3f}"
    r10_avg = f"{r10_tot/10:.3f}"
    b30_score = f"{b30_score/30:.0f}"
    r10_score = f"{r10_score/10:.0f}"
    b30_lv = f"{b30_lv/30:.2f}"
    r10_lv = f"{r10_lv/10:.2f}"

    margin_y += 150
    b30_pos = (margin_x, margin_y)
    r10_pos = 0

    # 计算歌曲位置
    margin_y += 80
    position = []
    for index, img in enumerate(song_imgs):
        x = margin_x + (index % 5) * 340
        y = margin_y + (index // 5) * 160
        if index > 29:
            y += 150
            r10_pos = (x, y - 80) if r10_pos == 0 else r10_pos
        position.append((x, y))

    best_bg = Image.open("asset/bg_b30.png")
    bg.paste(
        best_bg,
        b30_pos,
        best_bg,
    )
    bg.paste(
        best_bg,
        r10_pos,
        best_bg,
    )
    b30_pos = (b30_pos[0] + 18, b30_pos[1] + 5)
    r10_pos = (r10_pos[0] + 18, r10_pos[1] + 5)
    draw.text(
        b30_pos,
        f"B30 - {b30_avg}",
        font=font_xxl,
    )  # 最长宽度（5个数）：300
    draw.text(
        r10_pos,
        f"R10 - {r10_avg}",
        font=font_xxl,
    )
    b30_pos = (b30_pos[0] + 330, b30_pos[1] + 4)
    r10_pos = (r10_pos[0] + 330, r10_pos[1] + 4)
    draw.text(
        b30_pos,
        f"Avg. {b30_score} / {b30_lv}",
        font=font_xl,
    )
    draw.text(
        r10_pos,
        f"Avg. {r10_score} / {r10_lv}",
        font=font_xl,
    )

    cnt = 1  # 排名
    for img, pos, info in zip(
        song_imgs, position, user_info["records"]["b30"] + user_info["records"]["r10"]
    ):
        margin_left = 10
        margin_top = 10
        # 背景
        color_bg = Image.open(f"asset/bg_{info['level_label']}.png")
        bg.paste(
            color_bg,
            pos,
            color_bg,
        )

        # 曲绘
        bg.paste(
            img,
            (pos[0] + 8, pos[1] + margin_left),
            img,
        )
        pic_width = img.width + margin_left + 5

        # 排名、等级、类型
        cnt_minus = -4 if cnt > 9 else 0  # 两位数排名位置补正
        navi_margin = pic_width + 15
        draw.text(
            (pos[0] + navi_margin + cnt_minus, pos[1] + margin_top),
            f"#{cnt}",
            font=font_xs,
        )
        level_param = {
            "xy": (
                pos[0] + navi_margin + (28 if "+" in info["level"] else 32),  # 位置补正
                pos[1] + margin_top - 2,
            ),
            "text": f"{info["level"]}   {info['level_label']}",
            "font": font_small,
        }
        draw.text(**level_param)
        level_bbox = draw.textbbox(**level_param)
        top_height = level_bbox[3] - level_bbox[1] + margin_top + 12

        # 标题处理
        title = ""
        is_cut = False
        title_len = 168
        # sb日本人用全角，换个字体
        if "°" in info["title"]:
            du_param = {
                "xy": pos,
                "text": "°",
                "font": ImageFont.truetype("C:/WINDOWS/FONTS/ARIAL.TTF", 16),
            }
            du_bbox = draw.textbbox(**du_param)
            du_width = du_bbox[2] - du_bbox[0]
            title, is_cut = cut_title(info["title"], title_len - du_width * 2)
            texts = title.split("°")
            width = 0

            for text in texts:
                try:
                    texts[texts.index(text) + 1]
                except IndexError:
                    if is_cut:
                        text_bbox = draw.textbbox(
                            pos,
                            text,
                            font=font_small,
                        )
                        # 字体问题多了一点
                        text_width = text_bbox[2] - text_bbox[0] - 16
                        # 将处理过的文字图层合成到背景图上
                        txt = txt_faded(text, text_width)
                        bg.paste(
                            txt,
                            (pos[0] + pic_width + width, pos[1] + top_height),
                            txt,
                        )
                    break

                param = {
                    "xy": (pos[0] + pic_width + width, pos[1] + top_height),
                    "text": text,
                    "font": font_small,
                }  # 标题参数
                bbox = draw.textbbox(**param)
                width += bbox[2] - bbox[0]
                du_param["xy"] = (
                    pos[0] + pic_width + width,
                    pos[1] + top_height,
                )
                draw.text(**param)
                draw.text(**du_param)
                width += du_width
        else:
            title, is_cut = cut_title(info["title"], title_len)
            if is_cut:
                # 将处理过的文字图层合成到背景图上
                txt = txt_faded(title, title_len)
                bg.paste(
                    txt,
                    (pos[0] + pic_width, pos[1] + top_height),
                    txt,
                )
            else:
                draw.text(
                    (pos[0] + pic_width, pos[1] + top_height),
                    title,
                    font=font_small,
                )
        # 更新高度
        bbox = draw.textbbox(
            pos,
            title,
            font_small,
        )
        tot_height = top_height + bbox[3] - bbox[1] + 7

        # 达成率处理
        main_part = f"{int(info["score"]):,}"  # 每3个数字加一个逗号
        main_param = {
            "xy": (pos[0] + pic_width, pos[1] + tot_height),
            "text": main_part,
            "font": font_large,
        }
        draw.text(**main_param)

        main_box = draw.textbbox(**main_param)  # bbox (left, top, right, bottom)
        main_height = main_box[3] - main_box[1]
        tot_height += main_height + 5

        # 定数与rating
        ra = str(info["ra"]).split(".")
        rating = ra[0] + "."
        rating += ra[1].ljust(2, "0")
        ds_param = {
            "xy": (pos[0] + pic_width, pos[1] + tot_height),
            "text": (str(info["ds"]) + " → " + rating),
            "font": ImageFont.truetype(font, 21),
        }
        draw.text(**ds_param)
        ds_box = draw.textbbox(**ds_param)
        tot_height += ds_box[3] - ds_box[1] + 10

        # 评价图标与fc
        if info["score"] < 500000:
            rate = "d"  # D
        elif info["score"] < 600000:
            rate = "c"  # C
        elif info["score"] < 700000:
            rate = "b"  # B
        elif info["score"] < 800000:
            rate = "bb"
        elif info["score"] < 900000:
            rate = "bbb"
        elif info["score"] < 925000:
            rate = "a"  # A
        elif info["score"] < 950000:
            rate = "aa"
        elif info["score"] < 975000:
            rate = "aaa"
        elif info["score"] < 990000:
            rate = "s"  # S
        elif info["score"] < 1000000:
            rate = "sp"
        elif info["score"] < 1005000:
            rate = "ss"  # SS
        elif info["score"] < 1007500:
            rate = "ssp"
        elif info["score"] < 1009000:
            rate = "sss"  # SSS
        else:
            rate = "sssp"
        # 短原size 64x18    长size 132x24
        rate_image = Image.open(f"{asset}{rate}.webp").resize((83, 16))
        bg.paste(
            rate_image,
            (pos[0] + pic_width, pos[1] + tot_height),
        )

        fc = info["fc"]
        if fc != "":
            if "full" in fc:
                fc = "fullcombo"
            image = Image.open(f"{asset}{fc}.webp").resize((83, 16))
            bg.paste(
                image,
                (pos[0] + pic_width + rate_image.size[0] + 8, pos[1] + tot_height),
            )

        cnt += 1
        cnt = 1 if cnt > 30 else cnt

    bg.save("C:/Users/12203/Desktop/test123.png")
    bg = bg.convert("RGB")
    # bg.save("C:/Users/12203/Desktop/test111.jpg", quality=90)
    buffer = io.BytesIO()
    bg.save(buffer, format="JPEG", quality=90)
    bg = base64.b64encode(buffer.getvalue()).decode("utf-8")

    reply_msg = [{"type": "reply", "data": {"id": data["message_id"]}}] + [
        {
            "type": "image",
            "data": {"file": "base64://" + bg},
        }
    ]
    post_msg(data, reply_msg)
    return "b30", 200
