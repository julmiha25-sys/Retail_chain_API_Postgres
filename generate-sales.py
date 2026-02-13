#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os
import random
import uuid
import configparser
from pgdb import PGDatabase
import glob
import re

# Настройка конфигурации
config=configparser.ConfigParser()
dirname=os.path.dirname(__file__)
config.read(os.path.join(dirname, 'config.ini'),encoding='utf-8-sig')
SALES_PATH=config["Files"]["SALES_PATH"]
DATABASE_CREDS=config['Database']

# Функция для генерации бувенно-цифрового кода-идентификатора чека из 10-символов
def generate_check_id():
    return str(uuid.uuid4()).replace('-', '')[:10].upper()

# Функция для генерации файлов-выгрузок магазинов
def generate_file():

    os.makedirs('data', exist_ok=True) # Если папки data нет, то она создается в каталоге проекта

    matrix=np.random.choice([0, 1],size=(10, 10)) # Матрица работы 10 магазинов и их 10 касс

    # Генерируем датафрейм из работающих магазинов-касс (1 - касса работает, 0 - нет)
    df=pd.DataFrame(matrix, index=[f"Shop_{i+1}" for i in range(10)], columns=[f"Cash_{j+1}" for j in range(10)]) 
    
    # Словарь категорий - продуктов+цен
    product={'Посуда':{'Сковорода 25см Tefal': 2000,'Блинница Tefal' : 1500,'Кастрюля 5л Tefal': 3000,'Сковорода 28см Tefal': 2500,'Кастрюля 3л Tefal': 2500,'Миксер MP-30 Bosh': 2000,'Йогурница ML-5 Bosh': 4000}, 
          'Бытовая химия':{'Стиральный порошок БИОС 3кг': 300,'Стиральный порошок БИОС 5 кг': 400,'AOS 1л': 100,'AOS 0.5л': 50},
          'Текстиль':{'Постельное белье 2-х сп. Венера': 3000,'Постельное белье 1.5 сп. Венера': 2500,'Полотенце Венера 60*60': 300,'Полотенце Венера 80*120': 500}}

    # Создание иерархии магазин - касса - датафрейм чеков
    shop_cash_checks={}
    # Перебор магазинов
    for shop in df.index:
        shop_cash_checks[shop]={} # Словарь касс-чеков для магазина
        # Перебор касс
        for cash in df.columns:
            cash_checks_list=[]  # Список чеков в магазине-кассе
            if df.loc[shop, cash]==1:  # Магазин-касса работали
                for _ in range(random.randint(5, 15)):
                    doc_id=generate_check_id()  # Генерация идентификатора чека
                    # Генерация данных в чеке - от 1 до 3-х позиций  
                    for _ in range(random.randint(1, 3)):
                        category=random.choice(list(product.keys())) # Генерация категории
                        item_name=random.choice(list(product[category].keys())) # Генерация товара из этой категории
                        item_price=product[category][item_name] # Определение цены этого товара из словаря категорий - продуктов+цен  
                        amount=random.randint(1, 3) # Генерация количества покупаемого товара - от 1 до 3-х
                        discount=random.randint(0, 25) # Генерация % скидки - от 0 до 25%
                        check={'doc_id':doc_id,'item':item_name,'category':category,'amount':amount,'price':item_price,'discount':discount,}
                        if check not in cash_checks_list:  
                            cash_checks_list.append(check) # Добавление в список чеков только если такой позиции нет (нет дубликата всех значений ключей словаря)
            if cash_checks_list: # Список чеков в магазине-кассе сформирован
                shop_cash_checks[shop][cash]=pd.DataFrame(cash_checks_list)  # Добавление этого списка в виде  датафрейма  в словарь магазина-кассы 
                shop_num=shop.replace('Shop_', '') # Считывание номера магазина
                cash_num=cash.replace('Cash_', '') # Считывание номера кассы
                filename = os.path.join(dirname,f'data/{shop_num}_{cash_num}.csv') # Формирование имени файла 
                shop_cash_checks[shop][cash].to_csv(filename, index=False, encoding='utf-8') # Формирование файла
    
# Функция для загрузки файлов продаж csv в единый датафрейм для загрузки в БД Postgres
def load_csv():
    pattern = re.compile(r'^(\d+)_(\d+)\.csv$') # Регулярное выражение для загрузки файлов по шаблону 
    files=[f for f in glob.glob('data/*.csv') if pattern.match(os.path.basename(f))] # Список загружаемых файлов
    dfs=[] # Единый список для сбора датафреймов из каждого файла
    for f in files:
        df=pd.read_csv(f) # Считывание файла
        match=pattern.match(os.path.basename(f)) # Разбор имени файла по частям (группа 1 - номер магазина, группа 2 - номер кассы)
        # Добавление в датафрейм колонок с номером магазина и кассы
        df['shop_id']=int(match.group(1))
        df['cash_id']=int(match.group(2))
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)  # Соединение датафреймов файлов в единый датафрейм

# Функция для загрузки датафрейма в БД Postgres
def load_db(df_sales):

    # Вызов класса PGDatabase из файла pgdb.py
    database=PGDatabase(
        host=DATABASE_CREDS['HOST'],
        database=DATABASE_CREDS['DATABASE'],
        user=DATABASE_CREDS['USER'],
        password=DATABASE_CREDS['PASSWORD'],
        )

    for i, row in df_sales.iterrows(): # Добавляем данные из единого датафрейма продаж  df_sales в таблицу Sales БД Postgres
        query="""INSERT INTO sales (shop_id, cash_id, doc_id, item, category, amount, price, discount)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        database.post(query, (row['shop_id'],row['cash_id'],row['doc_id'],row['item'],row['category'],row['amount'],row['price'],row['discount']))

        
generate_file() # Вызов функции генерации файлов продаж формата csv
df_sales=load_csv() # Вызов функции загрузки файлов из каталога data формата {номер_магазина}_{номер_кассы}.csv и преобразования в единый датафрейм продаж df_sales
load_db(df_sales)  # Загрузка датафрейм продаж df_sales в таблицу Sales БД Postgres
pattern = re.compile(r'^(\d+)_(\d+)\.csv$') 
files=[f for f in glob.glob('data/*.csv') if pattern.match(os.path.basename(f))] # После успешной загрузки данных в БД удаление сгенерированных файлов из data
for f in files:
    os.remove(f)
