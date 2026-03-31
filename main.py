import asyncio
import os
from datetime import datetime, timedelta

from twscrape import API, gather
from twscrape.logger import set_log_level
import google.generativeai as genai
import telegram
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

# ====================== 載入 .env (優先) ======================
load_dotenv(override=True)  # override=True 讓 .env 覆蓋 Railway 變數

# ====================== 環境變數 ======================
X_USERNAME = os.getenv("lmaongchi")
X_PASSWORD = os.getenv("Lmaongchi123@")
X_EMAIL = os.getenv("lmaongchi@gmail.com")

GEMINI_API_KEY = os.getenv("AIzaSyCHrDcXab742GW097ApwOx0c760t7hEBcM")
TELEGRAM_TOKEN = os.getenv("8700350043:AAEWenpl6_MJFLwsj9KZBp-wSaW80RQKRAE")
TELEGRAM_CHAT_ID = os.getenv("761195164")

# ====================== 強力 Debug ======================
print("🔍 DEBUG - 環境變數檢查 (.env + Railway):")
print(f"X_USERNAME     = '{X_USERNAME}'")
print(f"X_PASSWORD     = {'✅ 已設定' if X_PASSWORD else '❌ 空的！'}")
print(f"X_EMAIL        = '{X_EMAIL}'")
print(f"GEMINI_API_KEY = {'✅ 已設定' if GEMINI_API_KEY else '❌ 空的！'}")
print(f"TELEGRAM_TOKEN = {'✅ 已設定' if TELEGRAM_TOKEN else '❌ 空的！'}")
print("-----------------------------------")

if not all([X_USERNAME, X_PASSWORD, X_EMAIL, GEMINI_API_KEY, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
    raise ValueError("❌ 缺少必要環境變數！請確認 .env 檔案或 Railway Variables 是否正確")

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
    print(f"[{datetime.now()}] 開始抓取最近 4 小時 Crypto & AI 熱點...")

    since_time = (datetime.utcnow() - timedelta(hours=4)).strftime("%Y-%m-%d_%H:%M:%S_UTC")
    query = f"(crypto OR bitcoin OR ethereum OR solana OR ai OR grok OR xai OR llm OR 比特幣 OR 以太坊 OR 加密貨幣 OR 人工智慧) since:{since_time} min_faves:5"  # 可再調整

    tweets = await gather(api.search(query, limit=40))

    if not tweets:
        print("這 4 小時沒有符合條件的熱點")
        return

    posts_text = "\n\n".join([
        f"作者: @{t.user.username}\n時間: {t.date}\n內容: {t.rawContent}\n曝光: {t.viewCount:,} | 讚: {t.likeCount}\n連結: {t.url}"
        for t in tweets
    ])

    print(f"抓到 {len(tweets)} 則推文，正在讓 Gemini 整理成繁體中文摘要...")

    model = genai.GenerativeModel('gemini-1.5-flash')   # 推薦使用較穩定的 1.5-flash

    prompt = f"""你是專業的 Crypto 和 AI 分析師，請用繁體中文、條理清晰的方式整理以下 X 推文成「Crypto & AI 每4小時熱點摘要」：

1. Top 5-8 則最重要熱點（每則包含：重點摘要、曝光量、連結）
2. 最後加一段「潛在機會 / 風險提醒」

推文資料：
{posts_text}
"""

    response = model.generate_content(prompt)
    summary_text = response.text

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=summary_text,
        parse_mode="HTML"
    )
    print(f"[{datetime.now()}] ✅ 摘要已成功發送到 Telegram")

async def main():
    await login_once()
    await fetch_and_send()                    # 先跑一次測試
    scheduler.add_job(fetch_and_send, 'interval', hours=4)
    scheduler.start()
    print("🤖 Bot 已啟動，每 4 小時自動執行一次... 保持運行中")

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
