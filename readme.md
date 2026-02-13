**Разработка проекта "Генерации файлов с продажами, загрузка данных в БД Postgres, создание дашборда в Metabase"**

1.	На сервере Ubuntu (у меня виртуальный) cоздаем папку  Торговая_сеть_API_Postgres (например, /home/vboxuser/Documents/Retail_chain_API_Postgres)

2.	Копируем в нее файлы: .gitignor, config.ini, generate-sales.py, pgbd.py, requirements.txt 

3.	Создаем и активируем виртуальное окружение:
   
_**vboxuser@Ubuntu:~/Documents/Retail_chain_API_Postgres$ python3 -m venv venv**_

_**vboxuser@Ubuntu:~/Documents/Retail_chain_API_Postgres$ source venv/bin/activate**_

4.	Устанавливаем зависимости:
   
_**(venv) vboxuser@Ubuntu:~/Documents/Retail_chain_API_Postgres$ pip install -r requirements.txt**_

5.	На локальном ПК (у меня Windows 10) через DBeaver подключаемся удаленному серверу Ubuntu и создаем БД Retail_chain:
   
<img width="655" height="329" alt="image" src="https://github.com/user-attachments/assets/5af0e3b8-ffb4-417e-9cd8-0f7a313da7e4" />

<img width="906" height="549" alt="image" src="https://github.com/user-attachments/assets/c7a949b9-5818-4363-9973-e40c818502ca" />

6.	Далее создаем взаимосвязанные таблицы sales и shop по следующим sql-запросам:

<img width="675" height="302" alt="image" src="https://github.com/user-attachments/assets/252a18f4-7e93-48bd-b989-35d41285ed86" />
<img width="675" height="302" alt="image" src="https://github.com/user-attachments/assets/583fc01f-7a79-4f3e-b8fb-e3a0693261ec" />

7.	Таблицу shop заполняем произвольными данными.

8. Установливаем все необходимые для проекта библиотеки (pandas, pg8000) через pip install.

9. Запускаем скрипт:  C:\Users\admin\source\repos\Торговая_сеть_API_Postgres> python generate-sales.py
    
   Появляется папка data с файлами формата 10_1.csv. После успешной загрузки данных в БД эти файлы (только эти по формату) удаляются. Под успешной загрузкой понимается и в.ч. наличие дубликатов (т.е. идет проверка на дубликаты). Неуспешная загрузка: отсутствие  доступа к БД, не прошла авторизация, нет такой БД, нет таких таблиц.

<img width="454" height="398" alt="image" src="https://github.com/user-attachments/assets/823a4a4c-1256-4da2-957c-b18dacd423b6" />
<img width="438" height="423" alt="image" src="https://github.com/user-attachments/assets/9e139931-7e17-42a1-980e-ebc2afb38133" />

10. Проверяем наличие строк в DBeaver и смотрим лог ошибок db_errors.log:
 
<img width="974" height="387" alt="image" src="https://github.com/user-attachments/assets/6698b1a6-0c71-4c4a-8d99-7dae9ad77836" />

    При наличии ошибок – они будут записаны в лог:

<img width="758" height="109" alt="image" src="https://github.com/user-attachments/assets/6296e62d-8e82-469b-a1d5-610ecf235814" />

11. Настроим crontab (раз в неделю в 3 часа)

_**EDITOR=nano crontab -e**_

* 3 * * 1 cd /home/vboxuser/Documents/Retail_chain_API_Postgres && /home/vboxuser/Documents/Retail_chain_API_Postgres/venv/bin/python3 /home/vboxuser/Documents/Retail_chain_API_P>
 
12.	Создадим запросы и дашборды в Metabase по своему усмотрению (пример):
      
<img width="974" height="282" alt="image" src="https://github.com/user-attachments/assets/49176afd-ae52-4914-9cef-062bd31858bc" />

<img width="733" height="740" alt="image" src="https://github.com/user-attachments/assets/11734a6e-bd22-4a66-9ba0-11121e6c06df" />

<img width="652" height="637" alt="image" src="https://github.com/user-attachments/assets/18c75b59-5fdc-46b3-9c94-94acc7dbc90a" />

<img width="480" height="434" alt="image" src="https://github.com/user-attachments/assets/cbb944e4-96b1-4eb8-bdb4-ae9d1233fae4" />

<img width="974" height="1068" alt="image" src="https://github.com/user-attachments/assets/58a8344c-d22e-4303-90bf-3ee8a53419d4" />

<img width="495" height="396" alt="image" src="https://github.com/user-attachments/assets/e646f68d-b334-47a9-be6b-22f466dce9cf" />

<img width="631" height="512" alt="image" src="https://github.com/user-attachments/assets/d5b00a4c-90c9-461f-9e8f-ab1a24c6e1b7" />

_**Комментарии к коду:**_

В generate-sales.py не делала лишних классов, т.к.  нет состояния между вызовами, нет связанных данных и методов, нужен один проход: генерация → загрузка.

