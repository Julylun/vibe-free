FROM python:3.11-slim

# 1. Cài đặt các thư viện hệ thống cần thiết
# Đã sửa lỗi apt-key not found bằng cách dùng gpg --dearmor
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    libnss3 \
    libfontconfig1 \
    libgbm1 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    --no-install-recommends \
    && curl -fSsL https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor | tee /usr/share/keyrings/google-chrome.gpg > /dev/null \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 2. Thiết lập thư mục làm việc
WORKDIR /app

# 3. Cài đặt dependencies Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy mã nguồn (main.py)
COPY . .

# 5. Tạo thư mục profile
RUN mkdir -p /app/gemini_automation_profile

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]