# works with both python 2 and 3
import os

import africastalking
from dotenv import load_dotenv


class SMS:

    @staticmethod
    def send(phone, message):
        # Set your app credentials
        load_dotenv()
        username = "MaishaSMSService"
        api_key = os.environ['AFRICA_TALKING_API_KEY']

        # Initialize the SDK
        africastalking.initialize(username, api_key)

        # Get the SMS service
        sms = africastalking.SMS
        recipients = [phone]

        # Set your shortCode or senderId
        sender = "shortCode or senderId"
        try:
            # response = self.sms.send(message, recipients, sender)
            response = sms.send(message, recipients)
            return response["SMSMessageData"]["Recipients"][0]["statusCode"]

        except Exception as e:
            print('Encountered an error while sending: %s' % str(e))
            return 404
