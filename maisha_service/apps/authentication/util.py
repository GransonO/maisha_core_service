import datetime
import jwt
from django.conf import settings


def generate_access_token(user):

    access_token_payload = {
        'user_id': user.id,
        'email': user.email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, minutes=5),
        'iat': datetime.datetime.utcnow(),
    }
    access_token = jwt.encode(access_token_payload, settings.SECRET_KEY, algorithm='HS256')
    return access_token


def generate_refresh_token(user):
    refresh_token_payload = {
        'user_id': user.id,
        'email': user.email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
        'iat': datetime.datetime.utcnow()
    }
    refresh_token = jwt.encode(
        refresh_token_payload, settings.REFRESH_TOKEN_SECRET, algorithm='HS256')

    return refresh_token


class EmailTemplates:

    @staticmethod
    def verify_email(name, code, password):
        return """
        <!DOCTYPE html>
            <html lang="en">
                <body style="text-align:center;">
                    <br/>
                    <img alt="Image" border="0" src="https://res.cloudinary.com/dolwj4vkq/image/upload/v1678089832/Maisha/resources/ic_launcher.png" title="Image" width="300"/>
                    <br/>
                    <br/>
                    <div style="color:#ff7463;font-family:'Montserrat', 'Trebuchet MS', 'Lucida Grande', 'Lucida Sans Unicode', 'Lucida Sans', Tahoma, sans-serif;line-height:1.2; padding:0;">
                        <div style="font-size: 12px; line-height: 1.2; font-family: 'Lucida Sans Unicode', 'Lucida Sans', Tahoma, sans-serif; color: #ff7463; mso-line-height-alt: 14px;">
                            <p style="font-size: 18px; line-height: 1.2; text-align: center; mso-line-height-alt: 22px; margin: 0;"><span style="font-size: 18px;"><strong><span style="font-size: 18px;"> Hello {}</span></strong></span></p>
                        </div>
                    </div>
                    <div style="color:#555555;font-family: 'Lucida Sans Unicode', 'Lucida Grande', 'Lucida Sans', Geneva, Verdana, sans-serif;line-height:1.2; padding:10px;">
                        <div style="font-family: 'Lucida Sans Unicode', 'Lucida Grande', 'Lucida Sans', Geneva, Verdana, sans-serif; font-size: 12px; line-height: 1.2; color: #555555; mso-line-height-alt: 14px;">
                            <p style="font-size: 17px; line-height: 1.2; mso-line-height-alt: 17px; margin: 0; font-family: Verdana, sans-serif;"> Your path to mental wellness starts here.</p>
                            <br/>
                            <p style="font-size: 14px; line-height: 1.2; mso-line-height-alt: 17px; margin: 0; font-family: Verdana, sans-serif;"> We are glad to have you on board. Thank you for joining us on this journey in making the world a better place <br/> through sharing, building and nurturing a healthy space for resolution of health issues</p>
                            <br/>
                            <p style="font-size: 14px; line-height: 1.2; mso-line-height-alt: 17px; margin: 0; font-family: Verdana, sans-serif;"> Your registration has been verified</p>
                            <br/>
                            <p style="font-size: 14px; line-height: 1.2; mso-line-height-alt: 17px; margin: 0; font-family: Verdana, sans-serif;"> Your activation code is <strong>{}</strong>. <br/> Your one time password is <strong>{}</strong> <br/>Please update once logged in <br/><br/> Thank you </p>
                            <br/>
                            <br/>
                        </div>
                    </div>
                </body>
            </html>
        """.format(name, code, password)

    @staticmethod
    def maisha_register_email(name, code):
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
                            <p style="font-size: 17px; line-height: 1.2; mso-line-height-alt: 17px; margin: 0; font-family: Verdana, sans-serif;"> Welcome</p>
                            <br/>
                            <p style="font-size: 14px; line-height: 1.2; mso-line-height-alt: 17px; margin: 0; font-family: Verdana, sans-serif;"> We are glad to have you on board. Thank you for joining us on this journey in making the world a better place <br/> through sharing, building and nurturing a healthy space for everyone</p>
                            <br/>
                            <p style="font-size: 14px; line-height: 1.2; mso-line-height-alt: 17px; margin: 0; font-family: Verdana, sans-serif;"> Use activation code: <strong>{}</strong> to activate your account.</p>
                            <br/>
                            <p style="font-size: 14px; line-height: 1.2; mso-line-height-alt: 17px; margin: 0; font-family: Verdana, sans-serif;"> Welcome {}</p>
                            <br/>
                            <br/>
                        </div>
                    </div>
                </body>
            </html>
        """.format(name, code, name)

    @staticmethod
    def maisha_reset_email(code):
        return """
            <!DOCTYPE html>
            <html lang="en">
                <body style="text-align:center;">
                    <br/>
                    <img alt="Image" border="0" src="https://res.cloudinary.com/dolwj4vkq/image/upload/v1678089832/Maisha/resources/ic_launcher.png" title="Image" width="200"/>
                    <br/>
                    <br/>
                    <div style="color:#008080;font-family:'Montserrat', 'Trebuchet MS', 'Lucida Grande', 'Lucida Sans Unicode', 'Lucida Sans', Tahoma, sans-serif;line-height:1.2; padding:0;">
                        <div style="font-size: 12px; line-height: 1.2; font-family: 'Lucida Sans Unicode', 'Lucida Sans', Tahoma, sans-serif; color: #ff7463; mso-line-height-alt: 14px;">
                            <p style="font-size: 18px; line-height: 1.2; text-align: center; mso-line-height-alt: 22px; margin: 0;"><span style="font-size: 18px;"><strong><span style="font-size: 18px;"> Did you requested to have your password changed?</span></strong></span></p>
                        </div>
                    </div>
                    <div style="color:#555555;font-family: 'Lucida Sans Unicode', 'Lucida Grande', 'Lucida Sans', Geneva, Verdana, sans-serif;line-height:1.2; padding:10px;">
                        <div style="font-family: 'Lucida Sans Unicode', 'Lucida Grande', 'Lucida Sans', Geneva, Verdana, sans-serif; font-size: 12px; line-height: 1.2; color: #555555; mso-line-height-alt: 14px;">
                            <p style="font-size: 14px; line-height: 1.2; mso-line-height-alt: 17px; margin: 0; font-family: Verdana, sans-serif;"> We received a request to reset your password. <br/>If you made the request, use the code <strong>{}</strong> to complete the process</p>
                            <br/>
                            <br/>
                        </div>
                    </div>
                </body>
            </html>
        """.format(code)
