# custos-chatbot/bot_testing/chatbot1/urls.py

from django.urls import path
from .views import ChatbotView, ChatUI

urlpatterns = [
    path("chat/", ChatbotView.as_view(), name="chat"),  # /chatbot1/chat/
    path("ui/", ChatUI.as_view(), name="chat_ui"),      # /chatbot1/ui/
]



