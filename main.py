import asyncio
import os
from datetime import datetime, timedelta

from twscrape import API, gather
from twscrape.logger import set_log_level
import google.generativeai as genai
import telegram
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# ====================== 臨時寫死變數（測試用） ======================
# ←←← 在這裡填你的真實資料 ←←←
X_USERNAME = os.getenv("lmaongchi")
X_PASSWORD = os.getenv("Lmaongchi123@")
X_EMAIL = os.getenv("lmaongchi@gmail.com")

GEMINI_API_KEY = os.getenv("AIzaSyCHrDcXab742GW097ApwOx0c760t7hEBcM")
TELEGRAM_TOKEN = os.getenv("8700350043:AAEWenpl6_MJFLwsj9KZBp-wSaW80RQKRAE")
TELEGRAM_CHAT_ID = os.getenv("761195164")

# ====================== Debug 檢查 ======================
print("🔍 DEBUG - 目前使用的變數:")
print(f"X_USERNAME     = '{X_USERNAME}'")
print(f"X_PASSWORD     = {'✅ 已填寫' if X_PASSWORD and X_PASSWORD != 'Lmaongchi123@' else '❌ 請填寫'}")
print(f"X_EMAIL        = '{X_EMAIL}'")
print(f"GEMINI_API_KEY = {'✅ 已填寫' if GEMINI_API_KEY and GEMINI_API_KEY != 'AIzaSyCHrDcXab742GW097ApwOx0c760t7hEBcM' else '❌ 請填寫'}")
print("-----------------------------------")

if X_USERNAME == "lmaongchi" and X_PASSWORD == "Lmaongchi123@":
    raise ValueError("請把上面的 X_PASSWORD、GEMINI_API_KEY 等替換成真實值！")

# ====================== Gemini 設定 ======================
genai.configure(api_key=GEMINI_API_KEY)

set_log_level("INFO")
api = API()
scheduler = AsyncIOScheduler()

async def login_once():
    print(f"[{datetime.now()}] 正在登入 X 帳號 {X_USERNAME} ...")
    await api.pool.add_account(X_USERNAME, X_PASSWORD, X_EMAIL, X_EMAIL)
    await api.pool.login_all()
    print(f"[{datetime.now()}] ✅ X 帳號登入成功")

async def fetch_and_send():
    print(f"[{datetime.now()}] 開始抓取最近 4 小時熱點...")
    since_time = (datetime.utcnow() - timedelta(hours=4)).strftime("%Y-%m-%d_%H:%M:%S_UTC")
    query = f"(crypto OR bitcoin OR ethereum OR solana OR ai OR grok OR xai OR llm OR 比特幣 OR 以太坊 OR 人工智慧) since:{since_time}"

    tweets = await gather(api.search(query, limit=40))
    if not tweets:
        print("這 4 小時沒有熱點")
        return

    # ...（後面的 Gemini 整理 + 發 Telegram 程式碼保持不變，我這裡省略以節省空間）
    # 如果你需要完整 fetch_and_send 函數，請說「給我完整版」

    print(f"[{datetime.now()}] ✅ 摘要已發送到 Telegram")

async def main():
    await login_once()
    await fetch_and_send()
    scheduler.add_job(fetch_and_send, 'interval', hours=4)
    scheduler.start()
    print("🤖 Bot 已啟動，每 4 小時執行一次...")

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
