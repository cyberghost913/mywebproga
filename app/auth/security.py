import os
from dotenv import load_dotenv
load_dotenv()

TOKEN_ALGORITHM = os.getenv("TOKEN_ALGORITHM")
ACCESS_TOKEN_LIFETIME = int(os.getenv("ACCESS_TOKEN_LIFETIME"))
TOKEN_SECRET = os.getenv("TOKEN_SECRET")

from .utils import verify_password

def validate_credentials(password: str, hashed_password: str) -> bool:
    return verify_password(password, hashed_password)
