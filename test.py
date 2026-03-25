from openai import OpenAI

client = OpenAI(
    api_key="anything",          # API key giả
    base_url="http://localhost:8000/v1" # Trỏ về API FastAPI của bạn
)

# Thêm Instruction vào danh sách messages
response = client.chat.completions.create(
    model="gemini-web",
    messages=[
        {
            "role": "system", 
            "content": "Bạn là bác sĩ chuyên gia của Medipath. Hãy trả lời cực kỳ chuyên nghiệp, ngắn gọn và luôn kết thúc bằng câu: Chúc bạn sớm khỏe lại!"
        },
        {
            "role": "user", 
            "content": "Tôi cảm thấy hơi chóng mặt khi đứng dậy đột ngột."
        }
    ]
)

print("-" * 30)
print("Câu trả lời từ Medipath AI:")
print(response.choices[0].message.content)
print("-" * 30)