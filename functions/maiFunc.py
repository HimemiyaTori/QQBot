from __init__ import *

mai_data = open("maiData/music_data.txt", "r", encoding="utf-8").read()
mai_alias = json.load(open("maiData/alias.json", "r", encoding="utf-8"))
asset = "asset/mai/"


def mai_update(data):
    etag = open("maiData/etag.txt", "r").read()
    etag = {"If-None-Match": etag}
    res = requests.get(
        "https://www.diving-fish.com/api/maimaidxprober/music_data",
        headers=etag,
        verify=certifi.where(),
    )
    if res.status_code == 200:
        print("mai更新数据")
        with open("maiData/music_data.txt", "w", encoding="utf-8") as file:
            file.write(str(res.text))
        with open("maiData/etag.txt", "w") as file:
            file.write(res.headers["etag"])
        global mai_data
        mai_data = open("maiData/music_data.txt", "r", encoding="utf-8").read()

    if data["user_id"] == "1220332747" and data["raw_message"] == "mai update":
        print("mai强制更新数据")
        res = requests.get(
            "https://www.diving-fish.com/api/maimaidxprober/music_data",
            verify=certifi.where(),
        )
        with open("maiData/music_data.txt", "w", encoding="utf-8") as file:
            file.write(str(res.text))
        name_res = requests.get(
            "https://download.fanyu.site/maimai/alias.json", verify=certifi.where()
        )
        with open("maiData/alias.json", "w", encoding="utf-8") as file:
            file.write(name_res.text)
        mai_data = open("maiData/music_data.txt", "r", encoding="utf-8").read()
        get_msg(data, "mai数据已更新")

    return "update", 200


def mai_search(data):
    mai_update(data)
    list = []  # 处理可能找到的多个歌曲
    id = []  # 储存id（包含别名表里找到的多个id）
    type = None  # dx sd 宴会場，None说明没找到
    songs = json.loads(str(mai_data), strict=False)
    text = "没找到你想要的歌曲呢"
    name = str(data["raw_message"]).partition(" ")[2].casefold()

    if any(sd in name for sd in ["sd", "st", "标准"]):
        type = "sd"
        name = re.sub(r"\s*(sd|st|标准)\s*", "", name)
    elif "dx" in name:
        type = "dx"
        name = re.sub(r"\s*dx\s*", "", name)
    elif "宴" in name and not any(
        n in name for n in ["珍顿汉", "顿珍汉", "頓珍漢", "之宴", "の宴"]
    ):  # 专门处理《頓珍漢の宴》
        type = "宴会場"
        name = re.sub(r"\s*(宴会場|宴会场|宴谱|宴)\s*", "", name)

    if "id" not in name:
        # 遍历别名数据，查找匹配的别名
        for s_id, aliases in mai_alias.items():
            if name in aliases:
                id.append(str(s_id))
    else:
        # 拆分 id1145 与 1145 id
        id = re.sub(r"\s*id\s*", "", name)

    if type == "宴会場" or len(id[0]) > 5 if len(id) > 0 else False:
        for i in range(id):
            if len(id[i]) <= 5:
                id[i] = id[i].zfill(5)
                id[i] = "1" + id[i]
        songs = songs[::-1]  # 倒序搜

    for song in songs:
        # id匹配 或 名称匹配
        if song["id"] in id or len(id) == 0 and name in song["title"].casefold():
            if type == "宴会場" or len(id[0]) > 5 if len(id) > 0 else False:
                nd_info = f"Utage {song["level"][0]}\n"
            else:
                nd_info = (
                    f"Exp {song["ds"][2]}  ({song["charts"][2]["charter"]})\n"
                    f"Mas {song["ds"][3]}  ({song["charts"][3]["charter"]})"
                )
            if len(song["ds"]) == 5:
                nd_info += f"\nReMas {song['ds'][4]}  ({song['charts'][4]['charter']})"
            text = (
                f"{song['title']}  -  ID {song['id']}\n{nd_info}\n"
                f"作者：{song['basic_info']['artist']}\n"
                f"BPM：{song['basic_info']['bpm']}\n"
                f"分类：{song['basic_info']['genre']}\n"
                f"版本：{song['basic_info']['from']}"
            )
            debug.print(text)
            list.append(song)
            if (
                len(id) == 1
                or (type != "宴会場" or len(id) <= 5 and len(song["id"]) > 5)
                or (type == "宴会場" or len(id) > 5 and len(song["id"]) <= 5)
            ):
                break

    if len(list) > 1:
        msg = "查询到多个歌曲，请使用ID查询。可加上“SD”或“DX”区分类型\n"
        for i in range(len(list)):
            msg += f"{list[i]['id']}. {list[i]['title']} ({list[i]['type']})\n"
        msg = msg[:-1]  # 切片删换行
        get_msg(data, msg)
        return "多个歌曲", 200

    img = ""
    if len(list) > 0:
        getPic(list[0], "mai")
        img = {
            "type": "image",
            "data": {
                "file": f"file:///sdcard/Pictures/maiPic/{str(list[0]["id"])}.png"
            },
        }
    msg = {
        "type": "text",
        "data": {"text": text},
    }
    post_msg(data, [img, msg])

    return "search", 200


