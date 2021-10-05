import os

from dotenv import load_dotenv
from mailjet_rest import Client


class SendMail:

    @staticmethod
    def send_support_email(email, code):
        subject = 'Password reset'
        message = EmailTemplates.reset_email(code)
        load_dotenv()
        api_key = os.environ['MJ_API_KEY_PUBLIC']
        api_secret = os.environ['MJ_API_KEY_PRIVATE']
        mailjet = Client(auth=(api_key, api_secret), version='v3.1')
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": "helloalfie@epitomesoftware.live",
                        "Name": "Hello Alfie"
                    },
                    "To": [
                        {
                            "Email": email,
                            "Name": ""
                        }
                    ],
                    "Subject": subject,
                    "HTMLPart": message
                }
            ]
        }
        result = mailjet.send.create(data=data)
        return result.status_code

    @staticmethod
    def send_doctor_request_email(email, patient_name, session_id):
        subject = 'New therapy request'
        message = EmailTemplates.request_to_doctor(patient_name)
        load_dotenv()
        api_key = os.environ['MJ_API_KEY_PUBLIC']
        api_secret = os.environ['MJ_API_KEY_PRIVATE']
        mailjet = Client(auth=(api_key, api_secret), version='v3.1')
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": "helloalfie@epitomesoftware.live",
                        "Name": "Hello Alfie"
                    },
                    "To": [
                        {
                            "Email": email,
                            "Name": ""
                        }
                    ],
                    "Subject": subject,
                    "HTMLPart": message
                }
            ]
        }
        result = mailjet.send.create(data=data)
        return result.status_code


