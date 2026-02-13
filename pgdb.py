#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pg8000
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    filename='db_errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

class PGDatabase:
    def __init__(self, host, database, user, password):
        self.host=host 
        self.database=database 
        self.user=user
        self.password=password

        try:
            self.connection=pg8000.connect(host=host,database=database,user=user,password=password)
            self.cursor=self.connection.cursor()
            self.connection.autocommit=True
        except Exception as e:
            error_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Получение кода ошибки и интерпретация
            error_dict=e.args[0] if e.args else {}
            error_code=error_dict.get('C', '')
            if error_code=='3D000':
                error_text="Database does not exist"
            elif error_code=='28P01':
                error_text="Wrong password"
            elif error_code=='42P01':
                error_text="Table does not exist"
            elif error_code=='08001' or 'ECONNREFUSED' in str(e):
                error_text="Server not running"
            else:
                error_text=f"Connection failed (code: {error_code})"
            logging.error(f"Time: {error_time}, {error_text}")
            raise SystemExit(1)

    def post(self, query, args=()):
        try:
            self.cursor.execute(query, args)
            return True
        except Exception as err:
            error_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Создание сообщения об ошибке
            error_msg=f"""Time: {error_time}, Errore: {repr(err)}"""
            logging.error(error_msg) # Запись в лог-файл
            if '23505' in str(err):  # Код ошибки уникальности в PostgreSQL
                logging.warning(f"Violation of uniqueness for the key: {args}")
                return True  # Считается успешной вставкой
            return False


            
            