import jwt
import datetime
from jwt import ExpiredSignatureError, InvalidTokenError

SECRET_KEY = "SUPER_SECRET_KEY"

def create_token(user_id: int):
    return jwt.encode(
        {
            "user_id": user_id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
        },
        SECRET_KEY,
        algorithm="HS256"
    )

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["user_id"]

    except ExpiredSignatureError:
        print("Token expired")
        return None

    except InvalidTokenError:
        print("Invalid token")
        return None