class EmailTemplates:

        @staticmethod
        def request_to_doctor(name):
            return """
            <!DOCTYPE html>
                <html lang="en">
                    <body style="text-align:center;">
                        <br/>
                        <img alt="Image" border="0" src="https://res.cloudinary.com/dolwj4vkq/image/upload/v1621418365/HelloAlfie/ic_launcher.png" title="Image" width="300"/>
                        <br/>
                        <br/>
                        <div style="color:#ff7463;font-family:'Montserrat', 'Trebuchet MS', 'Lucida Grande', 'Lucida Sans Unicode', 'Lucida Sans', Tahoma, sans-serif;line-height:1.2; padding:0;">
                            <div style="font-size: 12px; line-height: 1.2; font-family: 'Lucida Sans Unicode', 'Lucida Sans', Tahoma, sans-serif; color: #ff7463; mso-line-height-alt: 14px;">
                                <p style="font-size: 18px; line-height: 1.2; text-align: center; mso-line-height-alt: 22px; margin: 0;"><span style="font-size: 18px;"><strong><span style="font-size: 18px;"> New therapy session for you </span></strong></span></p>
                            </div>
                        </div>
                        <div style="color:#555555;font-family: 'Lucida Sans Unicode', 'Lucida Grande', 'Lucida Sans', Geneva, Verdana, sans-serif;line-height:1.2; padding:10px;">
                            <div style="font-family: 'Lucida Sans Unicode', 'Lucida Grande', 'Lucida Sans', Geneva, Verdana, sans-serif; font-size: 12px; line-height: 1.2; color: #555555; mso-line-height-alt: 14px;">
                                <p style="font-size: 17px; line-height: 1.2; mso-line-height-alt: 17px; margin: 0; font-family: Verdana, sans-serif;"> You have a new therapy session with {}. Click on this <a href=""> <strong>link</strong> </a> to view the details</p>
                                <br/>
                                <p style="font-size: 14px; line-height: 1.2; mso-line-height-alt: 17px; margin: 0; font-family: Verdana, sans-serif;"> Kindly update the status and confirm if you will be available for the session.</p>
                                <br/>
                                <p style="font-size: 14px; line-height: 1.2; mso-line-height-alt: 17px; margin: 0; font-family: Verdana, sans-serif;"> *** </p>
                                <br/>
                                <br/>
                            </div>
                        </div>
                    </body>
                </html>
            """.format(name)

        @staticmethod
        def request_to_patient(name):
            return """
            <!DOCTYPE html>
                <html lang="en">
                    <body style="text-align:center;">
                        <br/>
                        <img alt="Image" border="0" src="https://res.cloudinary.com/dolwj4vkq/image/upload/v1621418365/HelloAlfie/ic_launcher.png" title="Image" width="300"/>
                        <br/>
                        <br/>
                        <div style="color:#ff7463;font-family:'Montserrat', 'Trebuchet MS', 'Lucida Grande', 'Lucida Sans Unicode', 'Lucida Sans', Tahoma, sans-serif;line-height:1.2; padding:0;">
                            <div style="font-size: 12px; line-height: 1.2; font-family: 'Lucida Sans Unicode', 'Lucida Sans', Tahoma, sans-serif; color: #ff7463; mso-line-height-alt: 14px;">
                                <p style="font-size: 18px; line-height: 1.2; text-align: center; mso-line-height-alt: 22px; margin: 0;"><span style="font-size: 18px;"><strong><span style="font-size: 18px;"> Hello {}</span></strong></span></p>
                            </div>
                        </div>
                        <div style="color:#555555;font-family: 'Lucida Sans Unicode', 'Lucida Grande', 'Lucida Sans', Geneva, Verdana, sans-serif;line-height:1.2; padding:10px;">
                            <div style="font-family: 'Lucida Sans Unicode', 'Lucida Grande', 'Lucida Sans', Geneva, Verdana, sans-serif; font-size: 12px; line-height: 1.2; color: #555555; mso-line-height-alt: 14px;">
                                <p style="font-size: 17px; line-height: 1.2; mso-line-height-alt: 17px; margin: 0; font-family: Verdana, sans-serif;"> Your path to mental wellness administration starts here.</p>
                                <br/>
                                <p style="font-size: 14px; line-height: 1.2; mso-line-height-alt: 17px; margin: 0; font-family: Verdana, sans-serif;"> We are glad to have you on board. Thank you for joining us on this journey in making the world a better place <br/> through sharing, building and nurturing a healthy space for resolution of mental issues</p>
                                <br/>
                                <p style="font-size: 14px; line-height: 1.2; mso-line-height-alt: 17px; margin: 0; font-family: Verdana, sans-serif;"> Your registration has been duly received. We shall send you another email upon confirmation</p>
                                <br/>
                                <br/>
                            </div>
                        </div>
                    </body>
                </html>
            """.format(name)

        @staticmethod
        def completion_patient(name):
            return """
            <!DOCTYPE html>
                <html lang="en">
                    <body style="text-align:center;">
                        <br/>
                        <img alt="Image" border="0" src="https://res.cloudinary.com/dolwj4vkq/image/upload/v1621418365/HelloAlfie/ic_launcher.png" title="Image" width="300"/>
                        <br/>
                        <br/>
                        <div style="color:#ff7463;font-family:'Montserrat', 'Trebuchet MS', 'Lucida Grande', 'Lucida Sans Unicode', 'Lucida Sans', Tahoma, sans-serif;line-height:1.2; padding:0;">
                            <div style="font-size: 12px; line-height: 1.2; font-family: 'Lucida Sans Unicode', 'Lucida Sans', Tahoma, sans-serif; color: #ff7463; mso-line-height-alt: 14px;">
                                <p style="font-size: 18px; line-height: 1.2; text-align: center; mso-line-height-alt: 22px; margin: 0;"><span style="font-size: 18px;"><strong><span style="font-size: 18px;"> Hello {}</span></strong></span></p>
                            </div>
                        </div>
                        <div style="color:#555555;font-family: 'Lucida Sans Unicode', 'Lucida Grande', 'Lucida Sans', Geneva, Verdana, sans-serif;line-height:1.2; padding:10px;">
                            <div style="font-family: 'Lucida Sans Unicode', 'Lucida Grande', 'Lucida Sans', Geneva, Verdana, sans-serif; font-size: 12px; line-height: 1.2; color: #555555; mso-line-height-alt: 14px;">
                                <p style="font-size: 17px; line-height: 1.2; mso-line-height-alt: 17px; margin: 0; font-family: Verdana, sans-serif;"> Your path to mental wellness administration starts here.</p>
                                <br/>
                                <p style="font-size: 14px; line-height: 1.2; mso-line-height-alt: 17px; margin: 0; font-family: Verdana, sans-serif;"> We are glad to have you on board. Thank you for joining us on this journey in making the world a better place <br/> through sharing, building and nurturing a healthy space for resolution of mental issues</p>
                                <br/>
                                <p style="font-size: 14px; line-height: 1.2; mso-line-height-alt: 17px; margin: 0; font-family: Verdana, sans-serif;"> Your registration has been duly received. We shall send you another email upon confirmation</p>
                                <br/>
                                <br/>
                            </div>
                        </div>
                    </body>
                </html>
            """.format(name)
