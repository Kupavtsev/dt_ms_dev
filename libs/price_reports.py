# Принимаем данные из БД, которые отобранны по основным словам
# нет, принимать для обработки нечего! Если нельзя обращаться к конкретному письму!

# вставить функцию после subscribe и обрабатывать данные новой асинк функцией 
# которая будет осуществлять поиск Сумм и возвращать данные ввиде массива словарей

# Нужна новая таблица в БД
# От кого имя, имэел, когда полученно, получатель, совпадений по ключевым словам(итог, сумма)
# и три поля для найденных цифр

import base64
import re

# import psycopg2.extras

# from config import PG_LOGIN, PG_PASSWORD

PRICE_REPORTS_SOON = ['Итого']


# try:
#         conn = psycopg2.connect(
#             user = PG_LOGIN,
#             password = PG_PASSWORD,                           
#             database = 'antipodpiska',
#             host = 'localhost',                          # Development
#             # host = 'db',                                # Production
#             port = 5432,    
#         )
# except Exception as ex:
#     print(' /// ----- I am unable to connect to the database ----- ///', ex)
#     raise ex


# cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)


def price_reports(raw_data_of_mail):
    main_content : str = raw_data_of_mail[                   # We are getting MC by taking last string of Raw Data
            raw_data_of_mail.find('X-Antivirus-Status:') +       # plus Length of this string 
            len('X-Antivirus-Status: Clean') : ]            
        
    try:
        b = base64.b64decode(main_content)
        s = b.decode("utf-8")
        # print(s)
        main_content = s
    except: main_content
    
    def scan_text_latin(PRICE_REPORTS_SOON):
        # print(' --- scan_text_latin - START ---')
        
        # Calculate key values to create probability of Subscription
        subscription_count_mention : int = 0

        
        for value in PRICE_REPORTS_SOON:
            subscr = re.findall(value, main_content)

            if len(subscr) > 0 :
                for sub in range(len(subscr)):
                    subscription_count_mention += 1
            else:
                # print( "We didn't find any matches in this letter." )  
                pass
                    
        # print(subscription_count_mention)
        return subscription_count_mention


    text_html : list = re.findall('text/html', raw_data_of_mail)    # Find Coding in all data
    text_plain : list = re.findall('text/plain', raw_data_of_mail)
    # print(text_plain)
    
    
    if len(text_html) > 0 or len(text_plain) > 0:            # Array of key values for searchingkeys_list
        result : int = scan_text_latin(PRICE_REPORTS_SOON)            # Func which will do scanning job
    else:
        result = None
        print('No coding')
    
    # print('The result of mail scanning: ', result)
    return result


if __name__ == '__main__':
    price_reports()