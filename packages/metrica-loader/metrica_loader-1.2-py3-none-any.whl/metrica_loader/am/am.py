#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 29 14:10:33 2022.

@author: gp
"""
import time
import requests


# Выгрузчик
def download_file(
        str_fname: str,
        *args,
        **kwargs):
    """
    Выгрузчик файла с низким потреблением ОЗУ.

    Parameters
    ----------
    str_fname : str
        Путь к месту сохранения файла.
    *args : TYPE
        Параметры для запроса как список.
    **kwargs : TYPE
        Параметры для запроса как словарь.

    Returns
    -------
    object
        Статус-код запроса.

    """
    with requests.request(*args, **kwargs, stream=True) as r:
        r.raise_for_status()
        if r.status_code == 200:
            with open(str_fname, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
    return r.status_code


# Функция для скачивания логов с аппметрики без высокого потребления ОЗУ
def download_logs_api_app(
        str_fname: str,
        application_id: int,
        date_since: str,
        date_until: str,
        list_fields: list,
        auth: object,
        source: str):
    """
    Функция для скачивания логов с аппметрики без высокого потребления ОЗУ.

    Parameters
    ----------
    str_fname : str
        Имя файля для выгрузки, например 'ym_install.csv'.
    application_id : int
        Числовой идентификатор приложения в AppMetrica, наприме 123456.
    date_since : str
        Начало интервала дат в формате yyyy-mm-dd hh:mm:ss,
        например 2022-07-26.
    date_until : str
        Конец интервала дат в формате yyyy-mm-dd hh:mm:ss,
        например 2022-07-26.
    list_fields : list
        Список полей для выборки.
    auth : object
        Объект для авторизации, например OAuth(str_token).
    source : object
        Источник логов. Одно из трех installations/events/profiles.

    Returns
    -------
    None.

    """
    int_code = 202
    while int_code == 202:
        int_code = download_file(
            str_fname,
            'GET',
            f'https://api.appmetrica.yandex.ru/logs/v1/export/{source}.csv'
            f'?application_id={application_id}'
            f'&date_since={date_since}&date_until={date_until}'
            '&fields='+",".join(list_fields),
            auth=auth)
        print(int_code)
        time.sleep(60)
