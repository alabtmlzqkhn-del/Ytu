import os
import requests
from pyrogram import Client, idle

from localdb import r

token = os.getenv("BOT_TOKEN") or os.getenv("TOKEN")
owner_raw = os.getenv("OWNER_ID")

if not token:
    raise RuntimeError("BOT_TOKEN environment variable is missing.")
if not owner_raw:
    raise RuntimeError("OWNER_ID environment variable is missing.")

owner_id = int(owner_raw)
Dev_Neptune = token.split(":")[0]

try:
    username = requests.get(
        f"https://api.telegram.org/bot{token}/getMe", timeout=15
    ).json()["result"]["username"]
except Exception:
    username = "unknown"

botUsername = username
sudo_id = owner_id
api_id = int(os.getenv("API_ID", "28850159"))
api_hash = os.getenv("API_HASH", "09a3e7d212b434aec973ad5ea10d8ec6")

r.set(f"{Dev_Neptune}botowner", owner_id)
if not r.get(f"{Dev_Neptune}:botkey"):
    r.set(f"{Dev_Neptune}:botkey", "⇜")
if not r.get(f"{Dev_Neptune}botname"):
    r.set(f"{Dev_Neptune}botname", "Jack")

# Existing plugins import these names from config.py.
with open("config.py", "w", encoding="utf-8") as f:
    f.write("from localdb import r\n")
    f.write(f"token = {token!r}\n")
    f.write(f"Dev_Neptune = {Dev_Neptune!r}\n")
    f.write(f"sudo_id = {owner_id!r}\n")
    f.write(f"botUsername = {username!r}\n")
    f.write("from kvsqlite.sync import Client as DB\n")
    f.write("ytdb = DB('ytdb.sqlite')\n")
    f.write("sounddb = DB('sounddb.sqlite')\n")
    f.write("wsdb = DB('wsdb.sqlite')\n")

print("Loading Jack without Redis...")

app = Client(
    f"{Dev_Neptune}Neptune",
    api_id,
    api_hash,
    bot_token=token,
    plugins={"root": "Plugins"},
)

app.start()
print("• SOURCE JACK IS UP AND RUNNING (SQLite / no Redis)")
idle()
