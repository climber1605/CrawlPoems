#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import time
import random
from collections import OrderedDict
import sys
import os
from pathlib import Path
import utils
import requests

sys.stdout = utils.Logger('crawl.log')

def get_proxy():
    return requests.get('http://127.0.0.1:5010/get/').json()

def delete_proxy(proxy):
    requests.get('http://127.0.0.1:5010/delete/?proxy={}'.format(proxy))

def check_proxy(proxy):
    proxy = get_proxy().get('proxy')
    ok = True
    try:
        requests.get('http://httpbin.org/ip', proxies={'http': 'http://{}'.format(proxy)})
    except Exception:
        ok = False
    # 删除代理池中代理
    delete_proxy(proxy)
    return ok

# 将每三位以逗号分隔的字符串表示的数字转换成阿拉伯数字
def str2int(s):
    nums = [int(i) for i in s.split(',')]
    res = 0
    for num in nums:
        res = res * 1000 + num
    return res

# 检查年份y是否为在start与end之间
def check_date(y, start, end):
    for year in range(start, end + 1):
        if y == year:
            return True
    return False

url = 'https://www.cnki.net/old'
WAIT_SECONDS = 15
MAX_NUM_PAPERS = 1500

type_browser = 'chrome'  # 浏览器类型(目前仅支持chrome和firefox)
# 浏览器驱动路径
path_firefox_driver = '/home/panda/Downloads/geckodriver'
path_chrome_driver = '/home/panda/Downloads/chromedriver'
#path_chrome_driver = r'C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe'

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
        options.add_argument('start-maximized')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-extentions')
        if use_proxy:
            proxy = get_proxy().get('proxy')
            while not check_proxy(proxy):
                proxy = get_proxy().get('proxy')
            print('Using proxy: {}'.format(proxy))
            options.add_argument('--proxy-server=%s' % proxy)
        browser = webdriver.Chrome(options=options, executable_path=path_chrome_driver)
        
    return browser

