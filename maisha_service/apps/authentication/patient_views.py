# Create your views here.
import bugsnag
import datetime
import jwt
import random
import os

from dotenv import load_dotenv
from mailjet_rest import Client

from rest_framework import exceptions
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from rest_framework import views,  status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from ..profiles.models import PatientProfile
from .models import Reset, PatientActivation

from .serializers import UserSerializer
from ..profiles.serializers import PatientsProfileSerializer


class Register(views.APIView):
    """
        Deal with Authentication
    """
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        """ Add New User to DB """
        passed_data = request.data
        try:
            # Check if it exists
            user_exists = Register.get_user_exist(passed_data)
            print("--------------- 1 -----{}".format(user_exists))
            if not user_exists:
                try:
                    # Save data to DB
                    random_code = random.randint(1000, 9999)
                    activation_data = PatientActivation(
                        activation_code=random_code,
                        user_email=(passed_data["email"]).strip().lower()
                    )
                    value = Register.send_maisha_message((passed_data["email"]).lower(), passed_data["firstname"], random_code)
                    if value == 200:
                        activation_data.save()
                    else:
                        print("The value -----{}".format(value))
                        return Response({
                            "status": "failed",
                            "message": "Email sending error",
                            "code": 1
                        }, status.HTTP_200_OK)

                    return Response({
                        "status": "success",
                        "message": "Registration success",
                        "reg_code": random_code,
                        "code": 1
                    }, status.HTTP_200_OK)

                except Exception as E:
                    print("Activation error: {}".format(E))
                    bugsnag.notify(
                        Exception('Activation error: {}'.format(E))
                    )
                    return Response({
                            "status": "failed",
                            "message": "Registration failed",
                            "code": 0
                            }, status.HTTP_200_OK)

            else:
                return Response({
                    "status": "failed",
                    "message": "Registration failed, user with email exists",
                    "code": 2  # User already exists
                }, status.HTTP_200_OK)

        except Exception as E:
            print("Error: {}".format(E))
            bugsnag.notify(
                Exception('Authenticate Post: {}'.format(E))
            )
            return Response({
                "error": "{}".format(E),
                "status": "failed error occurred",
                "message": "Registration failed",
                "code": 0
                }, status.HTTP_200_OK)

    @staticmethod
    def get_user_exist(passed_data):
        """
        Check if exists
        """
        user = get_user_model()
        try:
            user_exists = user.objects.filter(username=(passed_data["email"]).lower().strip()).exists()
            return user_exists

        except Exception as e:
            print("------------------Exception: {}".format(e))
            return False

    @staticmethod
    def send_maisha_message(email, name, code):
        load_dotenv()
        api_key = os.environ['MJ_API_KEY_PUBLIC']
        api_secret = os.environ['MJ_API_KEY_PRIVATE']
        mailjet = Client(auth=(api_key, api_secret), version='v3.1')
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": "maisha@epitomesoftware.live",
                        "Name": "Maisha"
                    },
                    "To": [
                        {
                            "Email": email,
                            "Name": name
                        }
                    ],
                    "Subject": 'Welcome {} to Maisha'.format(name),
                    "HTMLPart":  EmailTemplates.maisha_register_email(name, code)
                }
            ]
        }
        result = mailjet.send.create(data=data)
        return result.status_code


