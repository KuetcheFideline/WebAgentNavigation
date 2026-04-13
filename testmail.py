""
import ast
import smtplib
import random
import re
import string
from enum import IntEnum
from itertools import chain
from typing import Any, TypedDict, Union, cast
import imaplib 
import email
import time
import math 
from collections import Counter
from bs4 import BeautifulSoup

from urllib.parse import urlparse



def receive_mail(url: str,user:str):
    code = 0000 
    Email = "chris.martin.gdpr@gmail.com"
    Password = "fnhcgcqgbwwplwdx"
    SERVEUR = 'imap.gmail.com'
    url = urlparse(url).netloc
    urls = url.split('.')[:-1]  

    try:
        mail = imaplib.IMAP4_SSL(SERVEUR)
        mail.login(Email, Password)

        mail.select('inbox')
        start_time = time.time()
        duration = 40 
        n = 0
        code = ''
        
        while time.time()-start_time <duration:  
            status, data = mail.search(None, 'ALL') 
            mail_ids = []
            for block in data:
                mail_ids += block.split()

            n += 1
          
            mail_id = mail_ids[-10:]
            for id in mail_id :
                status, data = mail.fetch(id, '(RFC822)')

                for response_part in data:
                    if isinstance(response_part, tuple):
                        message = email.message_from_bytes(response_part[1])
                        mail_from = message['from']
                        mail_subject = message['subject']
                        mail_from_cleaned = re.sub(r'\s+', '', mail_from.lower())
                        mail_to =message['To']                        



                        if message.is_multipart():
                            mail_content = ''
                            for part in message.get_payload():
                                if part.get_content_type() == 'text/plain':
                                    mail_content += part.get_payload()
                                elif  part.get_content_type() == 'text/html':
                                   html_content = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                   soup = BeautifulSoup(html_content, 'html.parser')
                                   cleane = soup.get_text()
                                   clean_content = re.sub(r'\s+', ' ', cleane)  
                                   mail_content= clean_content.strip()  
                        else :
                                mail_content = message.get_payload()
                        

                        mail_content_cleaned = re.sub(r'\s+', '', mail_content.lower())

                        for j in urls:
                            numeric_codes = re.search(r'\b\d{6,}\b', mail_content) 
                            alpha_num = re.search(r'\b(?=\w*[A-Za-z])(?=\w*\d)\w{6,}\b', mail_content)
                            alphamasj = re.search(r'\b[A-Z]{6,}\b', mail_content)

 


                            if j.lower() in mail_from.lower() and user.lower() in mail_to.lower():

                                if  numeric_codes :
                                    code = numeric_codes.group(0)
                                elif  alpha_num :
                                  code = alpha_num.group(0)

                                elif alphamasj :
                                    code = alphamasj.group(0)


                            elif  j.lower() in mail_content and user.lower() in mail_to.lower():

                                   
                                if  numeric_codes :
                                    code = numeric_codes.group(0)
                                elif  alpha_num :
                                  code = alpha_num.group(0)

                                elif alphamasj :
                                    code = alphamasj.group(0)

                            elif j.lower() in mail_from_cleaned and user.lower() in mail_to.lower():

                                if  numeric_codes :
                                    code = numeric_codes.group(0)
                                elif  alpha_num :
                                  code = alpha_num.group(0)

                                elif alphamasj :
                                    code = alphamasj.group(0)

                            elif j.lower() in mail_content_cleaned and user.lower() in mail_to.lower():

                                if  numeric_codes :
                                    code = numeric_codes.group(0)
                                elif  alpha_num :
                                  code = alpha_num.group(0)

                                elif alphamasj :
                                    code = alphamasj.group(0)
                               
                    
            return str(code)  

    except imaplib.IMAP4.error as e:
        print("IMAP4 error:", e)
    except Exception as e:
        print("An error occurred:", e)






 
def receive_link(url: str, user:str,Email = "chris.martin.gdpr@gmail.com", Password = "fnhcgcqgbwwplwdx"):
    link  =  "https://mail.google.com/"

    SERVEUR = 'imap.gmail.com'
    url = urlparse(url).netloc
    urls = url.split('.')[:-1]  

    try:
        mail = imaplib.IMAP4_SSL(SERVEUR)
        mail.login(Email, Password)

        mail.select('inbox')
        start_time = time.time()
        duration = 40 
        n = 0
        link= ''
        
        while time.time()-start_time <duration:  
            status, data = mail.search(None, 'ALL') 
            mail_ids = []
            for block in data:
                mail_ids += block.split()

            n += 1
          
            mail_id = mail_ids[-10:]
            for id in mail_id :
                status, data = mail.fetch(id, '(RFC822)')

                for response_part in data:
                    if isinstance(response_part, tuple):
                        message = email.message_from_bytes(response_part[1])
                        mail_from = message['from']
                        mail_subject = message['subject']
                        mail_to =message['To']                        

                        mail_from_cleaned = re.sub(r'\s+', '', mail_from.lower())
                        



                        if message.is_multipart():
                            mail_content = ''
                            for part in message.get_payload():
                                if part.get_content_type() == 'text/plain':
                                    mail_content += part.get_payload()
                                elif  part.get_content_type() == 'text/html':
                                   html_content = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                   soup = BeautifulSoup(html_content, 'html.parser')
                                   cleane = soup.get_text()
                                   clean_content = re.sub(r'\s+', ' ', cleane)  
                                   mail_content= clean_content.strip()  
                        else :
                                mail_content = message.get_payload()
                        

                        mail_content_cleaned = re.sub(r'\s+', '', mail_content.lower())
                    for j in urls:
                        
                        match = re.search(r'(https?://|www\.)[^\s]+', mail_content)


                        if j.lower() in mail_from.lower() and user.lower() in mail_to.lower():

                                if match :
                                    link = match.group(0) 

                        elif  j.lower() in mail_content and user.lower() in mail_to.lower():
                                
                                   
                                if match :
                                    link = match.group(0)

                        elif j.lower() in mail_from_cleaned and user.lower() in mail_to.lower():
                                 
                                if match :
                                    link = match.group(0)
                        elif j.lower() in mail_content_cleaned and user.lower() in mail_to.lower():
                                
                                 if match :
                                
                                    link = match.group(0)
                               
            
        return link 

    except imaplib.IMAP4.error as e:
        print("IMAP4 error:", e)
    except Exception as e:
        print("An error occurred:", e)
