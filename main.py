import os
import time, redis, os, json, re, requests, asyncio, sys
from pyrogram import *

# 1. تعريف المتغيرات الأساسية فوراً
to_config = "" 
token = os.getenv('8516176029:AAEiCQLVCf1HYoB4WOgwdK_cCAwsJXGyR2g') or input('Bot Token: ')
owner_id = os.getenv('8065884629') or input('Owner ID: ')
Dev_Neptune = token.split(':')[0]


# 2. محاولة الاتصال بـ Redis
try:
    r = redis.Redis.from_url(os.getenv('REDIS_URL', 'https://www.tiktok.com/@rmaxatee/video/7666134427214384404?_r=1&u_code=ej378a8a51b0ic&preview_pb=0&sharer_language=ar&_d=f09d18ag72h7ej&share_item_id=7666134427214384404&source=h5_m&timestamp=1786796927&user_id=7476050567253869584&sec_user_id=MS4wLjABAAAAREz3RNKeIhkgmx1s-MKlbne9e07a28bRRhXjgGWALmsiXAwASGXJftwBCPJixZLN&social_share_type=0&utm_source=copy&utm_campaign=client_share&utm_medium=android&share_iid=7673958488049272597&share_link_id=86c9d5ca-0b50-49be-8e80-97779def301c&share_app_id=1233&ugbiz_name=MAIN&ug_btm=b2001&sp_root_share_link_id=86c9d5ca-0b50-49be-8e80-97779def301c&link_reflow_popup_iteration_sharer=%7B%22click_empty_to_play%22%3A1%2C%22dynamic_cover%22%3A1%2C%22follow_to_play_duration%22%3A-1.0%2C%22profile_clickable%22%3A1%7D&panel_source_v2=share_panel&share_enter_from=homepage_hot&item_author_type=2&enable_checksum=1&sp_level=1&sp_root_u=ej378a8a51b0ic&sp_root_d=f09d18ag72h7ej'), decode_responses=True)
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
