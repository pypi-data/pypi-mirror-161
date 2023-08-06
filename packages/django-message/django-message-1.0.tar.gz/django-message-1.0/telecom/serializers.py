from rest_framework import serializers


class SendOTPSerializer(serializers.Serializer):
    """
    This class handle data validation for send otp .
    """
    telecom = serializers.CharField()
    channel = serializers.CharField()

    def validate_channel(self, value):
        if not value in ['sms', 'email']:
            raise serializers.ValidationError(
                "channel must be 'sms' or 'email'.")
        return value


class VerifyOTPSerializer(serializers.Serializer):
    """
    This class handle data validation verify otp APIs.
    """
    telecom = serializers.CharField()
    code = serializers.CharField(min_length=6, max_length=6)


class NotifyUserSerializer(serializers.Serializer):
    """
    This class handle data validation notify user.
    """
    subject = serializers.CharField()
    body = serializers.CharField()
    telecom = serializers.DictField()

    def validate_telecom(self, value):
        if not any(value):
            raise serializers.ValidationError("telecom can not be empty dict.")
        return value
