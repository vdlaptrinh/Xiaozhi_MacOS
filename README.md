# Py-Xiaozhi - Hướng dẫn cài đặt nhanh

## 🚀 Cài đặt môi trường

### 1. Kích hoạt Virtual Environment
```bash
source /Users/dailuu/py_xiaozhi_env/bin/activate
```

### 2. Nâng cấp pip và cài đặt cơ bản
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Cài đặt bổ sung (Quan trọng)
```bash
# Cho Python 3.13 và macOS
pip install lunar-python openai cryptography pendulum
pip install opencv-python-headless paho-mqtt pygame PyQt5
pip install soxr psutil pillow webrtcvad-wheels
pip install colorlog yeelight mutagen requests numpy --upgrade
```

## 📦 Danh sách thư viện đã cài (Environment hiện tại)

| Thư viện | Phiên bản | Mục đích |
|-----------|-------------|-----------|
| numpy | 2.2.6 | Xử lý dữ liệu số |
| torch | 2.11.0 | Machine Learning |
| transformers | 5.5.3 | AI models |
| openai | 2.0.0 | OpenAI API |
| openai-whisper | 20250625 | Speech recognition |
| sherpa-onnx | 1.13.0 | Wake word detection |
| lunar-python | 1.4.8 | Tính ngày âm lịch (Bazi) |
| cryptography | 46.0.2 | Mã hóa |
| pendulum | 3.1.0 | Xử lý thời gian |
| opencv-python | 4.12.0.88 | Xử lý ảnh |
| PyQt5 | 5.15.11 | Giao diện |
| pygame | 2.6.1 | Multimedia |
| paho-mqtt | 2.1.0 | MQTT |
| sounddevice | 0.5.5 | Audio I/O |
| yeelight | 0.7.16 | Điều khiển đèn |
| mutagen | 1.47.0 | Metadata nhạc |
| colorlog | 6.9.0 | Log màu sắc |
| mcp | 1.27.0 | MCP protocol |
| edge-tts | 7.2.7 | Text-to-Speech |
| llvmlite | 0.47.0 | JIT compiler |
| numba | 0.65.0 | Accelerator |
| pandas | 3.0.2 | Data analysis |
| sympy | 1.14.0 | Symbolic math |
| tinytuya | 1.18.0 | Tuya IoT |
| hf-xet | 1.4.3 | Hugging Face |
| huggingface-hub | 1.10.1 | Model hub |

## 💡 Cấu hình Desk Lamp

IP đèn: `192.168.1.14` (đã cấu hình trong `config/config.json`)

**Lệnh điều khiển:**
- "**小智 开灯**" - Bật đèn
- "**小智 关灯**" - Tắt đèn  
- "**小智 调亮一点**" - Tăng độ sáng
- "**小智 学习模式**" - Chế độ học tập
- "**小智 色温调到3000**" - Đặt nhiệt độ màu

## 🚀 Chạy ứng dụng

**Cách 1: Terminal**
```bash
cd /Users/dailuu/py-xiaozhi
source ../py_xiaozhi_env/bin/activate
python3 main.py
```

**Cách 2: Desktop Shortcut**
Double-click file `start_xiaozhi.command` trên Desktop

## 🔧 Khắc phục sự cố

### Lỗi thường gặp:

1. **ModuleNotFoundError: No module named 'XXX'**
   ```bash
   pip install XXX
   ```

2. **Desk lamp không hoạt động**
   - Kiểm tra IP trong `config/config.json`
   - Đảm bảo đèn bật "LAN Control"
   - Test: `python3 test_desk_lamp.py`

3. **Audio không hoạt động**
   ```bash
   pip install pyaudio sounddevice
   ```

4. **Wake word không nhận**
   ```bash
   pip install sherpa-onnx
   ```

## 📝 Ghi chú

- ✅ Đã sửa `add_common_tools()` để không bị lỗi silent
- ✅ Đã thêm từ khóa tiếng Trung vào tool descriptions
- ✅ Desk lamp tools (8 tools) hoạt động tốt
- ✅ Hỗ trợ Python 3.13

---
**Tác giả:** py-xiaozhi community  
**Ngôn ngữ:** Tiếng Việt / 中文  
**Phiên bản:** 2.0 (Đã sửa lỗi MCP tools)
