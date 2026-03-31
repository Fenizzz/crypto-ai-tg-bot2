import asyncio
import os
from datetime import datetime, timedelta

from twscrape import API, gather
from twscrape.logger import set_log_level
from google import genai  # ← 新版 Gemini SDK
import telegram
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# ====================== 臨時寫死變數（測試用） ======================
# ←←← 確認這些值正確 ←←←
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

# ====================== Gemini 設定（新版 SDK） ======================
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

    since_time = (datetime.utcnow() - timedelta(hours=4)).strftime("%
