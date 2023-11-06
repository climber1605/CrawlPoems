#!/usr/bin/env python3
import sys
import re

# 用于记录屏幕输出
class Logger(object):
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "w", encoding='UTF-8')
 
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
 
    def flush(self):
        pass

def remove_noise(s):
    s = re.sub('\[\!\[写翻译\]\n?(.*\n)*很差较差还行推荐力荐', '', s)
    s = re.sub('\[\!\[(写翻译|写赏析)\]\(.*?\) (写翻译|写赏析)\]\(.*?\)', '', s)
    #s = re.sub('\[\!\[.*?\]\(.*?\.jpg\)\]', '', s)
    s = re.sub('window.*\];', '', s)
    #s = re.sub('\(.*?\.html\)', '', s)
    s = re.sub('\[...\].*"查看全文"\)', '', s)
    s = re.sub('\n+', '\n', s)
    return s