def mai_random(data):
    level_num = random.randint(2, 4)  # 下面name的索引
    level_name = ["Utage ", "Advanced ", "Expert ", "Master ", "Re:Master "]
    nd = -1  # 难度。处理指定等级，若存在处理后为下面level的索引
    level = ["12", "12+", "13", "13+", "14", "14+", "15"]

    # 判断后面有无限定条件：等级、难度
    info = str(data["raw_message"]).partition(" ")
    if info[0] != data["raw_message"]:
        info = info[2]
        if "1" in info:
            num = int(info.partition("1")[2][0])
            nd = (num - 2) * 2
            if "+" in info:
                nd += 1
            if num >= 4:
                level_num = random.randint(3, 4)
        if "红" in info:
            level_num = 2
        if "紫" in info:
            level_num = 3
        if "白" in info:
            level_num = 4
        if "宴" in info:
            level_num = 0

    # 直接处理15
    if nd >= 6:
        song = [
            "PANDORA PARADOXXX  -  ID 834\n"
            "难度：Re:Master 15.0  (SD)\n"
            "曲师：削除\n"
            "谱师：PANDORA PARADOXXX\n"
            "BPM：150\n"
            "分类：舞萌\n"
            "版本：maimai FiNALE",
            "系ぎて - ID 11663\n"
            "难度：Re:Master 15.0  (DX)\n"
            "曲师：rinto soma\n"
            "谱师：to the future\n"
            "BPM：88\n分类：舞萌\n版本：maimai Buddies",
        ]
        msg = {
            "type": "text",
            "data": {"text": song[random.randint(0, 1)]},
        }
        post_msg(data, msg)
        return song, 200

    mai_update(data)
    songs = json.loads(str(mai_data), strict=False)
    song = random.choice(songs)

    while level_num == 0 or level_num == 4 or nd != -1:
        # 白谱判断
        if level_num == 4 and len(song["ds"]) == 5:
            if nd == -1:
                break
        # 宴谱判断
        elif level_num == 0 and song["basic_info"]["genre"] == "宴会場":
            break
        # 难度判断
        if song["level"][level_num] == level[nd]:
            break
        debug.print(song)
        song = random.choice(songs)

    if level_num == 0:
        ndInfo = level_name[level_num] + song["level"][level_num]
    else:
        ndInfo = f"{level_name[level_num]}{song['ds'][level_num]}  ({song['type']})"

    text = (
        f"{song['title']}  -  ID {song['id']}\n{ndInfo}\n"
        f"作者：{song['basic_info']['artist']}\n"
        f"谱师：{song['charts'][level_num]['charter']}\n"
        f"BPM：{song['basic_info']['bpm']}\n"
        f"分类：{song['basic_info']['genre']}\n"
        f"版本：{song['basic_info']['from']}"
    )
    msg = {
        "type": "text",
        "data": {"text": text},
    }
    getPic(song)
    img = {
        "type": "image",
        "data": {"file": f"file:///sdcard/Pictures/maiPic/{song["id"]}.png"},
    }
    post_msg(data, [img, msg])

    return song, 200


