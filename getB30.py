from __init__ import *


def b30(cookie):
    driver = webdriver.Edge()
    driver.get("https://arcaea.lowiro.com/zh/profile/potential")
    driver.delete_all_cookies()  # 首先清除浏览器已有的cookies

    # 读取cookies为json格式
    if cookie == "":
        with open("cookies.txt", "r") as f:
            cookie = json.load(f)
    else:
        cookie = json.loads(
            str(cookie)
            .replace("&#91;", "[")
            .replace("&#93;", "]")
            .replace("&#44;", ",")
        )

    # 删除字段防止报错
    for c in cookie:
        if "expiry" in c:
            del c["expiry"]
        driver.add_cookie(c)
    driver.refresh()

    # 关闭更新信息弹窗
    close = WebDriverWait(driver, 4).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "close"))
    )
    close.click()

    # 点击b30按钮
    buttons = WebDriverWait(driver, 1).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "button"))
    )
    buttons[5].click()

    # 等待b30图片出现
    image = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//div[@class='image-container']//a//img")
        )
    )

    # 获取图片的URL
    image_url = image.get_attribute("src")

    # 下载图片
    img_data = requests.get(image_url).content
    save_path = "C:\\Users\\12203\\Documents\\MuMu共享文件夹\\Pictures\\image.jpg"
    with open(save_path, "wb") as handler:
        handler.write(img_data)
    driver.close()

    if image == None:
        return Exception
