from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from jose import jwt

def get_user_or_ip(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            token = auth_header.split(" ")[1]
            payload = jwt.get_unverified_claims(token)
            user_id = payload.get("sub")
            if user_id:
                return f"user:{user_id}"
        except Exception:
            pass
    return f"ip:{get_remote_address(request)}"

limiter = Limiter(key_func=get_user_or_ip)
