import sys
import re
import pandas as pd
import time
from collections import OrderedDict
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from utils import *
from constants import *

sys.stdout = Logger(os.path.join(os.getcwd(), LOG_DIR, 'generate_task.log'))

def generate_task():
    start_time = time.localtime()
    print('Start generating task at {}'.format(time.strftime('%Y-%m-%d %H:%M:%S', start_time)))

    driver = get_driver(TYPE_BROWSER, HEADLESS)
    driver.get(URL)

    # 点击“更多”展开“分类标签”
    WebDriverWait(driver, WAIT_SECONDS).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="left"]/div[2]/ul/li[10]/a'))).click()
    # 定位所有的分类标签
    elem = WebDriverWait(driver, WAIT_SECONDS).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="middlediv"]/div/ul')))
    links = elem.find_elements(By.TAG_NAME, 'a')
    
    tasks = []
    current_window = driver.current_window_handle
    for link in links:
        task = OrderedDict()
        task['诗词标签'] = link.text

        link.click()
        driver.switch_to.window(driver.window_handles[-1])

        elem = WebDriverWait(driver, WAIT_SECONDS).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="shuaixuan"]')))
        matchObj = re.match('.*\((.*)首\)', elem.text)
        total = int(matchObj.group(1))

        task['诗词总数'] = total
        task['已爬诗词'] = 0
        task['未爬诗词'] = total
        tasks.append(task)
        print('Generate task for catageory {}'.format(task['诗词标签']))

        driver.close()
        driver.switch_to.window(current_window)
    
    driver.close()
    pd.DataFrame(data=tasks).to_excel(TASK_FILE)
    end_time = time.localtime()
    print('Finish generating task at {}, total used time: {}s'.format(time.strftime('%Y-%m-%d %H:%M:%S', end_time), time.mktime(end_time) - time.mktime(start_time)))

if __name__ == '__main__':
    generate_task()

