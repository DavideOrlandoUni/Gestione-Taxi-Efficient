# ============================================================
# logging_console.py
# - Logging robusto e compatibile con console non-UTF
# - Setup UTF-8 su stdout/stderr
# ============================================================

import sys

def log_sicuro_console_compatibile(prefisso: str, err: Exception):
    """Stampa errori anche su console non-UTF (fallback sicuro)."""
    try:
        print(f"{prefisso}{err}")
    except Exception:
        print(prefisso + repr(err))

try:
    if sys.stdout and (not sys.stdout.encoding or "utf" not in sys.stdout.encoding.lower()):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if sys.stderr and (not sys.stderr.encoding or "utf" not in sys.stderr.encoding.lower()):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
