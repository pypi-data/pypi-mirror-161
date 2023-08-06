========
Message
========

Message is a Django app that is used in REST APIs to send OTP on user mobile 
number and verify the OTP entered by user.

Quick start
-----------

1. Add "telecom" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'telecom',

    ]

2. Include the telecom URLconf in your project urls.py like this::

    path('telecom/', include('telecom.urls'), name='telecom'),

3. Send POST request http://127.0.0.1:8000/telecom/send-otp/ to send otp on user mobile::
    {

     "telecom": "mobile number" #+9134454343
     "channel": "sms"

    }

4. Send POST request http://127.0.0.1:8000/telecom/verify-otp/ to verify OTP::
    {

     "telecom": "mobile number" #+9134454343
     "code": "code" #343433
    
    }