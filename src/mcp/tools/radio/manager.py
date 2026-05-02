"""Radio Tools Manager.
Quản lý đăng ký các công cụ phát đài radio vào MCP
"""

from typing import Any, Dict

from src.utils.logging_config import get_logger

from .tools import play_radio, stop_radio, get_radio_list, get_current_radio

logger = get_logger(__name__)


class RadioToolsManager:
    """
    Quản lý các công cụ phát đài radio VOV.
    """

    def __init__(self):
        """
        Khởi tạo RadioToolsManager.
        """
        self._initialized = False
        logger.info("[RadioManager] Khởi tạo quản lý đài radio")

    def init_tools(self, add_tool, PropertyList, Property, PropertyType):
        """
        Đăng ký tất cả các công cụ phát đài radio.
        """
        try:
            logger.info("[RadioManager] Bắt đầu đăng ký công cụ radio")

            # Đăng ký công cụ phát đài radio
            self._register_play_radio_tool(
                add_tool, PropertyList, Property, PropertyType
            )

            # Đăng ký công cụ dừng phát
            self._register_stop_radio_tool(add_tool, PropertyList)

            # Đăng ký công cụ lấy danh sách đài
            self._register_get_radio_list_tool(add_tool, PropertyList)

            # Đăng ký công cụ lấy đài đang phát
            self._register_get_current_radio_tool(add_tool, PropertyList)

            self._initialized = True
            logger.info("[RadioManager] Đăng ký công cụ radio hoàn tất")

        except Exception as e:
            logger.error(
                f"[RadioManager] Lỗi đăng ký công cụ radio: {e}", exc_info=True
            )
            raise

    def _register_play_radio_tool(
        self, add_tool, PropertyList, Property, PropertyType
    ):
        """Đăng ký công cụ phát đài radio."""
        radio_props = PropertyList(
            [
                Property(
                    "radio_name",
                    PropertyType.STRING,
                ),
            ]
        )

        add_tool(
            (
                "radio.play",
                "Phát đài radio VOV. "
                "Sử dụng khi người dùng yêu cầu: phát đài vov1, nghe đài vov3, "
                "mở radio vovgt_hn, bật đài giao thông. "
                "Các đài có sẵn: vov1, vov2, vov3, vovgt_hn, vovgt_hcm. "
                "Tham số: radio_name (vov1/vov2/vov3/vovgt_hn/vovgt_hcm). "
                "Ví dụ: 'phát đài vov1', 'nghe đài vov3', 'mở radio giao thông Hà Nội'.",
                radio_props,
                play_radio,
            )
        )
        logger.debug("[RadioManager] Đăng ký công cụ phát radio thành công")

    def _register_stop_radio_tool(self, add_tool, PropertyList):
        """Đăng ký công cụ dừng phát radio."""
        add_tool(
            (
                "radio.stop",
                "Dừng phát đài radio. "
                "Sử dụng khi người dùng yêu cầu: tắt đài, dừng radio, ngừng phát đài. "
                "Lệnh này sẽ dừng đài radio đang phát và giải phóng tài nguyên.",
                PropertyList(),
                stop_radio,
            )
        )
        logger.debug("[RadioManager] Đăng ký công cụ dừng radio thành công")

    def _register_get_radio_list_tool(self, add_tool, PropertyList):
        """Đăng ký công cụ lấy danh sách đài radio."""
        add_tool(
            (
                "radio.list",
                "Lấy danh sách các đài radio VOV có sẵn. "
                "Sử dụng khi người dùng yêu cầu: danh sách đài radio, có những đài nào, "
                "hiển thị các đài radio. "
                "Trả về danh sách 5 đài: VOV1, VOV2, VOV3, VOV Giao thông Hà Nội, VOV Giao thông HCM.",
                PropertyList(),
                get_radio_list,
            )
        )
        logger.debug("[RadioManager] Đăng ký công cụ lấy danh sách radio thành công")

    def _register_get_current_radio_tool(self, add_tool, PropertyList):
        """Đăng ký công cụ lấy đài đang phát."""
        add_tool(
            (
                "radio.current",
                "Lấy thông tin đài radio đang phát. "
                "Sử dụng khi người dùng yêu cầu: đang phát đài nào, đài gì đang mở, "
                "trạng thái radio. "
                "Trả về tên đài đang phát hoặc thông báo không có đài nào đang phát.",
                PropertyList(),
                get_current_radio,
            )
        )
        logger.debug(
            "[RadioManager] Đăng ký công cụ lấy đài đang phát thành công"
        )

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
            "tools_count": 4,
            "available_tools": [
                "play",
                "stop",
                "list",
                "current",
            ],
            "stations_count": 5,
        }
