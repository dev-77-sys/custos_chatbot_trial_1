# custos-chatbot/bot_testing/chatbot1/alignment.py


import custos
from django.conf import settings

custos.set_api_key(settings.CUSTOS_API_KEY)

guardian = custos.Custos.guardian()
