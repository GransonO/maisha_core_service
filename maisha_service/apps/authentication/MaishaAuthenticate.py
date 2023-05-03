from rest_framework import exceptions
from datetime import datetime

import jwt
import bugsnag
import random
import os

from dotenv import load_dotenv
from mailjet_rest import Client
from django.contrib.auth import get_user_model, authenticate
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .serializers import UserSerializer
from .util import generate_access_token, generate_refresh_token
from ..notifiers.SMS.sms import SMS
from .models import UserActivation, Reset
from ..profiles.models import DoctorsProfiles, PatientProfile
from ..profiles.serializers import DoctorProfileSerializer, PatientsProfileSerializer
from ... import settings


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
            if not user_exists:
                try:
                    # Save data to DB
                    random_code = random.randint(1000, 9999)
                    activation_data = UserActivation(
                        activation_code=random_code,
                        user_phone=(passed_data["phone"]).lower().strip(),
                        user_email=(passed_data["email"]).lower()
                    )
                    message = "Hello {} Your Maisha OTP is {}".format(passed_data["firstname"], random_code)
                    status_code = SMS.send((passed_data["phone"]).lower(), message)
                    if status_code == 101:
                        activation_data.save()
                    else:
                        return Response({
                            "status": "failed",
                            "message": "OTP sending error",
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
            user_exists = user.objects.filter(username=(passed_data["email"]).lower()).exists()
            return user_exists

        except Exception as e:
            print("------------------Exception: {}".format(e))
            return False


class Verify(views.APIView):
    """
           Deal with Authentication
       """
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        passed_data = request.data
        try:
            # check for activation
            activate = UserActivation.objects.filter(
                user_email=(passed_data["email"]).lower().strip(),
                user_phone=(passed_data["phone"]).lower().strip(),
                activation_code=int(passed_data["activation_code"])
            )
            if activate.count() < 1:
                return Response({
                    "status": "failed",
                    "code": 0,
                    "message": "verification failed, wrong activation code passed"
                }, status.HTTP_200_OK)

            else:
                user = get_user_model()
                passed_username = (passed_data["email"].strip()).lower()
                user = user.objects.create_user(
                    username=passed_username,
                    first_name=passed_data["firstname"],
                    last_name=passed_data["lastname"],
                    email=(passed_data["email"]).lower().strip(),
                    password=passed_data["password"].strip()
                )
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
        response.data = {
            "status": "failed",
            "message": "Could not authenticate user",
            "code": 1
        }
        try:

            User = get_user_model()
            username = (passed_data["email"]).lower().strip()
            password = passed_data["password"]
            if (username is None) or (password is None):
                raise exceptions.AuthenticationFailed(
                    'username and password required')
            passed_user = User.objects.filter(username=username)
            if passed_user.exists():
                user = passed_user.first()
                if user is None:
                    raise exceptions.AuthenticationFailed('user not found')

                le_user = authenticate(username=username, password=password)
                if le_user is None:
                    return response

                if passed_data["isDoctor"] == "true":
                    profile = DoctorsProfiles.objects.filter(email=(passed_data["email"]).lower())
                    serialized_profile = DoctorProfileSerializer(profile.first()).data
                    serialized_user = UserSerializer(user).data
                else:
                    profile = PatientProfile.objects.filter(email=(passed_data["email"]).lower().strip())
                    serialized_profile = PatientsProfileSerializer(profile[0]).data
                    serialized_user = UserSerializer(user).data

                # Update Doctors FCM
                profile.update(fcm=passed_data["fcm"])
                access_token = generate_access_token(user)
                refresh_token = generate_refresh_token(user)

                response.set_cookie(key='refreshtoken', value=refresh_token, httponly=True)

                if profile[0].is_activated:
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
                    response.data = {
                        'access_token': access_token,
                        'user': serialized_user,
                        'profile': serialized_profile,
                        "status": "pending",
                        "message": "Account not verified",
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
            print("-----------------Error on login : {}".format(e))
            return Response({
                "status": "failed",
                "message": "Login Failed",
                "code": 2  # Login error
            }, status.HTTP_200_OK)


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
            if passed_data["isDoctor"] == "true":
                result = DoctorsProfiles.objects.filter(phone_number=(passed_data["phone"]).lower().strip())

            else:
                result = PatientProfile.objects.filter(phone_number=(passed_data["phone"]).strip())

            if result.count() < 1:
                return Response({
                    "status": "reset failed",
                    "code": 0,
                    "success": False
                }, status.HTTP_200_OK)
            else:

                random_code = random.randint(1000, 9999)
                message = "Your Maisha Reset code is {}".format(random_code)
                # check if reset before
                result = Reset.objects.filter(user_phone=(passed_data["phone"]).lower().strip())

                if result.count() < 1:
                    # Reset object does not exist, add reset details
                    status_code = SMS.send((passed_data["phone"]).lower(), message)

                    if status_code == 101:
                        add_reset = Reset(
                            user_phone=(passed_data["phone"]).lower().strip(),
                            reset_code=random_code,
                        )
                        add_reset.save()

                        return Response({
                            "status": "reset success",
                            "code": 1,
                            "success": True
                        }, status.HTTP_200_OK)

                else:
                    # Update Reset
                    status_code = SMS.send((passed_data["phone"]).lower(), message)

                    if status_code == 101:
                        Reset.objects.filter(
                            user_phone=(passed_data["phone"]).lower().strip()
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
        email = (passed_data["email"]).lower().strip()
        user_phone = (passed_data["phone"]).lower().strip()
        password = passed_data["password"]
        reset_code = passed_data["code"]
        response = Response()

        reset = Reset.objects.filter(user_phone=user_phone, reset_code=reset_code)
        if reset.count() < 1:
            response.data = {
                "status": "Failed",
                "code": 0,
                "message": "Reset failed, wrong code passed"
            }
            return response
        else:
            passed_user = user.objects.filter(username=email)
            if passed_user.exists():
                # Update user password
                passed_user = user.objects.filter(username=email).first()
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
