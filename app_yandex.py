# from datetime import datetime
from email.utils import parsedate_tz
import imaplib
import email
import re


from libs.subscription import subscription
from connect_db import add_to_base
# USE IT IN CASE WITHOUT API
# from libs.key_values_scan import keys_list
# from config import MAIL_SERVICE, MAIL_LOGIN, MAIL_PASSWORD


def get_data(MAIL_SERVICE, MAIL_LOGIN, MAIL_PASSWORD, keys_list) -> any:
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
    # print(len(numbers_mails_list))                       # Letters quantity in 'ínbox' for cycling
    
    
    # =================================================
    # --- Main Cycle of letters iteration
    # =================================================

    for num in range(len(numbers_mails_list)):              # In range of letters quantity
        id = num + 1
        result, data = mail.fetch(str(id), "(RFC822)")      # tuple (status, [ Total Content ])
        # raw_data_of_mail = data[0][1].decode()            # String of Total content decoded from binary
        raw_data_of_mail = data[0][1].decode('latin-1')     # Try to sole Cirylic proplem      
        
        data_dict : dict = raw_data_convert(raw_data_of_mail, keys_list)  # Dict of all main data
        print(data_dict)
        if data_dict['Subscription'] != 0:
            add_to_base(data_dict)                            # Send dict with data to Postgres
        # ==============================================
        # RawData -> Convert RD -> Dict of data -> to DB
        # ==============================================
        
    return print('ok ?')


# 
def raw_data_convert(raw_data_of_mail, keys_list) -> dict:

    #   --- Work with content of letter
    msg : str = email.message_from_string(raw_data_of_mail)     # ?    
    
    sender : str =  (msg['From'])
    print('sender: ', sender)
    index_of_finish = sender.find('<')          # Cut sender's name till '<'
    name = sender[:index_of_finish]             # We don't Cut quotes, some data without quotes
    print('name: ', name)

    # ----- Sender Email -----
    def name_email():                                             # We get email separated from sender
        # reg_name = r"\"[\w\s\?@\?.]+"         
        # reg_name = r"\w.*"         
        reg_email = r"<.*?>"                                      # It's find any in <>
        try:
            email : str = re.findall(reg_email, sender)[0]        # email from list
            email = email[1:-1]                                   # Cut quotes from both sides
            return email
        except:
            email = 'UnableTo@Read.Email'               # It's can't decode some data
            return email


    # ----- Sending date -----
    date_send =  (msg['Date'])                          # 'Tue, 29 Jun 2021 19:00:43 +0300'
    # print(date_send)
    tt : tuple = parsedate_tz(date_send)
    try:
        date_str : str = str(tt[0]) + ' ' + str(tt[1]) + ' ' + str(tt[2])       # Format date for PostgreSQL
    except:
        date_str : str = '2012 12 12'
    print('date_str: ', date_str)
    print(len(date_str))
    
    
    # ----- Recipient Email -----
    # def has_len(obj):
    #     return hasattr(obj, '__len__')

    recipient : str = msg['To']
    
    # in case we haven't correct Reciptient
    if hasattr(recipient, '__len__') and len(recipient) < 3:
    # if has_len(recipient) and len(recipient) < 3:
        recipient = 'not@found.net'
    print('Recipient email: ',recipient)

    def recipient_email():                                   # It's start in 'return'
        print('recipient_email')
        reg_email = r"<.*?>"                            # It's find any in <>
        try:
            email : str = re.findall(reg_email, recipient)[0]        # email from list
            email = email[1:-1]                             # Cut quotes from both sides
            print('email: ', email)
            return email
        except:
            return recipient


    # Subscription check
    subscription_check = subscription(
                                        raw_data_of_mail,
                                        keys_list
                                    )

    # print (msg.get_payload(decode=True))            
    return {
        'Sender': name,
        'Email': name_email(),
        'Date': date_str,
        'Recipient' : recipient_email(),
        'Subscription' : subscription_check
        }      


test = 'test'

if __name__ == '__main__':
    get_email_data = get_data(MAIL_SERVICE, MAIL_LOGIN, MAIL_PASSWORD, keys_list)
    # result = raw_data_convert(get_email_data)
