import json
import os
import random
import re
import subprocess
import time

import opencc
import requests
from flask import Flask, jsonify, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from debug import debug
from functions.botFunc import bot_exit, get_msg, post_msg
from functions.chuFunc import chu_data, chu_random, chu_search, chu_update
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
