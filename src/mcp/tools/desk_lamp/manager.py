"""Desk Lamp Tools Manager.
Quản lý đăng ký các công cụ điều khiển đèn bàn học vào MCP
"""

from typing import Any, Dict

from src.utils.logging_config import get_logger

from .tools import (
    turn_on,
    turn_off,
    toggle,
    set_brightness,
    set_color_temp,
    set_preset,
    get_status,
    set_timer,
)

logger = get_logger(__name__)


class DeskLampToolsManager:
    """
    Quản lý các công cụ điều khiển đèn bàn học.
    """

    def __init__(self):
        """
        Khởi tạo DeskLampToolsManager.
        """
        self._initialized = False
        logger.info("[DeskLampManager] Khởi tạo quản lý đèn bàn học")

    def init_tools(self, add_tool, PropertyList, Property, PropertyType):
        """
        Đăng ký tất cả các công cụ điều khiển đèn.
        """
        try:
            logger.info("[DeskLampManager] Bắt đầu đăng ký công cụ đèn bàn học")

            # Đăng ký công cụ bật đèn
            self._register_turn_on_tool(add_tool, PropertyList, Property, PropertyType)

            # Đăng ký công cụ tắt đèn
            self._register_turn_off_tool(add_tool, PropertyList, Property, PropertyType)

            # Đăng ký công cụ đảo trạng thái
            self._register_toggle_tool(add_tool, PropertyList, Property, PropertyType)

            # Đăng ký công cụ đặt độ sáng
            self._register_set_brightness_tool(
                add_tool, PropertyList, Property, PropertyType
            )

            # Đăng ký công cụ đặt nhiệt độ màu
            self._register_set_color_temp_tool(
                add_tool, PropertyList, Property, PropertyType
            )

            # Đăng ký công cụ đặt chế độ cài sẵn
            self._register_set_preset_tool(
                add_tool, PropertyList, Property, PropertyType
            )

            # Đăng ký công cụ lấy trạng thái
            self._register_get_status_tool(add_tool, PropertyList)

            # Đăng ký công cụ hẹn giờ
            self._register_set_timer_tool(
                add_tool, PropertyList, Property, PropertyType
            )

            self._initialized = True
            logger.info("[DeskLampManager] Đăng ký công cụ đèn bàn học hoàn tất")

        except Exception as e:
            logger.error(
                f"[DeskLampManager] Lỗi đăng ký công cụ đèn: {e}", exc_info=True
            )
            raise

    def _register_turn_on_tool(
        self, add_tool, PropertyList, Property, PropertyType
    ):
        """Đăng ký công cụ bật đèn."""
        add_tool(
            (
                "desk_lamp.turn_on",
                "Bật đèn bàn học thông minh. "
                "【开灯/关灯】当用户说：开灯、打开灯、开台灯、开一下灯、把灯打开、亮灯、小智开灯 时调用本工具。\n"
                "Sử dụng khi người dùng yêu cầu bật đèn, mở đèn, sáng đèn. "
                "Đèn sẽ bật với độ sáng và nhiệt độ màu mặc định hoặc lần trước đó.\n"
                "Examples: '小智开灯', '打开台灯', '把灯打开', '开一下灯', 'bật đèn', 'mở đèn'.",
                PropertyList(),
                turn_on,
            )
        )
        logger.debug("[DeskLampManager] Đăng ký công cụ bật đèn thành công")

    def _register_turn_off_tool(
        self, add_tool, PropertyList, Property, PropertyType
    ):
        """Đăng ký công cụ tắt đèn."""
        add_tool(
            (
                "desk_lamp.turn_off",
                "Tắt đèn bàn học thông minh. "
                "【开灯/关灯】当用户说：关灯、关闭灯、关台灯、把灯关掉、关一下灯、小智关灯 时调用本工具。\n"
                "Sử dụng khi người dùng yêu cầu tắt đèn, ngủ đèn, tối đi. "
                "Examples: '小智关灯', '关闭台灯', '把灯关掉', '关一下灯', 'tắt đèn', 'ngủ đèn'.",
                PropertyList(),
                turn_off,
            )
        )
        logger.debug("[DeskLampManager] Đăng ký công cụ tắt đèn thành công")

    def _register_toggle_tool(
        self, add_tool, PropertyList, Property, PropertyType
    ):
        """Đăng ký công cụ đảo trạng thái."""
        add_tool(
            (
                "desk_lamp.toggle",
                "Đảo trạng thái đèn bàn học (bật <-> tắt). "
                "【开灯/关灯】当用户说：切换灯光、切换台灯、开/关灯、小智切换灯光 时调用。\n"
                "Sử dụng khi người dùng muốn chuyển đổi trạng thái đèn. "
                "Examples: '小智切换灯光', '切换台灯', 'chuyển đổi đèn'.",
                PropertyList(),
                toggle,
            )
        )
        logger.debug("[DeskLampManager] Đăng ký công cụ đảo trạng thái thành công")

    def _register_set_brightness_tool(
        self, add_tool, PropertyList, Property, PropertyType
    ):
        """Đăng ký công cụ đặt độ sáng."""
        brightness_props = PropertyList(
            [
                Property(
                    "brightness",
                    PropertyType.INTEGER,
                    default_value=50,
                    min_value=1,
                    max_value=100,
                ),
            ]
        )

        add_tool(
            (
                "desk_lamp.set_brightness",
                "Điều chỉnh độ sáng đèn bàn học (0-100%). "
                "【调节亮度】当用户说：调亮、调暗、亮度调到50、稍微调亮、把灯调亮、亮度50、小智调亮 时调用。\n"
                "Sử dụng khi người dùng yêu cầu: chỉnh độ sáng, sáng hơn, tối hơn, "
                "đặt độ sáng 50%, mức sáng 80. "
                "Tham số: brightness (số nguyên 1-100, mặc định 50). "
                "Examples: '小智调亮一点', '亮度调到80', '稍微调暗', 'đặt độ sáng 50%'.",
                brightness_props,
                set_brightness,
            )
        )
        logger.debug("[DeskLampManager] Đăng ký công cụ đặt độ sáng thành công")

    def _register_set_color_temp_tool(
        self, add_tool, PropertyList, Property, PropertyType
    ):
        """Đăng ký công cụ đặt nhiệt độ màu."""
        temp_props = PropertyList(
            [
                Property(
                    "temperature",
                    PropertyType.INTEGER,
                    default_value=4000,
                    min_value=1700,
                    max_value=6500,
                ),
            ]
        )

        add_tool(
            (
                "desk_lamp.set_color_temp",
                "Điều chỉnh nhiệt độ màu đèn bàn học (1700-6500K). "
                "【调节色温】当用户说：暖光、冷光、白光、黄光、色温调到3000、小智调暖一点 时调用。\n"
                "Sử dụng khi người dùng yêu cầu: ánh sáng ấm, ánh sáng trắng, "
                "màu vàng, màu trắng, nhiệt độ 3000K. "
                "1700K: Ánh sáng ấm (vàng), 4000K: Trung tính, 6500K: Ánh sáng lạnh (trắng). "
                "Tham số: temperature (số nguyên 1700-6500, mặc định 4000). "
                "Examples: '小智调暖一点', '色温调到3000', '调成冷光', 'đặt nhiệt độ 4000K'.",
                temp_props,
                set_color_temp,
            )
        )
        logger.debug(
            "[DeskLampManager] Đăng ký công cụ đặt nhiệt độ màu thành công"
        )

    def _register_set_preset_tool(
        self, add_tool, PropertyList, Property, PropertyType
    ):
        """Đăng ký công cụ đặt chế độ cài sẵn."""
        preset_props = PropertyList(
            [
                Property(
                    "preset",
                    PropertyType.STRING,
                    default_value="study",
                ),
            ]
        )

        add_tool(
            (
                "desk_lamp.set_preset",
                "Đặt chế độ cài sẵn cho đèn bàn học. "
                "【场景模式】当用户说：学习模式、阅读模式、放松模式、专注模式、小智学习模式 时调用。\n"
                "Sử dụng khi người dùng yêu cầu: chế độ học tập, chế độ đọc sách, "
                "chế độ thư giãn, chế độ tập trung. "
                "Các chế độ có sẵn: "
                "'study' (Học tập/学习模式: 5000K, 100%), "
                "'reading' (Đọc sách/阅读模式: 4000K, 70%), "
                "'relax' (Thư giãn/放松模式: 2700K, 50%), "
                "'focus' (Tập trung/专注模式: 6000K, 90%). "
                "Tham số: preset (study/reading/relax/focus, mặc định study). "
                "Examples: '小智学习模式', '切换到阅读模式', 'chế độ thư giãn'.",
                preset_props,
                set_preset,
            )
        )
        logger.debug("[DeskLampManager] Đăng ký công cụ đặt chế độ thành công")

    def _register_get_status_tool(self, add_tool, PropertyList):
        """Đăng ký công cụ lấy trạng thái."""
        add_tool(
            (
                "desk_lamp.get_status",
                "Lấy trạng thái hiện tại của đèn bàn học. "
                "【查询状态】当用户说：灯亮吗、灯开了吗、台灯状态、亮度多少、色温多少、小智灯亮吗 时调用。\n"
                "Sử dụng khi người dùng yêu cầu: trạng thái đèn, đèn đang bật không, "
                "độ sáng bao nhiêu, nhiệt độ màu hiện tại. "
                "Trả về: Trạng thái nguồn, độ sáng, nhiệt độ màu và mô tả. "
                "Examples: '小智灯亮吗', '台灯状态', '亮度多少', 'trạng thái đèn'.",
                PropertyList(),
                get_status,
            )
        )
        logger.debug(
            "[DeskLampManager] Đăng ký công cụ lấy trạng thái thành công"
        )

    def _register_set_timer_tool(
        self, add_tool, PropertyList, Property, PropertyType
    ):
        """Đăng ký công cụ hẹn giờ tắt."""
        timer_props = PropertyList(
            [
                Property(
                    "minutes",
                    PropertyType.INTEGER,
                    default_value=30,
                    min_value=1,
                    max_value=480,
                ),
            ]
        )

        add_tool(
            (
                "desk_lamp.set_timer",
                "Hẹn giờ tắt đèn bàn học. "
                "【定时关闭】当用户说：30分钟后关灯、定时关灯、半小时关灯、小智定时关灯 时调用。\n"
                "Sử dụng khi người dùng yêu cầu: hẹn giờ tắt đèn, "
                "tắt đèn sau 30 phút, đặt báo thức tắt đèn. "
                "Đèn sẽ tự động tắt sau số phút chỉ định. "
                "Tham số: minutes (số nguyên 1-480, mặc định 30). "
                "Examples: '小智30分钟后关灯', '定时关灯', '半小时后关灯', 'hẹn giờ tắt đèn'.",
                timer_props,
                set_timer,
            )
        )
        logger.debug("[DeskLampManager] Đăng ký công cụ hẹn giờ thành công")

    def is_initialized(self) -> bool:
        """
        Kiểm tra manager đã được khởi tạo chưa.
        """
        return self._initialized

    def get_status_info(self) -> Dict[str, Any]:
        """
        Lấy thông tin trạng thái của manager.
        """
        return {
            "initialized": self._initialized,
            "tools_count": 8,
            "available_tools": [
                "turn_on",
                "turn_off",
                "toggle",
                "set_brightness",
                "set_color_temp",
                "set_preset",
                "get_status",
                "set_timer",
            ],
            "device_ip": "192.168.2.24",
        }
