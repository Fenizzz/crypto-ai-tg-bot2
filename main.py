import asyncio
from datetime import datetime, timedelta

from twscrape import API, gather
from twscrape.logger import set_log_level
from google import genai
import telegram
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# ====================== 變數設定 ======================
X_USERNAME = "lmaongchi"
X_PASSWORD = "Lmaongchi123@"
X_EMAIL    = "lmaongchi@gmail.com"

GEMINI_API_KEY = "AIzaSyCHrDcXab742GW097ApwOx0c760t7hEBcM"
TELEGRAM_TOKEN = "8700350043:AAEWenpl6_MJFLwsj9KZBp-wSaW80RQKRAE"
TELEGRAM_CHAT_ID = "761195164"

# ====================== Debug 檢查 ======================
print("🔍 DEBUG - 目前使用的變數:")
print(f"X_USERNAME     = '{X_USERNAME}'")
print(f"X_PASSWORD     = {'✅ 已填寫' if X_PASSWORD else '❌ 空的！'}")
print(f"X_EMAIL        = '{X_EMAIL}'")
print(f"GEMINI_API_KEY = {'✅ 已填寫' if GEMINI_API_KEY else '❌ 空的！'}")
print(f"TELEGRAM_TOKEN = {'✅ 已填寫' if TELEGRAM_TOKEN else '❌ 空的！'}")
print("-----------------------------------")

if not X_USERNAME or not X_PASSWORD or not GEMINI_API_KEY or not TELEGRAM_TOKEN:
    raise ValueError("❌ 某些必要變數是空的，請確認已正確填入！")

# ====================== Gemini 設定 ======================
client = genai.Client(api_key=GEMINI_API_KEY)

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
    query = f"(crypto OR bitcoin OR ethereum OR solana OR ai OR grok OR xai OR llm OR 比特幣 OR 以太坊 OR 人工智慧) since:{since_time}"

    tweets = await gather(api.search(query, limit=40))

    if not tweets:
        print("這 4 小時沒有新熱點")
        return

    posts_text = "\n\n".join([
        f"作者: @{t.user.username}\n時間: {t.date}\n內容: {t.rawContent}\n曝光: {t.viewCount:,} | 讚: {t.likeCount}\n連結: {t.url}"
        for t in tweets[:30]
    ])

    print(f"抓到 {len(tweets)} 則推文，正在讓 Gemini 整理...")

    prompt = f"""
你是 Crypto 和 AI 領域的專業分析師，請用繁體中文整理以下最近 4 小時的 X 推文。

請輸出以下格式：
**Crypto & AI 每4小時熱點摘要**（{datetime.now().strftime('%Y-%m-%d %H:%M')}）

1. **Top 熱點**（挑選 5-8 則最重要）
   - [曝光量] 簡短重點 + 連結
2. **潛在機會 / 風險提醒**

推文資料：
{posts_text}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        summary_text = response.text
    except Exception as e:
        summary_text = f"❌ Gemini 整理失敗：{str(e)}\n\n抓到推文數：{len(tweets)}"

    # 發送到 Telegram
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=summary_text,
            parse_mode="HTML"
        )
        print(f"[{datetime.now()}] ✅ 摘要已成功發送到 Telegram")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Telegram 發送失敗：{str(e)}")

async def main():
    await login_once()
    await fetch_and_send()
    scheduler.add_job(fetch_and_send, 'interval', hours=4)
    scheduler.start()
    print("🤖 Bot 已啟動，每 4 小時自動執行一次...")

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
