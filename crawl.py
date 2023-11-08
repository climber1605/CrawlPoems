#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
import markdownify
import time
import sys
import os
from utils import *

sys.stdout = Logger('crawl.log')

url = 'http://www.shangshiwen.com'
WAIT_SECONDS = 15

type_browser = 'chrome'  # 浏览器类型(目前仅支持chrome和firefox)

def get_browser(type_browser, headless=False, use_proxy=False):
    global path_firefox_driver, path_chrome_driver
    browser = None

    if type_browser == 'firefox':
        from selenium.webdriver.firefox.options import Options
        options = Options()
        if headless:
            options.add_argument('--headless')  
        browser = webdriver.Firefox(options=options, executable_path=path_firefox_driver) 
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
        browser = webdriver.Chrome(options=options)
        
    return browser

def start_crawl(output_file):
    global type_browser, url, WAIT_SECONDS
    print('Start crawling poem.')

    browser = get_browser(type_browser, headless=False, use_proxy=False)
    browser.get(url)

    succeed = failed = 0
    current_catageory = 1
    while True:
        current_window_catageory = browser.current_window_handle
        try:
            elem = WebDriverWait(browser, WAIT_SECONDS).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="middlediv"]/div[1]/ul/li[{}]/a'.format(current_catageory))
                )
            )
        except TimeoutException as e:
            print('Timeout during waiting for current catageory.')
            browser.quit()
            return False
        elem.click()
        time.sleep(1)
        current_catageory += 1

        # 切换到最新打开的窗口
        browser.switch_to.window(browser.window_handles[-1])
        time.sleep(1)

        poems_per_page = 20
        current_page = 1
        has_next_page = True

        while has_next_page:
            current_window = browser.current_window_handle
            for i in range(poems_per_page):
                try:
                    elem = WebDriverWait(browser, WAIT_SECONDS).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, '//*[@id="middlediv"]/div[1]/ul/li[{}]/a[1]'.format(i + 1)) 
                        )
                    )
                except TimeoutException as e:
                    print('Timeout during waiting for poem {}.'.format(i + 1))
                    failed += 1
                    continue
                elem.click()
                time.sleep(1)

                # 切换到最新打开的窗口
                browser.switch_to.window(browser.window_handles[-1])
                time.sleep(3)

                try:
                    elem = WebDriverWait(browser, WAIT_SECONDS).until(
                        EC.visibility_of_element_located(
                            (By.XPATH, '//*[@id="rightwo"]')  
                        )
                    )
                except TimeoutException as e:
                    print('Timeout during waiting for poem {}.'.format(i + 1))
                    continue
                    
                html = elem.get_attribute("outerHTML")
                md = markdownify.markdownify(html, heading_style='ATX')
                md = remove_noise(md)

                with open(output_file, 'a', encoding='utf-8') as f:
                    f.write(md)
                    f.write('\n')
                
                succeed += 1
                browser.close()
                browser.switch_to.window(current_window)
                time.sleep(1)

            if i + 1 == poems_per_page:
                try:
                    elem = WebDriverWait(browser, WAIT_SECONDS).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, '//*[contains(text(), "下一页")]') 
                        )
                    )
                except TimeoutException as e:
                    print('Timeout during waiting for next page')
                    has_next_page = False
                    continue      
                elem.click()  
                time.sleep(1)
                current_page += 1

                print('Succceed: {}, Failed: {}, Current page: {}'.format(succeed, failed, current_page)) 

        browser.close()
        browser.switch_to.window(current_window_catageory)
        
    return True

def main():
    start_time = time.time()
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

    # 创建用于保存输出结果的目录
    cwd = os.getcwd()
    output_dir = os.path.join(cwd, 'output')
    output_file = os.path.join(output_dir, 'poem.md')
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    start_crawl(output_file)
    print('Finished crawl. Total used time: {}'.format(time.time() - start_time))   
    
if __name__ == '__main__':
    main()