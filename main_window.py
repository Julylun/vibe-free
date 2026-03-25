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

app = FastAPI(title="Gemini Scraper API - Medipath Final", version="1.2")

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: Optional[str] = "gemini-web"
    messages: List[ChatMessage]

def get_gemini_content(user_query: str):
    chrome_options = Options()
    profile_path = os.path.join(os.getcwd(), "gemini_automation_profile")
    chrome_options.add_argument(f"--user-data-dir={profile_path}")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 40)

    try:
        driver.get("https://gemini.google.com/app")
        
        # 1. Tìm ô nhập liệu
        prompt_box = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='textbox']")))

        # 2. Gửi Query
        full_prompt = f'Hãy thực hiện: "1. Viết START_COPY lên đầu. Viết END_COPY ở dưới cùng. 2. {user_query}"'
        prompt_box.send_keys(full_prompt)
        time.sleep(1)
        prompt_box.send_keys(Keys.ENTER)
        
        print(f"[{datetime.now()}] Đang xử lý câu hỏi...")

        # 3. CHỜ ĐỢI CÂU TRẢ LỜI (Đợi cho đến khi phần tử phản hồi của AI xuất hiện)
        # Gemini thường dùng tag <model-response> cho câu trả lời
        time.sleep(15) # Đợi AI gõ xong

        # 4. CHIẾN THUẬT MỚI: Chỉ tìm trong các khối model-response
        # Cách này loại bỏ hoàn toàn việc quét nhầm vào ô Chat hay ô Search
        responses = driver.find_elements(By.TAG_NAME, "model-response")
        
        if not responses:
            # Nếu không tìm thấy tag model-response, thử tìm theo class phổ biến
            responses = driver.find_elements(By.CLASS_NAME, "message-content")

        if responses:
            # Lấy câu trả lời cuối cùng trên trang (là câu mới nhất)
            latest_response_text = responses[-1].text
            
            # 5. Dùng Regex để cắt nội dung bên trong START_COPY và END_COPY
            pattern = r"START_COPY(.*?)\bEND_COPY"
            match = re.search(pattern, latest_response_text, re.DOTALL)

            if match:
                content = match.group(1).strip()
                
                # Lưu log theo định dạng yêu cầu của Luan
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")[:-3]
                with open(f"{timestamp}.txt", "w", encoding="utf-8") as f:
                    f.write(content)
                return content
            else:
                # Nếu tìm thấy khối response nhưng AI không viết START/END (thường do AI lười)
                # Trả về toàn bộ text của khối đó luôn để tránh bị rỗng
                return latest_response_text.strip()
        
        return None
    except Exception as e:
        print(f"Lỗi: {e}")
        return None
    finally:
        driver.quit()

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    user_prompt = request.messages[-1].content
    print(f"Request nhận được: {user_prompt[:50]}...")
    
    result = get_gemini_content(user_prompt)
    
    if not result:
        raise HTTPException(status_code=500, detail="Lỗi trích xuất dữ liệu.")

    return {
        "id": f"chatcmpl-{int(time.time())}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": request.model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": result},
                "finish_reason": "stop"
            }
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)