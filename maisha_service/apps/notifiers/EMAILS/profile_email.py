import os

from dotenv import load_dotenv
from mailjet_rest import Client


class ProfileEmail:
    @staticmethod
    def send_registration_email(name, email):
        subject = 'Account verification'
        message = ProfileEmail.maisha_register_email(name)
        load_dotenv()
        api_key = os.environ['MJ_API_KEY_PUBLIC']
        api_secret = os.environ['MJ_API_KEY_PRIVATE']
        mailjet = Client(auth=(api_key, api_secret), version='v3.1')
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": "maisha@epitomesoftware.live",
                        "Name": "Maisha Service"
                    },
                    "To": [
                        {
                            "Email": email,
                            "Name": name
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
    def maisha_register_email(name):
        return """
         <!DOCTYPE html>
            <html lang="en">
                <body style="text-align:center;">
                    <br/>
                    <img alt="Image" border="0" src="https://res.cloudinary.com/dolwj4vkq/image/upload/v1678089832/Maisha/resources/ic_launcher.png" title="Image" width="200"/>
                    <br/>
                    <br/>
                    <div style="color:#008080;font-family:'Montserrat', 'Trebuchet MS', 'Lucida Grande', 'Lucida Sans Unicode', 'Lucida Sans', Tahoma, sans-serif;line-height:1.2; padding:0;">
                        <div style="font-size: 12px; line-height: 1.2; font-family: 'Lucida Sans Unicode', 'Lucida Sans', Tahoma, sans-serif; color: #008080; mso-line-height-alt: 14px;">
                            <p style="font-size: 18px; line-height: 1.2; text-align: center; mso-line-height-alt: 22px; margin: 0;"><span style="font-size: 18px;"><strong><span style="font-size: 18px;"> Hello {}</span></strong></span></p>
                        </div>
                    </div>
                    <div style="color:#555555;font-family: 'Lucida Sans Unicode', 'Lucida Grande', 'Lucida Sans', Geneva, Verdana, sans-serif;line-height:1.2; padding:10px;">
                        <div style="font-family: 'Lucida Sans Unicode', 'Lucida Grande', 'Lucida Sans', Geneva, Verdana, sans-serif; font-size: 12px; line-height: 1.2; color: #555555; mso-line-height-alt: 14px;">
                            <br/>
                            <p style="font-size: 14px; line-height: 1.2; mso-line-height-alt: 17px; margin: 0; font-family: Verdana, sans-serif;"> We are glad to have you on board. Thank you for joining us on this journey in making the world a better place <br/> through sharing, building and nurturing a healthy space for everyone</p>
                            <br/>
                            <p style="font-size: 14px; line-height: 1.2; mso-line-height-alt: 17px; margin: 0; font-family: Verdana, sans-serif;"> A new future awaits, and we are glad to take it with you.</p>
                            <br/>
                            <p style="font-size: 14px; line-height: 1.2; mso-line-height-alt: 17px; margin: 0; font-family: Verdana, sans-serif;"> Welcome {}</p>
                            <br/>
                            <br/>
                        </div>
                    </div>
                </body>
            </html>
        """.format(name, name)
