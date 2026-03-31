import asyncio
import os
from datetime import datetime, timedelta
from twscrape import API, gather
from twscrape.logger import set_log_level
import google.generativeai as genai
genai.configure(api_key=GEMINI_API_KEY)
import telegram
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

load_dotenv()

# ================== 設定 ==================
X_USERNAME = os.getenv("lmaongchi")
X_PASSWORD = os.getenv("Lmaongchi123@")
X_EMAIL = os.getenv("lmaongchi@gmail.com")

GEMINI_API_KEY = os.getenv("AIzaSyCHrDcXab742GW097ApwOx0c760t7hEBcM")
TELEGRAM_TOKEN = os.getenv("8700350043:AAEWenpl6_MJFLwsj9KZBp-wSaW80RQKRAE")
TELEGRAM_CHAT_ID = os.getenv("761195164")

# Gemini 新套件設定
genai.configure(api_key=GEMINI_API_KEY)

set_log_level("INFO")
api = API()
scheduler = AsyncIOScheduler()

# ================== 登入只做一次（重要修正） ==================
async def login_once():
    print("正在登入 X 帳號...")
    await api.pool.add_account(X_USERNAME, X_PASSWORD, X_EMAIL, X_EMAIL)
    await api.pool.login_all()
    print("✅ X 帳號登入成功")

async def fetch_and_send():
    print(f"[{datetime.now()}] 開始抓取最近 4 小時熱點...")
    
    since_time = (datetime.utcnow() - timedelta(hours=4)).strftime("%Y-%m-%d_%H:%M:%S_UTC")
    query = f"(crypto OR bitcoin OR ethereum OR solana OR ai OR grok OR xai OR llm OR 比特幣 OR 以太坊 OR 人工智慧) since:{since_time}"

    tweets = await gather(api.search(query, limit=50))

    if not tweets:
        print("這 4 小時沒有新熱點")
        return

    posts_text = "\n\n".join([
        f"作者: @{t.user.username}\n時間: {t.date}\n內容: {t.rawContent}\n曝光: {t.viewCount} | 讚: {t.likeCount}\n連結: {t.url}"
        for t in tweets
    ])

        print(f"抓到 {len(tweets)} 則，正在讓 Gemini 整理...")

    # Gemini 舊版穩定寫法
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-3-flash')
    prompt = f"""
你是 crypto 和 AI 領域的專業分析師。
請用繁體中文、條理分明的方式，把以下 X 推文整理成「Crypto & AI 每4小時熱點摘要」：

1. Top 5-8 則最重要熱點（每則附連結、曝光量、1-2句重點）
2. 最後加一句「潛在機會 / 風險提醒」

推文資料：
{posts_text}
"""

    response = model.generate_content(prompt)
    summary_text = response.text

    response = model.generate_content(prompt)
    summary_text = response.text

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=summary_text, parse_mode="HTML")
    print(f"[{datetime.now()}] ✅ 摘要已發送到 Telegram")

async def main():
    await login_once()                    # 啟動時只登入一次
    await fetch_and_send()                # 第一次立即執行
    scheduler.add_job(fetch_and_send, 'interval', hours=4)
    scheduler.start()
    print("🤖 Bot 已啟動，每 4 小時自動執行...")

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