class Login(views.APIView):
    """
        Login, Update
    """
    permission_classes = [AllowAny]

    @staticmethod
    def get(request):
        """ Generate the access token from refresh token"""
        User = get_user_model()
        refresh_token = request.COOKIES.get('refreshtoken')
        if refresh_token is None:
            raise exceptions.AuthenticationFailed(
                'Authentication credentials were not provided.')
        try:
            payload = jwt.decode(
                refresh_token, settings.REFRESH_TOKEN_SECRET, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed(
                'expired refresh token, please login again.')

        user = User.objects.filter(id=payload.get('user_id')).first()
        if user is None:
            raise exceptions.AuthenticationFailed('User not found')

        if not user.is_active:
            raise exceptions.AuthenticationFailed('user is inactive')

        access_token = generate_access_token(user)
        return Response({'access_token': access_token})

    @staticmethod
    def post(request):
        """ Login """
        passed_data = request.data
        response = Response()
        try:

            User = get_user_model()
            username = (passed_data["email"]).lower().strip()
            password = passed_data["password"]
            if (username is None) or (password is None):
                raise exceptions.AuthenticationFailed(
                    'username and password required')

            passed_user = User.objects.filter(username=username)
            if passed_user.exists():
                user = User.objects.filter(username=username).first()
                profile = PatientProfile.objects.filter(email=(passed_data["email"]).lower().strip())
                if user is None:
                    raise exceptions.AuthenticationFailed('user not found')
                le_user = authenticate(username=username, password=password)
                if le_user is None:
                    response.data = {
                        "status": "failed",
                        "message": "Could not authenticate user",
                        "code": 1
                    }

                    return response

                serialized_user = UserSerializer(user).data
                serialized_profile = PatientsProfileSerializer(profile.first()).data

                # Update Patients FCM
                profile.update(fcm=passed_data["fcm"])
                access_token = generate_access_token(user)
                refresh_token = generate_refresh_token(user)

                response.set_cookie(key='refreshtoken', value=refresh_token, httponly=True)
                response.data = {
                    'access_token': access_token,
                    'user': serialized_user,
                    'profile': serialized_profile,
                    "status": "success",
                    "isRegistered": profile.count() > 0,
                    "message": "Login success",
                    "code": 1
                }

                return response

            else:
                return Response({
                    "status": "failed",
                    "message": "Login failed, user does not exist",
                    "code": 0  # user added to db
                }, status.HTTP_200_OK)

        except Exception as e:
            print("login error -------------- {}".format(e))
            return Response({
                "status": "failed",
                "message": "Login failed",
                "code": 2  # Login error
            }, status.HTTP_200_OK)


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


class ResetPass(views.APIView):

    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        # Pass email
        # send reset code
        # Compare code attached to email
        passed_data = request.data
        try:
            # Check if it exists
            result = PatientProfile.objects.filter(email=(passed_data["email"]).lower().strip())
            print("--------------------------------{}".format(result.count()))
            if result.count() < 1:
                return Response({
                    "status": "reset failed",
                    "code": 0,
                    "success": False
                }, status.HTTP_200_OK)
            else:

                random_code = random.randint(1000, 9999)
                # check if reset before
                result = Reset.objects.filter(user_email=(passed_data["email"]).lower().strip())
                print("--------------------------------{}".format(result.count()))
                if result.count() < 1:
                    # Reset object does not exist, add reset details
                    add_reset = Reset(
                        user_email=(passed_data["email"]).lower().strip(),
                        reset_code=random_code,
                    )
                    add_reset.save()
                    ResetPass.send_maisha_support_email((passed_data["email"]).lower(), random_code)

                    return Response({
                            "status": "reset success",
                            "code": 1,
                            "success": True
                            }, status.HTTP_200_OK)
                else:
                    # Update Reset
                    value = ResetPass.send_maisha_support_email((passed_data["email"]).lower(), random_code)

                    if value == 200:
                        Reset.objects.filter(
                            user_email=(passed_data["email"]).lower().strip()
                        ).update(
                            reset_code=random_code,
                            )
                        return Response({
                                "status": "reset success",
                                "code": 1,
                                "success": True
                                }, status.HTTP_200_OK)
                    else:
                        return Response({
                                "status": "reset failed",
                                "code": 0,
                                "success": True
                                }, status.HTTP_200_OK)

        except Exception as E:
            print("Error: {}".format(E))
            bugsnag.notify(
                Exception('Reset Post: {}'.format(E))
            )
            return Response({
                "status": "reset failed",
                "code": 2,
                "success": False
                }, status.HTTP_200_OK)

    @staticmethod
    def put(request):

        passed_data = request.data

        user = get_user_model()
        username = (passed_data["email"]).lower().strip()
        password = passed_data["password"]
        reset_code = passed_data["code"]
        response = Response()

        reset = Reset.objects.filter(user_email=username, reset_code=reset_code)
        if reset.count() < 1:
            response.data = {
                "status": "Failed",
                "code": 0,
                "message": "Reset failed, wrong code passed"
            }
            return response
        else:
            passed_user = user.objects.filter(username=username)
            if passed_user.exists():
                # Update user password
                passed_user = user.objects.filter(username=username).first()
                passed_user.set_password(password)
                passed_user.save()
                response.data = {
                    "status": "success",
                    "message": "password updated",
                    "code": 1
                }
            else:
                response.data = {
                    "status": "failed",
                    "message": "user not found",
                    "code": 0
                }

            return response

    @staticmethod
    def send_maisha_support_email(email, code):
        subject = 'Password reset'
        message = EmailTemplates.maisha_reset_email(code)
        load_dotenv()
        api_key = os.environ['MJ_API_KEY_PUBLIC']
        api_secret = os.environ['MJ_API_KEY_PRIVATE']
        mailjet = Client(auth=(api_key, api_secret), version='v3.1')
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": "maisha@epitomesoftware.live",
                        "Name": "Maisha"
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
    def maisha_register_email(name, code):
        return """
         <!DOCTYPE html>
            <html lang="en">
                <body style="text-align:center;">
                    <br/>
                    <img alt="Image" border="0" src="https://res.cloudinary.com/dolwj4vkq/image/upload/v1631524225/RFH/EMAIL/patient.png" title="Image" width="200"/>
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
                            <p style="font-size: 14px; line-height: 1.2; mso-line-height-alt: 17px; margin: 0; font-family: Verdana, sans-serif;"> We are glad to have you on board. Thank you for joining us on this journey in making the world a better place <br/> through sharing, building and nurturing a healthy space for resolution of mental issues</p>
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
                    <img alt="Image" border="0" src="https://res.cloudinary.com/dolwj4vkq/image/upload/v1631524225/RFH/EMAIL/patient.png" title="Image" width="200"/>
                    <br/>
                    <br/>
                    <div style="color:#008080;font-family:'Montserrat', 'Trebuchet MS', 'Lucida Grande', 'Lucida Sans Unicode', 'Lucida Sans', Tahoma, sans-serif;line-height:1.2; padding:0;">
                        <div style="font-size: 12px; line-height: 1.2; font-family: 'Lucida Sans Unicode', 'Lucida Sans', Tahoma, sans-serif; color: #008080; mso-line-height-alt: 14px;">
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


class PatientVerify(views.APIView):

    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        passed_data = request.data
        try:
            print("------------------------passed_data---------------: {}".format(passed_data))
            # check for activation
            activate = PatientActivation.objects.filter(
                user_email=(passed_data["email"]).lower().strip(),
                activation_code=int(passed_data["activation_code"])
            )
            print("------------------------Activate---------------: {}".format(activate))
            if activate.count() < 1:
                return Response({
                    "status": "failed",
                    "code": 0,
                    "message": "verification failed, wrong activation code passed"
                }, status.HTTP_200_OK)

            else:
                user = get_user_model()
                passed_username = (passed_data["email"]).lower().strip()
                user = user.objects.create_user(username=passed_username, password=passed_data["password"].strip())
                user.first_name = passed_data["firstname"]
                user.last_name = passed_data["lastname"]
                user.email = (passed_data["email"]).lower().strip()

                user.save()
                return Response({
                    "status": "success",
                    "code": 0,
                    "message": "User account activated"
                }, status.HTTP_200_OK)

        except Exception as e:
            print("------------------------ {}".format(e))
            return Response({
                "status": "failed",
                "code": 0,
                "message": "User account NOT activated"
            }, status.HTTP_200_OK)
