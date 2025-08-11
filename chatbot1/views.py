# custos-chatbot/bot_testing/chatbot1/views.py

import logging
import re
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import MyChatbot1

logger = logging.getLogger(__name__)

_bot = None
def get_bot():
    global _bot
    if _bot is None:
        logger.info("Initializing model backend…")
        _bot = MyChatbot1()
        logger.info("Model backend ready.")
    return _bot

class ChatUI(TemplateView):
    template_name = "chatbot1/chat.html"

def _looks_derailed(text: str) -> bool:
    if not text or len(text) < 20:
        return True
    bad_markers = ["Customer:", "Associate:", "Submitted by:", "Date Posted:", "C:\\", "/usr/", "Instruction:", "###"]
    if any(m in text for m in bad_markers):
        return True
    if re.search(r"\bRe:\s*\[", text, re.I):
        return True
    return False

def _meal_fallback() -> str:
    return (
        "Quick question: any dietary restrictions or cravings?\n\n"
        "• ⚡ Quick: Scrambled eggs on toast with avocado + hot sauce.\n"
        "• 💸 Budget: Beans & rice with sautéed frozen veggies and salsa.\n"
        "• 🥗 Healthy: Greek yogurt bowl with berries, nuts, and honey."
    )

@method_decorator(csrf_exempt, name="dispatch")
class ChatbotView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"message": "Chatbot API is running! POST a prompt to this endpoint."})

    def post(self, request):
        prompt = (request.data.get("prompt") or "").strip()
        if not prompt:
            return Response({"error": "Prompt required"}, status=400)

        try:
            bot = get_bot()
        except Exception as e:
            logger.exception("Model init failed")
            return Response({"error": "Model init failed", "detail": str(e)}, status=500)

        try:
            response = bot.generate(prompt)
        except Exception as e:
            logger.exception("Generate failed")
            return Response({"error": "Generate failed", "detail": str(e)}, status=500)

        if any(k in prompt.lower() for k in ["hungry", "eat", "food", "meal", "dinner", "lunch", "breakfast"]):
            if _looks_derailed(response):
                response = _meal_fallback()

        # No explicit guardian call needed — Custos auto-captures and posts.
        return Response({"prompt": prompt, "response": response}, status=200)
