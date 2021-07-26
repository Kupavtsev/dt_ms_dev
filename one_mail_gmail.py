from email.utils import parsedate_tz
import imaplib
import email
import re
import base64


from libs.key_values_scan import keys_list
from libs.subscription import subscription

# from config import MAIL_SERVICE_GMAIL, MAIL_LOGIN_GMAIL, MAIL_PASSWORD_GMAIL

MAIL_SERVICE_GMAIL = 'imap.gmail.com'
MAIL_LOGIN_GMAIL = 'itfactoring@gmail.com'
MAIL_PASSWORD_GMAIL = 't333888o'


def get_data() -> any:
    #   --- Connection
    mail = imaplib.IMAP4_SSL(MAIL_SERVICE_GMAIL, 993)              # IMAP session with domain
    # mail = imaplib.IMAP4_SSL(MAIL_SERVICE_GMAIL)              # IMAP session with domain
    mail.login(MAIL_LOGIN_GMAIL, MAIL_PASSWORD_GMAIL)           # Login to account

    # print(mail.list())                                      # tuple of All Folders on Mail Server



    #   --- Work with emails
    mail.select("inbox")                                  # tuple with status and quantity in List
    result, data = mail.search(None, "ALL")               # tuple, status and list with qaunting of letters
                                                          # from 'select' folder  

    numbers_mails : str = data[0].decode()               # String of all letter's numbers
                                                         # decode it from binary

    numbers_mails_list : list = numbers_mails.split()           # List of numbers (each is Sring)
    print('Number of letters: ',len(numbers_mails_list))                       # Letters quantity in 'ínbox' for cycling
    
                                                        # ===============================================
    latest_email_id : str = (numbers_mails_list[-2])    # ======== Just for one letter id number ========
                                                        # ===============================================

    #   --- Work with One mail letter just for test
    result, data = mail.fetch(latest_email_id, "(RFC822)")      # tuple (status, [ Total content ])
    raw_data_of_mail : str = data[0][1].decode()         # String of Total content decoded from binary
    # b = base64.b64decode(raw_data_of_mail)
    # s = b.decode("utf-8")
    # print(b.decode())
    # raw_data_of_mail = s

    print(raw_data_of_mail)

    
    
    return raw_data_of_mail                             # When you use it out of cycle (OOC)
    # return print('ok ?')


# 
def raw_data_convert(raw_data_of_mail, keys_list) -> dict:
    # raw_data_of_mail = get_data()                       # OOC
    #   --- Work with content of letter
    msg : str = email.message_from_string(raw_data_of_mail)     # ?    
    
    sender : str =  (msg['From'])
    # Обрежим имя отпровителя до '<'
    index_of_finish = sender.find('<')
    name = sender[:index_of_finish]             # We don't Cut quotes, some data without quotes
    print('Sender: ', sender)
    

    # We get name amd email separated from sender
    def name_email():                                   # It's start in 'return'
        # reg_name = r"\"[\w\s\?@\?.]+"         
        # reg_name = r"\w.*"         
        reg_email = r"<.*?>"                            # It's find any in <>
        try:
            email : str = re.findall(reg_email, sender)[0]        # email from list
            email = email[1:-1]                             # Cut quotes from both sides
            return email
        except:
            email = 'UnableTo@Read.Email'               # It's can't decode some data
            return email
    # name_email()

    
    # ----- Sending date -----
    date_send =  (msg['Date'])                          # 'Tue, 29 Jun 2021 19:00:43 +0300'
    # print(date_send)
    tt : tuple = parsedate_tz(date_send)
    try:
        date_str : str = str(tt[0]) + ' ' + str(tt[1]) + ' ' + str(tt[2])       # Format date for PostgreSQL
    except:
        date_str : str = '2012 12 12'


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


    subscription_check = subscription(raw_data_of_mail, keys_list)
   
    return {
        'Sender': name,
        'Email': name_email(),
        'Date': date_str,
        'Recipient' : recipient_email(),
        'Subscription' : subscription_check
        }           

if __name__ == '__main__':
    get_email_data = get_data()
    result = raw_data_convert(get_email_data, keys_list)
    print(result)
