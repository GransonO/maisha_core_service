import json
import os

import requests
from dotenv import load_dotenv


class FcmCore:

    @staticmethod
    def doctor_validation_notice(all_tokens, message):
        url = 'https://fcm.googleapis.com/fcm/send'

        load_dotenv()
        fcm_key = os.environ['MAISHA_FCM_KEY']

        my_headers = {
            "Authorization": "key={}".format(fcm_key),
            "content-type": "application/json"
        }

        my_data = {
            "registration_ids": all_tokens,
            "notification": {
                      "title": "Maisha Doctor validation",
                      "body": message,
                      "icon": "request_icon"
                    }
        }

        # y = requests.post(url, headers=myHeaders, data=json.dumps(background))
        x = requests.post(url, headers=my_headers, data=json.dumps(my_data))
        print("message sen ------------------------------------ : {}".format(x))

    @staticmethod
    def doctor_core_notice(all_tokens, message, description, user_id, session_id, type, patient_fcm):
        """Send notification to the doctor"""
        url = 'https://fcm.googleapis.com/fcm/send'

        load_dotenv()
        fcm_key = os.environ['MAISHA_FCM_KEY']

        my_headers = {
            "Authorization": "key={}".format(fcm_key),
            "content-type": "application/json"
        }

        my_data = {
            "registration_ids": all_tokens,
            "data": {
                "patientId": user_id,
                "request_type": type,
                "patient_fcm": patient_fcm,
                "sessionID": session_id,
                "description": description,
            },
            "android": {
                "ttl": "40s"
            },
        }

        # y = requests.post(url, headers=myHeaders, data=json.dumps(background))
        x = requests.post(url, headers=my_headers, data=json.dumps(my_data))
        print("message sent ------------------------------------ : {}".format(x))

    @staticmethod
    def patient_core_notice(all_tokens, message, doctor_id, session_id, status):
        """Send notification to the doctor"""
        url = 'https://fcm.googleapis.com/fcm/send'

        load_dotenv()
        fcm_key = os.environ['MAISHA_FCM_KEY']

        my_headers = {
            "Authorization": "key={}".format(fcm_key),
            "content-type": "application/json"
        }

        my_data = {
            "registration_ids": all_tokens,
            # "notification": message_body,
            "data": {
                "doctorID": doctor_id,
                "sessionID": session_id,
                "status": status,
                "title": "Maisha request update",
                "body": "Click to view the details",
            }
        }

        x = requests.post(url, headers=my_headers, data=json.dumps(my_data))
        print("message sent ------------------------------------ : {}".format(x))

    @staticmethod
    def subscribers_notice(all_tokens, message, media_type, media_id, uploader):
        """Send notification to the doctor"""
        url = 'https://fcm.googleapis.com/fcm/send'

        load_dotenv()
        fcm_key = os.environ['FCM_KEY']

        my_headers = {
            "Authorization": "key={}".format(fcm_key),
            "content-type": "application/json"
        }

        message_body = {
            "title": "New {} from {}".format(media_type, uploader),
            "text": message,
            "icon": "https://res.cloudinary.com/dolwj4vkq/image/upload/v1621418365/HelloAlfie/ic_launcher.png",
        }

        my_data = {
            "registration_ids": all_tokens,
            "notification": message_body,
            "data": {
                "media_id": str(media_id),
                "page": "open_media",
                "title": "Maisha",
                "body": "Click to see the details",
            }
        }

        requests.post(url, headers=my_headers, data=json.dumps(my_data))
