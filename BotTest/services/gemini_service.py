from io import BytesIO
from django.conf import settings
from google import genai
from google.genai import types
from PIL import Image

# 初始化 Gemini 客戶端
client = genai.Client(api_key=settings.GEMINI_API_KEY)

async def edit_image(image_bytes: bytes, prompt: str):
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
                # 儲存為臨時檔案
                temp_path = "temp/edited_image.png"
                edited_image.save(temp_path)
                return temp_path
        return None
    except Exception as e:
        print(f"圖片編輯失敗：{str(e)}")
        return None

async def create_image(prompt):
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
                # 儲存為臨時檔案
                temp_path = "temp/temp_created_image.png"
                image.save(temp_path)
                return temp_path
        return None
    except Exception as e:
        print(f"圖片生成失敗：{str(e)}")
        return None