def cut_title(title, len):
    txt = ""  # 暂存文字
    is_cut = False
    draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    for word in title:
        box = draw.textbbox(
            (0, 0),
            txt.replace("°", ""),
            font=ImageFont.truetype("C:/WINDOWS/FONTS/UDDIGIKYOKASHON-B.TTC", 16),
        )
        width = box[2] - box[0]
        txt += word
        if width > len:
            is_cut = True
            break
    return txt, is_cut


def txt_faded(txt, width):
    width += 13  # 文字切掉的有点多，补正一下

    # 创建一个单独的图层绘制文字
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


def mai_b50(data):
    mai_update(data)
    name = None
    if data["raw_message"] == "b50" or data["raw_message"] == "B50":
        res = requests.post(
            "https://www.diving-fish.com/api/maimaidxprober/query/player",
            json={"qq": data["user_id"], "b50": "1"},
        )
    elif " " in data["raw_message"]:
        name = data["raw_message"].partition(" ")[2]
        res = requests.post(
            "https://www.diving-fish.com/api/maimaidxprober/query/player",
            json={"username": name, "b50": "1"},
        )
    else:
        return "nothing", 200
    if res.status_code == 400:
        if name != None:
            get_msg(data, "用户名错误，注意是水鱼网站的用户名，不是游戏ID哦！")
        else:
            get_msg(data, "你还没有绑定QQ号呢，请前往水鱼网站绑定或使用用户名查询。")
        return "b50", 400
    if res.status_code == 403:
        get_msg(data, "该用户设置了禁止查询哦！")
        return "b50", 403
    get_msg(data, "生成B50中，请稍等")
    user_info = json.loads(res.text)
    songs = json.loads(str(mai_data), strict=False)
    reply_msg = {"type": "text", "data": {"text": ""}}

    margin_x = 200
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
    if user_info["rating"] < 1000:
        rt_img = Image.open(asset + "rating_base_normal.png")
    elif user_info["rating"] < 2000:
        rt_img = Image.open(asset + "rating_base_blue.png")
    elif user_info["rating"] < 4000:
        rt_img = Image.open(asset + "rating_base_green.png")
    elif user_info["rating"] < 7000:  # 找不到黄色，先用红的
        rt_img = Image.open(asset + "rating_base_red.png")
    elif user_info["rating"] < 10000:
        rt_img = Image.open(asset + "rating_base_red.png")
    elif user_info["rating"] < 12000:
        rt_img = Image.open(asset + "rating_base_purple.png")
    elif user_info["rating"] < 13000:
        rt_img = Image.open(asset + "rating_base_bronze.png")
    elif user_info["rating"] < 14000:
        rt_img = Image.open(asset + "rating_base_silver.png")
    elif user_info["rating"] < 14500:
        rt_img = Image.open(asset + "rating_base_gold.png")
    elif user_info["rating"] < 15000:
        rt_img = Image.open(asset + "rating_base_platinum.png")
    else:
        rt_img = Image.open(asset + "rating_base_rainbow.png")

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
    bg.paste(
        name_bg,
        (margin_x, 30),
        name_bg,
    )
    draw.text(
        (margin_x + 180, 50),
        user_info["username"],
        "black",
        font=font_xxl,
    )

    rt_pos = (margin_x + 165, 110)
    bg.paste(
        rt_img,
        rt_pos,
        rt_img,
    )

    rt_pos = (rt_pos[0] + 131, rt_pos[1] + 23)
    space = 31
    for char in str(user_info["rating"]):
        draw.text(
            rt_pos,
            char,
            font=font_xl,
        )
        rt_pos = (rt_pos[0] + space, rt_pos[1])

    # logo
    logo_pos = (margin_x + 1350, 0)
    # size 396x329
    logo = Image.open("asset/maimai_DX_2024.png").resize((356, 296))
    bg.paste(
        logo,
        logo_pos,
        logo,
    )

    # 分数统计 & 曲绘准备
    b35_tot = b15_tot = b35_lv = b15_lv = 0
    img_paths = []
    for s in user_info["charts"]["sd"]:
        img_paths.append(getPic(s))
        b35_tot += s["ra"]
        b35_lv += s["ds"]
    for s in user_info["charts"]["dx"]:
        img_paths.append(getPic(s))
        b15_tot += s["ra"]
        b15_lv += s["ds"]
    song_imgs = []
    for i in img_paths:
        img = Image.open(i).resize((120, 120), Image.LANCZOS)
        # 生成圆角alpha遮罩
        rounded_mask = Image.new("L", img.size, 0)
        rounded_draw = ImageDraw.Draw(rounded_mask)
        rounded_draw.rounded_rectangle([(0, 0), img.size], 15, fill=255)  # 圆角半径15
        img.putalpha(rounded_mask)
        song_imgs.append(img)

    b35_lv = f"{b35_lv/35:.2f}"
    b15_lv = f"{b15_lv/15:.2f}"
    b35_avg = f"{b35_tot/35:.2f}"
    b15_avg = f"{b15_tot/15:.2f}"

    b35_pos = (margin_x, 250)
    b15_pos = 0

    # 计算歌曲位置
    position = []
    for index, img in enumerate(song_imgs):
        x = margin_x + (index % 5) * 340
        y = 330 + (index // 5) * 160
        if index > 34:
            y += 150
            b15_pos = (x, y - 80) if b15_pos == 0 else b15_pos
        position.append((x, y))

    best_bg = Image.open("asset/bg_b50.png")
    bg.paste(
        best_bg,
        b35_pos,
        best_bg,
    )
    bg.paste(
        best_bg,
        b15_pos,
        best_bg,
    )
    b35_pos = (b35_pos[0] + 18, b35_pos[1] + 5)
    b15_pos = (b15_pos[0] + 18, b15_pos[1] + 5)
    draw.text(
        b35_pos,
        f"B35 - {b35_tot}",
        font=font_xxl,
    )  # 最长宽度（5位数）：275
    draw.text(
        b15_pos,
        f"B15 - {b15_tot}",
        font=font_xxl,
    )
    b35_pos = (b35_pos[0] + 305, b35_pos[1] + 4)
    b15_pos = (b15_pos[0] + 305, b15_pos[1] + 4)
    draw.text(
        b35_pos,
        f"Avg. {b35_avg} / {b35_lv}",
        font=font_xl,
    )
    draw.text(
        b15_pos,
        f"Avg. {b15_avg} / {b15_lv}",
        font=font_xl,
    )

    cnt = 1  # 排名
    for img, pos, info in zip(
        song_imgs, position, user_info["charts"]["sd"] + user_info["charts"]["dx"]
    ):
        margin_left = 10
        margin_top = 10
        # 背景
        color_bg = Image.open(f"asset/bg_{info['level_label'].replace(':', '')}.png")
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
        draw.text(
            (
                pos[0] + navi_margin + (24 if "+" in info["level"] else 28),  # 位置补正
                pos[1] + margin_top - 2,
            ),
            info["level"],
            font=font_small,
        )
        # 原size 113x32
        image = Image.open(f"{asset}music_{info["type"]}.png").resize((60, 17))
        bg.paste(
            image,
            (pos[0] + navi_margin + 55, pos[1] + margin_top - 1),
            image,
        )
        top_height = image.height + margin_top + 10

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
        tot_height = top_height + bbox[3] - bbox[1] + 2

        # 达成率处理
        achievement = str(info["achievements"])
        main_part = achievement.split(".")[0]
        decimal_part = "." + (
            "0000"
            if "." not in achievement
            else achievement.split(".")[1].ljust(4, "0")
        )
        main_param = {
            "xy": (pos[0] + pic_width, pos[1] + tot_height),
            "text": main_part,
            "font": font_large,
        }
        main_box = draw.textbbox(**main_param)  # bbox (left, top, right, bottom)
        main_width = main_box[2] - main_box[0]
        main_height = main_box[3] - main_box[1]
        decimal_param = {
            "xy": (pos[0] + pic_width + main_width, pos[1] + tot_height),
            "text": decimal_part,
            "font": font_large,
        }
        decimal_box = draw.textbbox(**decimal_param)
        decimal_width = decimal_box[2] - decimal_box[0]

        draw.text(**main_param)
        draw.text(**decimal_param)
        draw.text(
            (
                pos[0] + pic_width + main_width + decimal_width + 2,
                pos[1] + tot_height + 6,
            ),
            "%",
            (222, 222, 222),  # 稍灰的白色
            font_small,
        )
        # 原size 200x89
        rate_image = Image.open(asset + info["rate"] + ".png").resize((80, 31))
        bg.paste(
            rate_image,
            (pos[0] + pic_width - 3, pos[1] + 103),
            rate_image,
        )
        tot_height += main_height + 3

        # 定数与rating
        ds_param = {
            "xy": (pos[0] + pic_width, pos[1] + tot_height),
            "text": f"{info['ds']} → {info['ra']}",
            "font": ImageFont.truetype(font, 21),
        }
        draw.text(**ds_param)
        ds_box = draw.textbbox(**ds_param)
        ds_width = ds_box[2] - ds_box[0]
        tot_height += ds_box[3] - ds_box[1] + 6

        # dx星处理
        if info["dxScore"] != 0:
            dxScore = 0
            for s in songs:
                if int(s["id"]) == int(info["song_id"]):
                    note = s["charts"][info["level_index"]]["notes"]
                    for n in note:
                        dxScore += n
                    break
            dxScore = info["dxScore"] / (dxScore * 3)
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
                # 原size 70x70
                image = Image.open(f"{asset}music_icon_dxstar_{dxScore}.png").resize(
                    (30, 30)
                )

                bg.paste(
                    image,
                    (
                        pos[0] + pic_width + ds_width + 12,
                        pos[1] + tot_height - 38,
                    ),
                    image,
                )
        else:
            reply_msg = {
                "type": "text",
                "data": {
                    "text": "发现到你设置了“对非网页查询的成绩使用掩码”，"
                    "若你想获取更详细的成绩与dx分，请在查分网站的个人资料中取消设置。"
                },
            }

        # fc与fs
        if info["fc"] != "":
            # 原size 42x47
            image = Image.open(asset + info["fc"] + ".png").resize((30, 34))
            bg.paste(
                image,
                (pos[0] + pic_width + rate_image.size[0] + 35, pos[1] + tot_height),
                image,
            )

        if info["fs"] != "":
            image = Image.open(asset + info["fs"] + ".png").resize((30, 34))
            bg.paste(
                image,
                (
                    pos[0] + pic_width + rate_image.size[0] + image.size[0] + 40,
                    pos[1] + tot_height,
                ),
                image,
            )

        cnt += 1
        cnt = 1 if cnt > 35 else cnt

    # bg.save("C:/Users/12203/Desktop/test123.png")
    bg = bg.convert("RGB")
    # bg.save("C:/Users/12203/Desktop/test111.jpg", quality=90)
    buffer = io.BytesIO()
    bg.save(buffer, format="JPEG", quality=90)
    bg = base64.b64encode(buffer.getvalue()).decode("utf-8")

    reply_msg = (
        [{"type": "reply", "data": {"id": data["message_id"]}}]
        + [reply_msg]
        + [
            {
                "type": "image",
                "data": {"file": "base64://" + bg},
            }
        ]
    )
    post_msg(data, reply_msg)
    return "b50", 200


def mai_alia(data):
    msg = ""
    list = []
    alia = []
    songs = json.loads(str(mai_data), strict=False)
    name = data["raw_message"].partition(" ")[2].casefold()

    if "id" not in name:
        # 遍历别名数据，查找匹配的别名
        for sID, aliases in mai_alias.items():
            if name in aliases:
                list.append({"id": sID})
                if len(alia) == 0:
                    alia = aliases

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
                msg += f"ID {l["id"]} - {l["title"]} ({l["type"]})\n"
            # 切片删换行
            msg = msg[:-1]
            get_msg(data, "查询到多个歌曲，请使用ID查询\n" + msg)
            return "多个别名", 200

        for a in alia:
            msg += a + "，"
        msg = msg[:-1]
        get_msg(data, f"ID为{list[0]["id"]}的歌曲有以下别名：\n{msg}")
    else:
        list.append({"id": re.sub(r"\s*id\s*", "", name)})

        for sID, aliases in mai_alias.items():
            if sID == list[0]["id"]:
                for a in aliases:
                    msg += a + "，"
                msg = msg[:-1]
                get_msg(data, f"ID为{sID}的歌曲有以下别名：\n{msg}")
                break

    return "别名", 200
