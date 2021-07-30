# from datetime import datetime
import datetime

from email.utils import parsedate_tz
import dateparser

import imaplib
import email
import re


from libs.subscription import subscription
from libs.price_reports import price_reports
from connect_db import add_to_base

# USE IT IN CASE WITHOUT API
# from libs.key_values_scan import keys_list
# from config import MAIL_SERVICE, MAIL_LOGIN, MAIL_PASSWORD

TWO_YEARS_PERIOD_CHECK : datetime = datetime.datetime.now() - datetime.timedelta(days=2*365)
REGEX_MAIL_VALIDATION = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

# 1. get_data функция принимает данные из Пост запроса из Веб Сервиса
# 2. Входит в почтовый сервер с этими данными
#    Проверяет наличие и количество писем в папке входящие
# 3. В цикле проходит по каждому письму
#    Проверяет, письма начиная с последнего,
#        проверяет дату, чтобы она была не старше 2х лет
#    и вызавет функцию raw_data_convert, передавая ей письмо, ключевые слова и дату письма
#    и помещает ответ данной функции в БД connect_db.py
# 4. raw_data_convert, получает ОТ, КОМУ,
# 5. запускает subscription (libs/subscription.py), передает все письмо и ключевые слова
#    Возвращает Число найденных совпадений
# 6. возвращает словарь помещаемый в connect_db.py
def get_data(MAIL_SERVICE, MAIL_LOGIN, MAIL_PASSWORD, keys_list) -> any:
   
    # -= 2 =-
    #   --- Connection
    mail = imaplib.IMAP4_SSL(MAIL_SERVICE)              # IMAP session with domain
    mail.login(MAIL_LOGIN, MAIL_PASSWORD)                             # Login to account

    # print(mail.list())                                      # tuple of All Folders on Mail Server



    #   --- Work with emails
    # mail.select("You can choise any Mail Folder from mail.list()")
    mail.select("inbox")                                  # tuple with status and quantity in List
    result, data = mail.search(None, "ALL")               # tuple, status and list with qaunting of letters
                                                          # from 'select' folder  

    numbers_mails : str = data[0].decode()               # String of all letter's numbers
                                                         # decode it from binary

    numbers_mails_list : list = numbers_mails.split()           # List of numbers (each is Sring)
 
    
    
    # =================================================
    # --- Main Cycle of letters iteration
    # =================================================

    #  -= 3 =-
    # for num in numbers_mails_list:
    for num in range(len(numbers_mails_list)):              # In range of letters quantity
        id = len(numbers_mails_list) - (num + 1)
        if id >= 1:
            # id = num + 1
            print("ID Main: ", id)
            result, data = mail.fetch(str(id), "(RFC822)")      # tuple (status, [ Total Content ])
            # result, data = mail.fetch(num, "(RFC822)")      # tuple (status, [ Total Content ])
            # raw_data_of_mail = data[0][1].decode()            # String of Total content decoded from binary
            raw_data_of_mail = data[0][1].decode('latin-1')     # Try to solve Cirylic proplem      
            

            #   --- Work with content of letter
            msg : str = email.message_from_string(raw_data_of_mail)     # ?   


            # ----- Sending date -----
            date_send =  (msg['Date'])                          # 'Tue, 29 Jun 2021 19:00:43 +0300'
            tt : tuple = parsedate_tz(date_send)
            try:
                date_str : str = str(tt[0]) + ' ' + str(tt[1]) + ' ' + str(tt[2])       # Format date for PostgreSQL
            except:
                date_str : str = '2012 12 12'

            current_mail_date : datetime = dateparser.parse(date_str)
            
            if current_mail_date > TWO_YEARS_PERIOD_CHECK:

                # Каждая переменная получит не словарь, а массив. И обратиться к своему словарю.
                # Нет data_dict получит массив словарей!
                data_dict : dict = raw_data_convert(msg, raw_data_of_mail, keys_list, date_str)  # Dict of all main data
                # print(data_dict)
                # data_price_report : dict = None
                if data_dict['Subscription'] != 0:
                    add_to_base(data_dict)                            # Send dict with data to Postgres
                else:
                    pass
                    # print('there was not matches')
            else:
                pass
                break
        else:
            pass
            break
        # ==============================================
        # RawData -> Convert RD -> Dict of data -> to DB
        # ==============================================
        
    return print('ok ?')


# -= 4 =-
def raw_data_convert(msg, raw_data_of_mail, keys_list, date_str) -> dict:

    # #   --- Work with content of letter
    # msg : str = email.message_from_string(raw_data_of_mail)     # ?    
    
    # SENDER
    sender : str =  (msg['From'])
    # print('sender: ', sender)
    index_of_finish = sender.find('<')          # Cut sender's name till '<'
    name = sender[:index_of_finish]             # We don't Cut quotes, some data without quotes
    # print('name: ', name)

    # ----- Sender Email -----
    def name_email():                                             # We get email separated from sender
        try:
            email : str = re.findall(REGEX_MAIL_VALIDATION, sender)[0]        # email from list
            return email
        except:
            email = 'UnableTo@Read.Email'               # It's can't decode some data
            return email


    
    # RECIPIENT
    recipient : str = msg['To']
    
    # in case we haven't correct Reciptient
    if hasattr(recipient, '__len__') and len(recipient) < 3:
    # if has_len(recipient) and len(recipient) < 3:
        recipient = 'not@found.net'
    # print('Recipient email: ',recipient)

    def recipient_email():                                   # It's start in 'return'
        try:
            email : str = re.findall(REGEX_MAIL_VALIDATION, recipient)[0]        # email from list
            return email
        except:
            return recipient


    # -= 5 =-
    # Subscription check
    subscription_check : int = subscription(
                                        raw_data_of_mail,
                                        keys_list
                                    )
    # print('subscription_check: ', subscription_check)
    # Если есть подписка переходим к поиску Цен и Отчетов
    if subscription_check != 0:
        print('Im on Price Data Chek')
        # data_price_report = price_reports(raw_data_of_mail)
    else:
        pass

    # print (msg.get_payload(decode=True))   
              

    # -= 6 =-
    # Здесь он вернет массив двух слварей
    return {
        'Sender': name,
        'Email': name_email(),
        'Date': date_str,
        'Recipient' : recipient_email(),
        'Subscription' : subscription_check
        }      



if __name__ == '__main__':
    get_email_data = get_data(MAIL_SERVICE, MAIL_LOGIN, MAIL_PASSWORD, keys_list)
    # result = raw_data_convert(get_email_data)
