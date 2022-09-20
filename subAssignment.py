import itertools

import pandas as pd
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import urllib.error as urle
import datetime

# custom utils
from oliver_util_package import crawling_utils
from oliver_util_package import log_utils
import logging

# 브라우저 꺼짐 방지
chrome_options = Options()
# chrome_options.add_experimental_option("detach", True)
# chrome_options.add_argument("User-Agent:'application/json;charset=utf-8'")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# for to see all data
pd.set_option('display.max_columns', None)

try:
    logger = log_utils.logging.getLogger()

    # if (result := crawling_utils.without_kor(
    #         crawling_utils.crawling_element('https://finance.naver.com/marketindex/?tabSel=exchange#tab_section',
    #                                         '.section_exchange .round'))) != (open('./round.txt', 'r').read().rstrip()):
    if True:
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
                # temp.append(result)
                temp.append("result")
                temp.append(currency_name)
                temp.append(temp_list[0].replace(',', ''))
                temp.append(temp_list[3].replace(',', ''))
                temp.append(temp_list[4].replace(',', ''))
                temp.append(temp_list[-1].replace(',', ''))
                exchange_rate_lists.append(temp)

        columns_basic_currency = ['Date', 'Round', 'Currency', 'Trade_std', 'Currency_send', 'Currency_receive',
                                  'by_dollar']
        # basic data complete
        basic_currency_df = pd.DataFrame(exchange_rate_lists, columns=columns_basic_currency)

        possible_arbitrage_list = []
        # calculate possible arbitrage list
        for idx, cases in enumerate(itertools.combinations(basic_currency_df['Currency'], 2)):
            temp_arbitrage = []
            currency_1_send = basic_currency_df[basic_currency_df['Currency'] == cases[0]]['Currency_send'].values
            currency_2_send = basic_currency_df[basic_currency_df['Currency'] == cases[1]]['Currency_send'].values
            back_to_home_currency = basic_currency_df[basic_currency_df['Currency'] == cases[1]][
                'Currency_receive'].values
            # currency 1 / currency 2
            final_multiple = float(currency_1_send) / float(currency_2_send)
            # won -> currency 1
            first_convert = float(1000000.0 / float(currency_1_send))
            # currency 1 -> currency 2
            second_convert = float(first_convert * final_multiple)
            # currency 2 -> won
            final_convert = second_convert * float(back_to_home_currency)
            final_profit = round((final_convert - 1000000.0), 2)

            # temp_arbitrage.append(cases[0])
            # temp_arbitrage.append(cases[1])
            exchange_type = cases[0] + '/' + cases[1]
            temp_arbitrage.append(exchange_type)
            temp_arbitrage.append(first_convert)
            temp_arbitrage.append(second_convert)
            temp_arbitrage.append(final_convert)
            temp_arbitrage.append(final_profit)
            possible_arbitrage_list.append(temp_arbitrage)

        columns_possible_arbitrage = ['Exchange_type', 'First_convert', 'Second_convert',
                                      'Final_convert',
                                      'Final_profit']
        possible_arbitrage_df = pd.DataFrame(possible_arbitrage_list, columns=columns_possible_arbitrage).sort_values(
            by='Final_profit', ascending=False)

        possible_arbitrage_df.reset_index(inplace=True, drop=True)
        # Arbitrage Calculation Compelte : possible_arbitrage_df
        # logger.info(possible_arbitrage_df[['Exchange_type', 'Final_convert', 'Final_profit']])

        news_list = crawling_utils.crawling_elements('https://finance.naver.com/marketindex/news/newsList.naver?category=exchange',
                                      '.news_list li dt a')

        exchange_news_list = []
        for idx, news in enumerate(news_list):
            # news_info = news.text
            print(news.text)
            news_detail = crawling_utils.crawling_element('https://finance.naver.com/' + news['href'],'div .article_cont').split('. ',2)
            print('. '.join(news_detail[0:2])+'...')
            print("src: ", 'https://finance.naver.com/' + news['href'])

            print()

        # round update
        open('./round.txt', 'w').write("1")
        # open('./round.txt', 'w').write(result)
    else:
        logger.info("Unchanged exchange rate data!")

except urle.HTTPError as e:
    logger.warn('HTTPError!\n', e)
except urle.URLError as e:
    logger.warn('The server could not be found!\n', e)
finally:
    logger.info('Finally')

"""
from oliver_util_package import email_utils
try:
    email_utils.send_mail('lvsin@naver.com', '결제확인메일', 'ㅋㅋㅋㅋㅋ', 'FILE')
except Exception as e:
    print("Error : ", e)
pass
"""

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
