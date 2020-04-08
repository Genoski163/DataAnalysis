��� ���������� ���������� ���������� PostgreSQL � ���������� ���� ������.
1.���������:
sudo apt update 
sudo apt install postgresql postgresql-contrib 

sudo service postgresql start
service postgresql status  #��������� - 'online'

2.���������� ����:
�������� ���� ������ ��������:

createdb zen --encoding='utf-8'

3.�������� ������������ � ����� ��� ������ ����� ��� ������� � ����
CREATE USER my_user WITH ENCRYPTED PASSWORD 'my_user_password';
GRANT ALL PRIVILEGES ON DATABASE games TO my_user;

4.��������� � ���� ������ ������ �� �����-�����:
pg_restore -d zen zen.dump

� ���� ������ ��������� ������� log_raw, dash_visits, dash_engagement

5. �������� ������ ���������, ������� ���������� ������ � ���������� �� � ����� ������� � ���� sql ������ ��� ���� ������ ������
python3 zen_pipeline.py -s '18:00:00 2019-09-24' -e '19:00:00 2019-09-24'

6. �������� ������ ��������, ������� ������� ��� ���� �� ��� ��������� ������ 
python3 python3 zen_pipeline.py.py


