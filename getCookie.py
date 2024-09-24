import json
import os
import time

from selenium import webdriver

browser = webdriver.Edge()
browser.get("https://arcaea.lowiro.com/zh/profile/potential")

# 18秒内登陆完毕后获取cookie
time.sleep(18)
cookie = browser.get_cookies()

# 复制到剪切板
os.system("echo " + json.dumps(cookie) + " | clip")

# 将cookies保存到当前目录的cookies.txt
with open("cookies.txt", "w") as file:
    file.write(json.dumps(cookie))

browser.close()
