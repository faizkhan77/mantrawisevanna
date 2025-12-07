from vanna.core.user import UserResolver, User, RequestContext

class SimpleUserResolver(UserResolver):
    async def resolve_user(self, request_context: RequestContext) -> User:
        # --- DEVELOPMENT MODE ---
        # We force everyone to be an admin so Streamlit/API works without cookies.
        return User(
            id="admin_user", 
            email="admin@localhost", 
            group_memberships=["admin", "viewer"]
        )