"""Radio Tool Functions.
Phát các đài radio VOV - Hỗ trợ HLS (m3u8) trực tiếp
"""

import asyncio
import subprocess
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional

from src.utils.logging_config import get_logger
from src.constants.constants import AudioConfig

logger = get_logger(__name__)

# Danh sách các đài radio VOV
RADIO_STATIONS = {
    "vov1": {
        "name": "VOV 1",
        "url": "https://audio-live.vov.vn/hls/live/vov1/audio/audio-eng.m3u8",
        "description": "Đài Tiếng nói Việt Nam 1",
    },
    "vov2": {
        "name": "VOV 2",
        "url": "https://audio-live.vov.vn/hls/live/vov2/audio/audio-eng.m3u8",
        "description": "Đài Tiếng nói Việt Nam 2",
    },
    "vov3": {
        "name": "VOV 3",
        "url": "https://audio-live.vov.vn/hls/live/vov3/audio/audio-eng.m3u8",
        "description": "Đài Tiếng nói Việt Nam 3",
    },
    "vovgt_hn": {
        "name": "VOV Giao thông Hà Nội",
        "url": "https://play.vovgiaothong.vn/live/gthn/playlist.m3u8",
        "description": "Đài Giao thông Hà Nội",
    },
    "vovgt_hcm": {
        "name": "VOV Giao thông Hồ Chí Minh",
        "url": "https://play.vovgiaothong.vn/live/gthcm/playlist.m3u8",
        "description": "Đài Giao thông Hồ Chí Minh",
    },
}

# Biến lưu trữ trạng thái
_current_radio = None
_radio_process = None
_radio_task = None


async def play_radio(args: dict) -> str:
    """MCP tool: Phát đài radio HLS (m3u8)."""
    radio_name = args.get("radio_name", "").lower().strip()

    if not radio_name:
        return "Vui lòng chọn đài radio. Các đài có sẵn: vov1, vov2, vov3, vovgt_hn, vovgt_hcm"

    if radio_name not in RADIO_STATIONS:
        available = ", ".join(RADIO_STATIONS.keys())
        return f"Không tìm thấy đài '{radio_name}'. Các đài có sẵn: {available}"

    station = RADIO_STATIONS[radio_name]
    radio_url = station["url"]
    station_name = station["name"]

    try:
        # Dừng radio hiện tại nếu có
        await _stop_radio_process()

        global _current_radio
        _current_radio = station_name

        # Khởi động FFmpeg để phát HLS trực tiếp
        success = await _start_radio_ffmpeg(radio_url, station_name)
        if success:
            return f"Đang phát đài {station_name} 📻"
        else:
            _current_radio = None
            return f"Lỗi khi phát đài {station_name}"

    except Exception as e:
        logger.error(f"Lỗi phát radio {radio_name}: {e}")
        return f"Lỗi phát đài radio: {str(e)}"


