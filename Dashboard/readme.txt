Для выполнения необходимо установить PostgreSQL и развернуть базу данных.
1.Установка:
sudo apt update 
sudo apt install postgresql postgresql-contrib 

sudo service postgresql start
service postgresql status  #результат - 'online'

2.Развернуть базу:
Создайте базу данных командой:

createdb zen --encoding='utf-8'

3.Создадим пользователя и дадим ему нужные права для доступа к базе
CREATE USER my_user WITH ENCRYPTED PASSWORD 'my_user_password';
GRANT ALL PRIVILEGES ON DATABASE games TO my_user;

4.Загрузите в базу данных данные из бэкап-файла:
pg_restore -d zen zen.dump

В базе данных появиться таблица log_raw, dash_visits, dash_engagement

5. Запустим скрипт пайплайна, который агригирует данные и записывает их в новые таблицы в базе sql удаляя при этом старые данные
python3 zen_pipeline.py -s '18:00:00 2019-09-24' -e '19:00:00 2019-09-24'

6. Запустим скрипт дашборда, который выведет даш борд на наш локальный сервер 
python3 python3 zen_pipeline.py.py


