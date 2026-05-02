"""Desk Lamp MCP Tools Module.
Điều khiển đèn bàn học thông minh qua MCP
"""

from .manager import DeskLampToolsManager

_desk_lamp_manager = None


def get_desk_lamp_manager() -> DeskLampToolsManager:
    """
    Lấy instance singleton của DeskLampToolsManager.
    """
    global _desk_lamp_manager
    if _desk_lamp_manager is None:
        _desk_lamp_manager = DeskLampToolsManager()
    return _desk_lamp_manager
