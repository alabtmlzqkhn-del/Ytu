import random, re, time, pytz
from datetime import datetime
from threading import Thread
from pyrogram import *
from pyrogram.enums import *
from pyrogram.types import *
from config import *
from helpers.Ranks import *
from helpers.Ranks import isLockCommand

default_welcome = """نورت الكروب

ɴᴀᴍᴇ ⌯ {الاسم}
ᴜѕᴇʀɴᴀᴍᴇ ⌯ {اليوزر}
𝖣𝖺𝗍𝖾 ⌯ {التاريخ}"""


@Client.on_message(filters.group & filters.text, group=29)
def setWelcomeHandler(c, m):
    k = r.get(f"{Dev_Neptune}:botkey")
    Thread(target=welcomeFunc, args=(c, m, k)).start()


def welcomeFunc(c, m, k):
    if not r.get(f"{m.chat.id}:enable:{Dev_Neptune}"):
        return
    if r.get(f"{m.chat.id}:mute:{Dev_Neptune}") and not admin_pls(
        m.from_user.id, m.chat.id
    ):
        return
    if r.get(f"{m.from_user.id}:mute:{m.chat.id}{Dev_Neptune}"):
        return
    if r.get(f"{m.from_user.id}:mute:{Dev_Neptune}"):
        return
    if r.get(f"{m.chat.id}:addCustom:{m.from_user.id}{Dev_Neptune}"):
        return
    if r.get(f"{m.chat.id}addCustomG:{m.from_user.id}{Dev_Neptune}"):
        return
    if r.get(f"{m.chat.id}:delCustom:{m.from_user.id}{Dev_Neptune}") or r.get(
        f"{m.chat.id}:delCustomG:{m.from_user.id}{Dev_Neptune}"
    ):
        return
    text = m.text
    name = r.get(f"{Dev_Neptune}:BotName") if r.get(f"{Dev_Neptune}:BotName") else "Jack"
    if text.startswith(f"{name} "):
        text = text.replace(f"{name} ", "")
    if r.get(f"{m.chat.id}:Custom:{m.chat.id}{Dev_Neptune}&text={text}"):
        text = r.get(f"{m.chat.id}:Custom:{m.chat.id}{Dev_Neptune}&text={text}")
    if r.get(f"Custom:{Dev_Neptune}&text={text}"):
        text = r.get(f"Custom:{Dev_Neptune}&text={text}")
    if isLockCommand(m.from_user.id, m.chat.id, text):
        return
    if text == "الغاء" and r.get(f"{m.chat.id}:setWelcome:{m.from_user.id}{Dev_Neptune}"):
        r.delete(f"{m.chat.id}:setWelcome:{m.from_user.id}{Dev_Neptune}")
        return m.reply(f"{k} تمام لغيت وضع الترحيب")

    if text == "الغاء" and r.get(f"{m.chat.id}:setRules:{m.from_user.id}{Dev_Neptune}"):
        r.delete(f"{m.chat.id}:setRules:{m.from_user.id}{Dev_Neptune}")
        return m.reply(f"{k} تمام لغيت وضع القوانين")

    if r.get(f"{m.chat.id}:setRules:{m.from_user.id}{Dev_Neptune}") and mod_pls(
        m.from_user.id, m.chat.id
    ):
        r.set(f"{m.chat.id}:CustomRules:{Dev_Neptune}", m.text.html)
        r.delete(f"{m.chat.id}:setRules:{m.from_user.id}{Dev_Neptune}")
        return m.reply(f"{k} تم حطيتها")

    if r.get(f"{m.chat.id}:setWelcome:{m.from_user.id}{Dev_Neptune}") and mod_pls(
        m.from_user.id, m.chat.id
    ):
        r.set(f"{m.chat.id}:CustomWelcome:{Dev_Neptune}", m.text.html)
        r.delete(f"{m.chat.id}:setWelcome:{m.from_user.id}{Dev_Neptune}")
        return m.reply(f"{k} تم وسوينا الترحيب ياعيني")

    if text == "مسح القوانين":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            r.delete(f"{m.chat.id}:CustomRules:{Dev_Neptune}")
            return m.reply(f"{k} من عيوني مسحت القوانين")

    if text == "وضع قوانين":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            r.set(f"{m.chat.id}:setRules:{m.from_user.id}{Dev_Neptune}", 1)
            return m.reply(f"{k} ارسل القوانين هسة")

    if text == "الترحيب":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:CustomWelcome:{Dev_Neptune}"):
                return m.reply(f"`{default_welcome}`")
            else:
                welcome = r.get(f"{m.chat.id}:CustomWelcome:{Dev_Neptune}")
                return m.reply(f"`{welcome}`")

    if text == "مسح الترحيب":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            r.delete(f"{m.chat.id}:CustomWelcome:{Dev_Neptune}")
            return m.reply(f"{k} مسحت الترحيب")

    if text == "وضع الترحيب" or text == "ضع الترحيب":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            r.set(f"{m.chat.id}:setWelcome:{m.from_user.id}{Dev_Neptune}", 1)
            return m.reply("""⇜ تمام عيني  
⇜ ارسل رسالة الترحيب هسة

⇜ ملاحظة تكدر تضيف دوال للترحيب مثلا :
⇜ اظهار قوانين المجموعه  ⇠ {القوانين}  
⇜ اظهار اسم العضو ⇠ {الاسم}
⇜ اظهار اليوزر العضو ⇠ {اليوزر}
⇜ اظهار اسم المجموعه ⇠ {المجموعه} 
⇜ اظهار تاريخ دخول العضو ⇠ {التاريخ} 
⇜ اظهار وقت دخول العضو ⇠ {الوقت} 
☆
""")


