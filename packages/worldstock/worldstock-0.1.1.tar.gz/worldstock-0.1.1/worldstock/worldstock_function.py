import numpy as np
import pandas as pd
from numpy import random
from tqdm import tqdm
import requests # 크롤링에 사용하는 패키지
from bs4 import BeautifulSoup # html 변환에 사용함
import time
import json
import math
from worldstock.utils import country_code_list, exchange_dataset_maker
import random

class yahoo_company_info_downloader:
    '''
    yahoo_dataset_maker : 다운로드할 나라와, 저장장소, 다운받을 데이터옵션을 input으로 받아, 해당 옵션에 맞는 기업데이터를 return
    yahoo_ticker_collector : 다운로드할 나라를 입력받아 해당나라에 상장된 종목의 Ticker와 기업이름 등 간단한 정보를 return
    total_ticker_number : yahoo_ticker_collector를 실행할때, 전체종목개수를 파악하는 함수
    multi_ticker_finance_info : yahoo_dataset_maker에서 각 Ticker에 대한 재무정보를 이어붙이는 함수
    yahoo_single_ticker_company_info : yahoo_dataset_maker에서 각 Ticker에 대한 기업정보를 이어붙이는 함수
    '''
    def __init__(self, country_name, save_root = 'worldstock/dataset/'):
        self.country_name = country_name
        self.save_root = save_root
        
    def yahoo_dataset_maker(self, company_option = False):
        df = self.yahoo_ticker_collector(self.country_name)
        # Symbol column을 문자로 변환 ( TRUE, NA, 수치형데이터와 같은 TICKER 사례 )
        for i in range(len(df['symbol'])):
            df['symbol'][i] = str(df['symbol'][i])
        # 각 티커에 대한 회사정보 가져오기
        df['company_info'] = 0
        if company_option:
            for i in tqdm(range(len(df))):
                time.sleep(random.uniform(3, 4))
                tries = 3
                for j in range(tries):
                    try:
                        df['company_info'][i] = self.yahoo_single_ticker_company_info(df['symbol'][i])
                    except :
                        if j < tries - 1: # i is zero indexed
                            time.sleep(random.uniform(500, 600))
                            continue
                        else:
                            raise ConnectionError('3회 접속실패')
                    break    
        # 각 티커에 대한 재무정보 가져오기
        ticker_finance_info = self.multi_ticker_finance_info(df['symbol'])
        if isinstance(ticker_finance_info, pd.DataFrame):  
            df = pd.merge(df, ticker_finance_info, left_on='symbol', right_on='symbol', how='left')
        else : 
            df['finance_info'] = ticker_finance_info
        # 목표 완성 list는 15100개
        # 테스트 목록 spain 194개 = 9분 / 15000개 950분 소요 / 30000개 2000분 소요 
        df.to_csv( self.save_root + self.country_name + '_yahoo_dataset.csv', encoding='utf-8-sig', index = False )    
        return df

    # 나라기준으로 전체 ticker와 그에대한 간단한 정보를 수집
    def yahoo_ticker_collector(self,country_name):
        '''
        <input parameter>
        _country_code : url의 국가 고유코드
        _count : 한번에 가져올 ticker 개수, min25 ~ max250
        _offset : 시작지점
        <output>
        야후 URL ticker list와 관련정보 DataFrame
        '''
        
        _basic_url = 'https://finance.yahoo.com/screener/unsaved'
        header_info = {
        'scheme': 'https',
        'authority': 'finance.yahoo.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        }
        _country_code = country_code_list(country_name)
        total_number = self.total_ticker_number(_basic_url,_country_code,header_info)
        rotate = math.ceil(total_number/250)
        _count = 250
        _offset = 0
        ticker_data = pd.DataFrame()
        for i in range(rotate):
            time.sleep(random.uniform(10, 15))
            url = "{}/{}?count={}&offset={}".format(_basic_url,_country_code,_count,_offset)

            response = requests.request("GET", 
                                        url, 
                                        headers=header_info, 
                                        )
            if response.status_code == requests.codes.ok:
                print('접속성공')
            else :
                print('접속실패 : ',response.status_code)
                # offset 초기화
            _offset =_offset + 250
            html = response.text
            json_str = html.split('root.App.main =')[1].split(
                '(this)')[0].split(';\n}')[0].strip()
            data = json.loads(json_str)[
                'context']['dispatcher']['stores']['ScreenerResultsStore']['results']['rows']
            data = pd.DataFrame.from_dict(data)
            # 빈 데이터프레임에 데이터 붙이기
            ticker_data = ticker_data.append(data)
        return ticker_data.reset_index(drop=True)
     
    # 카테고리 데이터 가져오기
    def total_ticker_number(self, _basic_url,_country_code,header_info):
        url = "{}/{}".format(_basic_url,_country_code)
        response = requests.request("GET", 
                                    url, 
                                    headers=header_info, 
                                    )
        if response.status_code == requests.codes.ok:
            print('접속성공')
        else :
            print('접속실패 : ',response.status_code)
        html = response.text
        json_str = html.split('root.App.main =')[1].split(
            '(this)')[0].split(';\n}')[0].strip()
        data = json.loads(json_str)[
            'context']['dispatcher']['stores']['ScreenerCriteriaStore']['meta']['total']
        return int(data)

    # AAPL,GOOG자리에 여러개의 ticker(한번에 2000개 까지 가능)를 넣으면 각각의 재무정보 결과값을 반환
    def multi_ticker_finance_info(self, ticker_list):
        '''
        input : ticker로 이루어진 list
        output : 입력한 multi-ticker에 대한 각각의 재무정보를 같은 길이의 list로 반환
        '''
        header_info = {
        'scheme': 'https',
        'authority': 'finance.yahoo.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        }
        multi_ticker_dataset = list()
        ticker_list = list(ticker_list)
        total_number = len(ticker_list)
        print('input list length : ', total_number)
        rotate = math.ceil(total_number/1000)
        for i in range(rotate):
            multi_list = ','.join(ticker_list[1000*i:1000*(i+1)])
            url = 'https://query1.finance.yahoo.com/v6/finance/quote?symbols={}'.format(multi_list)
            response = requests.request("GET", 
                                        url, 
                                        headers=header_info, 
                                        )
            # 재무정보 list 넣은 순서대로 
            multi_ticker_dataset = multi_ticker_dataset + json.loads(response.text)['quoteResponse']['result']
        print('output list length : ', len(multi_ticker_dataset))
        if total_number == len(multi_ticker_dataset):
            return multi_ticker_dataset
        else:
            print('Input and output length not matched : make exist sybol dataframe')
            exist_ticker_dataset = pd.DataFrame(multi_ticker_dataset)
            exist_ticker_dataset = exist_ticker_dataset[['symbol']]
            exist_ticker_dataset['finance_info'] = multi_ticker_dataset
            return exist_ticker_dataset
    # aapl 자리에 원하는 키워드를 서치하면 회사정보를 반환

    def yahoo_single_ticker_company_info(self, single_ticker):
        '''
        input : 단일 ticker를 입력
        output : 입력한 ticker에 상세한 회사정보를 반환
        ** 주의사항 :  you are limited to 2,000 requests per hour per IP (or up to a total of 48,000 requests a day)
        '''
        header_info = {
        'scheme': 'https',
        'authority': 'finance.yahoo.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        }
        url = 'https://query1.finance.yahoo.com/v10/finance/quoteSummary/{}?modules=assetProfile'.format(single_ticker)
        response = requests.request("GET", 
                                    url,
                                    headers=header_info, 
                                    )
        # 회사정보
        if json.loads(response.text)['quoteSummary']['result'] == None:
            return None
        else:
            return json.dumps(json.loads(response.text)['quoteSummary']['result'][0]['assetProfile'])    
        
        
        
class prep_company_name: 
    '''
    stock_list_symbol : dataset폴더에서 가져올 나라이름을 input으로 받아 여러 전처리 과정을 거쳐 회사를 대표하는 이름인 'name' 열이 포함된 dataframe을 return한다.
    company_representative_name : 특정단어와 단어개수 한정 옵션을 input으로 받아 해당 단어를 전처리한후 각 단어별로 분리된 리스트로 return한다.
    load_words : 신조어를 찾기위한 사전로드함수 
    unique_name_finder : 특정단어들을 input으로 받아 해당단어가 신조어이면 신조어(처음발견한 1 word)를 return하며, 없다면 None을 return한다.
    '''
    def __init__(self, country_name, save_root = 'worldstock/dataset/'):
        self.country_name = country_name
        self.save_root = save_root
    def stock_list_symbol(self, two_word_option = True):
        # 야후 or investingcom 판정
        try :
            stock_list = pd.read_csv(self.save_root + self.country_name + '_yahoo_dataset.csv',encoding='utf-8-sig') # 또는 DB에서 로드
        except FileNotFoundError:
            print('yahoo_company_info_downloader를 통해 해당국가의 데이터를 먼저 가져오기')
        stock_list = stock_list[['symbol', 'longName','quoteType','currency','marketCap']]
        # dict인 marketcap에서 raw 키값만 가져오기
        stock_list.reset_index(inplace=True,drop=True)
        # 환율데이터로 가공하기, yahoo_finance source
        ex_rate = exchange_dataset_maker(stock_list['currency'][0])
        stock_list['Market_Cap'] = 0
        for i in range(len(stock_list)):
            if pd.isna(stock_list['marketCap'][i]) :
                stock_list['Market_Cap'][i] = 0
            else :
                stock_list['Market_Cap'][i] = float(json.loads(stock_list['marketCap'][i].replace("\'", "\""))['raw'])/ex_rate
        # 시가총액 상위만 가져오기 ( 1조 )
        stock_list = stock_list[stock_list['Market_Cap']>=1000000000] # 100조
        stock_list.reset_index(inplace=True,drop=True)
        
        # United state, good, best와 같은 이름을 가진회사 삭제
        # 이름전처리
        stock_list['remove_name'] = stock_list['longName']
        remove_left_set = ['The','United States','Bank of','New York','National Health','National Bank','Clean Energy','Global Business','Manchester United','The New','The Bank','Turning','Arrival']
        for i in remove_left_set:
            print(i)
            stock_list['remove_name'] = [j.removeprefix(i).lstrip() for j in stock_list['remove_name']]

        stock_list['name'] = stock_list['longName']
        # 모듈로 빼기
        for i in tqdm(range(len(stock_list))):
            stock_list['name'][i] = self.unique_name_finder(stock_list['remove_name'][i])
            if stock_list['name'][i] is None:
                stock_list['name'][i] = self.company_representative_name(stock_list['remove_name'][i], two_word_option = two_word_option)
        stock_list = stock_list.loc[stock_list['name'].astype(str).drop_duplicates().index]
        stock_list['name'] = [ ','.join(i) for i in stock_list['name']]
        del stock_list['remove_name']
        # name이 공백인 함수는 제거 
        stock_list = stock_list[~stock_list['name'].isin([''])]
        stock_list.reset_index(inplace=True,drop=True)
        stock_list.to_csv( self.save_root + self.country_name + '_name_dataset.csv', encoding='utf-8-sig', index = False )    
        
        return stock_list    
    
    # 2번시도 유니크한 이름이 아닐때
    def company_representative_name(self,company_name='airbus, nice, s.a.',two_word_option = True):
        company_name = company_name.lower()
        company_name = company_name.replace(',', '')
        company_name = company_name.replace('.', '')
        company_name = company_name.replace('"', '')
        company_name = company_name.replace('(', '')
        company_name = company_name.replace(')', '')
        company_name = company_name.replace('#', '')
        company_name = company_name.replace('\n', '')
        company_name = company_name.split(' ')
        if two_word_option :
            company_name = company_name[:2]
        return company_name

    # 1번시도 유니크한 이름 찾기
    def load_words(self):
        with open('worldstock/dataset/words_470k.txt') as word_file:
            valid_words = set(word_file.read().lower().split())
        return valid_words

    def unique_name_finder(self, company_name='airbus, nice, s.a.'):
        english_words = self.load_words()
        for j in self.company_representative_name(company_name,two_word_option = False):
            if (j in english_words):
                continue
            else :
                if len(j)>1:
                    return j.split()
                continue
        # return None <- unique 단어를 못찾을시 None 반환
        