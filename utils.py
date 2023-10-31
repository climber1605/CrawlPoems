#!/usr/bin/env python3
import sys

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