@Client.on_message(filters.new_chat_members, group=4)
def welcomeRespons(c: Client, m: Message):
    if not r.get(f"{m.chat.id}:enable:{Dev_Neptune}"):
        return
    k = r.get(f"{Dev_Neptune}:botkey")
    channel = (
        r.get(f"{Dev_Neptune}:BotChannel") if r.get(f"{Dev_Neptune}:BotChannel") else "Jack_Vib"
    )
    print("member")
    if not r.get(f"{m.chat.id}:disableWelcome:{Dev_Neptune}") and m.new_chat_members:
        if not r.get(f"{m.chat.id}:CustomWelcome:{Dev_Neptune}"):
            welcome = default_welcome
        else:
            welcome = r.get(f"{m.chat.id}:CustomWelcome:{Dev_Neptune}")
        for me in m.new_chat_members:
            if not me.id == int(Dev_Neptune):
                if r.get(f"{m.chat.id}:enableVerify:{Dev_Neptune}") and not pre_pls(
                    me.id, m.chat.id
                ):
                    return
                photo = None
                if not r.get(f"{m.chat.id}:disableWelcomep:{Dev_Neptune}") and me.photo:
                    for photo in c.get_chat_photos(me.id, limit=1):
                        photo = photo.file_id
                title = m.chat.title
                name = me.first_name
                if me.username:
                    username = f"@{me.username}"
                else:
                    username = f"@{channel}"
                TIME_ZONE = "Asia/Riyadh"
                ZONE = pytz.timezone(TIME_ZONE)
                TIME = datetime.now(ZONE)
                clock = TIME.strftime("%I:%M %p")
                date = TIME.strftime("%d/%m/%Y")
                if r.get(f"{m.chat.id}:CustomRules:{Dev_Neptune}"):
                    rules = r.get(f"{m.chat.id}:CustomRules:{Dev_Neptune}")
                else:
                    rules = """{k} ممنوع نشر الروابط 
{k} ممنوع التكلم او نشر صور اباحيه 
{k} ممنوع اعاده توجيه 
{k} ممنوع العنصرية بكل انواعها 
{k} الرجاء احترام المدراء والادمنيه"""
                w = (
                    welcome.replace("{القوانين}", rules)
                    .replace("{الاسم}", name)
                    .replace("{المجموعه}", title)
                    .replace("{الوقت}", clock)
                    .replace("{التاريخ}", date)
                    .replace("{اليوزر}", username)
                )
                if not photo:
                    return m.reply(w, disable_web_page_preview=True)
                else:
                    return m.reply_photo(photo, caption=w)


"""
def welcomeRespons(c,m):
   if not r.get(f'{m.chat.id}:enable:{Dev_Neptune}'):  return
   k = r.get(f'{Dev_Neptune}:botkey')
   channel = r.get(f'{Dev_Neptune}:BotChannel') if r.get(f'{Dev_Neptune}:BotChannel') else 'Y88F8'
   print("member")
   if not r.get(f'{m.chat.id}:disableWelcome:{Dev_Neptune}') and m.new_chat_members:
     if not r.get(f'{m.chat.id}:CustomWelcome:{Dev_Neptune}'):
        welcome = default_welcome
     else:
        welcome = r.get(f'{m.chat.id}:CustomWelcome:{Dev_Neptune}')
     for me in m.new_chat_members:
      if not me.id == int(Dev_Neptune):
        if r.get(f'{m.chat.id}:enableVerify:{Dev_Neptune}') and not pre_pls(me.id,m.chat.id):
          return
        title = m.chat.title
        name = me.first_name
        if me.username:
          username = f'@{me.username}'
        else:
          username = f'@{channel}'
        TIME_ZONE = "Asia/Riyadh"
        ZONE = pytz.timezone(TIME_ZONE)
        TIME = datetime.now(ZONE)
        clock = TIME.strftime("%I:%M %p")
        date = TIME.strftime("%d/%m/%Y")
        if r.get(f'{m.chat.id}:CustomRules:{Dev_Neptune}'):
          rules = r.get(f'{m.chat.id}:CustomRules:{Dev_Neptune}')
        else:
          rules = '''{k} ممنوع نشر الروابط 
{k} ممنوع التكلم او نشر صور اباحيه 
{k} ممنوع اعاده توجيه 
{k} ممنوع العنصرية بكل انواعها 
{k} الرجاء احترام المدراء والادمنيه'''
        w = welcome.replace('{القوانين}',rules).replace('{الاسم}',name).replace('{المجموعه}',title).replace('{الوقت}', clock).replace('{التاريخ}',date).replace('{اليوزر}',username)
        try:
          c.send_message(m.chat.id,w, disable_web_page_preview=True,reply_to_message_id=m.id)
        except:
          c.send_message(m.chat.id,w, disable_web_page_preview=True)
        return True
"""
