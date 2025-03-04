import base64
import io
import json
import math
import os
import random
import re
import subprocess
import time

import certifi
import opencc
import requests
from flask import (
    Flask,
    jsonify,
    redirect,
    request,
    send_file,
    send_from_directory,
    url_for,
)
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from debug import debug
from functions.botFunc import bilibili_search, bot_exit, get_msg, post_msg
from functions.chuFunc import (
    chu_alia,
    chu_b30,
    chu_data,
    chu_random,
    chu_search,
    chu_update,
)
from functions.getSongPic import getPic
from functions.maiFunc import (
    mai_alia,
    mai_b50,
    mai_data,
    mai_random,
    mai_search,
    mai_update,
)
from getB30 import b30
