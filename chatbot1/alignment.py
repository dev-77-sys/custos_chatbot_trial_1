# custos-chatbot/bot_testing/chatbot1/alignment.py


from django.conf import settings
from .custos_compat import set_api_key, get_guardian

# one-liners:
set_api_key(settings.CUSTOS_API_KEY or "")
guardian = get_guardian()

