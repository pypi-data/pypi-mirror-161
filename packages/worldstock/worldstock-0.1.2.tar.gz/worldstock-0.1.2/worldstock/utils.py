import numpy as np
import pandas as pd
import json
import yfinance as yf
from datetime import datetime
import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))

# 나라이름을 넣으면 해당나라의 코드를 반환하는 함수
def country_code_list(country_name):
    '''
    east_asia : 한중일+홍콩
    another_europe : Netherlands, Sweden, Poland, Belgium, Ireland, Denmark,
    Finland, Portugal, Czechia, Greece, Hungary, Lithuania, Latvia, Estonia
    '''
    json_data = {}
    file_path = 'dataset/yahoo_country_code.json'
    with open(file_path, "r") as json_file:
        json_data = json.load(json_file)
    return json_data['country_code'].get(country_name)

def exchange_dataset_maker(exchange_symbol = False):
    # 환율 계산
    '''
    USD/각나라 환율
    'KRW=X' 한국 환율 티커
    'JPY=X' 일본 환율 티커
    'CNY=X' 중국 환율 티커
    'HKD=X' 홍콩 환율 티커
    'EUR=X' 유로화 환율 티커
    'GBP=X' 파운드 환율 티커
    해당 환율 적용은 stocksymbol 나라 이름과 매칭
    '''
    ex_ticker_list = ['KRW=X','JPY=X','CNY=X','HKD=X','GBP=X','EUR=X']
    ex_country_list = ['korea','japan','china','hongkong','unitedkingdom','europe']
    ex_dataset = pd.DataFrame(index = [i for i in range(len(ex_ticker_list))],columns=['country','ex_rate'])
    for i,j in enumerate(ex_ticker_list):
        ex_dataset['ex_rate'][i] = yf.download(j,start = datetime.today().strftime('%Y-%m-%d'))['Close'][-1]
        ex_dataset['country'][i] = ex_country_list[i]
    ex_dataset.loc[6]=[ 'us', 1 ]
    ex_dataset['exchange_symbol'] = ['KRW','JPY','CNY','HKD','GBP','EUR','USD']
    # 파라미터 미 입력시 환율 테이블 반환
    if exchange_symbol is False :
        return ex_dataset
    return float(ex_dataset[ex_dataset['exchange_symbol'] == exchange_symbol]['ex_rate'])    

def country_code_input():
    '''
    https://finance.yahoo.com/screener/new 링크로 부터 각나라의 yahoo code를 찾아 dictionary에 입력하는 함수
    ( 나라의 코드는 주기적으로 변경된다. 일주일안에 여러변 변경 )
    '''
    print('country code by : https://finance.yahoo.com/screener/new ')
    json_data = {}
    file_path = 'dataset/yahoo_country_code.json'
    with open(file_path, "r") as json_file:
        json_data = json.load(json_file)
    print(json_data)
    print('View the output and enter the (country and code values) you want to find company info')
    #json값 수정
    for i in range(len(json_data['country_code'])):
        print('If you want to exit the loop, Enter the exit')
        print('Enter Country name')
        x = input()
        if x == 'exit':
            break
        print('Enter Country code')
        y = input()
        if y == 'exit':
            break
        try : 
            json_data['country_code'][x]
            json_data['country_code'][x] = y
        except KeyError: 
            print('Wrong country name, Enter referring to the json_code_list')
            continue
        

    # json 값 저장
    with open(file_path, 'w') as outfile:
        json.dump(json_data, outfile, indent=4)
        
def refine_dataset_maker(country_name):
    handwork_dataset = pd.read_csv('dataset/handwork_dataset/' + country_name + '_handwork_name_dataset.csv',encoding='utf-8-sig') # 또는 DB에서 로드
    handwork_dataset = handwork_dataset[['symbol','refine_name']]
    # us를 입력받아 us_name_dataset 가져오기
    name_dataset = pd.read_csv('dataset/' + country_name + '_name_dataset.csv',encoding='utf-8-sig') # 또는 DB에서 로드
    # refine
    name_dataset = pd.merge(name_dataset, handwork_dataset, left_on='symbol', right_on='symbol', how='left')
    # refine_name이 "[]" 인 데이터는 제거 
    name_dataset = name_dataset[name_dataset['refine_name'] != "[]"]
    name_dataset.reset_index( inplace = True )
    for i in range(len(name_dataset)):
        # handwork데이터셋에 symbol이 존재하면 해당 이름으로 변경
        if name_dataset['refine_name'][i] is not np.nan :
            name_dataset['name'][i] = name_dataset['refine_name'][i]
    del name_dataset['refine_name']
    name_dataset.to_csv('dataset/' + country_name + '_refine_name_dataset.csv', encoding='utf-8-sig', index = False )
    return name_dataset