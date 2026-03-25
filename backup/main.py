import os
import re
import time
import uvicorn
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = FastAPI(title="Gemini Scraper API", version="1.0")

# --- Model cho Request (Giống OpenAI) ---
class ChatMessage(BaseModel):
    role: str # user, assistant
    content: str

class ChatRequest(BaseModel):
    model: Optional[str] = "gemini-web"
    messages: List[ChatMessage]

# --- Logic Scraper Core ---
def get_gemini_content(user_query: str):
    chrome_options = Options()
    profile_path = os.path.join(os.getcwd(), "gemini_automation_profile")
    chrome_options.add_argument(f"--user-data-dir={profile_path}")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--headless=new") # Chạy ngầm cho API đỡ tốn tài nguyên

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 30)

    try:
        driver.get("https://gemini.google.com/app")
        
        # Tìm ô nhập liệu
        prompt_box = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='textbox']")))

        # Prompt đặc biệt để trích xuất sạch
        full_prompt = f'Hãy thực hiện: "1. Viết START_COPY lên đầu. Viết END_COPY ở dưới cùng. 2. {user_query}"'
        prompt_box.send_keys(full_prompt)
        time.sleep(1)
        prompt_box.send_keys(Keys.ENTER)
        
        # Chờ AI trả lời (có thể tối ưu bằng cách check sự xuất hiện của END_COPY)
        time.sleep(15)

        page_text = driver.find_element(By.TAG_NAME, "body").text
        pattern = r"START_COPY(.*?)\bEND_COPY"
        matches = re.findall(pattern, page_text, re.DOTALL)

        if matches:
            content = max(matches, key=len).strip()
            # Lưu log nội bộ cho Medipath
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")[:-3]
            with open(f"{timestamp}.txt", "w", encoding="utf-8") as f:
                f.write(content)
            return content
        return None
    finally:
        driver.quit()

# --- API Endpoints ---

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    # Lấy nội dung tin nhắn cuối cùng từ danh sách messages
    user_prompt = request.messages[-1].content
    
    print(f"Đang xử lý request cho: {user_prompt[:50]}...")
    result = get_gemini_content(user_prompt)
    
    if not result:
        raise HTTPException(status_code=500, detail="Không thể lấy nội dung từ Gemini Web.")

    # Trả về cấu trúc giống hệt OpenAI để dễ tích hợp
    return {
        "id": f"chatcmpl-{int(time.time())}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": request.model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": result
                },
                "finish_reason": "stop"
            }
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)