========
Message
========

This is a Django app used in REST APIs to send SMS and OTP on user mobile 
number and verify the number using OTP entered by user.This app is using TWILIO
service to send sms, So before using this app make sure you have **TWILIO** account.

You can refer this TWILIO doc to know more.

`https://www.twilio.com/docs/sms/quickstart/python`

Quick start
-----------

1. Add "telecom" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'telecom',

    ]

2. Add these attribute to your setting like this::

    TWILIO_ACCOUNT_SID = 'set your ACCOUNT_SID'
    TWILIO_SERVICE_SID = 'set your SERVICE_SID'
    TWILIO_AUTH_TOKEN = 'set your AUTH_TOKEN'
    TWILIO_PHONE_NUMBER = 'set your PHONE_NUMBER'

3. Include the telecom URLconf in your project urls.py like this::
    path('telecom/', include('telecom.urls'), name='telecom'),

4. Send POST request http://127.0.0.1:8000/telecom/send-otp/ to send otp on user mobile::
    {

     "telecom": "mobile number" .. +919134454343
     "channel": "sms"

    }

5. Send POST request http://127.0.0.1:8000/telecom/verify-otp/ to verify OTP::
    {

     "telecom": "mobile number" .. +9134454343
     "code": "code" .. 343433
    
    }

6. Send POST request http://127.0.0.1:8000/telecom/send-sms/ to send sms::
    {

     "telecom": "mobile number" .. +919134454343
     "body": "message" .. Hi Zen!
    
    }