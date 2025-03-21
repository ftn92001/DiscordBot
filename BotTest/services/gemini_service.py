from io import BytesIO
from django.conf import settings
from google import genai
from google.genai import types
from PIL import Image
import os
import uuid
from datetime import datetime

# 初始化 Gemini 客戶端
client = genai.Client(api_key=settings.GEMINI_API_KEY)

def get_temp_path(user_id: str, prefix: str) -> str:
    # 建立使用者專屬目錄
    user_dir = f"temp/{user_id}"
    os.makedirs(user_dir, exist_ok=True)

    # 產生唯一檔案名稱
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    filename = f"{prefix}_{timestamp}_{unique_id}.png"

    return os.path.join(user_dir, filename)

async def edit_image(image_bytes: bytes, prompt: str, user_id: str):
    try:
        # 將bytes轉換為PIL Image
        image = Image.open(BytesIO(image_bytes))

        response = client.models.generate_content(
            model="models/gemini-2.0-flash-exp",
            contents=[
                f"請根據以下指令修改圖片: {prompt}",
                image
            ],
            config=types.GenerateContentConfig(
                response_modalities=['Text', 'Image']
            )
        )

        # 從回應中提取圖片
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                # 將圖片資料轉換為 PIL Image
                edited_image = Image.open(BytesIO(part.inline_data.data))
                # 儲存為使用者專屬的臨時檔案
                temp_path = get_temp_path(user_id, "edited")
                edited_image.save(temp_path)
                return temp_path
        return None
    except Exception as e:
        print(f"圖片編輯失敗：{str(e)}")
        return None

async def create_image(prompt: str, user_id: str):
    try:
        response = client.models.generate_content(
            model="models/gemini-2.0-flash-exp",
            contents=f"請根據以下指令生成圖片: {prompt}",
            config=types.GenerateContentConfig(
                response_modalities=['Text', 'Image']
            )
        )

        # 從回應中提取圖片
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                # 將圖片資料轉換為 PIL Image
                image = Image.open(BytesIO(part.inline_data.data))
                # 儲存為使用者專屬的臨時檔案
                temp_path = get_temp_path(user_id, "created")
                image.save(temp_path)
                return temp_path
        return None
    except Exception as e:
        print(f"圖片生成失敗：{str(e)}")
        return None
