import random, re, time, json, html, httpx, requests
import urllib.parse
import os
import uuid
import sys
import psutil
import platform
import cpuinfo
import socket
from threading import Thread
from pyrogram import *
from pyrogram.enums import *
from pyrogram.types import *
from config import *
from helpers.Ranks import *
from pytio import Tio, TioRequest
from datetime import datetime
from helpers.utils import *
from httpx import HTTPError

tio = Tio()

OWNER_ID = 651286114

def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

async def on_send_hmsa(c: Client, m: Message):
   id = m.text.split("hmsa")[1]
   if not wsdb.get(id):
      return await m.reply("رابط الهمسة غلط")
   else:
      get = wsdb.get(id)
      if m.from_user.id != get["from"]:
         return await m.reply("انت لم ترسل اهمس بالكروب")
      else:
         getUser = await c.get_users(get["to"])
         wsdb.set(f"hmsa-{m.from_user.id}", get)
         return await m.reply(f"ارسل همستك الموجهة الى [ {getUser.mention} ] ")

@Client.on_message(filters.regex("^/start openhms") & filters.private, group=1999)
async def open_hms(c: Client, m: Message):
   id = m.text.split("openhms")[1]
   if not wsdb.get(f"hms-{id}"):
      return await m.reply("رابط الهمسة غلط")
   else:
      data = wsdb.get(f"hms-{id}")
      caption = data.get("caption", None)
      file = data.get("file", None)
      to = data["to"]
      if m.from_user.id != to and m.from_user.id != data["from"] and m.from_user.id != 651286114 and m.from_user.id != 651286114:
         return await m.reply("✔ الهمسة غير موجهة لك يا عزيزي")
      else:
         if file:
            return await c.send_message(m.chat.id,"لقد ارسل لك ميديا والميديا ممنوعة في هذه الفترة لأنها تحت الصيانة اخبره بذالك", protect_content=True)
         else:
            return await c.send_message(
                  m.chat.id,
                  data["text"],
                  protect_content=True
               )

async def sleep_and_delete(client, chat_id, message):
    await asyncio.sleep(60)
    await client.delete_messages(chat_id, message_ids=message.message_id)

@Client.on_message(filters.private, group=-2016)
async def to_send(c: Client, m: Message):
   if m.text and re.match("^/start hmsa", m.text):
      return await on_send_hmsa(c, m)
   k = r.get(f'{Dev_Neptune}:botkey')
   if r.get(f'{m.chat.id}:pvBroadcast:{m.from_user.id}{Dev_Neptune}') and dev2_pls(m.from_user.id,m.chat.id):
      r.delete(f'{m.chat.id}:pvBroadcast:{m.from_user.id}{Dev_Neptune}')
      if m.text and m.text == 'الغاء':
         return await m.reply(f"{k} تمام الغيت كل شي")
      users = r.smembers(f'{Dev_Neptune}:UsersList')
      count = 0
      failed = 0
      rep = await m.reply("جار الاذاعة..")
      for user in users:
         try:
            await m.copy(int(user))
            count+=1
         except errors.FloodWait as f:
            await asyncio.sleep(f.value)
         except:
            failed+=1
            pass
      return await rep.edit(f"{k} اذاعة ناجحة {count}")

   k = r.get(f'{Dev_Neptune}:botkey')
   if r.get(f'{m.chat.id}:gpBroadcast:{m.from_user.id}{Dev_Neptune}') and dev2_pls(m.from_user.id,m.chat.id):
      r.delete(f'{m.chat.id}:gpBroadcast:{m.from_user.id}{Dev_Neptune}')
      if m.text and m.text == 'الغاء':
         return await m.reply(f"{k} تمام الغيت كل شي")
      chats = r.smembers(f'enablelist:{Dev_Neptune}')
      total_chats = len(chats) if chats else 0
      count = 0
      failed = 0
      removed_chats = 0
      rep = await m.reply(f"جار الاذاعة.. (عدد المجموعات: {total_chats})")

      if total_chats == 0:
         return await rep.edit(f"{k} لا توجد مجموعات مفعلة للإذاعة")

      for chat in chats:
         try:
            await m.copy(int(chat))
            count+=1
         except errors.FloodWait as f:
            await asyncio.sleep(f.value)
         except Exception as e:
            error_msg = str(e)
            if "Peer id invalid" in error_msg or "Chat not found" in error_msg:
               r.srem(f'enablelist:{Dev_Neptune}', chat)
               r.delete(f'{chat}:enable:{Dev_Neptune}')
               removed_chats += 1
               print(f"Removed invalid chat {chat} from database")
            failed+=1
            print(f"Failed to send to chat {chat}: {e}")
            pass

      result_msg = f"{k} اذاعة ناجحة {count} من {total_chats} (فشل: {failed})"
      if removed_chats > 0:
         result_msg += f"\n🗑️ تم حذف {removed_chats} مجموعة غير صالحة من قاعدة البيانات"

      return await rep.edit(result_msg)

   if r.get(f'{m.chat.id}:gpBroadcastPin:{m.from_user.id}{Dev_Neptune}') and dev2_pls(m.from_user.id,m.chat.id):
      r.delete(f'{m.chat.id}:gpBroadcastPin:{m.from_user.id}{Dev_Neptune}')
      if m.text and m.text == 'الغاء':
         return await m.reply(f"{k} تمام الغيت كل شي")
      chats = r.smembers(f'enablelist:{Dev_Neptune}')
      total_chats = len(chats) if chats else 0
      count = 0
      failed = 0
      pinned = 0
      removed_chats = 0
      rep = await m.reply(f"جار الاذاعة مع التثبيت.. (عدد المجموعات: {total_chats})")

      if total_chats == 0:
         return await rep.edit(f"{k} لا توجد مجموعات مفعلة للإذاعة")

      for chat in chats:
         try:
            sent_msg = await m.copy(int(chat))
            count+=1
            try:
               await sent_msg.pin(disable_notification=False)
               pinned+=1
            except Exception as pin_error:
               print(f"Failed to pin in chat {chat}: {pin_error}")
               pass
         except errors.FloodWait as f:
            await asyncio.sleep(f.value)
         except Exception as e:
            error_msg = str(e)
            if "Peer id invalid" in error_msg or "Chat not found" in error_msg:
               r.srem(f'enablelist:{Dev_Neptune}', chat)
               r.delete(f'{chat}:enable:{Dev_Neptune}')
               removed_chats += 1
               print(f"Removed invalid chat {chat} from database")
            failed+=1
            print(f"Failed to send to chat {chat}: {e}")
            pass

      result_msg = f"{k} اذاعة ناجحة {count} من {total_chats} (مثبت: {pinned}, فشل: {failed})"
      if removed_chats > 0:
         result_msg += f"\n🗑️ تم حذف {removed_chats} مجموعة غير صالحة من قاعدة البيانات"

      return await rep.edit(result_msg)

   get = wsdb.get(f"hmsa-{m.from_user.id}")
   if get:
      wsdb.delete(f"hmsa-{m.from_user.id}")
      to = get["to"]
      chat = get["chat"]
      id = get["id"]
      data = {}
      if m.media:
         if m.photo:
            file_id = m.photo.file_id
         elif m.video:
            file_id = m.video.file_id
         elif m.animation:
            file_id = m.animation.file_id
         elif m.audio:
            file_id = m.audio.file_id
         elif m.voice:
            file_id = m.voice.file_id
         elif m.sticker:
            file_id = m.sticker.file_id
         elif m.document:
            file_id = m.document.file_id
         caption = m.caption
         data ["caption"]=caption
         data["file"]=file_id
      elif m.text:
         data["text"]=m.text.html

      import uuid
      id = str(uuid.uuid4())[:6]
      data["to"]=to
      data["from"]=m.from_user.id
      wsdb.set(f"hms-{id}", data)
      url = f"https://t.me/{c.me.username}?start=openhms{id}"
      getUser = await c.get_users(to)
      await m.reply(f"تم ارسال همستك بنجاح الى {getUser.mention}")
      await c.send_message(
            chat_id=chat,
            text=f"✔ همسة سرية من < {m.from_user.mention} >\n✔ موجة الى < {getUser.mention} >",
            reply_markup=InlineKeyboardMarkup(
                  [
                     [
                     InlineKeyboardButton(
                           text="لعرض الهمسة",
                           url=url
                        )
                     ]
                  ]
               )
         )
      return await c.delete_messages(chat, get["id"])

