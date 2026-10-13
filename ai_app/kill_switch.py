
from pathlib import Path

# Shared by Django and monitor_langsmith.py
FLAG_FILE = Path(__file__).resolve().parent.parent / "kill_switch.flag"


def kill_switch():
    FLAG_FILE.write_text("DISABLED", encoding="utf-8")
    print("🛑 AI KILL SWITCH FLAG ACTIVATED")


def is_ai_enabled():
    return not FLAG_FILE.exists()


def reset_kill_switch():
    """Use only when you intentionally want to re-enable AI."""
    if FLAG_FILE.exists():
        FLAG_FILE.unlink()
        print("✅ AI KILL SWITCH RESET")
