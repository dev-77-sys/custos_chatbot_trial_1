# chatbot1/diag.py
import os, importlib
from django.http import JsonResponse
from django.conf import settings

def _mask(s: str) -> str:
    if not s:
        return ""
    return s[:4] + "..." + s[-4:] if len(s) > 8 else "set"

def custos_diag(request):
    info = {}

    # custos version
    try:
        import custos
        info["custos_version"] = getattr(custos, "__version__", "?")
    except Exception as e:
        info["custos_import_error"] = str(e)

    # middleware module presence
    try:
        mw = importlib.import_module("custos.integrations.django")
        info["middleware_module_path"] = getattr(mw, "__file__", "")
    except Exception as e:
        info["middleware_module_error"] = str(e)

    # envs visible to app (masked)
    info["backend_url"] = os.getenv("CUSTOS_BACKEND_URL", "")
    key = os.getenv("CUSTOS_API_KEY", "")
    info["api_key_present"] = bool(key)
    info["api_key_masked"] = _mask(key)

    # is middleware in settings?
    try:
        info["middleware_registered"] = any(
            m.endswith("CustosCaptureMiddleware") for m in settings.MIDDLEWARE
        )
    except Exception as e:
        info["middleware_check_error"] = str(e)

    # try to ping your Custos backend
    try:
        import requests
        url = (info["backend_url"] or "").rstrip("/") + "/simulator/ping/"
        r = requests.get(url, timeout=4)
        info["backend_ping_status"] = r.status_code
        info["backend_ping_ok"] = (200 <= r.status_code < 300)
    except Exception as e:
        info["backend_ping_error"] = str(e)

    return JsonResponse(info)


def custos_force_beat(request):
    """Send a one-off 'response' beat to prove the wire is live."""
    try:
        import custos
        g = custos.guardian()  # starts HB if not already
        g.evaluate("diag-prompt", "diag-response", confidence=0.95)
        return JsonResponse({"sent": True})
    except Exception as e:
        return JsonResponse({"sent": False, "error": str(e)}, status=500)