async def _start_radio_ffmpeg(url: str, station_name: str) -> bool:
    """Khởi động FFmpeg để phát HLS stream trực tiếp."""
    global _radio_process, _radio_task

    try:
        # Kiểm tra FFmpeg
        try:
            proc = await asyncio.create_subprocess_exec(
                "ffmpeg", "-version",
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            await proc.wait()
        except FileNotFoundError:
            logger.error("FFmpeg không được cài đặt")
            return False

        # Lấy AudioCodec từ app
        from src.application import Application
        app = Application.get_instance()
        audio_codec = getattr(app, "audio_codec", None)

        if not audio_codec:
            logger.error("AudioCodec chưa sẵn sàng")
            return False

        # FFmpeg command: đọc HLS, output PCM
        cmd = [
            "ffmpeg",
            "-protocol_whitelist", "file,http,https,tcp,tls",
            "-i", url,
            "-re",
            "-f", "s16le",
            "-ar", str(AudioConfig.OUTPUT_SAMPLE_RATE),
            "-ac", str(AudioConfig.CHANNELS),
            "-loglevel", "error",
            "-",
        ]

        logger.info(f"Khởi động radio FFmpeg: {station_name}")
        logger.info(f"Command: {' '.join(cmd)}")

        _radio_process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Task đọc PCM từ FFmpeg và phát qua AudioCodec
        _radio_task = asyncio.create_task(
            _radio_playback_loop(_radio_process, audio_codec, station_name)
        )

        return True

    except Exception as e:
        logger.error(f"Lỗi khởi động FFmpeg radio: {e}")
        return False


async def _radio_playback_loop(process, audio_codec, station_name: str):
    """Vòng lặp đọc PCM từ FFmpeg và phát qua AudioCodec."""
    frame_duration_ms = AudioConfig.FRAME_DURATION
    sample_rate = AudioConfig.OUTPUT_SAMPLE_RATE
    channels = AudioConfig.CHANNELS
    frame_size_samples = int(sample_rate * (frame_duration_ms / 1000))
    frame_size_bytes = frame_size_samples * 2 * channels

    logger.info(f"Bắt đầu playback radio: {station_name}")

    try:
        while True:
            # Đọc PCM data từ FFmpeg stdout
            data = await asyncio.to_thread(process.stdout.read, frame_size_bytes)
            if not data:
                break

            # Chuyển đổi bytes thành numpy array
            audio_array = np.frombuffer(data, dtype=np.int16)

            # Đưa vào AudioCodec để phát
            if audio_codec and hasattr(audio_codec, "write_pcm_direct"):
                await audio_codec.write_pcm_direct(audio_array)
            else:
                logger.warning("AudioCodec.write_pcm_direct không khả dụng")

        logger.info(f"Radio playback kết thúc: {station_name}")

    except asyncio.CancelledError:
        logger.info(f"Radio task bị hủy: {station_name}")
    except Exception as e:
        logger.error(f"Lỗi radio playback: {e}")
    finally:
        global _current_radio
        _current_radio = None


async def _stop_radio_process():
    """Dừng tiến trình radio hiện tại."""
    global _radio_process, _radio_task

    if _radio_task and not _radio_task.done():
        _radio_task.cancel()
        try:
            await _radio_task
        except asyncio.CancelledError:
            pass

    if _radio_process:
        try:
            _radio_process.terminate()
            await asyncio.wait_for(_radio_process.wait(), timeout=5.0)
        except asyncio.TimeoutError:
            _radio_process.kill()
        except Exception:
            pass
        _radio_process = None

    logger.info("Đã dừng radio process")


async def stop_radio(args: dict) -> str:
    """MCP tool: Dừng phát radio."""
    try:
        await _stop_radio_process()
        global _current_radio
        _current_radio = None
        return "Đã dừng phát radio 📻"
    except Exception as e:
        logger.error(f"Lỗi dừng radio: {e}")
        return f"Lỗi dừng radio: {str(e)}"


async def get_radio_list(args: dict) -> str:
    """MCP tool: Lấy danh sách các đài radio có sẵn."""
    try:
        radio_list = "📻 Danh sách đài radio có sẵn:\n"
        for key, station in RADIO_STATIONS.items():
            radio_list += f"  - {station['name']} (lệnh: {key})\n"
            radio_list += f"    {station['description']}\n"

        radio_list += "\nSử dụng: 'phát đài vov1', 'nghe đài vov3', 'mở radio vovgt_hn'"
        return radio_list

    except Exception as e:
        logger.error(f"Lỗi lấy danh sách radio: {e}")
        return f"Lỗi: {str(e)}"


async def get_current_radio(args: dict) -> str:
    """MCP tool: Lấy thông tin đài radio đang phát."""
    try:
        global _current_radio

        if _current_radio:
            return f"Đang phát: 📻 {_current_radio}"
        else:
            return "Không có đài radio nào đang phát. Sử dụng 'phát đài vov1' để bắt đầu."

    except Exception as e:
        logger.error(f"Lỗi lấy thông tin radio hiện tại: {e}")
        return f"Lỗi: {str(e)}"
