"""Radio MCP Tools Module.
Phát các đài radio VOV qua MCP
"""

from .manager import RadioToolsManager

_radio_manager = None


def get_radio_manager() -> RadioToolsManager:
    """
    Lấy instance singleton của RadioToolsManager.
    """
    global _radio_manager
    if _radio_manager is None:
        _radio_manager = RadioToolsManager()
    return _radio_manager
