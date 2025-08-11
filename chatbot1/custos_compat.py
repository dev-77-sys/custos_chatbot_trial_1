# chatbot1/custos_compat.py
"""
Compatibility layer so we can always do:
    from .custos_compat import set_api_key, get_guardian
    set_api_key("..."); guardian = get_guardian()
…regardless of the installed Custos SDK shape/version.
"""

from __future__ import annotations
import os
import logging

logger = logging.getLogger(__name__)

try:
    import custos  # the real SDK
except Exception as e:
    custos = None
    logger.warning("Custos SDK not importable: %s", e)

# Keep a cached client/guardian if the SDK uses a client pattern
_cached_client = None
_cached_guardian = None

def set_api_key(key: str) -> None:
    """
    Always available. Tries, in order:
      1) custos.set_api_key(key) if it exists
      2) custos.Client(api_key=key) and cache it
      3) fall back to env var CUSTOS_API_KEY
    """
    global _cached_client

    if not custos:
        os.environ["CUSTOS_API_KEY"] = key
        logger.info("Custos SDK missing; stored key in env for later.")
        return

    try:
        if hasattr(custos, "set_api_key"):
            custos.set_api_key(key)  # type: ignore[attr-defined]
            return
    except Exception as e:
        logger.debug("custos.set_api_key failed: %s", e)

    try:
        if hasattr(custos, "Client"):
            _cached_client = custos.Client(api_key=key)  # type: ignore[attr-defined]
            return
    except Exception as e:
        logger.debug("custos.Client init failed: %s", e)

    # Last resort: env var
    os.environ["CUSTOS_API_KEY"] = key


def get_guardian():
    """
    Returns an object with .evaluate(prompt, response) no matter the SDK flavor.
    Tries, in order:
      - custos.Custos.guardian(api_key=...) / custos.Custos.guardian()
      - _cached_client.guardian()
      - custos.Custos.guardian() (no args)
      - NullGuardian (no-op)
    """
    global _cached_client, _cached_guardian

    class _NullGuardian:
        def evaluate(self, prompt: str, response: str):
            return {"skipped": True}

    if _cached_guardian is not None:
        return _cached_guardian

    if not custos:
        _cached_guardian = _NullGuardian()
        return _cached_guardian

    # Prefer classmethod pattern with inline key if set
    api_key = os.getenv("CUSTOS_API_KEY", "")

    # custos.Custos.guardian(api_key=...) or custos.Custos.guardian()
    try:
        if hasattr(custos, "Custos") and hasattr(custos.Custos, "guardian"):
            try:
                _cached_guardian = custos.Custos.guardian(api_key=api_key)  # type: ignore
                return _cached_guardian
            except TypeError:
                _cached_guardian = custos.Custos.guardian()  # type: ignore
                return _cached_guardian
    except Exception as e:
        logger.debug("custos.Custos.guardian path failed: %s", e)

    # client.guardian()
    try:
        if _cached_client and hasattr(_cached_client, "guardian"):
            _cached_guardian = _cached_client.guardian()
            return _cached_guardian
    except Exception as e:
        logger.debug("client.guardian() failed: %s", e)

    # Final try without args
    try:
        if hasattr(custos, "Custos") and hasattr(custos.Custos, "guardian"):
            _cached_guardian = custos.Custos.guardian()  # type: ignore
            return _cached_guardian
    except Exception as e:
        logger.debug("final custos.Custos.guardian() failed: %s", e)

    _cached_guardian = _NullGuardian()
    return _cached_guardian
