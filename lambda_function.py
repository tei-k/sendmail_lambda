#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'vendor'))

import sendgrid
from sendgrid.helpers.mail import *
import re

SENDGRID_API_KEY = "_SENDGRID_API_KEY_"
TO_EMAIL = "_TO_EMAIL_"
FROM_EMAIL = "_FROM_EMAIL_"
SUBJECT = "{0}({1} : {2})"

def make_body(args):
    body = """
ID : {0[id]}
ゲーム内の名前 : {0[name]}
メールアドレス : {0[email]}
アプリのバージョン : {0[appver]}
ご利用機種 : {0[machine]}
OS,及びバージョン : {0[os]}
問題発生した日時 : {0[date]}
問い合わせの種類 : {0[kind]}
評価 : {0[evaluation]}
お問い合わせ内容 :
============================
{0[message]}
============================
"""

    return body.format(args)

def send_mail(mail_body, args):
    sg = sendgrid.SendGridAPIClient(apikey=SENDGRID_API_KEY)
    mail_from = Email(FROM_EMAIL)
    mail_to = Email(TO_EMAIL)
    content = Content("text/plain", mail_body)
    mail = Mail(mail_from, SUBJECT.format(args['kind'], args['id'], args['name']), mail_to, content)
    response = sg.client.mail.send.post(request_body=mail.get())
  
    return str(response.status_code)

def lambda_handler(event, context):
    args = {'id': event.get('id', ''),
            'name': event.get('name', ''),
            'email': event.get('email', ''),
            'date': event.get('happenDate', ''),
            'kind': event.get('kind', ''),
            'machine': event.get('machine', ''),
            'os': event.get('os', ''),
            'appver': event.get('appver', ''),
            'evaluation': event.get('other-evaluation', ''),
            'message':event.get('message', '')
#            'stage': context.invoked_function_arn.rsplit(':', 1)[1]
           }

    if args['id'] == '' or args['name'] == '' or args['email'] == '':
        return {'result': 'bad request'} 

    mail_body = make_body(args)
    result = send_mail(mail_body, args)

    if re.match(r"2\d\d", result):
        msg = 'success'
    elif re.match(r"4\d\d", result):
        msg = 'bad request'
    else:
        msg = 'server error'

    return {
        'result': msg
    }
