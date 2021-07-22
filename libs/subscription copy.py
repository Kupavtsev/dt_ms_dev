import base64
import re

from email.utils import parsedate_tz
import email

def subscription(raw_data_of_mail, keys_list) -> str:                       # Find mail body content
        main_content : str = raw_data_of_mail[                   # We are getting MC by taking last string of Raw Data
            raw_data_of_mail.find('X-Antivirus-Status:') +       # plus Length of this string 
            len('X-Antivirus-Status: Clean') : ]            
        
        try:
            b = base64.b64decode(main_content)
            s = b.decode("utf-8")
            # print(s)
            main_content = s
        except: main_content
        
        def scan_text_latin(keys_list):
            # print(' --- scan_text_latin - START ---')
            
            # Calculate key values to create probability of Subscription
            subscription_count_mention : int = 0

            
            for value in keys_list:
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
            result : int = scan_text_latin(keys_list)            # Func which will do scanning job


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

        else:
            name = None
            def name_email(): None
            date_str = '2012 12 12'
            def recipient_email(): None
            result = None
            print('No coding')





        
        print('The result of mail scanning: ', result)
        # return result
        return {
            'Sender': name,
            'Email': name_email(),
            'Date': date_str,
            'Recipient' : recipient_email(),
            'Subscription' : result
            }  


if __name__ == '__main__':
    subscription()