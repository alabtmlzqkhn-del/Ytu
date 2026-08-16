import time, redis, os, json, re, requests, asyncio, sys
from pyrogram import *

# 1. تعريف المتغيرات الأساسية فوراً
# ⚠️ حط توكن البوت الجديد (من BotFather) وآيديك الرقمي هنا بين علامتي التنصيص
to_config = ""
token = "8516176029:AAHCJPBLTRvWERxDD8ZVpUMmbcYRS0GkskU"
owner_id = "8065884629"
Dev_Neptune = token.split(':')[0]


# 2. محاولة الاتصال بـ Redis (مع محاولات إعادة لأن redis-server قد يحتاج وقت ليبدأ)
r = None
for _ in range(15):
    try:
        r = redis.Redis('localhost', decode_responses=True)
        r.ping()
        break
    except Exception:
        time.sleep(1)

if r is None:
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
    token = input('[+] Enter the bot token : ')
    Dev_Neptune = token.split(':')[0]
    owner_id = int(input('[+] Enter SUDO ID : '))
    r.set(f'{Dev_Neptune}botowner', owner_id)
    with open('information.py', 'w+') as www:
        www.write(f'token = "{token}"\nowner_id = {owner_id}')

print('''
10% 
███▒▒▒▒▒▒▒ ''')

# 4. تجهيز ملف الإعدادات
to_config = "import redis\nr = redis.Redis('localhost',decode_responses=True)\n"
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

with open('config.py', 'w+') as w:
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