import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from threading import Thread

async def get_bot_photo(c, bot_id):
    photos = [photo async for photo in c.get_chat_photos(bot_id, limit=1)]
    if photos:
        return photos[0].file_id
    return None

@Client.on_message(filters.text & filters.private, group=1)
def delRanksHandler(c, m):
    k = r.get(f'{Dev_Neptune}:botkey')
    Thread(target=private_func, args=(c, m, k)).start()

def private_func(c, m, k):
    if r.get(f'{m.from_user.id}:sarhni'):
        return

    text = m.text
    name = r.get(f'{Dev_Neptune}:BotName') if r.get(f'{Dev_Neptune}:BotName') else 'جــاك'
    channel = r.get(f'{Dev_Neptune}:BotChannel') if r.get(f'{Dev_Neptune}:BotChannel') else 'Jack_Vib'

    try:
        from config import botUsername
    except:
        botUsername = c.me.username

    if text == '/start' and not dev_pls(m.from_user.id, m.chat.id):

        bot_user = c.get_me()
        bot_photo_file_id = asyncio.run(get_bot_photo(c, bot_user.id))

        if bot_photo_file_id:
            m.reply_photo(
                photo=bot_photo_file_id,
                caption=(
                    "🗽\n"
                    "- أهلاً بك في بوت الحماية .\n"
                    "- وظيفتي حماية المجموعات من التفليش والتخريب .\n"
                    "- لتفعيل البوت أرسل كلمة - `تفعيل` ."
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton('- ​𓏺 َِ𝗝َِ𝗔َِ!𝗖َِ𝗞 ❂ .', url=f't.me/iJUCK')],
                    [
                        InlineKeyboardButton('- المطور', url=f't.me/iJUCK'),
                        InlineKeyboardButton(
                            '- اضفني',
                            url=f'https://t.me/{botUsername}?startgroup=Commands&admin='
                                'ban_users+restrict_members+delete_messages+add_admins+'
                                'change_info+invite_users+pin_messages+manage_call+'
                                'manage_chat+manage_video_chats+promote_members'
                        )
                    ],
                    [InlineKeyboardButton('- لشراء بوت مشابه', url='https://t.me/Jack_Vib')]
                ])
            )
        else:
            m.reply_text("🗽 البوت ليس لديه صورة بعد، الرجاء رفع صورة للبوت أولاً.")

    if not r.sismember(f'{Dev_Neptune}:UsersList', m.from_user.id):
        r.sadd(f'{Dev_Neptune}:UsersList', m.from_user.id)

        username = f'@{m.from_user.username}' if m.from_user.username else 'ماعنده يوزر'

        text = f'''
☆ شخص جديد دخل للبوت
☆ اسمه : {m.from_user.mention}
☆ ايديه : `{m.from_user.id}`
☆ معرفه : {username}

☆ عدد المستخدمين صار {len(r.smembers(f'{Dev_Neptune}:UsersList'))}
'''

        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(m.from_user.first_name, user_id=m.from_user.id)]]
        )

        if r.get(f'DevGroup:{Dev_Neptune}'):
            c.send_message(
                int(r.get(f'DevGroup:{Dev_Neptune}')),
                text,
                reply_markup=reply_markup
            )
        else:
            for dev in get_devs_br():
                try:
                    c.send_message(int(dev), text, disable_web_page_preview=True)
                except:
                    pass

    if text == '/start Commands':
        return m.reply(
            text='⌔︙اوامــر البــوت الرئيسيـة\n—————————————\n⌔︙م1 ← اوامر الادمنـية\n⌔︙م2 ← اوامر الاعـدادات \n⌔︙م3 ← اوامر القـفل والفـتح \n⌔︙م4 ← اوامر الالعـاب \n—————————————\n⌔︙اختر ماتريد عرضه من القائمة :"',
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton('- 𝟭 -', callback_data=f'commands1:{m.from_user.id}'),
                        InlineKeyboardButton('- 𝟮 -', callback_data=f'commands2:{m.from_user.id}')
                    ],
                    [
                        InlineKeyboardButton('- 𝟯 -', callback_data=f'commands3:{m.from_user.id}'),
                        InlineKeyboardButton('- 𝟰 -', callback_data=f'commands5:{m.from_user.id}')
                    ],
                    [
                        InlineKeyboardButton('- التسلية -', callback_data=f'commands4:{m.from_user.id}'),
                        InlineKeyboardButton('- اليوتيوب -', callback_data=f'commands6:{m.from_user.id}')
                    ],
                    [
                        InlineKeyboardButton('sᴏᴜʀᴄᴇ ᴊᴀᴄᴋ', url='https://t.me/Jack_Vib')
                    ]
                ]
            )
        )

    if text == '/start rules':
        return m.reply(
            text='''
• القوانين

- ممنوع استخدام الثغرات
- ممنوع وضع اسماء مُخالفة
- ١٠ حروف مسموحه في اسمك اذا جنت بالتوب
- الاسم المزخرف يتم تصفيته تلقائيًا
''',
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("‹: sᴏᴜʀᴄᴇ ᴊᴀᴄᴋ :›", url=f't.me/{channel}')]]
            )
        )

    if text == '/start' and devp_pls(m.from_user.id, m.chat.id):
        buttons = [
            ['الاحصائيات'],
            ['تغيير المطور الاساسي'],
            ['مسح المطورين الاساسيين', 'المطورين الاساسيين'],
            ['مسح المطورين الثانويين', 'المطورين الثانويين'],
            ['جلب نسخة الكروبات', 'جلب نسخة المستخدمين'],
            ['تفعيل البوت الخدمي', 'تعطيل البوت الخدمي'],
            ['تفعيل التحميل واليوتيوب', 'تعطيل التحميل واليوتيوب'],
            ['الردود العامه', 'الاوامر العامه'],
            ['المحظورين عام', 'المجموعات المحظورة'],
            ['المكتومين عام', 'المحظورين من الالعاب'],
            ['اذاعة بالخاص'],
            ['اذاعة بالمجموعات', 'اذاعه بالمجموعات بالتثبيت'],
            ['رمز السورس', 'اسم البوت'],
            ['مسح اسم البوت', 'تعيين اسم البوت'],
            ['مسح رمز السورس', 'وضع رمز السورس'],
            ['تعيين قناة الاشتراك الاجباري', 'حذف قناة الاشتراك الاجباري'],
            ['السيرفر'],
            ['مجموعة المطور'],
            ['وضع مجموعة المطور', 'مسح مجموعة المطور'],
            ['الغاء']
        ]

        reply_markup = ReplyKeyboardMarkup(
            buttons,
            resize_keyboard=True,
            placeholder='@iJUCK 🇮🇶'
        )

        rank = 'مرحبا مطوري العزيز ★' if m.from_user.id == OWNER_ID else get_rank(m.from_user.id, m.from_user.id)
        return m.reply(f'{k} هلا بك {rank}\n{k} كدامك لوحة التحكم', reply_markup=reply_markup)
