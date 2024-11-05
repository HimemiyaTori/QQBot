from __init__ import *


def getPic(song, res="mai"):
    id = str(
        song["id"]
        if "id" in song
        else song["song_id"] if "song_id" in song else song["mid"]
    )
    if res == "mai" and len(id) == 5:
        id = id[1:]
    save_path = f"C:/Users/12203/Documents/MuMu共享文件夹/Pictures/{res}Pic/{id}.png"
    if os.path.exists(save_path) == True:
        return save_path

    print("图片不存在")
    path = getLx(id, res)
    if path != None:
        return path

    # if res == "mai":
    #     # 获取 水鱼 曲绘
    #     image_url = "https://www.diving-fish.com/covers/" + id + ".png"
    #     req = requests.get(image_url)
    #     img_data = req.content
    #     if req.status_code == 200:
    #         print("水鱼get")
    #         with open(save_path, "wb") as handler:
    #             handler.write(img_data)
    #         return save_path
    return getFandom(song, res)


def getLx(id, res):
    if res == "mai":
        url = "https://assets2.lxns.net/maimai/jacket/" + id + ".png"
    else:
        url = "https://assets2.lxns.net/chunithm/jacket/" + id + ".png"
    # 发送 HTTP 请求获取网页内容
    response = requests.get(url)
    response.raise_for_status()  # 检查请求是否成功

    # 获取图片内容
    img_response = requests.get(url)
    img_response.raise_for_status()

    # 获取图片文件名
    img_name = os.path.basename(url)

    # 保存图片
    save_path = f"C:/Users/12203/Documents/MuMu共享文件夹/Pictures/{res}Pic"
    img_path = os.path.join(save_path, img_name)
    with open(img_path, "wb") as img_file:
        img_file.write(img_response.content)

    print(f"落雪get {img_name}")
    return img_path


def getFandom(song, res):
    # 获取 Fandom 曲绘
    options = webdriver.EdgeOptions()
    options.add_argument("log-level=3")  # 只显示致命错误

    options.page_load_strategy = "eager"  # 停止页面的不必要加载
    driver = webdriver.Edge(options=options)
    driRes = "maimai" if res == "mai" else "chunithm"
    driver.get(
        "https://"
        + driRes
        + ".fandom.com/zh/wiki/"
        + song["title"]
        .replace(" ", "_")
        .replace("'", "’")
        .replace("[", "［")
        .replace("]", "］")
    )
    image = WebDriverWait(driver, 3).until(
        EC.visibility_of_element_located((By.XPATH, "//div[@class='floatnone']//a"))
    )
    print("get - fandom")
    image_url = image.get_attribute("href")  # 获取图片的URL

    # 下载图片
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
        "Referer": "https://maimai.fandom.com/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    }
    img_data = requests.get(image_url, headers=headers).content
    id = (
        song["id"]
        if "id" in song
        else song["song_id"] if "song_id" in song else song["mid"]
    )
    id = str(id).zfill(5)
    save_path = (
        "C:/Users/12203/Documents/MuMu共享文件夹/Pictures/" + res + "Pic/" + id + ".png"
    )
    with open(save_path, "wb") as handler:
        handler.write(img_data)
    driver.close()
    return save_path

    # 将图片路径转换为安卓模拟器中的路径
    # android_path = "/sdcard/Pictures/maiPic/" + song["id"] + ".jpg"

    # 使用 adb 命令刷新相册，刷不出来哇
    # subprocess.run(
    #     [
    #         "adb",
    #         "shell",
    #         "am",
    #         "broadcast",
    #         "-a",
    #         "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
    #         "-d",
    #         "file://" + android_path,
    #     ],
    # )
    # os.system(
    #     "adb shell am broadcast -a android.intent.ACTION_MEDIA_SCANNER_SCAN_FILE -d file://"
    #     + android_path
    # )
