# custos-chatbot/bot_testing/chatbot1/urls.py

# chatbot1/urls.py
from django.urls import path
from .views import ChatbotView, ChatUI
from .diag import custos_diag, custos_force_beat

urlpatterns = [
    path("chat/", ChatbotView.as_view(), name="chat"),
    path("ui/", ChatUI.as_view(), name="chat_ui"),

    # diagnostics
    path("custos/diag/", custos_diag, name="custos_diag"),
    path("custos/beat/", custos_force_beat, name="custos_force_beat"),
]
