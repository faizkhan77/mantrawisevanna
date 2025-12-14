import os
from vanna.core.user import UserResolver, User, RequestContext

# Define a simple hardcoded admin token for now (as requested)
# In production, you would validate this against a DB or Auth0
ADMIN_TOKEN = os.getenv("ADMIN_API_KEY", "secret-admin-key-123")

class HeaderUserResolver(UserResolver):
    """
    Resolves users based on the 'Authorization' header.
    - If token matches ADMIN_TOKEN -> Admin User
    - If no token/wrong token -> Guest User (Viewer)
    """

    async def resolve_user(self, request_context: RequestContext) -> User:
        auth_header = request_context.get_header('Authorization')
        token = ""
        
        # Extract Bearer token
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
                group_memberships=["viewer"],
                permissions=["read"]
            )