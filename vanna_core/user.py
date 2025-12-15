import os
from vanna.core.user import UserResolver, User, RequestContext

# Simple secret token for admin
ADMIN_TOKEN = os.getenv("ADMIN_API_KEY", "secret-admin-key-123")

class CookieUserResolver(UserResolver):
    """
    Resolves users based on a 'vanna_auth' cookie.
    Required because the Vanna Web Component uses cookies automatically.
    """

    async def resolve_user(self, request_context: RequestContext) -> User:
        # 1. Try to get token from Cookie (Standard for Web Component)
        token = request_context.get_cookie('vanna_auth')
        
        # 2. Fallback to Header (For API testing tools like Postman)
        if not token:
            auth_header = request_context.get_header('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if token == ADMIN_TOKEN:
            return User(
                id="admin_user",
                email="admin@mantrawise.com",
                group_memberships=["admin", "viewer"],
                permissions=["read", "write", "execute_sql"]
            )
        else:
            # Default Guest User (Read Only)
            return User(
                id="guest_user",
                email="guest@mantrawise.com",
                group_memberships=["viewer"], # Guest can view but maybe not save
                permissions=["read"]
            )