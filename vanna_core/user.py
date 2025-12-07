from vanna.core.user import UserResolver, User, RequestContext


class SimpleUserResolver(UserResolver):
    """
    VERY SIMPLE user resolver for development.

    - Treats every request as the same 'admin_user'
    - Grants both 'admin' and 'viewer' access groups
    """

    async def resolve_user(self, request_context: RequestContext) -> User:  # type: ignore[override]
        return User(
            id="admin_user",
            email="admin@localhost",
            group_memberships=["admin", "viewer"],
        )
