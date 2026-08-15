import os
import sys
import redis
import requests
from pyrogram import Client, idle


# ==============================
# إعدادات البوت
# ==============================

TOKEN = os.getenv("8516176029:AAEnZZ9tO8EfPTzrc1TXnE1QcniuxYwcaqQ")
OWNER_ID = os.getenv("8065884629")

# إذا ما موجودة Variables، يحاول يقرأ information.py
if not TOKEN or not OWNER_ID:
    try:
        import information

        TOKEN = TOKEN or getattr(information, "token", None)
        OWNER_ID = OWNER_ID or getattr(information, "owner_id", None)

    except Exception:
        pass


if not TOKEN:
    print("❌ Bot token غير موجود")
    sys.exit(1)


if not OWNER_ID:
    print("❌ Owner ID غير موجود")
    sys.exit(1)


try:
    OWNER_ID = int(OWNER_ID)

except ValueError:
    print("❌ OWNER_ID يجب أن يكون رقم")
    sys.exit(1)


Dev_Neptune = TOKEN.split(":")[0]


# ==============================
# Redis Railway
# ==============================

REDIS_URL = os.getenv("redis://default:nFqeVQriqnXpFInOzCYxSvzHKreFWKvz@redis.railway.internal:6379")

if not REDIS_URL:
    print("❌ REDIS_URL غير موجود في Railway")
    sys.exit(1)


print("🔄 Connecting to Redis...")


try:

    r = redis.Redis.from_url(
        REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=10,
        socket_timeout=10,
        health_check_interval=30
    )

    r.ping()

    print("✅ Redis connected")


except Exception as e:

    print("❌ Redis connection failed:")
    print(type(e).__name__, repr(e))

    sys.exit(1)


# ==============================
# جلب Username البوت
# ==============================

username = "unknown"

try:

    response = requests.get(
        f"https://api.telegram.org/bot{TOKEN}/getMe",
        timeout=15
    )

    data = response.json()

    if data.get("ok"):
        username = data["result"].get(
            "username",
            "unknown"
        )

except Exception as e:

    print(
        "⚠️ Failed to get bot username:",
        type(e).__name__
    )


# ==============================
# إنشاء config.py
# ==============================

try:

    config = f'''import os
import redis

r = redis.Redis.from_url(
    os.getenv("REDIS_URL"),
    decode_responses=True
)

token = {TOKEN!r}

Dev_Neptune = token.split(":")[0]

sudo_id = {OWNER_ID}

owner_id = {OWNER_ID}

botUsername = {username!r}

from kvsqlite.sync import Client as DB

ytdb = DB("ytdb.sqlite")

sounddb = DB("sounddb.sqlite")

wsdb = DB("wsdb.sqlite")
'''

    with open(
        "config.py",
        "w",
        encoding="utf-8"
    ) as f:

        f.write(config)

    print("✅ config.py created")


except Exception as e:

    print("❌ config.py error:")
    print(type(e).__name__, repr(e))

    sys.exit(1)


# ==============================
# Redis بيانات البوت
# ==============================

try:

    if not r.get(
        f"{Dev_Neptune}:botkey"
    ):

        r.set(
            f"{Dev_Neptune}:botkey",
            "⇜"
        )


    if not r.get(
        f"{Dev_Neptune}botname"
    ):

        r.set(
            f"{Dev_Neptune}botname",
            "Jack"
        )


    r.set(
        f"{Dev_Neptune}botowner",
        str(OWNER_ID)
    )


    print("✅ Redis data initialized")


except Exception as e:

    print("❌ Redis data initialization failed:")

    print(
        type(e).__name__,
        repr(e)
    )

    sys.exit(1)


# ==============================
# تشغيل Pyrogram
# ==============================

app = None


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


    print(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

    print(
        "✅ SOURCE JACK IS UP"
    )

    print(
        "✅ BOT IS RUNNING"
    )

    print(
        "✅ REDIS CONNECTED"
    )

    print(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )


    idle()


except Exception as e:

    print("❌ BOT START ERROR:")

    print(
        type(e).__name__,
        repr(e)
    )

    sys.exit(1)


finally:

    if app:

        try:
            app.stop()

        except Exception:
            pass