def start_crawl(newspaper, publishdate_from, publishdate_to, output_file):
    global type_browser, url, WAIT_SECONDS, MAX_NUM_PAPERS
    print('Start crawling news from {} published during {} - {}'.format(newspaper, publishdate_from, publishdate_to))

    browser = get_browser(type_browser, headless=False, use_proxy=False)
    browser.get(url)

    # 等待高级检索按键加载完成并点击
    try:
        a_high_search = WebDriverWait(browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable(
                (By.LINK_TEXT, '高级检索')
            )
        )
    except TimeoutException as e:
        print('Timeout during waiting for loading of high search buttom.')
        browser.quit()
        return False
    a_high_search.click()
    time.sleep(1)

    # 切换到最新打开的窗口
    browser.switch_to.window(browser.window_handles[-1])
    time.sleep(3)
    
    # 找到文献来源标签，用于判断点击刷新完成
    try:
        input_src = WebDriverWait(browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="magazine_value1"]')
            )
        )
    except TimeoutException as e:
        print('Timeout during waiting for loading of buttom magazine_value1. newspaper: {}, time: {} - {}.'.format(newspaper, publishdate_from, publishdate_to))
        browser.quit()
        return False 
    browser.execute_script('arguments[0].click();', input_src)
    input_src.send_keys(newspaper)  # 输入报纸名
    time.sleep(2)

    # 找到文献来源对应的模糊/精确下拉框
    try:
        select_special = WebDriverWait(browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="magazine_special1"]')
            )
        )
    except TimeoutException as e:
        print('Timeout during waiting for loading of buttom magazine_special1. newspaper: {}, time: {} - {}.'.format(newspaper, publishdate_from, publishdate_to))
        browser.quit()
        return False 
    select_special.click()
    
    try:
        option_exact = WebDriverWait(browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="magazine_special1"]/option[2]')
            )
        )
    except TimeoutException as e:
        print('Timeout during waiting for loading of buttom option_exact. newspaper: {}, time: {} - {}.'.format(newspaper, publishdate_from, publishdate_to))
        browser.quit()
        return False 
    option_exact.click()

    # 找到起始时间输入框并输入起始时间
    try:
        input_publishdate_from = WebDriverWait(browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="publishdate_from"]')
            )
        )
    except TimeoutException as e:
        print('Timeout during waiting for loading of buttom publishdate_from. newspaper: {}, time: {} - {}.'.format(newspaper, publishdate_from, publishdate_to))
        browser.quit()
        return False 
    input_publishdate_from.send_keys(publishdate_from)

    # 找到结束时间输入框并输入结束时间
    try:
        input_publishdate_to = WebDriverWait(browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="publishdate_to"]')
            )
        )
    except TimeoutException as e:
        print('Timeout during waiting for loading of buttom publishdate_to. newspaper: {}, time: {} - {}.'.format(newspaper, publishdate_from, publishdate_to))
        browser.quit()
        return False 
    input_publishdate_to.send_keys(publishdate_to)
    input_publishdate_to.send_keys(Keys.ENTER)
    time.sleep(1)

    # 等待iframe加载完成并切换到iframe
    try:
        iframe_result = WebDriverWait(browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="iframeResult"]')
            )
        )
    except TimeoutException as e:
        print('Timeout during waiting for loading of iframe_reuslt. newspaper: {}, time: {} - {}.'.format(newspaper, publishdate_from, publishdate_to))
        browser.quit()
        return False 
    browser.switch_to.frame(iframe_result)

    # 找到每页文献数50标签并点击
    try:
        div_grid_display_num = WebDriverWait(browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="id_grid_display_num"]/a[3]')
            )
        )
    except TimeoutException as e:
        print('Timeout during waiting for loading of buttom div_grid_display_num. newspaper: {}, time: {} - {}.'.format(newspaper, publishdate_from, publishdate_to))
        browser.quit()
        return False 
    # 找到每页文献数标签，用于判断文献列表是否刷新完成
    try:
        span_count_page = browser.find_element_by_xpath('//*[@id="lbPagerTitle"]/../../span[1]')
    except NoSuchElementException as e:
        print(str(e))
        browser.quit()
        return False
    div_grid_display_num.click()
    
    # 通过每页文献数量标签的过期，判断文献列表刷新完成
    try:
        WebDriverWait(browser, WAIT_SECONDS).until(EC.staleness_of(span_count_page))
    except TimeoutException as e:
        print('Timeout during waiting for refresh of search results after clciking buttom div_grid_display_num. newspaper: {}, year: {} - {}.'.format(newspaper, publishdate_from, publishdate_to))
        browser.quit()
        return False

    #cols = ['题名', '作者', '报纸名称', '报纸日期', '关键词', '版名', '版号', '专辑', '专题', 'DOI', '分类号', '原文'] # 需要保存的信息种类
    result = []
    page_cnt = 0
    captcha_pages = [30, 60, 70, 80, 90, 100]  # 包含验证码的页面
    # 保存所有页的文献信息
    while True:
        page_cnt +=1
        '''
        if page_cnt > 1:
            break
        '''
        current_window = browser.current_window_handle
        try: 
            trs = browser.find_elements_by_xpath('//*[@id="ctl00"]/table/tbody/tr[2]/td/table/tbody/tr')
        except NoSuchElementException as e:
            print(str(e))
            break

        seq = 2  # 第一条新闻的tr下标
        # 保存当前页的所有文献信息
        while seq <= len(trs):
            '''
            if seq > 2:
                break
            '''
            # 表格的一列(td)对应一篇文献的特定信息，如篇名、作者         
            info = OrderedDict()

            a_news_name = browser.find_element_by_xpath('//*[@id="ctl00"]/table/tbody/tr[2]/td/table/tbody/tr[{}]/td[2]/a'.format(seq))
            info['题名'] = a_news_name.text

            td_author = browser.find_element_by_xpath('//*[@id="ctl00"]/table/tbody/tr[2]/td/table/tbody/tr[{}]/td[3]'.format(seq))
            info['作者'] = td_author.text

            a_newspaper_name = browser.find_element_by_xpath('//*[@id="ctl00"]/table/tbody/tr[2]/td/table/tbody/tr[{}]/td[4]/a'.format(seq))
            info['报纸名称'] = a_newspaper_name.text      

            td_publish_time = browser.find_element_by_xpath('//*[@id="ctl00"]/table/tbody/tr[2]/td/table/tbody/tr[{}]/td[5]'.format(seq))
            info['报纸时间'] = td_publish_time.text         

            # 点击题名并切换到最新打开的窗口
            a_news_name.click()
            time.sleep(1)
            browser.switch_to.window(browser.window_handles[-1])

            try:
                divs = browser.find_elements_by_xpath('//div[@class="row"]')
            except NoSuchElementException as e:
                print(str(e))
                browser.quit()
                return False

            for div in divs[1:-1]:
                idx = div.text.find('：')
                key, value = div.text[ : idx], div.text[idx + 1 : ]
                if key == '正文快照':
                    continue
                info[key] = value
            lines = divs[-1].text.split('\n')
            for line in lines:
                #print(line)
                idx = line.find('：')
                key, value = line[ : idx], line[idx + 1 : ]
                info[key] = value
            
            # 关闭当前窗口，返回上级窗口
            browser.close()
            browser.switch_to.window(current_window)
            # 等待iframe加载完成并切换到iframe
            try:
                iframe_result = WebDriverWait(browser, WAIT_SECONDS).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, '//*[@id="iframeResult"]')
                    )
                )
            except TimeoutException as e:
                print('Timeout during waiting for loading of iframe_reuslt. newspaper: {}, time: {} - {}.'.format(newspaper, publishdate_from, publishdate_to))
                browser.quit()
                return False 
            browser.switch_to.frame(iframe_result)

            '''
            # 点击html阅读并切换窗口
            a_html = browser.find_element_by_xpath('//*[@id="ctl00"]/table/tbody/tr[2]/td/table/tbody/tr[{}]/td[9]/a'.format(seq))
            a_html.click()
            time.sleep(1)
            browser.switch_to.window(browser.window_handles[-1])

            try:
                ps = browser.find_elements_by_xpath('//div[@class="p1"]')
            except NoSuchElementException as e:
                print(str(e))
                browser.quit()
                return False 
            #print('number of paragraph: {}'.format(len(ps)))
            full_news = []
            for p in ps:
                full_news.append(p.text)
                #print(p.text)
                info['原文'] = '\n'.join(full_news)

            # 关闭当前窗口，返回上级窗口
            browser.close()
            browser.switch_to.window(current_window)
            # 等待iframe加载完成并切换到iframe
            try:
                iframe_result = WebDriverWait(browser, WAIT_SECONDS).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, '//*[@id="iframeResult"]')
                    )
                )
            except TimeoutException as e:
                print('Timeout during waiting for loading of iframe_reuslt. newspaper: {}, time: {} - {}.'.format(newspaper, publishdate_from, publishdate_to))
                browser.quit()
                return False 
            browser.switch_to.frame(iframe_result)
            '''

            result.append(info)
            seq += 1

        # 寻找下一页按键
        try:
            next_page = WebDriverWait(browser, WAIT_SECONDS).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="Page_next"]')
                )
            )
        except TimeoutException:
            break
        next_page.click()

        '''
        # 30页必出验证码
        if page_cnt in captcha_pages:
            time.sleep(15)
        '''
        time.sleep(1)
    
    # 将爬取结果保存到excel中
    if len(result):
        df = pd.DataFrame(data=result)
        df.to_excel(output_file) 
    
    browser.quit()
    print('Finish crawling papers from {} published in year: {} - {}, number of papers: {}'.format(newspaper, publishdate_from, publishdate_to, len(result)))
    return len(result) > 0

