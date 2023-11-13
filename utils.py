#!/usr/bin/env python3
import os
import sys
import re
import pandas as pd
from collections import defaultdict
from selenium import webdriver
from constants import *

# 用于记录屏幕输出
class Logger(object):
    def __init__(self, filepath):
        self.terminal = sys.stdout
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        self.log = open(filepath, "a", encoding='UTF-8')
 
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
 
    def flush(self):
        pass

def get_driver(type_browser='chrome', headless=False):
    driver = None

    if type_browser == 'firefox':
        from selenium.webdriver.firefox.options import Options
        options = Options()
        if headless:
            options.add_argument('--headless')  
        driver = webdriver.Firefox(options=options) 
    elif type_browser == 'chrome':
        from selenium.webdriver.chrome.options import Options
        options = Options()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-extentions')
        options.add_argument('--ignore-certificate-errors-spki-list')
        options.add_argument('--ignore-ssl-errors')
        driver = webdriver.Chrome(options=options)
        
    return driver

# 获取爬取进度--每个分类标签已爬取的诗词
def get_crawled_poems_by_catageory():
    crawled = defaultdict(set)
    output_dirpath = os.path.join(os.getcwd(), OUTPUT_DIR)
    for (dirpath, dirnames, filenames) in os.walk(output_dirpath):
        foldername = dirpath.split('\\')[-1]
        for filename in filenames:
            if filename.endswith('.md'): 
                crawled[foldername].add(filename[:-3])
    return crawled

def get_expected_poems_by_catageory():
    expected = defaultdict(int)
    df = pd.read_excel(TASK_FILE, usecols='B, C', index_col=0)
    return df.to_dict()['诗词总数']

# 清除markdown文件中的noise
def remove_noise(s):
    s = re.sub('\[\!\[写翻译\]\n?(.*\n)*很差较差还行推荐力荐', '', s)
    s = re.sub('\[\!\[(写翻译|写赏析)\]\(.*?\) (写翻译|写赏析)\]\(.*?\)', '', s)
    s = re.sub('window.*\];', '', s)
    s = re.sub('\[...\].*"查看全文"\)', '', s)
    s = re.sub('\n+', '\n', s)
    return s

