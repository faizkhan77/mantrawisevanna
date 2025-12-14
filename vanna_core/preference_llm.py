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
        # --- START OF DEBUGGING BLOCK ---
        print("\n" + "="*50)
        if user:
            print(f"🕵️  [DEBUG] Preference Service: Preparing request for user: '{user.id}'")
            prefs = preference_store.get_prefs(user.id)
            print(f"📚 [DEBUG] Preference Service: Found preferences in store: {prefs}")
            if prefs:
                pref_text = "\n\n[USER PREFERENCES — STRICTLY FOLLOW]:\n"
                for k, v in prefs.items():
                    pref_text += f"- {k}: {v}\n"

                for msg in request.messages:
                    if msg.role == "system":
                        msg.content += pref_text
                        print("✅ [DEBUG] Preference Service: Successfully injected preferences into system prompt.")
                        break
            else:
                print("⚠️  [DEBUG] Preference Service: No preferences found for this user. Nothing to inject.")
        else:
            print("👤 [DEBUG] Preference Service: No user identified in request.")
        print("="*50 + "\n")
        # --- END OF DEBUGGING BLOCK ---

        return await self.inner.prepare_request(request, user)

    # ... rest of the class remains the same
    async def send_request(self, request: LlmRequest):
        return await self.inner.send_request(request)

    def stream_request(self, request: LlmRequest):
        return self.inner.stream_request(request)

    def validate_tools(self, tools):
        return self.inner.validate_tools(tools)