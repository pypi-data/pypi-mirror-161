#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 29 12:32:28 2022.

@author: gp
"""
import json
import time
import requests
from tqdm.notebook import tqdm


# Функция для выгрузки отчетов из яндекс метрики
def download_report_web(
        path: str,
        type_request: str,
        request: str,
        auth: object):
    """
    Функция выгружает отчеты.

    Parameters
    ----------
    path : str
        Часть пути к общим файлам, например
        os.path.join(os.getcwd(), 'web', 'ym_web_1_file_').
    type_request : str
        Тип запроса, например 'GET'.
    request : str
        Сам запрос, например
        'https://api-metrika.yandex.ru/stat/v1/data.csv'
        '?metrics='
        'ym:s:visits,'
        'ym:s:users'
        '&dimensions='
        'ym:s:clientID,'
        'ym:s:visitID,'
        'ym:s:counterID,'
        'ym:s:regionCountry,'
        'ym:s:regionCity,'
        # 'ym:s:networkType,'
        'ym:s:lastTrafficSource,'
        'ym:s:lastReferalSource,'
        'ym:s:browserLanguage,'
        'ym:s:clientTimeZone'
        "&date1=yesterday&date2=yesterday&ids=12345"
        ""&accuracy=full&lang=en&filters=ym:s:deviceCategory=='mobile'".
    auth : object
        Объект для авторизации, например OAuth(str_token).

    Returns
    -------
    None.

    """
    limit = 100000
    offset_flag = True
    iteration = 0
    while offset_flag:
        if iteration == 0:
            txt_offset = f'&limit={limit}'
        else:
            txt_offset = f'&limit={limit}&offset=' + str(iteration * limit)
        with requests.request(
            type_request,
            request+txt_offset,
            auth=auth
                ) as r:
            r.raise_for_status()
            if r.content.decode("utf-8").count("\n") >= limit:
                iteration += 1
            else:
                offset_flag = False
            with open(path+str(iteration)+'.csv', 'wb') as f:
                f.write(r.content)


# Функция для выгрузки logs api из яндекс метрики
def download_logs_api_web(
    auth: object,
    list_fields: list,
    path: str = 'folder_web/export_1_',
    date1: str = '2022-07-27',
    date2: str = '2022-07-27',
    source: str = 'visits',
    counter_id: int = 123456
        ):
    """
    Функция выгружает logs api.

    Parameters
    ----------
    auth : object
        Объект для авторизации, например OAuth(str_token).
    list_fields : list
        Список полей для выгрузки, например
        ['ym:s:clientID', 'ym:s:visitID', 'ym:s:counterID'].
    path : str, optional
        Часть пути к общим файлам, например
        os.path.join(os.getcwd(), 'folder_web', 'export_1_').
    date1 : str, optional
        Дата начала периода выгрузки, например '2022-07-27'.
    date2 : str, optional
        Дата окончания периода выгрузки, напрмиер '2022-07-27'.
    source : str, optional
        Источник логов. Одно из двух hits/visits.
    counter_id : int, optional
        Идентификатор счетчика, например 123456

    Returns
    -------
    None.

    """
    # Создаем задачу на формирование
    r = requests.post(
        'https://api-metrika.yandex.net/management/v1'
        f'/counter/{counter_id}/logrequests'
        f'?date1={date1}&date2={date2}'
        '&fields='+",".join(list_fields) + f'&source={source}',
        auth=auth)
    r.raise_for_status()

    # Получаем номер запроса
    request_id = r.json()['log_request']['request_id']
    while True:
        # Запрашиваем статус запроса
        r = requests.get(
            'https://api-metrika.yandex.net/management/v1'
            f'/counter/{counter_id}/logrequest/{request_id}',
            auth=auth)
        print(json.loads(r.text)['log_request']['status'])
        time.sleep(60)
        if r.status_code == 200:
            # Получаем статус запроса
            status = json.loads(r.text)['log_request']['status']
            if status == 'processed':
                # Проверяем количество частей ответа
                size = len(json.loads(r.text)['log_request']['parts'])
                # Скачиваем в отдельные файлы
                for part in tqdm(range(size)):
                    r = requests.get(
                        'https://api-metrika.yandex.net/management/v1'
                        f'/counter/{counter_id}/logrequest/{request_id}/'
                        f'part/{part}/download',
                        auth=auth)
                    with open(path+str(part)+'.csv', 'wb') as f:
                        f.write(r.content)
                r = requests.post(
                    'https://api-metrika.yandex.net/management/v1'
                    f'/counter/{counter_id}/logrequest/{request_id}/clean?',
                    auth=auth)
                break
