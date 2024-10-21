import base64
import io

from PIL import Image, ImageDraw, ImageFilter, ImageFont

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
        with open("maiData/etag.txt", "w") as file:
            file.write(res.headers["etag"])
        global mai_data
        mai_data = open("maiData/music_data.txt", "r", encoding="utf-8").read()

    if data["user_id"] == "1220332747" and data["raw_message"] == "mai update":
        print("mai强制更新数据")
        res = requests.get("https://www.diving-fish.com/api/maimaidxprober/music_data")
        with open("maiData/music_data.txt", "w", encoding="utf-8") as file:
            s = str(res.text)
            file.write(s)
        name_res = requests.get("https://download.fanyu.site/maimai/alias.json")
        with open("maiData/alias.json", "w", encoding="utf-8") as file:
            file.write(name_res.text)
        mai_data = open("maiData/music_data.txt", "r", encoding="utf-8").read()
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
                nd_info = "Utage " + song["level"][0] + "\n"
            else:
                nd_info = (
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
                nd_info += (
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
                + nd_info
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
                or (type == "宴会場" or len(id) > 5 and len(song["id"]) <= 5)
            ):
                break

    if len(list) > 1:
        msg = "查询到多个歌曲，请使用ID查询。可加上“SD”或“DX”区分类型\n"
        for i in range(len(list)):
            msg += (
                str(list[i]["id"])
                + ". "
                + list[i]["title"]
                + " ("
                + list[i]["type"]
                + ")\n"
            )
        msg = msg[:-1]  # 切片删换行
        get_msg(data, msg)
        return "多个歌曲", 200

    debug.print(text)

    img = ""
    if len(list) > 0:
        getPic(list[0], "mai")
        img = {
            "type": "image",
            "data": {
                "file": "file:///sdcard/Pictures/maiPic/"
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
        "data": {"file": "file:///sdcard/Pictures/maiPic/" + str(song["id"]) + ".jpg"},
    }

    msg = {
        "type": "text",
        "data": {"text": text},
    }
    post_msg(data, [img, msg])

    return song, 200


def add_rounded_corners(img, radius):
    # 创建一个与图像大小相同的 alpha 遮罩
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)

    # 画圆角矩形
    draw.rounded_rectangle([(0, 0), img.size], radius, fill=255)

    # 将遮罩应用到图像上
    img.putalpha(mask)
    return img


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


def txt_faded(txt, text_width):
    text_width += 13  # 文字切掉的有点多，补正一下

    # 创建一个单独的图层用于绘制文字
    text_layer = Image.new("RGBA", (text_width, 18), (255, 255, 255, 0))  # 完全透明背景
    text_draw = ImageDraw.Draw(text_layer)

    # 在文字图层上绘制文字
    text_draw.text(
        (0, 0),
        txt,
        font=ImageFont.truetype("C:/WINDOWS/FONTS/UDDIGIKYOKASHON-B.TTC", 16),
        fill=(255, 255, 255),
    )

    # 创建渐变蒙版，控制右侧逐渐透明
    gradient = Image.new("L", text_layer.size, 255)  # 单通道（L模式），全白
    for x in range(text_width):
        transparency = int(
            max(0, 255 - (x - text_width + 20) * 12.75)
        )  # 渐变从最后20px开始，最后的因子由255/x得到
        for y in range(18):
            gradient.putpixel((x, y), transparency)

    # 将渐变蒙版应用到文字图层
    text_with_fade = Image.composite(
        text_layer,
        Image.new("RGBA", text_layer.size, (255, 255, 255, 0)),
        gradient,
    )

    return text_with_fade


def mai_b50(data):
    mai_update(data)
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
        get_msg(data, "用户名错误，注意是水鱼网站的用户名，不是游戏的ID哦！")
        return "b50", 400
    if res.status_code == 403:
        get_msg(data, "该用户设置了禁止查询哦！")
        return "b50", 403
    user_info = json.loads(res.text)
    songs = json.loads(str(mai_data), strict=False)
    reply_msg = {"type": "text", "data": {"text": ""}}

    margin_x = 200
    font_xxl = ImageFont.truetype("C:/WINDOWS/FONTS/UDDIGIKYOKASHON-B.TTC", 50)
    font_xl = ImageFont.truetype("C:/WINDOWS/FONTS/UDDIGIKYOKASHON-B.TTC", 40)
    font_large = ImageFont.truetype("C:/WINDOWS/FONTS/UDDIGIKYOKASHON-B.TTC", 25)
    font_small = ImageFont.truetype("C:/WINDOWS/FONTS/UDDIGIKYOKASHON-B.TTC", 16)
    font_xs = ImageFont.truetype("C:/WINDOWS/FONTS/UDDIGIKYOKASHON-B.TTC", 13)

    bg = (
        Image.open("C:/Users/12203/Desktop/bg/119614191_p0.png")
        .resize([2100, 2100])
        .convert("RGBA")
    )
    draw = ImageDraw.Draw(bg)

    # 用户名与rt
    if user_info["rating"] < 1000:
        rt_img = Image.open("C:/Users/12203/Desktop/rating_base_normal.png")
    elif user_info["rating"] < 2000:
        rt_img = Image.open("C:/Users/12203/Desktop/rating_base_blue.png")
    elif user_info["rating"] < 4000:
        rt_img = Image.open("C:/Users/12203/Desktop/rating_base_green.png")
    elif user_info["rating"] < 7000:  # 找不到黄色的，先用红的
        rt_img = Image.open("C:/Users/12203/Desktop/rating_base_red.png")
    elif user_info["rating"] < 10000:
        rt_img = Image.open("C:/Users/12203/Desktop/rating_base_red.png")
    elif user_info["rating"] < 12000:
        rt_img = Image.open("C:/Users/12203/Desktop/rating_base_purple.png")
    elif user_info["rating"] < 13000:
        rt_img = Image.open("C:/Users/12203/Desktop/rating_base_bronze.png")
    elif user_info["rating"] < 14000:
        rt_img = Image.open("C:/Users/12203/Desktop/rating_base_silver.png")
    elif user_info["rating"] < 14500:
        rt_img = Image.open("C:/Users/12203/Desktop/rating_base_gold.png")
    elif user_info["rating"] < 15000:
        rt_img = Image.open("C:/Users/12203/Desktop/rating_base_platinum.png")
    else:
        rt_img = Image.open("C:/Users/12203/Desktop/rating_base_rainbow.png")

    name_bg = (
        Image.open("C:/Users/12203/Desktop/deco27_enhanced.jpg")
        .resize([600, 170], Image.LANCZOS)
        .convert("RGBA")
    )
    outline = Image.new("RGBA", (name_bg.width + 3, name_bg.height + 3), (0, 0, 0, 0))
    outline_draw = ImageDraw.Draw(outline)
    outline.paste(name_bg, (2, 2))
    outline_draw.rectangle(
        [(0, 0), (name_bg.width + 3, name_bg.height + 3)],
        outline=(255, 0, 255, 255),  # 粉紫
        width=3,
    )
    name_bg = outline.filter(ImageFilter.GaussianBlur(2))
    bg.paste(
        name_bg,
        (margin_x, 30),
    )
    draw.text(
        (margin_x + 35, 50),
        user_info["username"],
        font=font_xxl,
    )

    rt_pos = (margin_x + 20, 100)
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
    logo = Image.open("C:/Users/12203/Desktop/maimai_DX_2024.png").resize((356, 296))
    bg.paste(
        logo,
        logo_pos,
        logo,
    )

    # 分数统计 & 曲绘准备
    sd_tot, sd_avg, dx_tot, dx_avg = 0, 0, 0, 0
    img_paths = []
    for s in user_info["charts"]["sd"]:
        img_paths.append(getPic(s))
        sd_tot += s["ra"]
        sd_avg += s["ds"]
    for s in user_info["charts"]["dx"]:
        img_paths.append(getPic(s))
        dx_tot += s["ra"]
        dx_avg += s["ds"]
    song_imgs = []
    for i in img_paths:
        img = Image.open(i).resize((120, 120), Image.LANCZOS)
        img = add_rounded_corners(img, 15)
        song_imgs.append(img)

    sd_avg /= 35
    dx_avg /= 15
    sd_avg_score = sd_tot / 35
    dx_avg_score = dx_tot / 15
    sd_avg = f"{sd_avg:.2f}"
    dx_avg = f"{dx_avg:.2f}"
    sd_avg_score = f"{sd_avg_score:.2f}"
    dx_avg_score = f"{dx_avg_score:.2f}"

    b35_pos = (margin_x, 220)
    b15_pos = 0

    # 计算歌曲位置
    position = []
    for index, img in enumerate(song_imgs):
        x = margin_x + (index % 5) * 340
        y = 300 + (index // 5) * 160
        if index > 34:
            y += 150
            b15_pos = (x, y - 80) if b15_pos == 0 else b15_pos
        position.append((x, y))

    best_bg = Image.open("C:/Users/12203/Desktop/bg_b30.png")
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
    b15_pos = (b15_pos[0] + 18, b15_pos[1] + 5)
    b35_pos = (b35_pos[0] + 18, b35_pos[1] + 5)
    draw.text(
        b35_pos,
        f"B35 - {sd_tot}",
        font=font_xxl,
    )  # 最长宽度（5位数）：275
    draw.text(
        b15_pos,
        f"B15 - {dx_tot}",
        font=font_xxl,
    )
    b35_pos = (b35_pos[0] + 305, b35_pos[1] + 4)
    b15_pos = (b15_pos[0] + 305, b15_pos[1] + 4)
    draw.text(
        b35_pos,
        f"Avg. {sd_avg_score} / {sd_avg}",
        font=font_xl,
    )
    draw.text(
        b15_pos,
        f"Avg. {dx_avg_score} / {dx_avg}",
        font=font_xl,
    )

    cnt = 1  # 排名
    for img, pos, info in zip(
        song_imgs, position, user_info["charts"]["sd"] + user_info["charts"]["dx"]
    ):
        margin_left = 10
        margin_top = 10
        # 背景
        color_bg = Image.open(
            "C:/Users/12203/Desktop/bg_"
            + str(info["level_label"]).replace(":", "")
            + ".png"
        )
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
        image = Image.open(
            "C:/Users/12203/Desktop/music_" + info["type"] + ".png"
        ).resize((60, 17))
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
        # bbox (left, top, right, bottom)
        main_box = draw.textbbox(**main_param)
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
        rate_image = Image.open(
            "C:/Users/12203/Desktop/" + info["rate"] + ".png"
        ).resize((80, 31))
        bg.paste(
            rate_image,
            (pos[0] + pic_width - 3, pos[1] + 103),
            rate_image,
        )
        tot_height += main_height + 3

        # 定数与rating
        ds_param = {
            "xy": (pos[0] + pic_width, pos[1] + tot_height),
            "text": (str(info["ds"]) + " → " + str(info["ra"])),
            "font": ImageFont.truetype("C:/WINDOWS/FONTS/UDDIGIKYOKASHON-B.TTC", 21),
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
                image = Image.open(
                    "C:/Users/12203/Desktop/music_icon_dxstar_" + str(dxScore) + ".png"
                ).resize((30, 30))

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
                    "text": "发现到你设置了“对非网页查询的成绩使用掩码”，若你想获取更详细的成绩与dx分，请在查分网站的个人资料中取消设置。"
                },
            }

        # fc与fs
        if info["fc"] != "":
            # 原size 42x47
            image = Image.open("C:/Users/12203/Desktop/" + info["fc"] + ".png").resize(
                (30, 34)
            )
            bg.paste(
                image,
                (pos[0] + pic_width + rate_image.size[0] + 35, pos[1] + tot_height),
                image,
            )

        if info["fs"] != "":
            image = Image.open("C:/Users/12203/Desktop/" + info["fs"] + ".png").resize(
                (30, 34)
            )
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
                msg += "ID " + l["id"] + " - " + l["title"] + " (" + l["type"] + ")\n"
            # 切片删换行
            msg = msg[:-1]
            get_msg(data, "查询到多个歌曲，请使用ID查询\n" + msg)
            return "多个别名", 200

        for a in alia:
            msg += a + "，"
        msg = msg[:-1]
        get_msg(data, "ID为" + str(list[0]["id"]) + "的歌曲有以下别名：\n" + msg)
    else:
        list.append({"id": re.sub(r"\s*id\s*", "", name)})

        for sID, aliases in mai_alias.items():
            if sID == list[0]["id"]:
                for a in aliases:
                    msg += a + "，"
                msg = msg[:-1]
                get_msg(data, "ID为" + sID + "的歌曲有以下别名：\n" + msg)
                break

    return "别名", 200
