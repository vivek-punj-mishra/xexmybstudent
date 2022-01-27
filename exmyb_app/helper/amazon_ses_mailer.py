from email import message
from operator import sub
from flask import Flask,jsonify
import boto3
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
from flask_restful import Resource
from exmyb_app.models.email_logs_model import EmailLogging
from exmyb_app import app
from exmyb_app import db


class EmptyMailBodyException(Exception):
    pass

class AmazonSESMailSend(object):
    def __init__(self,from_email):
        '''
            From email is email from which email is being send.
        '''
        self.from_email=f"Expand My Business <{from_email}>"
        self.AWS_REGION="ap-south-1"

    def send_mail(self,subject,to_email,html_message="",text_message="",attachment=""):
        '''
            
            Subject is email's subject (String)
            to_email is the list of receipent to which mail is being sent.
            returns status,msg
        
        '''
        CHARSET="UTF-8"


        client=boto3.client('ses',self.AWS_REGION,aws_access_key_id=app.config["AWS_SES_ACCESS_KEY_ID"],aws_secret_access_key=app.config["AWS_SES_SECRET_ACCESS_KEY"])
        msg=MIMEMultipart('mixed')

        to_email=",".join(to_email)
        msg['Subject']=subject
        msg['From']=self.from_email
        msg['To']=to_email
        msg_body=MIMEMultipart('alternative')

        if not(html_message or text_message or attachment):

            return False,"You have not specified html_message or text_message or attachment."
            


        if html_message:
            html_message=MIMEText(html_message.encode(CHARSET),'html',CHARSET)
            msg_body.attach(html_message)
        if text_message:
            text_message=MIMEText(text_message.encode(CHARSET),'plain',CHARSET)
            msg_body.attach(text_message)
        
        ######### Make sure to test attachment functionality
        if attachment and 0:
            att=MIMEApplication(open(attachment,'rb').read())
            att.add_header('Content-Disposition','attachment',filename=os.path.basename(attachment))
            msg.attach(att)
        
        msg.attach(msg_body)
        try:
            is_sent=True
            response=client.send_raw_email(
                Source=self.from_email,
                # Destinations=["hackerrohanpahwa@gmail.com"],
                RawMessage={"Data":msg.as_string()}
                
            )
            err_msg= "Email Sent!"
        except ClientError as e:
            is_sent=False
            err_msg=str(e)
            obj=EmailLogging(subject=subject,from_email=self.from_email,to_email=to_email,body=msg.as_string(),sent=0)
            db.session.add(obj)
            app.logger.error("Amazon SES Error : " + str(e.response['Error']['Message']))
        else :
            obj=EmailLogging(subject=subject,from_email=self.from_email,to_email=to_email,body=msg.as_string(),sent=1,aws_email_message_id=response["MessageId"])
            db.session.add(obj)
            app.logger.info("Amazon SES Sucess: "+response['MessageId'])
        finally:
            db.session.commit()        
        return is_sent,err_msg



    