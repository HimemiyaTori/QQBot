from __init__ import *


def getPic(song):
    id = str(song["id"]) if "id" in song else str(song["song_id"])
    # if len(id) == 5:
    #     id = id[1:]
    id = id.zfill(5)
    if (
        os.path.exists(
            "C:/Users/12203/Documents/MuMu共享文件夹/Pictures/maiPic/" + id + ".png"
        )
        == False
    ):
        print("图片不存在")
    else:
        return "C:/Users/12203/Documents/MuMu共享文件夹/Pictures/maiPic/" + id + ".png"

    # 先获取 水鱼 曲绘
    image_url = "https://www.diving-fish.com/covers/" + id + ".png"
    req = requests.get(image_url)
    img_data = req.content
    if req.status_code != 404:
        print("get - 水鱼")
        save_path = (
            "C:/Users/12203/Documents/MuMu共享文件夹/Pictures/maiPic/" + id + ".png"
        )
        with open(save_path, "wb") as handler:
            handler.write(img_data)
    else:
        # 获取 Fandom 曲绘
        options = webdriver.EdgeOptions()
        options.add_argument("log-level=3")  # 只显示致命错误
        # options.add_argument("--ignore-certificate-error")
        # options.add_argument("--ignore-ssl-errors")
        # caps = webdriver.DesiredCapabilities.EDGE.copy()
        # caps["acceptInsecureCerts"] = True
        # caps["acceptSslCerts"] = True
        # 停止页面的不必要加载
        options.page_load_strategy = "eager"
        driver = webdriver.Edge(options=options)
        driver.get("https://maimai.fandom.com/zh/wiki/" + song["title"])
        image = WebDriverWait(driver, 1).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@class='floatnone']//a"))
        )
        # 获取图片的URL
        print("get - fandom")
        image_url = image.get_attribute("href")

        # 下载图片
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
            "Referer": "https://maimai.fandom.com/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        }
        img_data = requests.get(image_url, headers=headers).content
        save_path = (
            "C:/Users/12203/Documents/MuMu共享文件夹/Pictures/maiPic/" + id + ".png"
        )
        with open(save_path, "wb") as handler:
            handler.write(img_data)
        driver.close()
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

    return "C:/Users/12203/Documents/MuMu共享文件夹/Pictures/maiPic/" + id + ".png"