def is_leapyear(year):
    return year % 100 and year % 4 == 0 or year % 400 == 0

def main():
    start_time = time.time()
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

    # 创建用于保存输出结果的目录
    cwd = os.getcwd()
    output_dir = os.path.join(cwd, 'output')
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    newspaper = '证券时报'
    dates = [('01-01', '01-31'), ('02-01', '02-28'), ('03-01', '03-31'), ('04-01', '04-30'), ('05-01', '05-31'), ('06-01', '06-30'), 
             ('07-01', '07-31'), ('08-01', '08-31'), ('09-01', '09-30'), ('10-01', '10-31'), ('11-01', '11-30'), ('12-01', '12-31')]
    succeed = failed = skipped = 0

    for year in range(2008, 2021):
        for from_, to in dates:
            if is_leapyear(year) and to == '02-28':
                to = '02-29'
            publishdate_from, publishdate_to = str(year) + '-' + from_, str(year) + '-' + to
            output_file = os.path.join(output_dir, newspaper + '_' + publishdate_from + '_' + publishdate_to + '.xlsx')

            if not Path(output_file).is_file():
                if start_crawl(newspaper, publishdate_from, publishdate_to, output_file):
                    succeed += 1
                else:
                    failed += 1
            else:
                skipped += 1  

            print('Finished crawl {} from {} to {}. Total succeed: {}, total failed: {}, total skipped: {}, total used time: {}'.format(newspaper, publishdate_from, publishdate_to, succeed, failed, skipped, time.time() - start_time))   

    print('Finished crawl. Total succeed: {}, total failed: {}, total skipped: {}, total used time: {}'.format(succeed, failed, skipped, time.time() - start_time))  
    
if __name__ == '__main__':
    main()
