import jwt
import bcrypt
from datetime import datetime, timedelta

SECRET_KEY = "your_secret_key"
TOKEN_EXPIRATION = timedelta(hours=1)


def generate_token(user_id):
    """Generate a JWT token for a user."""
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + TOKEN_EXPIRATION
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')


def verify_token(token):
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token has expired
    except jwt.DecodeError:
        return None  # Token is invalid


def hash_password(password):
    """Hash a user's password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


def check_password(plain_password, hashed_password):
    """Check if a plain password matches a hashed password."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
