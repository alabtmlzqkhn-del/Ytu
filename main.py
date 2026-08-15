import os
import time, redis, os, json, re, requests, asyncio, sys
from pyrogram import *

# 1. تعريف المتغيرات الأساسية فوراً
to_config = "" 
token = os.getenv('BOT_TOKEN') or input('Bot Token: ')
owner_id = os.getenv('OWNER_ID') or input('Owner ID: ')
Dev_Neptune = token.split(':')[0]


# 2. محاولة الاتصال بـ Redis
try:
    r = redis.Redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'), decode_responses=True)
    r.ping()
except:
    print("[-] Error: Redis is not running. Please run: sudo systemctl start redis-server")
    sys.exit()

print('''
Loading…
█▒▒▒▒▒▒▒▒▒''')

# 3. جلب البيانات
try:
    from information import *
    Dev_Neptune = token.split(':')[0]
    r.set(f'{Dev_Neptune}botowner', owner_id)
except:
    token = input ('[+] Enter the bot token : ')
    Dev_Neptune = token.split(':')[0]
    owner_id = int(input('[+] Enter SUDO ID : '))
    r.set(f'{Dev_Neptune}botowner', owner_id)
    with open ('information.py','w+') as www:
        www.write(f'token = "{token}"\nowner_id = {owner_id}')

print('''
10% 
███▒▒▒▒▒▒▒ ''')

# 4. تجهيز ملف الإعدادات
to_config = "import redis, os\nr = redis.Redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'), decode_responses=True)\n"
to_config += f"token = '{token}'\n"
to_config += f"Dev_Neptune = token.split(':')[0]\n"
to_config += f"sudo_id = {owner_id}\n"

# جلب اليوزر نيم
try:
    username = requests.get(f"https://api.telegram.org/bot{token}/getMe").json()["result"]["username"]
except:
    username = "unknown"

to_config += f"botUsername = '{username}'\n"
to_config += "from kvsqlite.sync import Client as DB\n"
to_config += "ytdb = DB('ytdb.sqlite')\n"
to_config += "sounddb = DB('sounddb.sqlite')\n"
to_config += "wsdb = DB('wsdb.sqlite')"

print('''
30% 
█████▒▒▒▒▒ ''')

with open('config.py','w+') as w:
    w.write(to_config)

print('''
50% 
███████▒▒▒ ''')

# 5. تشغيل التطبيق
app = Client(f'{Dev_Neptune}Neptune', 28850159, '09a3e7d212b434aec973ad5ea10d8ec6', bot_token=token, plugins={"root": "Plugins"})

if not r.get(f'{Dev_Neptune}:botkey'): r.set(f'{Dev_Neptune}:botkey', '⇜')
if not r.get(f'{Dev_Neptune}botname'): r.set(f'{Dev_Neptune}botname', 'Jack')

app.start()
print("• 𝖲𝖮𝖴𝖱𝖢𝖤 𝖩𝖠𝖢𝖪 𝖨𝖲 𝖴𝖯 𝖠𝖭𝖣 𝖱𝖴𝖭𝖭I𝖭𝖦 ...")
print('100% \n██████████')
idle()
