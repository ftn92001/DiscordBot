# 安裝套件
`pip install -r requirement.txt`

# 設定環境變數
`cp .env.example .env`

在`.env`檔案加上自己的DISCORD_TOKEN

# 執行migrate建立資料庫欄位
`python manage.py migrate`

# 執行Discord Bot
`python manage.py discord_bot`
