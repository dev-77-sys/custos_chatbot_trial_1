# custos-chatbot/bot_testing/chatbot1/alignment.py


from django.conf import settings
from .custos_compat import set_api_key, get_guardian

import custos
custos.set_backend_url(getattr(settings, "CUSTOS_BACKEND_URL", "https://custoslabs-backend.onrender.com"))

set_api_key(settings.CUSTOS_API_KEY or "")
guardian = get_guardian()
