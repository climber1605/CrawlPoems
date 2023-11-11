#!/usr/bin/env python3
import os
import sys
import time
import markdownify
from collections import defaultdict
from retrying import retry
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from utils import *
from constants import *

sys.stdout = Logger(os.path.join(os.getcwd(), LOG_DIR, 'crawl.log'))

#@retry(stop_max_attempt_number=3)
def start_crawl(url):
    start_time = time.localtime()
    print('Start crawling {} at {}'.format(url, time.strftime('%Y-%m-%d %H:%M:%S', start_time)))

    succeed = failed = skipped = 0
    crawled = get_crawled_output()
    
    driver = get_driver(TYPE_BROWSER, HEADLESS)
    driver.get(url)
 
    # 点击“更多”展开“分类标签”
    WebDriverWait(driver, WAIT_SECONDS).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="left"]/div[2]/ul/li[10]/a')
        )
    ).click()
    # 定位所有的分类标签
    elem = WebDriverWait(driver, WAIT_SECONDS).until(
        EC.visibility_of_element_located(
            (By.XPATH, '//*[@id="middlediv"]/div/ul')
        )
    )
    links = elem.find_elements(By.TAG_NAME, 'a')
    
    current_window = driver.current_window_handle
    cnt = defaultdict(int)

    def crawl_catageory(catageory: str) -> None:
        nonlocal succeed, failed, skipped
        start_time = time.localtime()
        print('Start crawling catageory {} at {}'.format(catageory, time.strftime('%Y-%m-%d %H:%M:%S', start_time)))

        def crawl_page(catageory: str, page: int) -> None:
            nonlocal succeed, failed, skipped
            start_time = time.localtime()
            print('Start crawling page {} at {}'.format(page, time.strftime('%Y-%m-%d %H:%M:%S', start_time)))

            elems = WebDriverWait(driver, WAIT_SECONDS).until(
                EC.visibility_of_all_elements_located(
                    (By.XPATH, '//*[@id="middlediv"]/div[1]/ul/li')
                )
            )
            poems_per_page = len(elems)

            current_window = driver.current_window_handle   
            for i in range(poems_per_page):
                # 定位当前页每一首诗词的链接并点击
                try:
                    poem_links = WebDriverWait(driver, WAIT_SECONDS).until(
                        EC.visibility_of_all_elements_located(
                            (By.XPATH, '//*[@id="middlediv"]/div[1]/ul/li[{}]/a'.format(i + 1))
                        )
                    )
                except TimeoutException as e:
                    print('Timeout during waiting for link of poem #{} in page {} in catageory {}'.format(i + 1, page, catageory))
                    failed += 1
                    continue

                # 清洗标题作者朝代中不能出现在文件名中的字符
                title = poem_links[0].text
                author = poem_links[1].text if len(poem_links) > 1 else ''
                dynasty = poem_links[2].text if len(poem_links) > 2 else ''
                poem = '_'.join([title, author, dynasty])
                poem = re.sub(r'[\\\/\:\*\?\"\<\>\|\ue423]', '', poem)

                # 当同一分类标签中的诗词出现重复时，文件名额外添加后缀（?）
                cnt[poem] += 1
                if cnt[poem] > 1:
                    print("Poem {} appears {} times in catageory {}".format(poem, cnt[poem], catageory))
                    poem += '（{}）'.format(cnt[poem] - 1)

                # 判断当前诗词是否已经爬取过，是则跳过
                if poem in crawled[catageory]:
                    print('Skip poem #{} in page {} in catageory {}, poem: {}'.format(i + 1, page, catageory, poem))
                    skipped += 1
                    continue

                # 点击诗词链接并切换到最新打开的窗口
                poem_links[0].click()
                driver.switch_to.window(driver.window_handles[-1])

                # 定位到感兴趣的DOM结点
                try:
                    elem = WebDriverWait(driver, WAIT_SECONDS).until(
                        EC.visibility_of_element_located(
                            (By.XPATH, '//*[@id="rightwo"]')  
                        )
                    )
                except TimeoutException as e:
                    print('Timeout during waiting for info of poem #{} in page {} in catageory {}, poem: {}'.format(i + 1, page, catageory, poem))
                    continue
                
                # 提取诗词信息并转换为markdown格式
                html = elem.get_attribute("outerHTML")
                md = markdownify.markdownify(html, heading_style='ATX')
                md = remove_noise(md)
                
                # 以“标题_作者_朝代.md”作为文件名保存爬取结果
                filename = poem + '.md'
                filepath = os.path.join(os.getcwd(), OUTPUT_DIR, catageory, filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(md)
            
                print('Current succeed: {}, current failed: {}, current skipped: {}'.format(succeed, failed, skipped))          
                print('Successfully crawled poem #{} in page {} in catageory {}, poem: {}'.format(i + 1, page, catageory, poem))
                succeed += 1
                driver.close()
                driver.switch_to.window(current_window)

            end_time = time.localtime()
            print('Finish crawling page {} at {}, total used time: {}s'.format(page, time.strftime('%Y-%m-%d %H:%M:%S', end_time), time.mktime(end_time) - time.mktime(start_time)))

        has_next_page = True
        while has_next_page:
            # 找到当前页码
            elem = WebDriverWait(driver, WAIT_SECONDS).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="middlediv"]/div[2]/div')))
            span = elem.find_element(By.CLASS_NAME, 'cur')
            page = int(span.text)
        
            crawl_page(catageory, page)

            # 尝试点击下一页
            try:
                WebDriverWait(driver, WAIT_SECONDS).until(EC.element_to_be_clickable((By.XPATH, '//*[contains(text(), "下一页")]'))).click()
            except TimeoutException as e:
                print('Timeout during waiting for next page on page {}.'.format(page))
                has_next_page = False         

        end_time = time.localtime()
        print('Finish crawling catageory {} at {}, total used time: {}s'.format(catageory, time.strftime('%Y-%m-%d %H:%M:%S', end_time), time.mktime(end_time) - time.mktime(start_time)))
        
    for link in links:
        # 点击每个分类标签并切换至新打开的窗口
        catageory = link.text
        link.click()
        driver.switch_to.window(driver.window_handles[-1])

        # 提取该分类标签的诗词总数
        elem = WebDriverWait(driver, WAIT_SECONDS).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="shuaixuan"]')
            )
        )
        matchObj = re.match('.*\((.*)首\)', elem.text)
        total = int(matchObj.group(1))

        if total <= len(crawled[catageory]):
            print("Skip catageory {} since crawl has completed".format(catageory))
            skipped += total
        else:
            print('Found {} poems in catageory {} while only {} of them have been crawled'.format(total, catageory, len(crawled[catageory])))
            if catageory != '描写黄河':
                crawl_catageory(catageory)

        driver.close()
        driver.switch_to.window(current_window)

    driver.close()
    end_time = time.localtime()
    print('Total succeed: {}, total failed: {}, total skipped: {}'.format(succeed, failed, skipped))
    print('Finish crawling {} at {}, total used time: {}s'.format(url, time.strftime('%Y-%m-%d %H:%M:%S', end_time), time.mktime(end_time) - time.mktime(start_time)))

def main():
    start_crawl(URL) 
    
if __name__ == '__main__':
    main()