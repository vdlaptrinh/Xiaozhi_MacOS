"""Desk Lamp Tool Functions.
Các hàm thực thi điều khiển đèn bàn học
Hỗ trợ đọc IP từ config.json và quét mạng tự động
"""

import asyncio
import json
from pathlib import Path
from typing import Optional

from yeelight import Bulb, discover_bulbs
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def _get_config_file() -> Path:
    """Lấy đường dẫn config.json trực tiếp từ thư mục config/."""
    # Thử từ thư mục hiện tại
    local_config = Path("config/config.json")
    if local_config.exists():
        return local_config.resolve()
    
    # Thử từ thư mục gốc dự án (file này nằm ở src/mcp/tools/desk_lamp/)
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    project_config = project_root / "config" / "config.json"
    if project_config.exists():
        return project_config
    
    # Trả về mặc định (sẽ được tạo nếu cần)
    return project_root / "config" / "config.json"


def _read_config() -> dict:
    """Đọc config.json."""
    try:
        config_file = _get_config_file()
        if config_file.exists():
            return json.loads(config_file.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning(f"Lỗi đọc config.json: {e}")
    return {}


def _write_config(data: dict) -> None:
    """Ghi config.json."""
    try:
        config_file = _get_config_file()
        config_file.parent.mkdir(parents=True, exist_ok=True)
        config_file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
    except Exception as e:
        logger.error(f"Lỗi ghi config.json: {e}")


class DeskLampController:
    """Quản lý kết nối và điều khiển đèn bàn học."""

    def __init__(self):
        self._bulb: Optional[Bulb] = None
        self._ip: Optional[str] = None

    def _get_config_ip(self) -> str:
        """Lấy IP từ config.json."""
        try:
            config = _read_config()
            desk_lamp_config = config.get("DESK_LAMP", {})
            ip = desk_lamp_config.get("ip", "")
            if ip:
                logger.info(f"Đọc IP đèn từ config.json: {ip}")
                return ip
        except Exception as e:
            logger.warning(f"Lỗi đọc config DESK_LAMP: {e}")
        return ""

    def _save_ip_to_config(self, ip: str) -> None:
        """Lưu IP vào config.json."""
        try:
            config = _read_config()
            if "DESK_LAMP" not in config:
                config["DESK_LAMP"] = {}
            config["DESK_LAMP"]["ip"] = ip
            config["DESK_LAMP"]["auto_scan"] = True
            config["DESK_LAMP"]["scan_timeout"] = 3
            _write_config(config)
            logger.info(f"Đã lưu IP {ip} vào config.json")
        except Exception as e:
            logger.warning(f"Lỗi lưu config: {e}")

    async def _scan_network(self) -> Optional[str]:
        """Quét mạng tìm đèn Yeelight."""
        try:
            logger.info("Đang quét mạng tìm đèn Yeelight...")
            loop = asyncio.get_event_loop()
            bulbs = await loop.run_in_executor(None, discover_bulbs)

            if not bulbs:
                logger.warning("Không tìm thấy đèn nào trên mạng")
                return None

            found_ip = bulbs[0]['ip']
            logger.info(f"Tìm thấy đèn: {found_ip}")
            return found_ip

        except Exception as e:
            logger.error(f"Lỗi quét mạng: {e}")
            return None

    def get_bulb(self):
        """Lấy instance Bulb, tạo mới nếu chưa có."""
        if self._bulb is not None:
            return self._bulb

        # Thử đọc IP từ config trước
        self._ip = self._get_config_ip()

        # Nếu không có trong config, thử quét mạng
        if not self._ip:
            logger.info("Không có IP trong config.json, đang quét mạng...")
            try:
                bulbs = discover_bulbs()
                if bulbs:
                    self._ip = bulbs[0]['ip']
                    logger.info(f"Tìm thấy đèn qua quét mạng: {self._ip}")
                    self._save_ip_to_config(self._ip)
            except Exception as e:
                logger.error(f"Lỗi quét mạng: {e}")

        if not self._ip:
            raise Exception("Không tìm thấy đèn. Hãy cấu hình IP trong config.json hoặc bật 'LAN Control'")

        logger.info(f"Kết nối đèn tại {self._ip}")
        self._bulb = Bulb(
            self._ip, auto_on=True, effect="smooth", duration=300
        )
        return self._bulb

    async def _execute(self, func_name: str, *args, **kwargs):
        """Thực thi lệnh điều khiển đèn bất đồng bộ."""
        loop = asyncio.get_event_loop()
        try:
            bulb = self.get_bulb()
            result = await loop.run_in_executor(
                None, getattr(bulb, func_name), *args, **kwargs
            )
            return result
        except Exception as e:
            logger.error(f"Lỗi thực thi {func_name}: {e}")
            # Nếu lỗi kết nối, thử quét lại mạng
            if "timeout" in str(e).lower() or "connection" in str(e).lower():
                logger.info("Lỗi kết nối, đang quét lại mạng tìm đèn...")
                new_ip = await self._scan_network()
                if new_ip:
                    self._bulb = None  # Reset bulb
                    self._ip = new_ip
                    self._save_ip_to_config(new_ip)
                    # Thử lại
                    bulb = self.get_bulb()
                    result = await loop.run_in_executor(
                        None, getattr(bulb, func_name), *args, **kwargs
                    )
                    return result
            raise

    async def turn_on(self) -> str:
        """Bật đèn."""
        try:
            await self._execute("turn_on")
            return "Đã bật đèn bàn học 💡"
        except Exception as e:
            return f"Lỗi bật đèn: {str(e)}"

    async def turn_off(self) -> str:
        """Tắt đèn."""
        try:
            await self._execute("turn_off")
            return "Đã tắt đèn bàn học 💡"
        except Exception as e:
            return f"Lỗi tắt đèn: {str(e)}"

    async def toggle(self) -> str:
        """Đảo trạng thái đèn."""
        try:
            await self._execute("toggle")
            return "Đã chuyển đổi trạng thái đèn 💡"
        except Exception as e:
            return f"Lỗi chuyển đổi đèn: {str(e)}"

    async def set_brightness(self, brightness: int) -> str:
        """Điều chỉnh độ sáng (0-100)."""
        try:
            if not 0 <= brightness <= 100:
                return "Độ sáng phải từ 0-100"
            await self._execute("set_brightness", brightness)
            return f"Đã đặt độ sáng: {brightness}% 💡"
        except Exception as e:
            return f"Lỗi đặt độ sáng: {str(e)}"

    async def set_color_temp(self, temp: int) -> str:
        """Điều chỉnh nhiệt độ màu (1700-6500K)."""
        try:
            if not 1700 <= temp <= 6500:
                return "Nhiệt độ màu phải từ 1700-6500K"
            await self._execute("set_color_temp", temp)
            return f"Đã đặt nhiệt độ màu: {temp}K 💡"
        except Exception as e:
            return f"Lỗi đặt nhiệt độ màu: {str(e)}"

    async def set_preset(self, preset: str) -> str:
        """Đặt chế độ cài đặt sẵn."""
        presets = {
            "study": (5000, 100, "Học tập"),
            "reading": (4000, 70, "Đọc sách"),
            "relax": (2700, 50, "Thư giãn"),
            "focus": (6000, 90, "Tập trung"),
        }

        if preset not in presets:
            return f"Chế độ không hợp lệ. Các chế độ có sẵn: {', '.join(presets.keys())}"

        temp, bright, name = presets[preset]
        try:
            await self._execute("set_color_temp", temp)
            await self._execute("set_brightness", bright)
            return f"Đã đặt chế độ: {name} ({temp}K, {bright}%) 💡"
        except Exception as e:
            return f"Lỗi đặt chế độ: {str(e)}"

    async def get_status(self) -> str:
        """Lấy trạng thái hiện tại của đèn."""
        try:
            loop = asyncio.get_event_loop()
            bulb = self.get_bulb()
            props = await loop.run_in_executor(None, bulb.get_properties)

            power = "BẬT" if props["power"] == "on" else "TẮT"
            bright = props.get("bright", "N/A")
            ct = props.get("ct", "N/A")

            temp_desc = ""
            if ct != "N/A":
                ct_int = int(ct)
                if ct_int < 3300:
                    temp_desc = "(Ánh sáng ấm - vàng)"
                elif ct_int < 5000:
                    temp_desc = "(Ánh sáng trung tính)"
                else:
                    temp_desc = "(Ánh sáng lạnh - trắng)"

            return f"Trạng thái đèn: {power} | Độ sáng: {bright}% | Nhiệt độ màu: {ct}K {temp_desc}"
        except Exception as e:
            return f"Lỗi lấy trạng thái đèn: {str(e)}"

    async def set_timer(self, minutes: int) -> str:
        """Hẹn giờ tắt đèn."""
        try:
            if minutes <= 0:
                return "Thời gian hẹn giờ phải lớn hơn 0"
            await self._execute("turn_off", minutes * 60)
            return f"Đã hẹn giờ tắt đèn sau {minutes} phút ⏰"
        except Exception as e:
            return f"Lỗi hẹn giờ: {str(e)}"


_controller = DeskLampController()


async def turn_on(args: dict) -> str:
    """MCP tool: Bật đèn bàn."""
    return await _controller.turn_on()


async def turn_off(args: dict) -> str:
    """MCP tool: Tắt đèn bàn."""
    return await _controller.turn_off()


async def toggle(args: dict) -> str:
    """MCP tool: Đảo trạng thái đèn."""
    return await _controller.toggle()


async def set_brightness(args: dict) -> str:
    """MCP tool: Đặt độ sáng."""
    brightness = args.get("brightness", 50)
    return await _controller.set_brightness(brightness)


async def set_color_temp(args: dict) -> str:
    """MCP tool: Đặt nhiệt độ màu."""
    temp = args.get("temperature", 4000)
    return await _controller.set_color_temp(temp)


async def set_preset(args: dict) -> str:
    """MCP tool: Đặt chế độ cài sẵn."""
    preset = args.get("preset", "study")
    return await _controller.set_preset(preset)


async def get_status(args: dict) -> str:
    """MCP tool: Lấy trạng thái đèn."""
    return await _controller.get_status()


async def set_timer(args: dict) -> str:
    """MCP tool: Hẹn giờ tắt đèn."""
    minutes = args.get("minutes", 30)
    return await _controller.set_timer(minutes)
