import os
import sys
import pandas as pd
from constants import *
from utils import *

def update_task():
    crawled = get_crawled_poems_by_catageory()
    df = pd.read_excel(TASK_FILE, index_col=0)
    df['已爬诗词'] = df.apply(lambda x: len(crawled[x['诗词标签']]), axis=1)
    df['未爬诗词'] = df.apply(lambda x: x['诗词总数'] - x['已爬诗词'], axis=1)
    df.to_excel(TASK_FILE)

if __name__ == '__main__':
    update_task()