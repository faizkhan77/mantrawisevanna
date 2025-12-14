from vanna.core.llm import LlmService, LlmRequest
from vanna.core.user import User
from vanna_core.store import preference_store


class PreferenceAwareLlmService(LlmService):
    def __init__(self, inner: LlmService):
        self.inner = inner

    async def prepare_request(
        self,
        request: LlmRequest,
        user: User | None = None
    ) -> LlmRequest:
        if user:
            prefs = preference_store.get_prefs(user.id)
            if prefs:
                pref_text = "\n\n[USER PREFERENCES — STRICTLY FOLLOW]:\n"
                for k, v in prefs.items():
                    pref_text += f"- {k}: {v}\n"

                for msg in request.messages:
                    if msg.role == "system":
                        msg.content += pref_text
                        break

        return await self.inner.prepare_request(request, user)

    # ✅ Correct: normal awaitable
    async def send_request(self, request: LlmRequest):
        return await self.inner.send_request(request)

    # ✅ Correct: return async iterator directly (NO await, NO async def body logic)
    def stream_request(self, request: LlmRequest):
        return self.inner.stream_request(request)

    # ✅ Pass-through
    def validate_tools(self, tools):
        return self.inner.validate_tools(tools)
