import pandas as pd
# import json
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import urllib.error as urle
import datetime

# custom utils
from oliver_util_package import crawling_utils

# 브라우저 꺼짐 방지
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
# chrome_options.add_argument("User-Agent:'application/json;charset=utf-8'")

chrome_path = r'D:\99. Dev\chromedriver.exe'
driver = webdriver.Chrome(chrome_path, options=chrome_options)

try:

    if (result := crawling_utils.without_kor(crawling_utils.crawling_element('https://finance.naver.com/marketindex/?tabSel=exchange#tab_section',
                                            '.section_exchange .round'))) != (
            round_numb := open('./round.txt', 'r').read().rstrip()):
        # if True:
        driver.get("https://finance.naver.com/marketindex/exchangeList.naver")
        crawling_results = driver.find_elements(By.CLASS_NAME, 'tbl_area tbody tr')

        exchange_rate_lists = []

        for exchange_rate_info in crawling_results:
            exchange_data_array = exchange_rate_info.text.split()
            temp_list = exchange_data_array[len(exchange_data_array) - 6:]

            if not 'N/A' in temp_list:
                temp = []
                currency_name = crawling_utils.without_kor(exchange_rate_info.find_element(By.CLASS_NAME, 'tit').text)

                temp.append(datetime.datetime.now().strftime('%Y-%m-%d'))
                # temp.append("result")
                temp.append(result)
                temp.append(currency_name)
                temp.append(temp_list[0])
                temp.append(temp_list[3])
                temp.append(temp_list[4])
                temp.append(temp_list[-1])
                # print("temp_list", temp)
                exchange_rate_lists.append(temp)

        columns = ['date', 'round', 'curren', 'trade_std', 'currency_send', 'currency_receive', 'by_dollar']
        df = pd.DataFrame(exchange_rate_lists, columns=columns)

        print(df)
        # round update
        open('./round.txt', 'w').write(result)
    else:
        print("Unchanged exchange rate data!")


# print(exchange_rate_lists)

except urle.HTTPError as e:
    print('HTTPError!\n', e)
except urle.HTTPError as e:
    print('The server could not be found!\n'.e)
finally:
    print('Finally')

"""
while page_number < 5:
    driver.get(f'https://finance.naver.com/marketindex/worldExchangeList.naver?key=exchange&page={page_number}')

    exchange_rate_lists = driver.find_elements(By.CLASS_NAME, 'tbl_exchange tr')


    for exchange_rate_info in exchange_rate_lists[1:]:
        temp = {
            '통화명': exchange_rate_info.find_element(By.CLASS_NAME, 'tit').text,
            '심볼': exchange_rate_info.find_element(By.CLASS_NAME, 'symbol').text,
            '현재가': float(exchange_rate_info.find_elements(By.CLASS_NAME, 'num')[0].text.replace(",", '')),
            '전일대비': float(exchange_rate_info.find_elements(By.CLASS_NAME, 'num')[1].text.replace(",", '')),
            '등락율': exchange_rate_info.find_elements(By.CLASS_NAME, 'num')[2].text
        }
        exchange_rate_array.append(temp)

        # if 'AUD' in temp['심볼']:
        #     print(temp)

    page_number += 1

print(exchange_rate_array)
"""
