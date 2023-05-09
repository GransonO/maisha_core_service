import datetime
import jwt
import os

from dotenv import load_dotenv


def generate_access_token(user):

    access_token_payload = {
        'user_id': user.id,
        'email': user.email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, minutes=5),
        'iat': datetime.datetime.utcnow(),
    }
    load_dotenv()
    token_secret = os.environ['SECRET_KEY']
    access_token = jwt.encode(access_token_payload, token_secret, algorithm='HS256')
    return access_token


def generate_refresh_token(user):
    refresh_token_payload = {
        'user_id': user.id,
        'email': user.email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
        'iat': datetime.datetime.utcnow()
    }

    load_dotenv()
    refresh_token_secret = os.environ['REFRESH_TOKEN_SECRET']
    refresh_token = jwt.encode(
        refresh_token_payload, refresh_token_secret, algorithm='HS256')

    return refresh_token
