# -*- coding: utf-8 -*-
import os
import dotenv
from sqlalchemy import create_engine, text



dotenv.load_dotenv()
MAIL_SERVICE = os.getenv('mail_service')
MAIL_LOGIN = os.getenv('login')
MAIL_PASSWORD = os.getenv('password')
PG_LOGIN = os.getenv('user_login')
PG_PASSWORD = os.getenv('user_pass')



DEBUG = True
SECRET_KEY = 'asdfsdfssf asf dsgsdg'

# Database settings:
# SQLALCHEMY_DATABASE_URI = 'sqlite:///mails.db'
# SQLALCHEMY_TRACK_MODIFICATIONS = False

WTF_CSRF_ENABLED = False




# def execute_SQL():
#     # We use 'sqlalchemy' to get data from DB
#     with engine.connect() as connection:
#         result = connection.execute(text("SELECT * from public.anti;"))
#         # result = connection.execute(text("SELECT sender from public.anti;"))
#         for row in result:
#             # print(row)
#             print("seneder:", row['sender'])


# if __name__ == '__main__':
#     execute_SQL()


