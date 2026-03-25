# Gemini API (OpenAI Standard)

Dự án cung cấp một API trung gian (Proxy) giúp bạn sử dụng Google Gemini Web hoàn toàn miễn phí thông qua giao thức chuẩn của OpenAI.  

---

## 📁 Cấu trúc tệp tin

- **main_window.py**: Chạy trên Windows (có giao diện) để đăng nhập và tạo thư mục Profile (Cookies).
- **main.py**: Chạy trên Docker/Linux Server (Headless) để phục vụ API.
- **gemini_automation_profile/**: Thư mục chứa session đăng nhập (được tạo ra sau khi chạy `main_window.py`).

---

## 🚀 Hướng dẫn cài đặt & Sử dụng

### 🔹 Bước 1: Lấy Session đăng nhập (Trên Windows)

Vì Gemini Web yêu cầu đăng nhập Google, bạn cần tạo một Profile "sạch" có chứa Cookies trên máy cá nhân trước khi đưa lên Server.

**Yêu cầu:**
- Đã cài đặt Chrome
- Đã cài Python

**Thực hiện:**
```bash
python main_window.py
````

* Một cửa sổ Chrome sẽ hiện ra.
* Đăng nhập tài khoản Google vào Gemini.
* Sau khi vào được giao diện chat → tắt trình duyệt và dừng script.

📌 Kết quả:
Thư mục `gemini_automation_profile` sẽ được tạo trong project.

---

### 🔹 Bước 2: Triển khai API với Docker (Trên Server Linux / Arch Linux)

1. Nén toàn bộ project (bao gồm thư mục profile).
2. Upload lên server.

**Cấu hình Docker Compose:**

* Đảm bảo file `docker-compose.yml` đã mount thư mục profile.

**Khởi chạy:**

```bash
docker-compose up -d --build
```

**Kiểm tra:**

* Truy cập: `http://<IP-Server>:8000/docs`
* Swagger UI sẽ hiển thị.

---

## 🛠 Cách kết nối với ứng dụng khác

API này tuân thủ chuẩn OpenAI, có thể dùng với SDK hoặc các ứng dụng chat.

**Cấu hình:**

* **Base URL:** `http://<IP-Server>:8000/v1`
* **API Key:** anything (không kiểm tra key)
* **Model:** `gemini-web`

---

### 📌 Ví dụ gọi API bằng Python (Hỗ trợ System Instruction)

```python
from openai import OpenAI

client = OpenAI(
    api_key="secret",
    base_url="http://localhost:8000/v1"
)

response = client.chat.completions.create(
    model="gemini-web",
    messages=[
        {
            "role": "system", 
            "content": "Bạn là bác sĩ chuyên gia của. Hãy trả lời chuyên nghiệp và ngắn gọn."
        },
        {
            "role": "user", 
            "content": "Triệu chứng sốt xuất huyết là gì?"
        }
    ]
)

print(response.choices[0].message.content)
```

---

## ⚠️ Lưu ý quan trọng

* **Tốc độ:**
  Do sử dụng scraping, mỗi request mất khoảng **15–20 giây**.

* **Quyền hạn (Linux):**

```bash
chmod -R 777 gemini_automation_profile
```

* **Trình duyệt:**
  Không mở Chrome thủ công bằng profile này khi script đang chạy để tránh lỗi `SessionNotCreated`.

---

## ✅ Tổng kết

* Tạo session trên Windows
* Upload profile lên server
* Chạy Docker để expose API
* Kết nối như OpenAI API
