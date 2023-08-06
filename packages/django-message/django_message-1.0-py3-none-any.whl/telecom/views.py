
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from telecom.utils import (mask, send_otp, send_sms, verify_otp)
from telecom import serializers
# Create your views here.

class SendOTPView(APIView):
    '''Check user credential and send OTP phone or email'''
    def post(self, request, format=None):
        serializer = serializers.SendOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"message": "Invalid Input", "errors": serializer.errors,
                             "status": "failed"}, status=status.HTTP_400_BAD_REQUEST)
        #Get Mobile Number
        telecom = request.data.get("telecom")
        channel = request.data.get("channel")
        #send otp on telecom
        if send_otp(telecom, channel=channel):
            # mask telecom
            masked_telecom = mask.apply(telecom, channel=channel)
            message = '{} OTP has been sent to {}'.format(
                channel.upper(), masked_telecom)
            return Response({"message": message, "status": "success",
                             "telecom": masked_telecom, "channel": channel})
        return Response({"message": "Can't send OTP", "status": "failed"},
                        status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    '''This view will verify the OTP entered by user'''

    def post(self, request, format=None):
        data = request.data.copy()
        serializer = serializers.VerifyOTPSerializer(data=data)
        if not serializer.is_valid():
            return Response({"message": "Invalid Input", "errors": serializer.errors,
                         "status": "failed"}, status=status.HTTP_400_BAD_REQUEST)
        #get data
        code = data.get("code")
        telecom = data.get("telecom")
        if verify_otp(telecom, code):
            #Let user enter to homepage
            return Response({"message": "Success", "status": "success"},
                status=status.HTTP_200_OK)
        #Incorrect OTP
        return Response({"message": "Invalid OTP", "status": "failed"},
            status=status.HTTP_400_BAD_REQUEST)


class Notify(APIView):
    '''It will notify the users'''

    def post(self, request, format=None):
        pass