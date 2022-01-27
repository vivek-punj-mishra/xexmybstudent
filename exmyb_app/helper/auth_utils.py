

import jwt
import datetime

key = 'this_is_exmyb_token'


def generate_jwt_token(_id):
    payload = {
        '_id': _id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
    }
    token = jwt.encode(payload, key, algorithm="HS512")
    return token


def decode_jwt_token(token):
    try:
        payload = jwt.decode(token, key, algorithms=['HS512'])
        return payload

    except Exception as e:
        return {'err': 'invalid token'}
