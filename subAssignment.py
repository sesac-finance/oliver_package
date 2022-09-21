import itertools

import pandas as pd
from tabulate import tabulate
from pretty_html_table import build_table

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
from oliver_util_package import email_utils
import logging

# 브라우저 꺼짐 방지
# chrome_options = Options()
# chrome_options.add_experimental_option("detach", True)
# chrome_options.add_argument("User-Agent:'application/json;charset=utf-8'")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# for to see all data
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 100)
pd.set_option('display.colheader_justify', 'left')

# if DataFrame kor broken
# tabulate.WIDE_CHARS_MODE=False

try:
    logger = log_utils.logging.getLogger()

    # if (result := crawling_utils.without_kor(
    #         crawling_utils.crawling_element('https://finance.naver.com/marketindex/?tabSel=exchange#tab_section',
    #                                         '.section_exchange .round'))) != (open('./round.txt', 'r').read().rstrip()):
    if True:
        driver.get("https://finance.naver.com/marketindex/exchangeList.naver")
        crawling_results = driver.find_elements(By.CLASS_NAME, 'tbl_area tbody tr')

        today = datetime.datetime.now().strftime('%Y-%m-%d')
        exchange_rate_lists = []
        for exchange_rate_info in crawling_results:
            exchange_data_array = exchange_rate_info.text.split()
            temp_list = exchange_data_array[len(exchange_data_array) - 6:]

            if not 'N/A' in temp_list:
                temp = []
                currency_name = crawling_utils.without_kor(exchange_rate_info.find_element(By.CLASS_NAME, 'tit').text)

                temp.append(today)
                # temp.append(result)
                temp.append("result")
                temp.append(currency_name)
                temp.append(temp_list[0].replace(',', ''))
                temp.append(temp_list[3].replace(',', ''))
                temp.append(temp_list[4].replace(',', ''))
                temp.append(temp_list[-1].replace(',', ''))
                exchange_rate_lists.append(temp)

        columns_basic_currency = ['날짜', '회차', '통화', '매매기준율', '송금 보내실때', '송금 받으실때',
                                  '미화환산율']
        # basic data complete
        basic_currency_df = pd.DataFrame(exchange_rate_lists, columns=columns_basic_currency)
        # logger.info(tabulate(basic_currency_df, headers='keys', tablefmt='pretty'))

        possible_arbitrage_list = []
        # calculate possible arbitrage list
        for idx, cases in enumerate(itertools.combinations(basic_currency_df['통화'], 2)):
            temp_arbitrage = []
            currency_1_send = basic_currency_df[basic_currency_df['통화'] == cases[0]]['송금 보내실때'].values
            currency_2_send = basic_currency_df[basic_currency_df['통화'] == cases[1]]['송금 보내실때'].values
            back_to_home_currency = basic_currency_df[basic_currency_df['통화'] == cases[1]][
                '송금 받으실때'].values
            # currency 1 / currency 2
            final_multiple = float(currency_1_send) / float(currency_2_send)
            # won -> currency 1
            first_convert = round(float(1000000.0 / float(currency_1_send)), 2)
            # currency 1 -> currency 2
            second_convert = round(float(first_convert * final_multiple), 2)
            # currency 2 -> won
            final_convert = round(second_convert * float(back_to_home_currency))
            final_profit = round(final_convert - 1000000.0)

            exchange_flow = 'KOR -> ' + cases[0] + ' -> ' + cases[1] + ' -> KOR'
            temp_arbitrage.append(exchange_flow)
            temp_arbitrage.append(str(format(first_convert, ',')) + '(' + cases[0] + ')')
            temp_arbitrage.append(str(format(second_convert, ',')) + '(' + cases[1] + ')')
            temp_arbitrage.append(format(final_convert, ','))
            temp_arbitrage.append(format(final_profit, ','))
            possible_arbitrage_list.append(temp_arbitrage)

        columns_possible_arbitrage = ['재정거래 흐름', '1차 환전', '2차 환전',
                                      '거래결과(원화)',
                                      '최종수익(원화)']
        possible_arbitrage_df = pd.DataFrame(possible_arbitrage_list, columns=columns_possible_arbitrage).sort_values(
            by='거래결과(원화)', ascending=False)

        possible_arbitrage_df.reset_index(inplace=True, drop=True)
        # Arbitrage Calculation Compelte : possible_arbitrage_df
        # logger.info(possible_arbitrage_df[['재정거래 흐름', '재정거래 결과', '최종수익']])

        # Saving total exchange rate data to excel
        path = './oliver_util_package/excel/' + today + '_회차' + '.xlsx'
        with pd.ExcelWriter(path) as writer:
            basic_currency_df.to_excel(writer, sheet_name='환율정보')
            possible_arbitrage_df.to_excel(writer, sheet_name='재정거래 시나리오')

        # Exchange rate News part
        news_list = crawling_utils.crawling_elements(
            'https://finance.naver.com/marketindex/news/newsList.naver?category=exchange',
            '.news_list li dt a')

        news_str_list = []
        news_start = '<tr><td><strong><a href="https://finance.naver.com'
        news_end = '</td></tr>'
        for idx, news in enumerate(news_list):
            news_detail = crawling_utils.crawling_element('https://finance.naver.com/' + news['href'],
                                                          'div .article_cont').split('. ', 2)
            temp = f'''
                    {news_start}{news['href']}" target="_blank"><h2>{news.text}</h2></a></strong></font><br/><h3>{'. '.join(news_detail[0:2])}...</h3>{news_end}
            '''
            news_str_list.append(temp)

        currency_info_str = f'<h3>오늘의 고시회차 1의 환율정보</h3><br/>'
        possible_arbitrage_str = f'<h3>재정거래 시나리오 리스트</h3><br/>'
        body = currency_info_str + build_table(basic_currency_df[0:15], 'blue_dark', width="120px", font_size='medium',
                                               text_align='center',
                                               font_family='Open Sans, sans-serif'
                                               ) + '<br/><br/>' \
               + possible_arbitrage_str + build_table(possible_arbitrage_df[0:10], 'orange_dark', font_size='medium',
                                                      font_family='Open Sans, sans-serif',
                                                      conditions={
                                                          '최종수익': {
                                                              'min': 0,
                                                              'max': 1,
                                                              'min_color': 'red',
                                                              'max_color': 'blue',
                                                          }}) + '<br/>'.join(news_str_list)

        # Sending email by html style
        email_utils.send_mail_html('lvsin@naver.com', '차 환율정보 및 재정거래 시나리오', body, path)

        # round update
        open('./round.txt', 'w').write("1")
        # open('./round.txt', 'w').write(result)
    else:
        logger.info("Unchanged exchange rate data!")

except urle.HTTPError as e:
    logger.warning('HTTPError!\n', e)
except urle.URLError as e:
    logger.warning('The server could not be found!\n', e)
except Exception as e:
    logger.warning("Error!\n", e)
finally:
    logger.info('Finally')

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
