# custos-chatbot/bot_testing/chatbot1/alignment.py

import os
from django.conf import settings


# 1) Point the SDK at your backend without depending on custos.set_backend_url
BACKEND_URL = getattr(settings, "CUSTOS_BACKEND_URL", "https://custoslabs-backend.onrender.com")
os.environ.setdefault("CUSTOS_BACKEND_URL", BACKEND_URL)

# 2) Set API key via our compat wrapper (handles many SDK shapes)
from .custos_compat import set_api_key, get_guardian

set_api_key(settings.CUSTOS_API_KEY or "")
guardian = get_guardian()  # lazy object with .evaluate(prompt, response)

