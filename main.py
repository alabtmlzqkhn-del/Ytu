import os
import sys
import time
import redis
import requests
from pyrogram import Client, idle


# ==============================
# إعدادات البوت
# ==============================

TOKEN = "8516176029:AAEiCQLVCf1HYoB4WOgwdK_cCAwsJXGyR2g"
OWNER_ID = 8065884629

REDIS_URL = "redis://@redis.railway.internal:6379"


# ==============================
# التحقق من الإعدادات
# ==============================

if not TOKEN or ":" not in TOKEN:
    print("❌ توكن البوت غير صحيح")
    sys.exit(1)

Dev_Neptune = TOKEN.split(":")[0]


# ==============================
# Redis
# ==============================

try:
    r = redis.Redis.from_url(
        REDIS_URL,
        decode_responses=True
    )

    r.ping()
    print("✅ Redis connected")

except Exception as e:
    print("❌ Redis connection failed:")
    print(e)
    sys.exit(1)


# ==============================
# إنشاء information.py
# ==============================

try:
    with open("information.py", "w", encoding="utf-8") as f:
        f.write(f'token = "{TOKEN}"\n')
        f.write(f"owner_id = {OWNER_ID}\n")

except Exception as e:
    print("⚠️ Could not create information.py:", e)


# ==============================
# إعداد config.py
# ==============================

try:
    response = requests.get(
        f"https://api.telegram.org/bot{TOKEN}/getMe",
        timeout=15
    )

    data = response.json()

    if data.get("ok"):
        username = data["result"].get("username", "unknown")
    else:
        username = "unknown"

except Exception as e:
    print("⚠️ Failed to get bot username:", e)
    username = "unknown"


config = f'''import redis
import os

r = redis.Redis.from_url(
    "{REDIS_URL}",
    decode_responses=True
)

token = "{TOKEN}"
Dev_Neptune = token.split(":")[0]
sudo_id = {OWNER_ID}
owner_id = {OWNER_ID}

botUsername = "{username}"

from kvsqlite.sync import Client as DB

ytdb = DB("ytdb.sqlite")
sounddb = DB("sounddb.sqlite")
wsdb = DB("wsdb.sqlite")
'''


try:
    with open("config.py", "w", encoding="utf-8") as f:
        f.write(config)

    print("✅ config.py created")

except Exception as e:
    print("❌ Failed to create config.py:", e)
    sys.exit(1)


# ==============================
# Redis بيانات البوت
# ==============================

try:

    if not r.get(f"{Dev_Neptune}:botkey"):
        r.set(f"{Dev_Neptune}:botkey", "⇜")

    if not r.get(f"{Dev_Neptune}botname"):
        r.set(f"{Dev_Neptune}botname", "Jack")

    r.set(f"{Dev_Neptune}botowner", OWNER_ID)

    print("✅ Redis data initialized")

except Exception as e:
    print("❌ Redis data error:")
    print(e)
    sys.exit(1)


# ==============================
# تشغيل Pyrogram
# ==============================

try:

    app = Client(
        f"{Dev_Neptune}Neptune",
        api_id=28850159,
        api_hash="09a3e7d212b434aec973ad5ea10d8ec6",
        bot_token=TOKEN,
        plugins={
            "root": "Plugins"
        }
    )

    print("🚀 Starting Jack Bot...")

    app.start()

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("• SOURCE JACK IS UP")
    print("• BOT IS RUNNING")
    print("• REDIS CONNECTED")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━")

    idle()

except Exception as e:

    print("❌ BOT START ERROR:")
    print(e)

    try:
        app.stop()
    except:
        pass

    sys.exit(1)
