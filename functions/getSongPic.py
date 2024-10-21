from __init__ import *


def getPic(song, res="mai"):
    id = song["id"] if "id" in song else song["song_id"]
    id = str(id).zfill(5)
    save_path = (
        "C:/Users/12203/Documents/MuMu共享文件夹/Pictures/" + res + "Pic/" + id + ".png"
    )
    if res == "mai":
        if os.path.exists(save_path) == False:
            print("图片不存在")
        else:
            return save_path

        # 先获取 水鱼 曲绘
        image_url = "https://www.diving-fish.com/covers/" + id + ".png"
        req = requests.get(image_url)
        img_data = req.content
        if req.status_code == 200:
            print("get - 水鱼")
            with open(save_path, "wb") as handler:
                handler.write(img_data)
            return save_path
        return getFandom(song, res)
    else:
        if os.path.exists(save_path) == False:
            print("图片不存在")
        else:
            return save_path
        return getFandom(song, res)


def getFandom(song, res):
    # 获取 Fandom 曲绘
    options = webdriver.EdgeOptions()
    options.add_argument("log-level=3")  # 只显示致命错误
    # options.add_argument("--ignore-certificate-error")
    # options.add_argument("--ignore-ssl-errors")
    # caps = webdriver.DesiredCapabilities.EDGE.copy()
    # caps["acceptInsecureCerts"] = True
    # caps["acceptSslCerts"] = True

    options.page_load_strategy = "eager"  # 停止页面的不必要加载
    driver = webdriver.Edge(options=options)
    driRes = "maimai" if res == "mai" else "chunithm"
    driver.get(
        "https://"
        + driRes
        + ".fandom.com/zh/wiki/"
        + song["title"].replace(" ", "_").replace("'", "’")
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
    id = song["id"] if "id" in song else song["song_id"]
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
