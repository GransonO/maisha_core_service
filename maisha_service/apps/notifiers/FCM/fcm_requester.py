import json
import os

import requests
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, messaging

load_dotenv()
firebase_cred = credentials.Certificate(
    {
        "type": os.environ['type'],
        "project_id": os.environ['project_id'],
        "private_key_id": os.environ['private_key_id'],
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDgnOCw0NcEVmVL\nGGwp0jHDm6VW5+Li3Gt40qPhpEWBBdDf2ed6tWdswGpH3gp9SpumwVTbg1voXqEb\nJVs4jHjmZOXk5bkDzZPZ7OxfRAjcpWrCATyKMEWcurIagvWdIFl7/auf6CGBkQGs\nlfJYQE/ireBO3StgT84iCrzTnTwizW+lD+TRF5o/VnG/bPSsxi+4lo1z8EBpaRa/\n5RhAnTfQxLIWib5Cc+xpNr/iKKb+u6c6I+aDBrpbX0nwDNTcQhD/HEqxl9jEV1wB\n8rtrHUcOk/464F673/t8GT2IhrRpEYfsuUyBrrHWpBVtg1EhgjTWRAHT1MowoQx8\no4eHAfkTAgMBAAECggEAJ2O7j6aAHpWcG+hDh64B5iDUhQITat9mxYCDFt39Blxj\nve3zxzQq2AqCWOoagtBjrYG4BOrrYju+GwmZDrirtxO4sUSMBpu1swD2jtpah39G\n0pDu8fj3LD4dX8LZmd2Dc9gPkfJedd9dIMwG/O0CVWlSreHhanl0V8n0RVQMqLlz\n/QBKvWm5fWqRIhQDrwVqM2IM9eZsKcrt9OHxcg0tKMfkILazazzBwuqynLchxlvl\n+Pzbc7Fv99nspF2FKSehq1QcSBBphPL0NaERbPvAd44yHWp+f0cbA8kL/IQrAaA8\nbiOselqiXk0vVAyLKW0IEC5Bseymzr1AQ2xiCAydOQKBgQD+DwtaZYU9KKh+IKHX\n+yjuG1wF4jh7dkq5AezegBzeh+wagSLtjsrLxr4xHiv0mmo+zuuDQpoFtgI+1WOW\nMulUzOVDzPO0ACqZLFCnxC3hhL15XDFiY6d0KWEHF5pTIGuDn4rlHaraAHicYrNk\nr3NoZTcIO5GQVFjYMqA9MP/eBQKBgQDiVDwwIFGArhPYTCbpCeK5rYclXMNUDt7Y\nWD6bAJIvlniof6pklUZAVqN3/e23rqexDus4I20AtOnUPFvUVKQ/1sLUdb5esa0x\nH94a6ZOG4Fv+px4Xri/KXyAEPokAjO++cMYDHE+mMDaHeIn0dwsARPwX/s5sxWen\n2ykw+mEONwKBgF+ele1N7FnaZaAi9AbwFrWXQolMXWnKWdFL8jTEDxmKGsjW9ahn\nZ9hOUuL1siF7xKUjB+z9Mi8YE7xGYBb1znAGNfvQtaB3t5Cy5yBda89HQHDezA91\n5l6H/GbI8WJ7/zso3wPgqJ8oMjzZwR8SEeOmxJGqqdyiglXMqBafzI1pAoGBAIFL\nO8MGg2juiTm0bzoLwrDt99mZP6DCif2vk7w6vEhhPnaL0Ax71lEk7We78VRQe03D\nxw4f9sJDl5z+CjunStmJV23GAcXY3KbGnLxlGTkg7IzybVd706NZalHiY6Oj38W8\naPIX90xqGIyViMHWS7uQrS8MCmLK9udGZSassktLAoGAXGT59aAFQTd3U3LXXvPY\nFCt24hyJf1CC/hpcBlXQ2ulnFsttdIuClUJTqBt9RU0hu1j182YCuYAs4K15fLoV\nxJbJpRnRP8nobiMLAc8bEGKMGpSwYttU86kQFdl1LTTaxnHPaKWThrkQdwH1TL91\nxIT93+kfEmN4ALJAflzpI3Q=\n-----END PRIVATE KEY-----\n",
        "client_email": os.environ['client_email'],
        "client_id": os.environ['client_id'],
        "auth_uri": os.environ['auth_uri'],
        "token_uri": os.environ['token_uri'],
        "auth_provider_x509_cert_url": os.environ['auth_provider_x509_cert_url'],
        "client_x509_cert_url": os.environ['client_x509_cert_url'],
        "universe_domain": os.environ['universe_domain']
    }
)
firebase_app = firebase_admin.initialize_app(firebase_cred)


class FcmCore:

    @staticmethod
    def doctor_validation_notice(fcm_token, message):

        message = messaging.Message(
            notification=messaging.Notification(
                title="Maisha Doctor validation",
                body=message,
            ),
            token=fcm_token
        )
        try:
            x = messaging.send(message)
        except Exception as c:
            print("--------Error---X C I-{}".format(c))

    @staticmethod
    def maisha_schedule_notice(fcm_token, title_text, body_text):

        message = messaging.Message(
            notification=messaging.Notification(
                title=title_text,
                body=body_text
            ),
            token=fcm_token
        )
        try:
            x = messaging.send(message)
        except Exception as c:
            print("--------Error---X C I-{}".format(c))

    @staticmethod
    def doctor_core_notice(fcm_token, message, description, user_id, session_id, type, patient_fcm):
        """Send notification to the doctor"""

        message = messaging.Message(
            data={
                "patientId": user_id,
                "request_type": type,
                "patient_fcm": patient_fcm,
                "sessionID": session_id,
                "description": description,
                "request": "MaishaCoreRequest"
            },
            android=messaging.AndroidConfig(
                ttl=50
            ),
            token=fcm_token
        )
        try:
            x = messaging.send(message)
        except Exception as c:
            print("--------Error---X C I-{}".format(c))

    @staticmethod
    def patient_core_notice(fcm_token, message, doctor_id, session_id, status):
        """Send notification to the patient"""

        message = messaging.Message(
            data={
                "doctorID": doctor_id,
                "sessionID": session_id,
                "status": status,
                "title": "Maisha request update",
                "body": "Click to view the details",
            },
            token=fcm_token
        )
        try:
            x = messaging.send(message)
        except Exception as c:
            print("--------Error---X C I-{}".format(c))

    @staticmethod
    def subscribers_notice(all_tokens, message, media_type, media_id, uploader):
        # Update subscribers

        message = messaging.Message(
            notification=messaging.Notification(
                title="New {} from {}".format(media_type, uploader),
                body=message
            ),
            data={
                "media_id": str(media_id),
                "page": "open_media",
                "title": "Maisha",
                "body": "Click to see the details",
            }
        )
        try:
            x = messaging.send(message)
        except Exception as c:
            print("--------Error---X C I-{}".format(c))