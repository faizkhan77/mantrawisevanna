import os
import jwt
from dotenv import load_dotenv
from vanna.core.user import UserResolver, User, RequestContext

# Ensure env is loaded
load_dotenv()

# Load Config
JWT_SECRET = os.getenv("JWT_SECRET", "secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# Debug print to verify Secret consistency (prints first 3 chars)
print(f"🔐 [USER AUTH] Init with Secret: {JWT_SECRET[:3]}***")

class CookieUserResolver(UserResolver):
    async def resolve_user(self, request_context: RequestContext) -> User:
        # 1. Try Cookie
        token = request_context.get_cookie('vanna_auth')
        
        # 2. Try Header (Backup)
        if not token:
            auth_header = request_context.get_header('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            # print("⚠️ [AUTH] No token found. Defaulting to Guest.")
            return self._guest_user()

        try:
            # Decode
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_email = payload.get("sub")
            
            # Success Log
            print(f"✅ [AUTH] User Authenticated: {user_email}")
            
            return User(
                id=user_email,
                email=user_email,
                group_memberships=payload.get("groups", ["viewer"]),
                permissions=payload.get("permissions", ["read"])
            )
        except jwt.ExpiredSignatureError:
            print("❌ [AUTH] Token Expired")
            return self._guest_user()
        except jwt.InvalidTokenError as e:
            print(f"❌ [AUTH] Invalid Token Error: {e}")
            # print(f"   -> Expecting Secret: {JWT_SECRET[:3]}***")
            return self._guest_user()

    def _guest_user(self):
        return User(
            id="guest",
            email="guest@mantrawise.com",
            group_memberships=["viewer"],
            permissions=["read"]
        )