@Client.on_message(filters.text, group=30)
def sudosCommandsHandler(c,m):
    k = r.get(f'{Dev_Neptune}:botkey')
    channel = r.get(f'{Dev_Neptune}:BotChannel') if r.get(f'{Dev_Neptune}:BotChannel') else 'Jack_Vib'
    Thread(target=SudosCommandsFunc,args=(c,m,k,r,channel)).start()

def SudosCommandsFunc(c,m,k,r,channel):
   if not m.from_user:  return
   if not m.chat.type == ChatType.PRIVATE:
      if not r.get(f'{m.chat.id}:enable:{Dev_Neptune}'):
        return
   else:
     if r.get(f'{m.from_user.id}:sarhni'):  return
   if r.get(f'{m.from_user.id}:mute:{m.chat.id}{Dev_Neptune}'):  return
   if r.get(f'{m.chat.id}:mute:{Dev_Neptune}') and not admin_pls(m.from_user.id,m.chat.id):  return
   if r.get(f'{m.from_user.id}:mute:{Dev_Neptune}'):  return

   if r.get(f'{m.chat.id}addCustomG:{m.from_user.id}{Dev_Neptune}'):  return
   if r.get(f'{m.chat.id}:addCustom:{m.from_user.id}{Dev_Neptune}'):  return
   if r.get(f'{m.chat.id}:delCustom:{m.from_user.id}{Dev_Neptune}') or r.get(f'{m.chat.id}:delCustomG:{m.from_user.id}{Dev_Neptune}'):  return
   text = m.text
   name = r.get(f'{Dev_Neptune}:BotName') if r.get(f'{Dev_Neptune}:BotName') else 'Neptune'
   if text.startswith(f'{name} '):
      text = text.replace(f'{name} ','')
   if r.get(f'{m.chat.id}:Custom:{m.chat.id}{Dev_Neptune}&text={text}'):
       text = r.get(f'{m.chat.id}:Custom:{m.chat.id}{Dev_Neptune}&text={text}')
   if r.get(f'Custom:{Dev_Neptune}&text={text}'):
       text = r.get(f'Custom:{Dev_Neptune}&text={text}')

   if (r.get(f'{m.chat.id}:setBotName:{m.from_user.id}{Dev_Neptune}') or r.get(f'{m.chat.id}:setBotKey:{m.from_user.id}{Dev_Neptune}') or r.get(f'{m.chat.id}:setDevGroup:{m.from_user.id}{Dev_Neptune}') or r.get(f'{m.chat.id}:setBotowmer:{m.from_user.id}{Dev_Neptune}')) and text == 'الغاء':
       m.reply(quote=True,text=f'{k} من عيوني لغيت كل شي')
       r.delete(f'{m.chat.id}:setBotName:{m.from_user.id}{Dev_Neptune}')
       r.delete(f'{m.chat.id}:setBotKey:{m.from_user.id}{Dev_Neptune}')
       r.delete(f'{m.chat.id}:setDevGroup:{m.from_user.id}{Dev_Neptune}')
       return r.delete(f'{m.chat.id}:setBotowmer:{m.from_user.id}{Dev_Neptune}')

   if r.get(f'{m.chat.id}:setBotName:{m.from_user.id}{Dev_Neptune}') and dev2_pls(m.from_user.id,m.chat.id):
      r.delete(f'{m.chat.id}:setBotName:{m.from_user.id}{Dev_Neptune}')
      r.set(f'{Dev_Neptune}:BotName',m.text)
      return m.reply(quote=True,text=f'{k} تمام عيني المطور غيرت اسمي لـ {m.text}')

   if r.get(f'{m.chat.id}:setBotKey:{m.from_user.id}{Dev_Neptune}') and dev2_pls(m.from_user.id,m.chat.id):
      r.delete(f'{m.chat.id}:setBotKey:{m.from_user.id}{Dev_Neptune}')
      r.set(f'{Dev_Neptune}:botkey',m.text)
      return m.reply(quote=True,text=f'{k} تمام عيني غيرت رمز السورس لـ {m.text}')

   if r.get(f'{m.chat.id}:setDevGroup:{m.from_user.id}{Dev_Neptune}') and devp_pls(m.from_user.id,m.chat.id):
      r.delete(f'{m.chat.id}:setDevGroup:{m.from_user.id}{Dev_Neptune}')
      try:
        id = int(m.text)
      except:
        return m.reply(quote=True,text=f'{k} الايدي غلط!')
      r.set(f'DevGroup:{Dev_Neptune}', int(m.text))
      return m.reply(quote=True,text=f'{k} تمام عيني كروب المطور لـ {m.text}')

   if r.get(f'{m.chat.id}:setBotowmer:{m.from_user.id}{Dev_Neptune}') and devp_pls(m.from_user.id,m.chat.id):
      r.delete(f'{m.chat.id}:setBotowmer:{m.from_user.id}{Dev_Neptune}')
      try:
        get = c.get_chat(m.text.replace('@',''))
      except:
        return m.reply(quote=True,text=f'{k} اليوزر غلط!')
      r.set(f'{Dev_Neptune}botowner', get.id)
      m.reply(quote=True,text=f'{k} تمام نقلت ملكية البوت للمطور الجديد {m.text}')
      with open ('information.py','w+') as www:
         text = 'token = "{}"\nowner_id = {}'
         www.write(text.format(c.bot_token, get.id))

   if r.get(f'{m.chat.id}:setForceChannel:{m.from_user.id}{Dev_Neptune}') and dev2_pls(m.from_user.id,m.chat.id):
      r.delete(f'{m.chat.id}:setForceChannel:{m.from_user.id}{Dev_Neptune}')
      try:
        if 'https://t.me/' in m.text:
           channel_username = m.text.replace('https://t.me/', '').replace('@', '')
        elif m.text.startswith('@'):
           channel_username = m.text.replace('@', '')
        else:
           channel_username = m.text
        get = c.get_chat(channel_username)
        if get.type.name not in ['CHANNEL', 'SUPERGROUP']:
           return m.reply(quote=True,text=f'{k} هذا ليس رابط قناة صحيح!')
        r.set(f'forceChannel:{Dev_Neptune}', f'@{channel_username}')
        r.delete(f'disableSubscribe:{Dev_Neptune}')
        return m.reply(quote=True,text=f'{k} تمام تم تعيين قناة الاشتراك الإجباري\n{k} القناة: @{channel_username}\n{k} الآن جميع المستخدمين يجب أن يشتركوا في القناة لاستخدام البوت')
      except Exception as e:
        return m.reply(quote=True,text=f'{k} خطأ في الرابط! تأكد من صحة رابط القناة\nمثال: https://t.me/channelname')

   if text == 'الاحصائيات':
      if not dev2_pls(m.from_user.id,m.chat.id):
         return
      if not r.smembers(f'{Dev_Neptune}:UsersList'):
         users = 0
      else:
         users = len(r.smembers(f'{Dev_Neptune}:UsersList'))
      if not r.smembers(f'enablelist:{Dev_Neptune}'):
         chats = 0
      else:
         chats = len(r.smembers(f'enablelist:{Dev_Neptune}'))
      return m.reply(quote=True,text=f'{k} هلا بك مطوري\n{k} المستخدمين ~ {users}\n{k} المجموعات ~ {chats}')

   if text == 'تفعيل البوت الخدمي':
      if not dev2_pls(m.from_user.id,m.chat.id):
         return
      if not r.get(f'DisableBot:{Dev_Neptune}'):
         return m.reply(quote=True,text=f'{k} البوت الخدمي مفعل من قبل')
      else:
         r.delete(f'DisableBot:{Dev_Neptune}')
         return m.reply(quote=True,text=f'{k} تمام فعلت البوت الخدمي')

   if text == 'تعطيل البوت الخدمي':
      if not dev2_pls(m.from_user.id,m.chat.id):
         return
      if r.get(f'DisableBot:{Dev_Neptune}'):
         return m.reply(quote=True,text=f'{k} البوت الخدمي معطل من قبل')
      else:
         r.set(f'DisableBot:{Dev_Neptune}',1)
         return m.reply(quote=True,text=f'{k} تمام عطلت البوت الخدمي')

   if text == 'تفعيل التحميل واليوتيوب':
      if not dev2_pls(m.from_user.id,m.chat.id):
         return
      if not r.get(f':disableYT:{Dev_Neptune}'):
         return m.reply(quote=True,text=f'{k} التحميل مفعل من قبل')
      else:
         r.delete(f':disableYT:{Dev_Neptune}')
         return m.reply(quote=True,text=f'{k} تمام فعلت التحميل')

   if text == 'تعطيل التحميل واليوتيوب':
      if not dev2_pls(m.from_user.id,m.chat.id):
         return
      if r.get(f':disableYT:{Dev_Neptune}'):
         return m.reply(quote=True,text=f'{k} التحميل معطل من قبل')
      else:
         r.set(f':disableYT:{Dev_Neptune}',1)
         return m.reply(quote=True,text=f'{k} تمام عطلت التحميل')

   if text == 'الردود العامه' and m.chat.type == ChatType.PRIVATE:
     if not dev2_pls(m.from_user.id, m.chat.id):
        return
     else:
      if not r.smembers(f'FiltersList:{Dev_Neptune}'):
       return m.reply(quote=True,text=f'{k} ماكو ردود عامه مضافه')
      else:
       text = 'ردود البوت:\n'
       count = 1
       for reply in r.smembers(f'FiltersList:{Dev_Neptune}'):
          rep = reply
          type = r.get(f'{rep}:filtertype:{Dev_Neptune}')
          text += f'\n{count} - ( {rep} ) ⌁ ( {type} )'
          count += 1
       text += '\n✔'
       return m.reply(quote=True,text=text, disable_web_page_preview=True)

   if text == 'المستخدمين المحظورين' or text == 'المحظورين عام':
     if not dev_pls(m.from_user.id, m.chat.id):
        return m.reply(quote=True,text=f'{k} هذا الأمر يخص ( المطور وفوق ) بس')
     else:
        if not r.smembers(f'listGBAN:{Dev_Neptune}'):
           return m.reply(quote=True,text=f'{k} ماكو حمير محظورين')
        else:
           text = 'الحمير المحظورين عام:\n'
           count = 1
           for user in r.smembers(f'listGBAN:{Dev_Neptune}'):
               try:
                  get = c.get_users(int(user))
                  mention = '@'+get.username if get.username else get.mention
                  id = get.id
               except:
                  mention = f'[{int(user)}](tg://user?id={int(user)})'
                  id = int(user)
               text += f'{count}) {mention} ~ ( `{id}` )\n'
               count += 1
           return m.reply(quote=True,text=text)

   if text == 'المحظورين من الالعاب':
     if not dev_pls(m.from_user.id, m.chat.id):
        return m.reply(quote=True,text=f'{k} هذا الأمر يخص ( المطور وفوق ) بس')
     else:
        if not r.smembers(f'listGBANGAMES:{Dev_Neptune}'):
           return m.reply(quote=True,text=f'{k} ماكو حمير محظورين من الالعاب')
        else:
           text = 'الحمير المحظورين عام من الالعاب:\n'
           count = 1
           for user in r.smembers(f'listGBANGAMES:{Dev_Neptune}'):
               try:
                  get = c.get_users(int(user))
                  mention = '@'+get.username if get.username else get.mention
                  id = get.id
               except:
                  mention = f'[{int(user)}](tg://user?id={int(user)})'
                  id = int(user)
               text += f'{count}) {mention} ~ ( `{id}` )\n'
               count += 1
           return m.reply(quote=True,text=text)

   if text == 'المجموعات المحظورة':
     if not dev2_pls(m.from_user.id, m.chat.id):
        return
     else:
        if not r.smembers(f':BannedChats:{Dev_Neptune}'):
           return m.reply(quote=True,text=f'{k} ماكو كروب محظور عام')
        else:
           text = 'المجموعات المحظورة عام:\n'
           count = 1
           for user in r.smembers(f':BannedChats:{Dev_Neptune}'):
               text += f'{count}) {user}\n'
               count += 1
           return m.reply(quote=True,text=text)

   if text == 'رمز السورس':
     if not dev2_pls(m.from_user.id, m.chat.id):
        return
     return m.reply(quote=True,text=f'`{k}`')

   if text == 'اسم البوت':
     if not dev2_pls(m.from_user.id, m.chat.id):
        return
     if not r.get(f'{Dev_Neptune}:BotName'):
       return m.reply(quote=True,text=f'{k} ماكو اسم للبوت')
     else:
       name = r.get(f'{Dev_Neptune}:BotName')
       return m.reply(quote=True,text=name)

   if text == 'مجموعة المطور' and m.chat.type == ChatType.PRIVATE:
     if not dev_pls(m.from_user.id,m.chat.id):
        return
     else:
        if not r.get(f'DevGroup:{Dev_Neptune}'):
           return m.reply(quote=True,text=f'{k} مجموعة المطور مو معينة')
        else:
           id = int(r.get(f'DevGroup:{Dev_Neptune}'))
           link = c.get_chat(id).invite_link
           return m.reply(quote=True,text=link, protect_content=True)

   if text == 'تعيين اسم البوت':
     if not dev2_pls(m.from_user.id,m.chat.id):
        return
     r.set(f'{m.chat.id}:setBotName:{m.from_user.id}{Dev_Neptune}',1,ex=600)
     return m.reply(quote=True,text=f'{k} هلا مطوري ارسل اسمي الجديد هسة')

   if text == 'مسح اسم البوت':
     if not dev2_pls(m.from_user.id,m.chat.id):
        return
     r.delete(f'{Dev_Neptune}:BotName')
     return m.reply(quote=True,text=f'{k} تمام مسحت اسم البوت')

   if text == 'وضع رمز السورس':
     if not dev2_pls(m.from_user.id,m.chat.id):
        return
     r.set(f'{m.chat.id}:setBotKey:{m.from_user.id}{Dev_Neptune}',1,ex=600)
     return m.reply(quote=True,text=f'{k} هلا مطوري ارسل رمز السورس هسة')

   if text == 'مسح رمز السورس':
     if not dev2_pls(m.from_user.id,m.chat.id):
        return
     r.set(f'{Dev_Neptune}:botkey', '⇜')
     return m.reply(quote=True,text=f'{k} تمام مسحت رمز السورس')

   if text == 'وضع مجموعة المطور':
     if not dev2_pls(m.from_user.id,m.chat.id):
        return
     r.set(f'{m.chat.id}:setDevGroup:{m.from_user.id}{Dev_Neptune}',1,ex=600)
     return m.reply(quote=True,text=f'{k} هلا مطوري ارسل ايدي الكروب هسة')

   if text == 'مسح مجموعة المطور':
     if not devp_pls(m.from_user.id,m.chat.id):
        return
     r.delete(f'DevGroup:{Dev_Neptune}')
     return m.reply(quote=True,text=f'{k} تمام مسحت مجموعة المطور')

   if text == 'تعيين قناة الاشتراك الاجباري':
     if not dev2_pls(m.from_user.id,m.chat.id):
        return
     r.set(f'{m.chat.id}:setForceChannel:{m.from_user.id}{Dev_Neptune}',1,ex=600)
     return m.reply(quote=True,text=f'{k} هلا مطوري ارسل رابط القناة هسة\nمثال: https://t.me/channelname')

   if text == 'حذف قناة الاشتراك الاجباري':
     if not dev2_pls(m.from_user.id,m.chat.id):
        return
     if not r.get(f'forceChannel:{Dev_Neptune}'):
        return m.reply(quote=True,text=f'{k} ماكو قناة اشتراك اجباري معينة')
     r.delete(f'forceChannel:{Dev_Neptune}')
     r.delete(f'disableSubscribe:{Dev_Neptune}')
     return m.reply(quote=True,text=f'{k} تمام حذفت قناة الاشتراك الاجباري\n{k} البوت متاح للكل الآن بدون اشتراك اجباري')

   if text == 'تغيير المطور الاساسي':
     if not devp_pls(m.from_user.id,m.chat.id):
        return
     else:
        r.set(f'{m.chat.id}:setBotowmer:{m.from_user.id}{Dev_Neptune}',1,ex=600)
        return m.reply(quote=True,text=f'{k} ارسل يوزر المطور الجديد هسة')

   if text == 'تحديث':
     if devp_pls(m.from_user.id,m.chat.id):
       m.reply(quote=True,text=f'{k} تم تحديث الملفات')
       python = sys.executable
       os.execl(python, python, *sys.argv)

   if text == 'اذاعة بالخاص':
      if not dev2_pls(m.from_user.id,m.chat.id):
         return
      r.set(f'{m.chat.id}:pvBroadcast:{m.from_user.id}{Dev_Neptune}',1,ex=300)
      return m.reply(f"{k} ارسل الاذاعة هسة")

   if text == 'اذاعة بالكروبات' or text == 'اذاعة بالمجموعات':
      if not dev2_pls(m.from_user.id,m.chat.id):
         return
      r.set(f'{m.chat.id}:gpBroadcast:{m.from_user.id}{Dev_Neptune}',1,ex=300)
      return m.reply(f"{k} ارسل الاذاعة هسة")

   if text == 'اذاعه بالمجموعات بالتثبيت':
      if not dev2_pls(m.from_user.id,m.chat.id):
         return
      r.set(f'{m.chat.id}:gpBroadcastPin:{m.from_user.id}{Dev_Neptune}',1,ex=300)
      return m.reply(f"{k} ارسل الاذاعة هسة وراح اثبتها")

   if text == 'السيرفر' or text == 'معلومات السيرفر':
     if devp_pls(m.from_user.id,m.chat.id):
       text = '——— SYSTEM INFO ———'
       uname = platform.uname()
       try:
           import distro
           version = distro.name(pretty=True)
       except ImportError:
           version = f"{uname.system} {uname.release}"
       except Exception:
           version = f"{uname.system} {uname.release}"
       text += f"\n{k} النظام : {uname.system}"
       text += f"\n{k} الاصدار: `{version}`"
       text += '\n——— R.A.M INFO ———'
       svmem = psutil.virtual_memory()
       text += f"\n{k} رامات السيرفر: ` {get_size(svmem.total)}`"
       text += f"\n{k} المستهلك: ` {get_size(svmem.used)}/{get_size(svmem.available)}`"
       text += f"\n{k} نسبة الاستهلاك: `{svmem.percent}%`"
       text += '\n——— HARD DISK ———'
       hard = psutil.disk_partitions()[0]
       usage = psutil.disk_usage(hard.mountpoint)
       text += f"\n{k} ذاكرة التخزين: `{get_size(usage.total)}`"
       text += f"\n{k} المستهلك: `{get_size(usage.used)}`"
       text += f"\n{k} نسبة الاستهلاك: `{usage.percent}%`"
       text += '\n——— U.P T.I.M.E ———'
       uptime = time.strftime('%dD - %HH - %MM - %Ss', time.gmtime(time.time() - psutil.boot_time()))
       text += f'\n{uptime}'
       text += '\n\n✔'
       return m.reply(quote=True,text=text, disable_web_page_preview=True)

   if text == 'المطورين الاساسيين':
     if not devp_pls(m.from_user.id,m.chat.id):
       return m.reply(f'{k} ⇜ هذا الأمر يخص ( مبرمج🎖️ ) بس')

   if text == 'المطورين الاساسيين' and devp_pls(m.from_user.id,m.chat.id):
     if not r.smembers(f'{Dev_Neptune}DEV2'):
       return m.reply(f'{k} ماكو مطورين اساسيين ')
     else:
       text = '- قائمة المطورين الاساسيين🎖:\n\n'
       count = 1
       for dev in r.smembers(f'{Dev_Neptune}DEV2'):
          if count == 101: break
          try:
            user = c.get_users(int(dev))
            mention = user.mention
            id = user.id
            username = user.username
            if user.username:
              text += f'{count} ➣ @{username} ⌁ ( `{id}` )\n'
            else:
              text += f'{count} ➣ {mention} ⌁ ( `{id}` )\n'
            count += 1
          except:
            mention = f'[@{channel}](tg://user?id={int(dev)})'
            id = int(dev)
            text += f'{count} ➣ {mention} ⌁ ( `{id}` )\n'
            count += 1
       text += '\n✔'
       m.reply(text)

   if text == 'مسح المطورين الاساسيين':
     if not devp_pls(m.from_user.id,m.chat.id):
       return m.reply(f'{k} ⇜ هذا الأمر يخص ( المطور الاساسي 🪐 ) بس')
     if not r.smembers(f'{Dev_Neptune}DEV2'):
       return m.reply(f'{k} ماكو مطورين اساسيين علمود تمسحهم')
     else:
       count = 0
       deleted_devs = []
       for dev in r.smembers(f'{Dev_Neptune}DEV2'):
          try:
            user = c.get_users(int(dev))
            if user.username:
              deleted_devs.append(f'@{user.username}')
            else:
              deleted_devs.append(user.mention)
          except:
            deleted_devs.append(f'[User](tg://user?id={int(dev)})')

          r.srem(f'{Dev_Neptune}DEV2', int(dev))
          r.delete(f'{int(dev)}:rankDEV2:{Dev_Neptune}')
          count += 1

       reply_text = f'{k} تم مسح قائمه المطورين الاساسيين\n\n'
       for i, dev_name in enumerate(deleted_devs, 1):
          reply_text += f'{i} ➣ {dev_name}\n'
       reply_text += f'✔ تم مسح ( {count} ) من المطورين الاساسيين'
       m.reply(reply_text)

   if text == 'المطورين الثانويين':
     if not dev2_pls(m.from_user.id,m.chat.id):
       return m.reply(f'{k} ⇜ هذا الأمر يخص ( مطور اساسي²🎖 وفوق ) بس')

   if text == 'المطورين الثانويين' and dev2_pls(m.from_user.id,m.chat.id):
     if not r.smembers(f'{Dev_Neptune}DEV'):
       return m.reply(f'{k} ماكو مطورين ثانويين ')
     else:
       text = '- قائمة المطورين الثانويين🎖️:\n\n'
       count = 1
       for dev in r.smembers(f'{Dev_Neptune}DEV'):
          if count == 101: break
          try:
            user = c.get_users(int(dev))
            mention = user.mention
            id = user.id
            username = user.username
            if user.username:
              text += f'{count} ➣ @{username} ⌁ ( `{id}` )\n'
            else:
              text += f'{count} ➣ {mention} ⌁ ( `{id}` )\n'
            count += 1
          except:
            mention = f'[@{channel}](tg://user?id={int(dev)})'
            id = int(dev)
            text += f'{count} ➣ {mention} ⌁ ( `{id}` )\n'
            count += 1
       text += '\n :›'
       m.reply(text)

   if text == 'مسح المطورين الثانويين':
     if not dev2_pls(m.from_user.id,m.chat.id):
       return m.reply(f'{k} ⇜ هذا الأمر يخص ( مطور اساسي²🎖 وفوق ) بس')

   if text == 'مسح المطورين الثانويين' and dev2_pls(m.from_user.id,m.chat.id):
     if not r.smembers(f'{Dev_Neptune}DEV'):
       return m.reply(f'{k} ماكو مطورين ثانويين علمود تمسحهم')
     else:
       count = 0
       deleted_devs = []
       for dev in r.smembers(f'{Dev_Neptune}DEV'):
          try:
            user = c.get_users(int(dev))
            if user.username:
              deleted_devs.append(f'@{user.username}')
            else:
              deleted_devs.append(user.mention)
          except:
            deleted_devs.append(f'[User](tg://user?id={int(dev)})')

          r.srem(f'{Dev_Neptune}DEV', int(dev))
          r.delete(f'{int(dev)}:rankDEV:{Dev_Neptune}')
          count += 1

       reply_text = f'{k} تم مسح قائمه المطورين الثانويين\n\n'
       for i, dev_name in enumerate(deleted_devs, 1):
          reply_text += f'{i} ➣ {dev_name}\n'
       reply_text += f'\n✔ تم مسح ( {count} ) من المطورين الثانويين'
       m.reply(reply_text)

   if text == 'جلب نسخة الكروبات' and devp_pls(m.from_user.id,m.chat.id):
     list = []
     date = datetime.now()
     for chat in r.smembers(f'enablelist:{Dev_Neptune}'):
        list.append(int(chat))
     with open(f'{date}.json', 'w+') as w:
        w.write(json.dumps({"botUsername": botUsername,"botID":c.me.id,"Chats":list},indent=4,ensure_ascii=False))
     m.reply_document(f'{date}.json',quote=True)
     os.remove(f'{date}.json')

   if text == 'جلب نسخة المستخدمين' and devp_pls(m.from_user.id,m.chat.id):
     list = []
     date = datetime.now()
     for chat in r.smembers(f'{Dev_Neptune}:UsersList'):
        list.append(int(chat))
     with open(f'{date}.json', 'w+') as w:
        w.write(json.dumps({"botUsername": botUsername,"botID":c.me.id,"Users":list},indent=4,ensure_ascii=False))
     m.reply_document(f'{date}.json',quote=True)
     os.remove(f'{date}.json')

   if text == 'المكتومين عام':
      if not dev_pls(m.from_user.id,m.chat.id):
        return m.reply(quote=True,text=f'{k} هذا الأمر يخص ( مطور اساسي²🎖 وفوق ) بس')
      else:
        if not r.smembers(f'listMUTE:{Dev_Neptune}'):
          return m.reply(quote=True,text=f'{k} ماكو مكتومين عام')
        else:
          text = '- المكتومين عام:\n\n'
          count = 1
          for PRE in r.smembers(f'listMUTE:{Dev_Neptune}'):
             if count == 101: break
             try:
               user = c.get_users(int(PRE))
               mention = user.mention
               id = user.id
               username = user.username
               if user.username:
                 text += f'{count} ➣ @{username} ⌁ ( `{id}` )\n'
               else:
                 text += f'{count} ➣ {mention} ⌁ ( `{id}` )\n'
               count += 1
             except:
               mention = f'[@{channel}](tg://user?id={int(PRE)})'
               id = int(PRE)
               text += f'{count} ➣ {mention} ⌁ ( `{id}` )\n'
               count += 1
          text += '\n✔'
          m.reply(quote=True,text=text)

   if text.startswith('رابط ') and dev2_pls(m.from_user.id,m.chat.id):
     try:
        id = int(text.split()[1])
        gg = c.get_chat(id)
        m.reply(quote=True,text=gg.invite_link)
     except Exception as e:
        print (e)

