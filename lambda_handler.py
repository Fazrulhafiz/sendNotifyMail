import datetime
import json
import os
import base64
import boto3
from botocore.exceptions import ClientError
from datetime import date

def lambda_handler(event, context):
    params = {}
    if 'queryStringParameters' in event and 'datahat' in event['queryStringParameters'] and 'information' in event['queryStringParameters']:
        return { 'statusCode': 422, 'body': json.dumps('Missing required request parameters') }
    else:
        params["datahat"] = event['queryStringParameters']['datahat']
        params["information"] = event['queryStringParameters']['information']

        today = format(datetime.datetime.now() + datetime.timedelta(hours=8, minutes=10), '%Y-%m-%d')

        plainCreds = base64.b64decode(params["datahat"]).decode('utf8').split(':')
        isdate = datetime.datetime.strptime(plainCreds[0], '%Y-%m-%d').date()
        password = plainCreds[1]

        if (isdate != today and password != os.environ['password']) :
            return { 'statusCode': 401, 'body': json.dumps('Unauthorized') }
        else :
            info_ = base64.b64decode(params["information"]).decode('utf8').split(':')
            articleid = info_[0]
            errorinfo = info_[1]

            SENDER = os.environ['sender']
            RECIPIENT = os.environ['recipient']
            AWS_REGION = os.environ['ses_region']
            SUBJECT = "Article Webhook Synchronization Error"
            BODY_TEXT = ("Webhook error has occured.\r\nArticle with ID {} has an error on executing the webhook. Below are the details:\r\n{}".format(articleid, errorinfo))
            BODY_HTML = """<html>
            <head></head>
            <body>
              <h1>Webhook error has occured.</h1>
              <p>Article with ID {} has an error on executing the webhook.<br/> Below are the details:<br/>
                {}.</p>
            </body>
            </html>
                        """.format(articleid, errorinfo)
            CHARSET = "UTF-8"

            client = boto3.client('ses',region_name=AWS_REGION)

            try:
                response = client.send_email(
                    Destination={
                        'ToAddresses': [
                            RECIPIENT,
                        ],
                    },
                    Message={
                        'Body': {
                            'Html': {
                                'Charset': CHARSET,
                                'Data': BODY_HTML,
                            },
                            'Text': {
                                'Charset': CHARSET,
                                'Data': BODY_TEXT,
                            },
                        },
                        'Subject': {
                            'Charset': CHARSET,
                            'Data': SUBJECT,
                        },
                    },
                    Source=SENDER,
                )

            except ClientError as e:
                print(e.response['Error']['Message'])
            else:
                print("Email sent! Message ID:"),
                print(response['MessageId'])

        return {
            'statusCode': 200,
            'body': json.dumps('Email sent!')
        }
