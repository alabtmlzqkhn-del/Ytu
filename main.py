import time, redis, os, json, re, requests, asyncio, sys
from pyrogram import *

# 1. إعدادات البوت والمالك
token = "8516176029:AAFZFmZKCRKW7pXcw77mHQtHrUAUk6CWVig"
owner_id = 8065884629
Dev_Neptune = token.split(':')[0]

# 2. الاتصال المباشر بـ Redis (بياناتك المباشرة)
try:
    r = redis.Redis(
        host='redis-1-staging-icy-cord.cloud.layerbase.dev',
        port=6379,
        password='VbjnxTMjdotyhDbulOLA4tnt',
        ssl=True,
        decode_responses=True
    )
    r.ping()
    print("[+] Connected to Redis successfully!")
except Exception as e:
    print(f"[-] Error connecting to Redis: {e}")
    sys.exit()

print('''
Loading…
█▒▒▒▒▒▒▒▒▒''')

# 3. حفظ بيانات المالك في Redis و إنشاء ملف information.py تلقائياً
r.set(f'{Dev_Neptune}botowner', owner_id)
with open('information.py', 'w+') as www:
    www.write(f'token = "{token}"\nowner_id = {owner_id}')

print('''
10% 
███▒▒▒▒▒▒▒ ''')

# 4. إنشاء ملف config.py تلقائياً مع بيانات Redis المباشرة
to_config = f"""import redis
r = redis.Redis(
    host='redis-1-staging-icy-cord.cloud.layerbase.dev',
    port=6379,
    password='VbjnxTMjdotyhDbulOLA4tnt',
    ssl=True,
    decode_responses=True
)
token = '{token}'
Dev_Neptune = token.split(':')[0]
sudo_id = {owner_id}
"""

# جلب معرف البوت (Username)
try:
    username = requests.get(f"https://api.telegram.org/bot{token}/getMe").json()["result"]["username"]
except Exception:
    username = "unknown"

to_config += f"botUsername = '{username}'\n"
to_config += "from kvsqlite.sync import Client as DB\n"
to_config += "ytdb = DB('ytdb.sqlite')\n"
to_config += "sounddb = DB('sounddb.sqlite')\n"
to_config += "wsdb = DB('wsdb.sqlite')"

print('''
30% 
█████▒▒▒▒▒ ''')

with open('config.py', 'w+') as w:
    w.write(to_config)

print('''
50% 
███████▒▒▒ ''')

# 5. تشغيل البوت
app = Client(
    f'{Dev_Neptune}Neptune',
    api_id=28850159,
    api_hash='09a3e7d212b434aec973ad5ea10d8ec6',
    bot_token=token,
    plugins={"root": "Plugins"}
)

if not r.get(f'{Dev_Neptune}:botkey'): 
    r.set(f'{Dev_Neptune}:botkey', '⇜')

if not r.get(f'{Dev_Neptune}botname'): 
    r.set(f'{Dev_Neptune}botname', 'fadi')

app.start()
print("• SOURCE FADI IS UP AND RUNNING ...")
print('100% \n██████████')
idle()
