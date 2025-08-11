# custos-chatbot/bot_testing/bot_testing/urls.py



from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

urlpatterns = [
    path("admin/", admin.site.urls),
    path("chatbot1/", include("chatbot1.urls")),
    path("ping/", lambda r: JsonResponse({"ok": True})),
]