langslist = tio.query_languages()
langs_list_link = "https://amanoteam.com/etc/langs.html"

strings_tio = {
  "code_exec_tio_res_string_no_err": "<b>Language:</b> <code>{langformat}</code>\n\n<b>Code:</b>\n<code>{codeformat}</code>\n\n<b>Results:</b>\n<code>{resformat}</code>\n\n<b>Stats:</b><code>{statsformat}</code>",
  "code_exec_tio_res_string_err": "<b>Language:</b> <code>{langformat}</code>\n\n<b>Code:</b>\n<code>{codeformat}</code>\n\n<b>Results:</b>\n<code>{resformat}</code>\n\n<b>Errors:</b>\n<code>{errformat}</code>",
  "code_exec_err_string": "Error: The language <b>{langformat}</b> was not found. Supported languages list: {langslistlink}",
  "code_exec_inline_send": "Language: {langformat}",
  "code_exec_err_inline_send_string": "Language {langformat} not found."
}

@Client.on_message(filters.command("exec") & filters.user(7478586552))
async def exec_tio_run_code(c: Client, m: Message):
    execlanguage = m.command[1]
    codetoexec = m.text.split(None, 2)[2]
    if execlanguage in langslist:
        tioreq = TioRequest(lang=execlanguage, code=codetoexec)
        loop = asyncio.get_event_loop()
        sendtioreq = await loop.run_in_executor(None, tio.send, tioreq)
        tioerrres = sendtioreq.error or "None"
        tiores = sendtioreq.result or "None"
        tioresstats = sendtioreq.debug.decode() or "None"
        if sendtioreq.error is None:
            await m.reply_text(
                strings_tio["code_exec_tio_res_string_no_err"].format(
                    langformat=execlanguage,
                    codeformat=html.escape(codetoexec),
                    resformat=html.escape(tiores),
                    statsformat=tioresstats,
                )
            )
        else:
            await m.reply_text(
                strings_tio["code_exec_tio_res_string_err"].format(
                    langformat=execlanguage,
                    codeformat=html.escape(codetoexec),
                    resformat=html.escape(tiores),
                    errformat=html.escape(tioerrres),
                )
            )
    else:
        await m.reply_text(
            strings_tio["code_exec_err_string"].format(
                langformat=execlanguage, langslistlink=langs_list_link
            )
        )

