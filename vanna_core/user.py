import os
import jwt
from vanna.core.user import UserResolver, User, RequestContext

# Load Config
JWT_SECRET = os.getenv("JWT_SECRET", "default-secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

class CookieUserResolver(UserResolver):
    """
    Resolves users by decoding a JWT token from the 'vanna_auth' cookie.
    """
    async def resolve_user(self, request_context: RequestContext) -> User:
        token = request_context.get_cookie('vanna_auth')
        
        # Fallback to Header for API tools
        if not token:
            auth_header = request_context.get_header('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return self._guest_user()

        try:
            # Decode JWT
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            
            # Return Authenticated User from Payload
            return User(
                id=payload.get("sub"),       # email is used as ID here
                email=payload.get("sub"),
                group_memberships=payload.get("groups", ["viewer"]),
                permissions=payload.get("permissions", ["read"])
            )
        except jwt.ExpiredSignatureError:
            print("⚠️ Token expired")
            return self._guest_user()
        except jwt.InvalidTokenError:
            print("⚠️ Invalid token")
            return self._guest_user()

    def _guest_user(self):
        return User(
            id="guest",
            email="guest@mantrawise.com",
            group_memberships=["viewer"],
            permissions=["read"]
        )