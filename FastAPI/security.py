import os
from datetime import datetime, timedelta, timezone

from passlib.context import CryptContext
from jose import jwt


# Indicating that we want to use the bcrypt hashing algorithm:
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# A JWT needs an algorithm and secret key:
HASH_SECRET_KEY = os.getenv("HASH_SECRET_KEY")
HASH_ALGORITHM = os.getenv("HASH_ALGORITHM")
# The time to live for the JWT:
TOKEN_TTL = timedelta(minutes=int(os.getenv("TOKEN_TTL")))


def create_access_token(user_id: int, ttl: timedelta = TOKEN_TTL) -> str:
    expiry = datetime.now(timezone.utc) + ttl
    
    # Payload is the data encoded within the token - in our case just the user ID:
    payload = {"sub": str(user_id), "exp": expiry}

    # Creating the JWT, using the secret key and algorithm to encode the payload:
    return jwt.encode(payload, HASH_SECRET_KEY, HASH_ALGORITHM)