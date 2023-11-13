#!/usr/bin/env python3
import os
import sys
import time
import markdownify
from collections import Counter
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

@retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=10000)
def start_crawl(url):
    start_time = time.localtime()
    print('Start crawling {} at {}'.format(url, time.strftime('%Y-%m-%d %H:%M:%S', start_time)))

    succeed = failed = skipped = 0
    crawled = get_crawled_poems_by_catageory()
    expected = get_expected_poems_by_catageory()
    
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

                with open('poems.txt', 'a', encoding='utf-8') as f:
                    f.write(poem)
                    f.write('\n')

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
                    failed += 1
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
            
                print('Successfully crawled poem #{} in page {} in catageory {}, poem: {}'.format(i + 1, page, catageory, poem))
                succeed += 1
                driver.close()
                driver.switch_to.window(current_window)

            print('Current succeed: {}, current failed: {}, current skipped: {}'.format(succeed, failed, skipped))          
            end_time = time.localtime()
            print('Finish crawling page {} at {}, total used time: {}s'.format(page, time.strftime('%Y-%m-%d %H:%M:%S', end_time), time.mktime(end_time) - time.mktime(start_time)))

        while True:
            # 定位到当前页码，注意当只有一页的时候不存在当前页码，必然定位失败
            try:
                elem = WebDriverWait(driver, WAIT_SECONDS).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, '//*[@id="middlediv"]/div[2]/div')
                    )
                )
                span = elem.find_element(By.CLASS_NAME, 'cur')
                page = int(span.text)
            except TimeoutException as e:
                print('Timeout during waiting for current page span')
                page = 1

            crawl_page(catageory, page)

            # 尝试点击下一页
            try:
                next_page_link = WebDriverWait(driver, WAIT_SECONDS).until(EC.element_to_be_clickable((By.XPATH, '//*[contains(text(), "下一页")]')))
            except TimeoutException as e:
                print('Timeout during waiting for next page link on page {}.'.format(page))
                break 

            # 将鼠标拖动到下一页按键附近并点击
            driver.execute_script("arguments[0].scrollIntoView();", next_page_link) 
            ActionChains(driver).move_to_element(next_page_link).click().perform()    

            # 通过当前页码元素是否过期判断页面是否刷新
            try:
                WebDriverWait(driver, WAIT_SECONDS).until(EC.staleness_of(span))  
            except TimeoutException as e:
                print('Timeout during waiting for refresh of current page after clicking next page in page {} in catageory {}.'.format(page, catageory))   

        end_time = time.localtime()
        print('Finish crawling catageory {} at {}, total used time: {}s'.format(catageory, time.strftime('%Y-%m-%d %H:%M:%S', end_time), time.mktime(end_time) - time.mktime(start_time)))
        
    for link in links:
        # 判断当前分类标签的诗词是否已经爬取完成
        catageory = link.text

        # if catageory != '写景诗':
        #     continue

        if expected[catageory] <= len(crawled[catageory]):
            print("Skip catageory {} since crawl has completed".format(catageory))
            skipped += expected[catageory]
        else:
            print('Found {} poems in catageory {} while only {} of them have been crawled'.format(expected[catageory], catageory, len(crawled[catageory])))
            # 点击每个分类标签并切换至新打开的窗口
            link.click()
            driver.switch_to.window(driver.window_handles[-1])
         
            cnt = Counter()
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