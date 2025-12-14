from vanna.core.llm import LlmService, LlmRequest
from vanna.core.user import User
from vanna_core.store import preference_store


class PreferenceAwareLlmService(LlmService):
    async def prepare_request(
        self,
        request: LlmRequest,
        user: User | None = None
    ) -> LlmRequest:
        # If no user, do nothing
        if not user:
            return request

        prefs = preference_store.get_prefs(user.id)
        if not prefs:
            return request

        pref_text = "\n\n[USER PREFERENCES - STRICTLY FOLLOW]:\n"
        for key, value in prefs.items():
            pref_text += f"- {key}: {value}\n"

        # Inject preferences into SYSTEM message
        for msg in request.messages:
            if msg.role == "system":
                msg.content += pref_text
                break
        else:
            # If no system message exists, create one
            request.messages.insert(
                0,
                {
                    "role": "system",
                    "content": pref_text
                }
            )

        return request