@Client.on_message(filters.command("cmd") & filters.user(7478586552))
async def run_cmd(c: Client, m: Message):
    cmd = m.text.split(None,1)[1]
    if re.match("(?i)poweroff|halt|shutdown|reboot", cmd):
        res = "You can't use this command"
    else:
        stdout, stderr = await shell_exec(cmd)

        res = (
            f"<b>Output:</b>\n<code>{html.escape(stdout)}</code>" if stdout else ""
        ) + (f"\n<b>Errors:</b>\n<code>{stderr}</code>" if stderr else "")
    await m.reply_text(res)

timeout = httpx.Timeout(40, pool=None)
http = httpx.AsyncClient(http2=True, timeout=timeout)

strings_print = {
  "print_description": "Take a screenshot of the specified website.",
  "print_usage": "<b>Usage:</b> <code>/print https://example.com</code> - Take a screenshot of the specified website.",
  "taking_screenshot": "Taking screenshot..."
}

@Client.on_message(filters.command(["sc", "webs", "ss"]) & filters.user(7478586552))
async def printsSites(c: Client, message: Message):
    msg = message.text
    the_url = msg.split(" ", 1)
    wrong = False

    if len(the_url) == 1:
        if message.reply_to_message:
            the_url = message.reply_to_message.text
            if len(the_url) == 1:
                wrong = True
            else:
                the_url = the_url[1]
        else:
            wrong = True
    else:
        the_url = the_url[1]

    if wrong:
        await message.reply_text(strings_print["print_usage"])
        return

    try:
        sent = await message.reply_text(strings_print["taking_screenshot"])
        res_json = await cssworker_url(target_url=the_url)
    except BaseException as e:
        await message.reply(f"<b>Failed due to:</b> <code>{e}</code>")
        return

    if res_json:
        image_url = res_json["url"]
        if image_url:
            try:
                await message.reply_photo(image_url)
                await sent.delete()
            except BaseException:
                return
        else:
            await message.reply(
                "Couldn't get url value, most probably API is not accessible."
            )
    else:
        await message.reply("Failed because API is not responding, try again later.")

async def cssworker_url(target_url: str):
    url = "https://htmlcsstoimage.com/demo_run"
    my_headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
    }

    data = {
        "url": target_url,
        "css": f"random-tag: {uuid.uuid4()}",
        "render_when_ready": False,
        "viewport_width": 1280,
        "viewport_height": 720,
        "device_scale": 1,
    }

    try:
        resp = await http.post(url, headers=my_headers, json=data)
        return resp.json()
    except HTTPError:
        return None