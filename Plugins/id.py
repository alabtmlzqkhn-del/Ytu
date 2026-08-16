import random, re, time, os
from threading import Thread
from pyrogram import *
from pyrogram.enums import *
from pyrogram.types import *
from config import *
from helpers.Ranks import *
from helpers.get_create import get_creation_date
from pyrogram.raw.functions.users import GetFullUser
from io import BytesIO
from pyrogram.file_id import FileId, FileType, ThumbnailSource
from pyrogram.raw.functions.channels import GetFullChannel
from .games import get_emoji_bank
from helpers.Ranks import isLockCommand

def get_top(users):
   users = [tuple(i.items()) for i in users]
   top = sorted(users, key=lambda i: i[-1][-1], reverse=True)
   top = [dict(i) for i in top]
   return top

custom_ids = ['''
- ᴜѕᴇʀɴᴀᴍᴇ ➣ {اليوزر} .
- ᴍѕɢѕ ➣ {الرسائل} .
- ѕᴛᴀᴛѕ ➣ {الرتبه} .
- ʏᴏᴜʀ ɪᴅ ➣ {الايدي} .
- ᴇᴅɪᴛ ᴍsɢ ➣ {التعديل} .
- ᴅᴇᴛᴀɪʟs ➣ {التفاعل} .
-  ɢᴀᴍᴇ ➣ {المجوهرات} .
{البايو}
''','''
• USE 𖦹 {اليوزر}
• MSG 𖥳 {الرسائل}
• STA 𖦹 {الرتبه}
• iD 𖥳 {الايدي}
{البايو}
''','''
➞: 𝒔𝒕𝒂𓂅 {اليوزر} 𓍯
➞: 𝒖𝒔𝒆𝒓𓂅 {المعرف} 𓍯
➞: 𝒎𝒔𝒈𝒆𓂅 {الرسائل} 𓍯
➞: 𝒊𝒅 𓂅 {الايدي} 𓍯
{البايو}
''','''
♡ : 𝐼𝐷 𖠀 {الايدي} .
♡ : 𝑈𝑆𝐸𝑅 𖠀 {اليوزر} .
♡ : 𝑀𝑆𝐺𝑆 𖠀 {الرسائل} .
♡ : 𝑆𝑇𝐴𝑇𝑆 𖠀 {الرتبه} .
♡ : 𝐸𝐷𝐼𝑇  𖠀 {التعديل} .
{البايو}
''', '''
- الايـدي || {الايدي}.
• الاسـم  || {الاسم}.
• المُعرف || {اليوزر}.
• الرُتبـه || {الرتبه}.
• الرسائل || {الرسائل}.
{البايو}
''', '''
⌁ NaMe ⇨ {الاسم}
⌁ Use ⇨ {اليوزر}
⌁ Msg ⇨ {الرسائل}
⌁ Sta ⇨ {الرتبه}
⌁ iD ⇨ {الايدي}
⌁ Bio ⇨ {البايو}
''', '''
📋¦ ɴᴀᴍᴇ ➺ {الاسم}
🗞¦ ʏᴏᴜʀ ɪᴅ ➺ {الايدي}
🔦¦ ᴜѕᴇʀɴᴀᴍᴇ ➺ {اليوزر}
🕹¦ ѕᴛᴀᴛѕ ➺ {الرتبه}
🔭¦ ᴅᴇᴛᴀɪʟs ➺ {التفاعل}
📨¦  ᴍѕɢѕ ➺ {الرسائل}
🎰¦ ɢᴀᴍᴇ ➺ {المجوهرات}
{البايو}
''', '''
✾ 𝐔𝐒𝐄 ⤷ {اليوزر}
✾ 𝐌𝐒𝐆 ⤷ {الرسائل}
✾ 𝐒𝐓𝐀 ⤷ {الرتبه}
✾ 𝐈𝐃 ⤷ {الايدي}
✾ 𝐁𝐈𝐎 ⤷ {البايو}
''', '''
𓆰 𝑼𝑬𝑺 : {اليوزر}
𓆰 𝑺𝑻𝑨 : {الرتبه}
𓆰 𝑰𝑫 : {الايدي}
𓆰 𝑴𝑺𝑮 : {الرسائل}
{البايو}'''
]


comments = [
  'تيكفه لاتكتب ايدي',
  'يع',
  'جبر',
  'احلى من يكتب ايدي',
  'افخم ايدي',
  'لحد يرسل ايدي من بعده',
  'يلبييه اطلق ايدي',
  'ازق ايدي',
  'لعد تكتب ايدي',
  'للاسف ايديك تلوث بصري ):',
  'جابك الله انت وأيديك على شكل جبر خاطر لقلبّي'
]

# ============ نظام اللايكات الموحد ============
def get_likes_count(user_id, chat_id):
    """الحصول على عدد لايكات المستخدم في المجموعة"""
    key = f'{Dev_Neptune}:likes:{chat_id}:{user_id}'
    # استخدام SET لتخزين المعجبين
    count = r.scard(key)  # عدد العناصر في الـ Set
    return count if count else 0

def has_user_liked(user_id, target_user_id, chat_id):
    """التحقق إذا كان المستخدم قد أعطى لايك للشخص"""
    key = f'{Dev_Neptune}:likes:{chat_id}:{target_user_id}'
    return r.sismember(key, user_id)

def toggle_like(user_id, target_user_id, chat_id):
    """تبديل حالة اللايك (إضافة/إزالة)"""
    key = f'{Dev_Neptune}:likes:{chat_id}:{target_user_id}'
    
    if has_user_liked(user_id, target_user_id, chat_id):
        # إزالة اللايك
        r.srem(key, user_id)
        return False  # تمت الإزالة
    else:
        # إضافة اللايك
        r.sadd(key, user_id)
        return True  # تمت الإضافة

def get_liked_users(user_id, chat_id):
    """الحصول على قائمة الأشخاص الذين أعطوا لايك للشخص"""
    key = f'{Dev_Neptune}:likes:{chat_id}:{user_id}'
    liked_users = r.smembers(key)
    return list(liked_users) if liked_users else []

# ============ زر اللايك في الأيدي ============
@Client.on_callback_query(filters.regex(r'^like_(\d+)_(-?\d+)$'))
def handle_like_button(c, callback_query):
    """معالجة زر اللايك"""
    try:
        # استخراج البيانات من callback_data
        data_parts = callback_query.data.split('_')
        target_user_id = int(data_parts[1])  # المستخدم المستهدف
        chat_id = int(data_parts[2])  # معرف المجموعة
        liker_user_id = callback_query.from_user.id  # المستخدم الذي ضغط على الزر
        
        # منع المستخدم من الإعجاب على نفسه
        if liker_user_id == target_user_id:
            return callback_query.answer("لا يمكنك الإعجاب على نفسك! 🙅", show_alert=True)
        
        # تبديل حالة اللايك
        added = toggle_like(liker_user_id, target_user_id, chat_id)
        
        # الحصول على العدد الجديد
        new_likes_count = get_likes_count(target_user_id, chat_id)
        
        # الحصول على بيانات المستخدم الهدف
        try:
            target_user = c.get_chat(target_user_id)
            target_name = target_user.first_name
        except:
            target_name = "المستخدم"
        
        # تحديث الزر في الرسالة
        like_button = InlineKeyboardButton(f"🤎 {new_likes_count}", callback_data=f"like_{target_user_id}_{chat_id}")
        
        # الحفاظ على الأزرار الأخرى في الرسالة
        original_keyboard = callback_query.message.reply_markup
        new_buttons = []
        
        # نسخ الأزرار الحالية وتحديث زر اللايك فقط
        for row in original_keyboard.inline_keyboard:
            new_row = []
            for button in row:
                if 'like_' in button.callback_data:
                    # استبدال زر اللايك القديم بالجديد
                    new_row.append(like_button)
                else:
                    new_row.append(button)
            new_buttons.append(new_row)
        
        new_keyboard = InlineKeyboardMarkup(new_buttons)
        
        # تحديث الرسالة
        callback_query.edit_message_reply_markup(new_keyboard)
        
        # إظهار إشعار للمستخدم
        if added:
            callback_query.answer(f"تم الإعجاب بـ {target_name} 🤎", show_alert=False)
        else:
            callback_query.answer(f"تم إزالة الإعجاب عن {target_name} ❌", show_alert=False)
            
    except Exception as e:
        print(f"Error handling like callback: {e}")
        callback_query.answer("حدث خطأ في معالجة الإعجاب", show_alert=True)

@Client.on_message(filters.group, group=9)
def addmsgCount(c,m):
   if r.get(f'{m.from_user.id}:mute:{m.chat.id}{Dev_Neptune}'):  return
   if not r.get(f'{Dev_Neptune}{m.chat.id}:TotalMsgs:{m.from_user.id}'):
      r.set(f'{Dev_Neptune}{m.chat.id}:TotalMsgs:{m.from_user.id}', 1)
   else:
      get = int(r.get(f'{Dev_Neptune}{m.chat.id}:TotalMsgs:{m.from_user.id}'))
      r.set(f'{Dev_Neptune}{m.chat.id}:TotalMsgs:{m.from_user.id}', get+1)
   r.set(f"{m.from_user.id}:bankName", m.from_user.first_name[:25])

@Client.on_edited_message(filters.group, group=10)
def addeditedmsgCount(c,m):
   if r.get(f'{m.from_user.id}:mute:{m.chat.id}{Dev_Neptune}'):  return
   if not r.get(f'{m.chat.id}:TotalEDMsgs:{m.from_user.id}{Dev_Neptune}'):
      r.set(f'{m.chat.id}:TotalEDMsgs:{m.from_user.id}{Dev_Neptune}', 1)
   else:
      get = int(r.get(f'{m.chat.id}:TotalEDMsgs:{m.from_user.id}{Dev_Neptune}'))
      r.set(f'{m.chat.id}:TotalEDMsgs:{m.from_user.id}{Dev_Neptune}', get+1)

@Client.on_message(filters.text & filters.group, group=11)
def rankGetHandler(c,m):
   k = r.get(f'{Dev_Neptune}:botkey')
   Thread(target=get_my_rank,args=(c,m,k)).start()

def get_my_rank(c,m,k):
   if not r.get(f'{m.chat.id}:enable:{Dev_Neptune}'):  return
   if r.get(f'{m.chat.id}:mute:{Dev_Neptune}') and not admin_pls(m.from_user.id,m.chat.id):  return
   if r.get(f'{m.from_user.id}:mute:{m.chat.id}{Dev_Neptune}'):  return
   if r.get(f'{m.from_user.id}:mute:{Dev_Neptune}'):  return
   if r.get(f'{m.chat.id}:addCustom:{m.from_user.id}{Dev_Neptune}'):  return
   if r.get(f'{m.chat.id}addCustomG:{m.from_user.id}{Dev_Neptune}'):  return
   if r.get(f'{m.chat.id}:delCustom:{m.from_user.id}{Dev_Neptune}') or r.get(f'{m.chat.id}:delCustomG:{m.from_user.id}{Dev_Neptune}'):  return
   text = m.text
   name = r.get(f'{Dev_Neptune}:BotName') if r.get(f'{Dev_Neptune}:BotName') else 'jack'
   if text.startswith(f'{name} '):
      text = text.replace(f'{name} ','')
   if r.get(f'{m.chat.id}:Custom:{m.chat.id}{Dev_Neptune}&text={text}'):
       text = r.get(f'{m.chat.id}:Custom:{m.chat.id}{Dev_Neptune}&text={text}')
   if r.get(f'Custom:{Dev_Neptune}&text={text}'):
       text = r.get(f'Custom:{Dev_Neptune}&text={text}')
   if isLockCommand(m.from_user.id, m.chat.id, text): return
   
   # ============ أمر لايكاتي ============
   if text in ['لايكاتي', 'لايكي', 'إعجاباتي']:
       likes_count = get_likes_count(m.from_user.id, m.chat.id)
       
       liked_users = get_liked_users(m.from_user.id, m.chat.id)
       if liked_users:
           liked_list = []
           for user_id_str in liked_users[:10]:  # عرض أول 10 أشخاص
               try:
                   user_id = int(user_id_str)
                   user = c.get_chat(user_id)
                   name = user.first_name[:15]
                   liked_list.append(f"• {name}")
               except:
                   liked_list.append(f"• ID: {user_id_str}")
           
           liked_text = "\n".join(liked_list)
           if len(liked_users) > 10:
               liked_text += f"\n• +{len(liked_users) - 10} أكثر..."
       else:
           liked_text = "لا يوجد إعجابات بعد"
       
       response = f'''{k} إحصائيات الإعجابات:

{k} عدد لايكاتك في هذه المجموعة: {likes_count} 🤎

{k} الأشخاص الذين أعجبوا بك:
{liked_text}

{k} لإعطاء لايك لأي شخص، اضغط على زر اللايك في الأيدي'''
       
       m.reply(response)
       return
   
   # ============ أمر لايكات ============
   if text.startswith('لايكات') and m.reply_to_message:
       target_user_id = m.reply_to_message.from_user.id
       likes_count = get_likes_count(target_user_id, m.chat.id)
       
       try:
           target_user = c.get_chat(target_user_id)
           target_name = target_user.first_name
       except:
           target_name = "هذا المستخدم"
       
       response = f'''{k} إحصائيات الإعجابات لـ {target_name}:

{k} عدد لايكاته في هذه المجموعة: {likes_count} 🤎

{k} لإعطاء لايك له، اضغط على زر اللايك في الأيدي'''
       
       m.reply(response)
       return

   if text == 'مجموعاتي':
     if not r.smembers(f'{m.from_user.id}:groups'):
       return m.reply(f'{k} ماعندك مجموعات')
     else:
       groups = len(r.smembers(f'{m.from_user.id}:groups'))
       return m.reply(f'{k} عدد مجموعاتك ↼ ( {groups} )')

   if text == 'انشائي':
      create_date = get_creation_date(m.from_user.id)
      return m.reply(f'{k} الانشاء ( {create_date} )')

   if text == 'الانشاء' and not m.reply_to_message:
      create_date = get_creation_date(m.from_user.id)
      return m.reply(f'{k} الانشاء ( {create_date} )')

   if (text == 'الانشاء' or text == 'انشائه') and m.reply_to_message:
      create_date = get_creation_date(m.reply_to_message.from_user.id)
      return m.reply(f'{k} الانشاء ( {create_date} )')

   if text == 'اسمي':
     return m.reply(m.from_user.first_name, disable_web_page_preview=True)

   if text == 'معلوماتي':
      msgs = int(r.get(f'{Dev_Neptune}{m.chat.id}:TotalMsgs:{m.from_user.id}'))
      if msgs > 50:
        tfa3l = 'شد حيلك'
      if msgs > 500:
        tfa3l = 'يجي منك'
      if msgs > 750:
        tfa3l = 'تفاعل متوسط'
      if msgs > 2500:
        tfa3l = 'متفاعل'
      if msgs > 5000:
        tfa3l = 'اسطورة التفاعل'
      if msgs > 10000:
        tfa3l = 'كنق التلي'
      else:
        tfa3l = 'تفاعل صفر'
      if not r.get(f'{m.chat.id}:TotalEDMsgs:{m.from_user.id}{Dev_Neptune}'):
         edits = 0
      else:
         edits= int(r.get(f'{m.chat.id}:TotalEDMsgs:{m.from_user.id}{Dev_Neptune}'))
      if not r.get(f'{m.chat.id}TotalContacts{m.from_user.id}{Dev_Neptune}'):
         contacts = 0
      else:
         contacts = int(r.get(f'{m.chat.id}TotalContacts{m.from_user.id}{Dev_Neptune}'))
      if hasattr(m.from_user, 'usernames') and m.from_user.usernames:
         username = ''
         for i in m.from_user.usernames: username += f"@{i.username} "
      elif m.from_user.username:
         username = f'@{m.from_user.username}'
      else:
         username = 'ماكو يوزر'
      rank = get_rank(m.from_user.id,m.chat.id)
      # إضافة عدد اللايكات
      likes_count = get_likes_count(m.from_user.id, m.chat.id)
      text = f'''
⚘ المعلومات
❁ الاسم ↼ {m.from_user.mention}
❁ اليوزر ↼ {username}
❁ الايدي  ↼ {m.from_user.id}
❁ الرتبه ↼ {rank}
❁ اللايكات ↼ {likes_count} 🤎
┄─┅═ـ═┅─┄
⚘ احصائيات الرسايل
❁ الرسايل ↼ {msgs}
❁ التعديل ↼ {edits}
❁ التفاعل ↼ {tfa3l}
'''
      return m.reply(text)

   if text == 'بايو' and m.reply_to_message and m.reply_to_message.from_user:
      if r.get(f'{m.chat.id}:disableBio:{Dev_Neptune}'):  return
      get = c.get_chat(m.reply_to_message.from_user.id)
      if not get.bio:
        return m.reply(f'{k} ماعنده بايو')
      else:
        return m.reply(f'`{get.bio}`')

   if text == 'بايو' and not m.reply_to_message:
      if r.get(f'{m.chat.id}:disableBio:{Dev_Neptune}'):  return
      get = c.get_chat(m.from_user.id)
      if not get.bio:
        return m.reply(f'{k} ماعندك بايو')
      else:
        return m.reply(f'`{get.bio}`')

   if text == 'المجموعه' or text == 'المجموعة':
      get = c.invoke(GetFullChannel(channel=c.resolve_peer(m.chat.id)))
      if get.full_chat.exported_invite:
        link = get.full_chat.exported_invite.link
      else:
        link = 'ماكو رابط'
      admins = get.full_chat.admins_count
      kicked = get.full_chat.kicked_count
      count = get.full_chat.participants_count
      if m.chat.photo:
        type = 'photo'
        if m.chat.username:
          photo = f'https://t.me/{m.chat.username}'
        else:
          photo = c.download_media(m.chat.photo.big_file_id)
      else:
        type = 'text'
      text = f'معلومات المجموعة:\n\n{k} الاسم ↢ {m.chat.title}\n{k} الايدي ↢ {m.chat.id}\n{k} عدد الاعضاء ↢ ( {count} )\n{k} عدد المشرفين ↢ ( {admins} )\n{k} عدد المحظورين ↢ ( {kicked} )\n{k} الرابط ↢ {link} '
      if type == 'photo':
         m.reply_photo(photo, caption=text)
         try:
           os.remove(photo)
         except:
           pass
         return
      else:
         return m.reply(text, disable_web_page_preview=True)

   if text == 'جهاتي':
     if not r.get(f'{m.chat.id}TotalContacts{m.from_user.id}{Dev_Neptune}'):
       contacts = 0
     else:
       contacts = int(r.get(f'{m.chat.id}TotalContacts{m.from_user.id}{Dev_Neptune}'))
     return m.reply(f'{k} عدد جهاتك ↢ {contacts}')

   if text == 'افتاري':
     if r.get(f'{m.chat.id}:disableAV:{Dev_Neptune}'): return False
     if not m.from_user.photo:
       return m.reply(f'{k} ماقدر اجيب افتارك ارسل نقطه خاص وارجع جرب')
     else:
       if m.from_user.username:
         photo = f'http://t.me/{m.from_user.username}'
       else:
         for p in c.get_chat_photos(m.from_user.id,limit=1):
           photo = p.file_id
       get_bio = c.get_chat(m.from_user.id).bio
       if not get_bio:
         caption=None
       else:
         caption = f'`{get_bio}`'
       return m.reply_photo(photo,caption=caption)

   if text == 'افتار' and m.reply_to_message and m.reply_to_message.from_user:
     if r.get(f'{m.chat.id}:disableAV:{Dev_Neptune}'): return False
     if not m.reply_to_message.from_user.photo:
       return m.reply(f'{k} مقدر اجيب افتاره يمكن حاظرني')
     else:
       if m.reply_to_message.from_user.username:
         photo = f'http://t.me/{m.reply_to_message.from_user.username}'
       else:
         for p in c.get_chat_photos(m.reply_to_message.from_user.id,limit=1):
           photo = p.file_id
       get_bio = c.get_chat(m.reply_to_message.from_user.id).bio
       if not get_bio:
         caption=None
       else:
         caption = f'`{get_bio}`'
       return m.reply_photo(photo,caption=caption)

   if text == 'ايديي':
     return m.reply(f'( `{m.from_user.id}` )')

   if text.startswith('افتار') and len(text.split()) == 2:
     if r.get(f'{m.chat.id}:disableAV:{Dev_Neptune}'): return False
     try:
       user = int(text.split()[1])
     except:
       user = text.split()[1]
     try:
       get = c.get_chat(user)
       if get.photo:
         for p in c.get_chat_photos(get.id,limit=1):
           photo = p.file_id
         if get.bio:
           caption = f'`{get.bio}`'
         else:
           caption = None
         return m.reply_photo(photo,caption=caption)
     except Exception as e:
       print (e)
       return

   if text == 'رتبتي':
      rank = get_rank(m.from_user.id, m.chat.id)
      m.reply(f'{k} رتبتك ↢ {rank}')

   if text == 'مسح رسائلي' or text == 'مسح رسايلي':
      msgs = int(r.get(f'{Dev_Neptune}{m.chat.id}:TotalMsgs:{m.from_user.id}'))
      r.delete(f'{Dev_Neptune}{m.chat.id}:TotalMsgs:{m.from_user.id}')
      return m.reply(f'{k} تمام مسحت ( {msgs} ) من رسائلك')

   if text == 'مسح تكليجاتي':
      if not r.get(f'{m.chat.id}:TotalEDMsgs:{m.from_user.id}{Dev_Neptune}'):
        return m.reply(f'{k} عدد تكليجاتك ↢ 0')
      msgs = int(r.get(f'{m.chat.id}:TotalEDMsgs:{m.from_user.id}{Dev_Neptune}'))
      r.delete(f'{m.chat.id}:TotalEDMsgs:{m.from_user.id}{Dev_Neptune}')
      return m.reply(f'{k} تمام مسحت ( {msgs} ) من تكليجاتك')

   if text == 'تكليجاتي' or text == 'تعديلاتي':
      if not r.get(f'{m.chat.id}:TotalEDMsgs:{m.from_user.id}{Dev_Neptune}'):
        return m.reply(f'{k} عدد تكليجاتك ↢ 0')
      msgs = int(r.get(f'{m.chat.id}:TotalEDMsgs:{m.from_user.id}{Dev_Neptune}'))
      return m.reply(f'{k} عدد تكليجاتك ↢ {msgs}')

   if text == 'رسايلي' or text == 'رسائلي':
      msgs = int(r.get(f'{Dev_Neptune}{m.chat.id}:TotalMsgs:{m.from_user.id}'))
      return m.reply(f'{k} عدد رسايلك ↢ {msgs}')

   if (text == 'رسايله' or text == 'رسائلة') and m.reply_to_message and m.reply_to_message.from_user:
      msgs = int(r.get(f'{Dev_Neptune}{m.chat.id}:TotalMsgs:{m.reply_to_message.from_user.id}'))
      return m.reply(f'{k} عدد رسايله ↢ {msgs}')

   if text == 'رتبته' and m.reply_to_message and m.reply_to_message.from_user:
      rank = get_rank(m.reply_to_message.from_user.id, m.chat.id)
      status = m.chat.get_member(m.reply_to_message.from_user.id).status
      if status == ChatMemberStatus.OWNER:
        rank2 = 'المالك'
      if status == ChatMemberStatus.ADMINISTRATOR:
        rank2 = 'مشرف'
      if status == ChatMemberStatus.RESTRICTED:
        rank2 = 'مقيد'
      if status == ChatMemberStatus.LEFT:
        rank2 = 'طالع'
      if status == ChatMemberStatus.MEMBER:
        rank2 = 'عضو'
      if status == ChatMemberStatus.BANNED:
        rank2 = 'لاقم حظر'
      m.reply(f'رتبته:\n{k} في البوت ( {rank} )\n{k} في المجموعة ( {rank2} )\n-')

   if text == 'نقل ملكية' or text == 'نقل ملكيه':
     if r.get(f'{m.chat.id}:rankGOWNER:{m.from_user.id}{Dev_Neptune}'):
       status = m.chat.get_member(m.from_user.id).status
       if status == ChatMemberStatus.OWNER:
          return m.reply(f'{k} انت مالك الكروب')
       else:
          for member in m.chat.get_members(filter=ChatMembersFilter.ADMINISTRATORS):
            if member.status == ChatMemberStatus.OWNER:
              if member.user.is_deleted:
                return m.reply(f'{k} حساب المالك محذوف')
              else:
                r.delete(f'{m.chat.id}:rankGOWNER:{m.from_user.id}{Dev_Neptune}')
                r.srem(f'{m.chat.id}:listGOWNER:{Dev_Neptune}', m.from_user.id)
                r.set(f'{m.chat.id}:rankGOWNER:{member.user.id}{Dev_Neptune}')
                r.sadd(f'{m.chat.id}:listGOWNER:{Dev_Neptune}', member.user.id)
                return m.reply(f'「 {member.user.mention} 」\n{k} نقلت له ملكية المجموعة')

   if text == "مسح المتفاعلين" or text == "تصفير المتفاعلين":
     if not owner_pls(m.from_user.id, m.chat.id):
       return m.reply(f'{k} عذراً الامر يخص ↤〖 المالك 〗فقط .')
     else:
       keys = r.keys(f"{Dev_Neptune}{m.chat.id}:TotalMsgs:*")
       for _ in keys: r.delete(_)
       return m.reply(f"{k} تمام مسحت كل المتفاعلين")

   if text == "مسح الكروبات" or text == "تصفير الكروبات":
     if not devp_pls(m.from_user.id, m.chat.id):
       return m.reply(f'{k} عذراً الامر يخص ↤〖 مبرمج🎖️ 〗فقط .')
     else:
       keys = r.keys(f"{Dev_Neptune}:TotalGroupMsgs:*")
       for _ in keys: r.delete(_)
       return m.reply(f"{k} تمام مسحت توب الكروبات")

   if text == "ترتيبي" or text == "تفاعلي":
     users = r.keys(f"{Dev_Neptune}{m.chat.id}:TotalMsgs:*")
     jj = []
     for user in users:
          try:
            id = int(user.split("TotalMsgs:")[1])
            msgs = r.get(user)
            jj.append({"id": id, "msgs": int(msgs)})
          except:
            pass
     top = get_top(jj)
     ids = [i["id"] for i in top]
     rank = ids.index(m.from_user.id) + 1
     msgs = int(r.get(f"{Dev_Neptune}{m.chat.id}:TotalMsgs:{m.from_user.id}"))
     return m.reply(f"{k} ترتيبك بالمتفاعلين ↢ {rank}\n{k} رسائلك بالتفاعل ↢ {msgs:,}\n-")

   if text == "المتفاعلين" or text == "توب المتفاعلين":
        users = r.keys(f"{Dev_Neptune}{m.chat.id}:TotalMsgs:*")
        jj = []
        for user in users:
                  try:
                    id = int(user.split("TotalMsgs:")[1])
                    msgs = r.get(user)
                    name = r.get(f"{id}:bankName") or str(id)
                    jj.append({"name": name, "id": id, "msgs": int(msgs)})
                  except:
                    pass
        top = get_top(jj)
        text = "- توب اكثر 20 متفاعل :\n━━━━━━━━━\n"
        count = 1
        for i in top:
            if count == 21: break
            emoji = get_emoji_bank(count)
            text += f"{emoji}{i['msgs']:,} l [{i['name']}](tg://user?id={i['id']})\n"
            count +=1
        return c.send_message(m.chat.id, text, disable_web_page_preview=True, reply_to_message_id=m.id)

   if text == "الكروبات" or text == "توب الكروبات":
        groups = r.keys(f"{Dev_Neptune}:TotalGroupMsgs:*")
        result = []

        for group in groups:
            try:
                chat_id = int(group.split("TotalGroupMsgs:")[1])
                msgs = r.get(group)
                group_title = c.get_chat(chat_id).title
                result.append({"group_title": group_title, "chat_id": chat_id, "msgs": int(msgs)})
            except:
                pass

        top_groups = get_top(result)
        response_text = "- توب اكثر 20 كروب متفاعل:\n━━━━━━━━━\n"
        count = 1

        for group in top_groups:
            if count == 21:
                break
            emoji = get_emoji_bank(count)
            response_text += f"{emoji}{group['msgs']:,} l {group['group_title']}\n"
            count += 1

        return c.send_message(m.chat.id, response_text, disable_web_page_preview=True, reply_to_message_id=m.id)

   if text == 'كشف' and m.reply_to_message and m.reply_to_message.from_user:
       try:
           get = m.chat.get_member(m.reply_to_message.from_user.id)
           rank = get_rank(m.reply_to_message.from_user.id, m.chat.id)
           name = m.reply_to_message.from_user.first_name
           msgs = int(r.get(f'{Dev_Neptune}{m.chat.id}:TotalMsgs:{m.reply_to_message.from_user.id}'))
           id = m.reply_to_message.from_user.id
           if m.reply_to_message.from_user.username:
               username = f'@{m.reply_to_message.from_user.username}'
           elif hasattr(m.reply_to_message.from_user, 'usernames') and m.reply_to_message.from_user.usernames:
               username = ''
               for i in m.reply_to_message.from_user.usernames: username += f"@{i.username} "
           else:
               username = 'ماكو يوزر'
           status = m.chat.get_member(m.reply_to_message.from_user.id).status
           if status == ChatMemberStatus.OWNER:
               rank2 = 'المالك'
           if status == ChatMemberStatus.ADMINISTRATOR:
               rank2 = 'مشرف'
           if status == ChatMemberStatus.RESTRICTED:
               rank2 = 'مقيد'
           if status == ChatMemberStatus.LEFT:
               rank2 = 'طالع'
           if status == ChatMemberStatus.MEMBER:
               rank2 = 'عضو'
           if status == ChatMemberStatus.BANNED:
               rank2 = 'لاقم حظر'
           # إضافة عدد اللايكات
           likes_count = get_likes_count(m.reply_to_message.from_user.id, m.chat.id)
           text = f'''
{k} الاسم ↢ {name}
{k} الايدي ↢ {id}
{k} اليوزر : ( {username} )
{k} الرتبه ↢ ( {rank} )
{k} الرسائل ↢ ( {msgs} )
{k} اللايكات ↢ ( {likes_count} 🤎 )
{k} بالمجموعة ↢ ( {rank2} )
{k} نوع الكشف ↢ بالرد
-
'''
           return m.reply(text, disable_web_page_preview=True)
       except:
           return m.reply(f'{k} العضو مو بالمجموعة')

   if text.startswith('كشف') and len(text.split()) > 1 and 'tg://user?id=' in m.text.html:
       user = int(re.search(r'href="([^"]+)', m.text.html).group(1).split('=')[1])
       ks = 'بالمنشن'
       try:
           get = m.chat.get_member(user)
           name = get.user.first_name
           id = get.user.id
           msgs = int(r.get(f'{Dev_Neptune}{m.chat.id}:TotalMsgs:{get.user.id}'))
           if get.user.username:
               username = f'@{get.user.username}'
           elif hasattr(get.user, 'usernames') and get.user.usernames:
               username = ""
               for i in get.user.usernames: username += f"@{i.username} "
           else:
               username = 'ماعنده يوزر'
           status = get.status
           if status == ChatMemberStatus.OWNER:
               rank = 'المالك'
           if status == ChatMemberStatus.ADMINISTRATOR:
               rank = 'مشرف'
           if status == ChatMemberStatus.RESTRICTED:
               rank = 'مقيد'
           if status == ChatMemberStatus.LEFT:
               rank = 'طالع'
           if status == ChatMemberStatus.MEMBER:
               rank = 'عضو'
           if status == ChatMemberStatus.BANNED:
               rank = 'لاقم حظر'
       except:
           rank = 'طالع'
           try:
               get = c.get_chat(user)
               name = get.first_name
               id = get.id
               msgs = int(r.get(f'{Dev_Neptune}{m.chat.id}:TotalMsgs:{get.id}'))
               if get.user.username:
                   username = f'@{get.user.username}'
               if hasattr(get.user, 'usernames') and get.user.usernames:
                   username = ""
                   for i in get.user.usernames: username += f"@{i.username} "
               else:
                   username = 'ماعنده يوزر'
           except Exception as e:
               print(e)
               return
       rank2 = get_rank(id, m.chat.id)
       # إضافة عدد اللايكات
       likes_count = get_likes_count(id, m.chat.id)
       text = f'''
{k} الاسم ↢ {name}
{k} الايدي ↢{id}
{k} اليوزر : ↢ ( {username} )
{k} الرتبه ↢ ({rank2} )
{k} الرسائل ↢ ( {msgs} )
{k} اللايكات ↢ ( {likes_count} 🤎 )
{k} بالمجموعة ↢ ( {rank} )
{k} نوع الكشف ↢ {ks}
-
        '''
       return m.reply(text, disable_web_page_preview=True)

   if text.startswith('كشف') and len(text.split()) == 2:
       try:
           user = int(text.split()[1])
           ks = 'بالايدي'
       except:
           user = text.split()[1].replace('@', '')
           ks = 'باليوزر'
       try:
           get = m.chat.get_member(user)
           name = get.user.first_name
           id = get.user.id
           msgs = int(r.get(f'{Dev_Neptune}{m.chat.id}:TotalMsgs:{get.user.id}'))
           if get.user.username:
               username = f'@{get.user.username}'
           elif hasattr(get.user, 'usernames') and get.user.usernames:
               username = ""
               for i in get.user.usernames: username += f"@{i.username} "
           else:
               username = 'ماعنده يوزر'
           status = get.status
           if status == ChatMemberStatus.OWNER:
               rank = 'المالك'
           if status == ChatMemberStatus.ADMINISTRATOR:
               rank = 'مشرف'
           if status == ChatMemberStatus.RESTRICTED:
               rank = 'مقيد'
           if status == ChatMemberStatus.LEFT:
               rank = 'طالع'
           if status == ChatMemberStatus.MEMBER:
               rank = 'عضو'
           if status == ChatMemberStatus.BANNED:
               rank = 'لاقم حظر'
       except:
           rank = 'طالع'
           try:
               get = c.get_chat(user)
               name = get.first_name
               id = get.id
               msgs = int(r.get(f'{Dev_Neptune}{m.chat.id}:TotalMsgs:{get.id}'))
               if get.user.username:
                   username = f'@{get.user.username}'
               if hasattr(get.user, 'usernames') and get.user.usernames:
                   username = ""
                   for i in get.user.usernames: username += f"@{i.username} "
               else:
                   username = 'ماعنده يوزر'
           except Exception as e:
               print(e)
               return
       rank2 = get_rank(id, m.chat.id)
       # إضافة عدد اللايكات
       likes_count = get_likes_count(id, m.chat.id)
       text = f'''
{k} الاسم ↢ {name}
{k} الايدي ↢{id}
{k} اليوزر : ↢ ( {username} )
{k} الرتبه ↢ ({rank2} )
{k} الرسائل ↢ ( {msgs} )
{k} اللايكات ↢ ( {likes_count} 🤎 )
{k} بالمجموعة ↢ ( {rank} )
{k} نوع الكشف ↢ {ks}
-
        '''
       return m.reply(text, disable_web_page_preview=True)

   if text == 'صلاحياته' and m.reply_to_message and m.reply_to_message.from_user:
      get = m.chat.get_member(m.reply_to_message.from_user.id)
      if not get.status in [ChatMemberStatus.ADMINISTRATOR,ChatMemberStatus.OWNER]:
         return m.reply(f'{k} هو العضو وما عنده صلاحيات')
      if get.status == ChatMemberStatus.OWNER:
         return m.reply(f'{k} هو المالك وعنده كل الصلاحيات')
      if get.status == ChatMemberStatus.ADMINISTRATOR:
         p = get.privileges
         p1 = "✔️" if p.can_manage_chat else "✖️"
         p2 = "✔️" if p.can_delete_messages else "✖️"
         p3 = "✔️" if p.can_manage_video_chats else "✖️"
         p4 = "✔️" if p.can_restrict_members else "✖️"
         p5 = "✔️" if p.can_promote_members else "✖️"
         p6 = "✔️" if p.can_change_info else "✖️"
         p7 = "✔️" if p.can_pin_messages else "✖️"
         text = f'''
{k} هو مشرف وهذي صلاحياته :

1) - ادارة المجموعة ↼ ( {p1} )
2) - مسح الرسائل ↼ ( {p2} )
3) - ادارة مكالمات ↼ ( {p3} )
4) - تقييد الأعضاء وحظرهم ↼ ( {p4} )
5) - رفع المشرفين ↼ ( {p5} )
6) - تعديل معلومات المجموعة ↼ ( {p6} )
7) - تثبيت الرسايل ↼ ( {p7} )


'''
         return m.reply(text)

   if text == 'صلاحياتي':
      get = m.chat.get_member(m.from_user.id)
      if not get.status in [ChatMemberStatus.ADMINISTRATOR,ChatMemberStatus.OWNER]:
         return m.reply(f'{k} انت العضو وماعندك صلاحيات')
      if get.status == ChatMemberStatus.OWNER:
         return m.reply(f'{k} انت المالك وعندك كل الصلاحيات')
      if get.status == ChatMemberStatus.ADMINISTRATOR:
         p = get.privileges
         p1 = "✔️" if p.can_manage_chat else "✖️"
         p2 = "✔️" if p.can_delete_messages else "✖️"
         p3 = "✔️" if p.can_manage_video_chats else "✖️"
         p4 = "✔️" if p.can_restrict_members else "✖️"
         p5 = "✔️" if p.can_promote_members else "✖️"
         p6 = "✔️" if p.can_change_info else "✖️"
         p7 = "✔️" if p.can_pin_messages else "✖️"
         text = f'''
{k} انت مشرف وهذي صلاحياتك :

1) - ادارة المجموعة ↼ ( {p1} )
2) - مسح الرسائل ↼ ( {p2} )
3) - ادارة مكالمات ↼ ( {p3} )
4) - تقييد الأعضاء وحظرهم ↼ ( {p4} )
5) - رفع المشرفين ↼ ( {p5} )
6) - تعديل معلومات المجموعة ↼ ( {p6} )
7) - تثبيت الرسايل ↼ ( {p7} )


'''
         return m.reply(text)

   if r.get(f'{m.chat.id}:addCustomID:{m.from_user.id}{Dev_Neptune}') and text == 'الغاء':
     r.delete(f'{m.chat.id}:addCustomID:{m.from_user.id}{Dev_Neptune}')
     m.reply(f'{k} تمام تم الغاء تعيين الايدي ')
     return

   if r.get(f'{m.chat.id}:addCustomIDG:{m.from_user.id}{Dev_Neptune}') and text == 'الغاء':
     r.delete(f'{m.chat.id}:addCustomIDG:{m.from_user.id}{Dev_Neptune}')
     m.reply(f'{k} تمام تم الغاء تعيين الايدي عام')
     return

   if r.get(f'{m.chat.id}:addCustomIDG:{m.from_user.id}{Dev_Neptune}') and dev_pls(m.from_user.id, m.chat.id):
      r.set(f'customID:{Dev_Neptune}', m.text)
      m.reply(f'{k} وسوينا الايدي العام\n{k} تكدر تجرب شكل الايدي الجديد هسة')
      r.delete(f'{m.chat.id}:addCustomIDG:{m.from_user.id}{Dev_Neptune}')
      return

   if r.get(f'{m.chat.id}:addCustomID:{m.from_user.id}{Dev_Neptune}') and mod_pls(m.from_user.id, m.chat.id):
      r.set(f'{m.chat.id}:customID:{Dev_Neptune}', m.text)
      m.reply(f'{k} وسوينا الايدي\n{k} تكدر تجرب شكل الايدي الجديد هسة')
      r.delete(f'{m.chat.id}:addCustomID:{m.from_user.id}{Dev_Neptune}')
      return

   if text == 'مسح الايدي':
      if not mod_pls(m.from_user.id, m.chat.id):
        return m.reply(f'{k} عذراً الامر يخص ↤〖 المدير 〗فقط .')
      if not r.get(f'{m.chat.id}:customID:{Dev_Neptune}'):
        return m.reply(f'{k} الايدي مو معدل')
      else:
        m.reply(f'{k} تمام مسحت الايدي')
        r.delete(f'{m.chat.id}:customID:{Dev_Neptune}')
        return

   if text == 'مسح الايدي العام' or text == 'مسح الايدي عام':
      if not dev2_pls(m.from_user.id, m.chat.id):
        return m.reply(f'{k} عذراً الامر يخص ↤〖 مطور ثانوي🎖 〗فقط .')
      if not r.get(f'customID:{Dev_Neptune}'):
        return m.reply(f'{k} الايدي العام مو معدل')
      else:
        m.reply(f'{k} تمام مسحت الايدي العام')
        r.delete(f'customID:{Dev_Neptune}')

   if text == 'الايدي':
      if not mod_pls(m.from_user.id, m.chat.id):
        return
      if not r.get(f'{m.chat.id}:customID:{Dev_Neptune}'):
        return m.reply(f'{k} الايدي مو معدل')
      else:
        id = r.get(f'{m.chat.id}:customID:{Dev_Neptune}')
        return m.reply(f'`{id}`')

   if text == 'الايدي العام':
      if not dev2_pls(m.from_user.id, m.chat.id):
        return
      if not r.get(f'customID:{Dev_Neptune}'):
        return m.reply(f'{k} الايدي العام مو معدل')
      else:
        id = r.get(f'customID:{Dev_Neptune}')
        return m.reply(f'`{id}`')

   if text == 'تغيير الايدي':
      if not mod_pls(m.from_user.id, m.chat.id):
        return m.reply(f'{k} عذراً الامر يخص ↤〖 المدير 〗فقط .')
      else:
        current_index = 0
        id_template = custom_ids[current_index]

        if hasattr(m.from_user, 'usernames') and m.from_user.usernames:
           username = ''
           for i in m.from_user.usernames: username += f"@{i.username} "
        elif m.from_user.username:
           username = f'@{m.from_user.username}'
        else:
           username = 'ماكو يوزر'

        rank = get_rank(m.from_user.id, m.chat.id)
        msg = int(r.get(f'{Dev_Neptune}{m.chat.id}:TotalMsgs:{m.from_user.id}')) if r.get(f'{Dev_Neptune}{m.chat.id}:TotalMsgs:{m.from_user.id}') else 0
        msgs = f"{msg}"
        iD = f'`{m.from_user.id}`'
        if not r.get(f'{m.chat.id}:TotalEDMsgs:{m.from_user.id}{Dev_Neptune}'):
           edits = 0
        else:
           edit= int(r.get(f'{m.chat.id}:TotalEDMsgs:{m.from_user.id}{Dev_Neptune}'))
           edits = f"{edit}"
        name = m.from_user.first_name
        create = get_creation_date(m.from_user.id)
        get_chat = c.get_chat(m.from_user.id)
        if get_chat.bio :
           bio = get_chat.bio
        else:
           bio = 'ماكو بايو'
        if msg > 50:
          tfa3l = 'شد حيلك'
        if msg > 500:
          tfa3l = 'يجي منك'
        if msg > 750:
          tfa3l = 'تفاعل متوسط'
        if msg > 2500:
          tfa3l = 'متفاعل'
        if msg > 5000:
          tfa3l = 'اسطورة التفاعل'
        if msg > 10000:
          tfa3l = 'اسطورة التلي'
        else:
          tfa3l = 'تفاعل صفر'
        comment = random.choice(comments)

        preview_text = id_template.replace('{الاسم}', name).replace('{اليوزر}', username).replace('{الرسائل}',str(msgs)).replace('{التعديل}', str(edits)).replace('{الانشاء}', create).replace('{البايو}', f'{bio}').replace('{الايدي}', iD).replace('{الرتبه}', rank).replace('{التفاعل}', tfa3l).replace('{تعليق}', comment)

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("•  التالي  •", callback_data=f"id_next:{current_index}:{m.from_user.id}"),
                InlineKeyboardButton("•  السابق  •", callback_data=f"id_prev:{current_index}:{m.from_user.id}")
            ],
            [
                InlineKeyboardButton("•  تعيين  •", callback_data=f"id_set:{current_index}:{m.from_user.id}")
            ]
        ])

        header_text = f"{k} معاينة النموذج ({current_index + 1}/{len(custom_ids)}):\n\n"
        full_text = header_text + preview_text

        return m.reply(full_text, disable_web_page_preview=True, reply_markup=keyboard)

   if text == 'تعيين الايدي':
      if not mod_pls(m.from_user.id, m.chat.id):
        return m.reply(f'{k} عذراً الامر يخص ↤〖 المدير 〗فقط .')
      reply = '''
تمام , هسة ارسل شكل الايدي الجديد

- الاختصارات:

{الاسم} ↼ يطلع اسم الشخص
{الايدي} ↼ يطلع ايدي الشخص
{اليوزر} ↼ يطلع يوزر الشخص
{الرتبه} ↼ يطلع رتبته الشخص
{التفاعل} ↼ يطلع تفاعل الشخص
{الرسائل} ↼ يطلع كم رسالة عند الشخص
{التعديل} ↼ يطلع كم مره عدل الشخص
{البايو} ↼ يطلع البايو اللي كاتبه
{تعليق} ↼ يطلع تعليق عشوائي
{الانشاء} ↼ يطلع انشاء الحساب
{لايكات} ↼ يطلع عدد اللايكات في المجموعة

قناة اشكال الايدي https://t.me/IIIIIlI8

'''
      m.reply(reply)
      r.set(f'{m.chat.id}:addCustomID:{m.from_user.id}{Dev_Neptune}', 1)
      return
   if text == 'تعيين الايدي عام':
      if not dev2_pls(m.from_user.id, m.chat.id):
        return m.reply(f'{k} عذراً الامر يخص ↤〖 مطور ثانوي🎖 〗فقط .')
      reply = '''
تمام , هسة ارسل شكل الايدي الجديد

- الاختصارات:

{الاسم} ↼ يطلع اسم الشخص
{الايدي} ↼ يطلع ايدي الشخص
{اليوزر} ↼ يطلع يوزر الشخص
{الرتبه} ↼ يطلع رتبته الشخص
{التفاعل} ↼ يطلع تفاعل الشخص
{الرسائل} ↼ يطلع كم رسالة عند الشخص
{التعديل} ↼ يطلع كم مره عدل الشخص
{البايو} ↼ يطلع البايو اللي كاتبه
{تعليق} ↼ يطلع تعليق عشوائي
{الانشاء} ↼ يطلع انشاء الحساب
{لايكات} ↼ يطلع عدد اللايكات في المجموعة

قناة اشكال الايدي https://t.me/OO0U1/187
'''
      m.reply(reply)
      r.set(f'{m.chat.id}:addCustomIDG:{m.from_user.id}{Dev_Neptune}', 1)
      return True

   if text == 'تفعيل الايدي':
     if not admin_pls(m.from_user.id,m.chat.id):
       return m.reply(f'{k} عذراً الامر يخص ↤〖 الادمن 〗فقط .')
     else:
       if not r.get(f'{m.chat.id}:disableID:{Dev_Neptune}'):
         return m.reply(f'{k} بواسطة ↤ {m.from_user.mention}\n{k} الايدي مفعل من قبل')
       else:
         r.delete(f'{m.chat.id}:disableID:{Dev_Neptune}')
         return m.reply(f'{k} بواسطة ↤ {m.from_user.mention}\n{k} تمام فعلت الايدي')

   if text == 'تعطيل الايدي':
     if not admin_pls(m.from_user.id,m.chat.id):
       return m.reply(f'{k} عذراً الامر يخص ↤〖 الادمن 〗فقط .')
     else:
       if r.get(f'{m.chat.id}:disableID:{Dev_Neptune}'):
         return m.reply(f'{k} بواسطة ↤ {m.from_user.mention}\n{k} الايدي معطل من قبل')
       else:
         r.set(f'{m.chat.id}:disableID:{Dev_Neptune}',1)
         return m.reply(f'{k} بواسطة ↤ {m.from_user.mention}\n{k} تمام عطلت الايدي')

   if text == 'تفعيل افتاري':
     if not admin_pls(m.from_user.id,m.chat.id):
       return m.reply(f'{k} عذراً الامر يخص ↤〖 الادمن 〗فقط .')
     else:
       if not r.get(f'{m.chat.id}:disableAV:{Dev_Neptune}'):
         return m.reply(f'{k} بواسطة ↤ {m.from_user.mention}\n{k} افتار مفعل من قبل')
       else:
         r.delete(f'{m.chat.id}:disableAV:{Dev_Neptune}')
         return m.reply(f'{k} بواسطة ↤ {m.from_user.mention}\n{k} تمام فعلت افتار')

   if text == 'تعطيل افتاري':
     if not admin_pls(m.from_user.id,m.chat.id):
       return m.reply(f'{k} عذراً الامر يخص ↤〖 الادمن 〗فقط .')
     else:
       if r.get(f'{m.chat.id}:disableAV:{Dev_Neptune}'):
         return m.reply(f'{k} بواسطة ↤ {m.from_user.mention}\n{k} افتار معطل من قبل')
       else:
         r.set(f'{m.chat.id}:disableAV:{Dev_Neptune}',1)
         return m.reply(f'{k} بواسطة ↤ {m.from_user.mention}\n{k} تمام عطلت افتار')

   if text == 'تعطيل الايدي بالصوره':
     if not admin_pls(m.from_user.id,m.chat.id):
       return m.reply(f'{k} عذراً الامر يخص ↤〖 الادمن 〗فقط .')
     else:
       if r.get(f'{m.chat.id}:disableIDPHOTO:{Dev_Neptune}'):
         return m.reply(f'{k} بواسطة ↤ {m.from_user.mention}\n{k} الايدي بالصوره معطل من قبل')
       else:
         r.set(f'{m.chat.id}:disableIDPHOTO:{Dev_Neptune}',1)
         return m.reply(f'{k} بواسطة ↤ {m.from_user.mention}\n{k} تمام عطلت الايدي بالصوره')

   if text == 'تفعيل الايدي بالصوره':
     if not admin_pls(m.from_user.id,m.chat.id):
       return m.reply(f'{k} عذراً الامر يخص ↤〖 الادمن 〗فقط .')
     else:
       if not r.get(f'{m.chat.id}:disableIDPHOTO:{Dev_Neptune}'):
         return m.reply(f'{k} بواسطة ↤ {m.from_user.mention}\n{k} الايدي بالصوره مفعل من قبل')
       else:
         r.delete(f'{m.chat.id}:disableIDPHOTO:{Dev_Neptune}')
         return m.reply(f'{k} بواسطة ↤ {m.from_user.mention}\n{k} تمام فعلت الايدي بالصوره')

   if text == "لقبي":
     title = m.chat.get_member(m.from_user.id).custom_title
     if not title:
       return m.reply(f"{k} ماعندك لقب")
     else:
       return m.reply(f"{k} لقبك ↢ ( {title} )")

   if (text == 'ايدي' or text.lower() == 'ا') and m.reply_to_message and m.reply_to_message.from_user:
       return m.reply(f'الايدي ↢ ( `{m.reply_to_message.from_user.id}` )')

   if (text == 'ايدي' or text.lower() == 'id') and not m.reply_to_message:
      if r.get(f'{m.chat.id}:disableID:{Dev_Neptune}'):  return
      if r.get(f'{m.chat.id}:customID:{Dev_Neptune}'):
         id = r.get(f'{m.chat.id}:customID:{Dev_Neptune}')
      else:
         if r.get(f'customID:{Dev_Neptune}'):
           id = r.get(f'customID:{Dev_Neptune}')
         else:
           id = '''
𖡋 𝐔𝐒𝐄 ⌯  {اليوزر}
𖡋 𝐌𝐒𝐆 ⌯  {الرسائل}
𖡋 𝐒𝐓𝐀 ⌯  {الرتبه}
𖡋 𝐈𝐃 ⌯  {الايدي}
𖡋 𝐄𝐃𝐈𝐓 ⌯  {التعديل}
𖡋 𝐂𝐑  ⌯  {الانشاء}
{البايو}'''
      if hasattr(m.from_user, 'usernames') and m.from_user.usernames:
         username = ''
         for i in m.from_user.usernames: username += f"@{i.username} "
      elif m.from_user.username:
         username = f'@{m.from_user.username}'
      else:
         username = 'ماكو يوزر'
      rank = get_rank(m.from_user.id, m.chat.id)
      msg = int(r.get(f'{Dev_Neptune}{m.chat.id}:TotalMsgs:{m.from_user.id}'))
      msgs = f"{msg}"
      iD = f'`{m.from_user.id}`'
      if not r.get(f'{m.chat.id}:TotalEDMsgs:{m.from_user.id}{Dev_Neptune}'):
         edits = 0
      else:
         edit= int(r.get(f'{m.chat.id}:TotalEDMsgs:{m.from_user.id}{Dev_Neptune}'))
         edits = f"{edit}"
      name = m.from_user.first_name
      create = get_creation_date(m.from_user.id)
      get_chat = c.get_chat(m.from_user.id)
      if get_chat.bio :
         bio = get_chat.bio
      else:
         bio = 'ماكو بايو'
      if msg > 50:
        tfa3l = 'شد حيلك'
      if msg > 500:
        tfa3l = 'يجي منك'
      if msg > 750:
        tfa3l = 'تفاعل متوسط'
      if msg > 2500:
        tfa3l = 'متفاعل'
      if msg > 5000:
        tfa3l = 'اسطورة التفاعل'
      if msg > 10000:
        tfa3l = 'اسطورة التلي'
      else:
        tfa3l = 'تفاعل صفر'
      comment = random.choice(comments)
      
      # إضافة عدد اللايكات
      likes_count = get_likes_count(m.from_user.id, m.chat.id)
      
      # تحديث النص ليشمل اللايكات إذا كانت موجودة
      if '{لايكات}' in id:
          id_with_likes = id.replace('{لايكات}', str(likes_count))
      else:
          id_with_likes = id + f'\n𖡋 𝐋𝐈𝐊𝐄 ⌯ {likes_count} 🤎'
      
      text = id_with_likes.replace('{الاسم}', name).replace('{اليوزر}', username).replace('{الرسائل}',str(msgs)).replace('{التعديل}', str(edits)).replace('{الانشاء}', create).replace('{البايو}', f'{bio}').replace('{الايدي}', iD).replace('{الرتبه}', rank).replace('{التفاعل}', tfa3l).replace('{تعليق}', comment)

      # إضافة زر اللايك
      likes_count = get_likes_count(m.from_user.id, m.chat.id)
      like_button = InlineKeyboardButton(f"🤎 {likes_count}", callback_data=f"like_{m.from_user.id}_{m.chat.id}")

      if m.from_user.username:
         chat_url = f"https://t.me/{m.from_user.username}"
         keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{name}", url=chat_url)],
            [like_button]
         ])
      else:
         keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{name} ليس لديه معرف", callback_data="no_username")],
            [like_button]
         ])

      if r.get(f'{m.chat.id}:disableIDPHOTO:{Dev_Neptune}'):
         return m.reply(text, disable_web_page_preview=True, reply_markup=keyboard)
      else:
         if m.from_user.photo:
           get_user = c.invoke(GetFullUser(id=(c.resolve_peer(m.from_user.id))))
           photo = get_user.full_user.profile_photo
           video = photo.video_sizes
           if video:
             if len(video) == 3:
               video = video[-2]
             else:
               video = video[-1]
           if video:
              file = BytesIO()
              hash = photo.access_hash
              if r.get(f"{hash}:{m.from_user.id}"):
                return m.reply_animation(r.get(f"{hash}:{m.from_user.id}"), caption=text, reply_markup=keyboard)
              for byte in c.stream_media(
                message=FileId(
                  file_type=FileType.PHOTO,
                  dc_id=photo.dc_id, media_id=photo.id,
                  access_hash=photo.access_hash,
                  file_reference=photo.file_reference,
                  thumbnail_source=ThumbnailSource.THUMBNAIL,
                  thumbnail_file_type=FileType.PHOTO,
                  thumbnail_size=video.type,
                  volume_id=0, local_id=0
                ).encode()
              ):
                file.write(byte)
              file.name = f'{m.from_user.id}vid{m.chat.id}.mp4'
              send = m.reply_animation(file, caption=text, reply_markup=keyboard)
              r.set(f"{hash}:{m.from_user.id}",send.animation.file_id,ex=3600)
              return True
           else:
              file_id=FileId(
                        file_type=FileType.PHOTO,
                        dc_id=photo.dc_id,
                        media_id=photo.id,
                        access_hash=photo.access_hash,
                        file_reference=photo.file_reference,
                        thumbnail_source=ThumbnailSource.THUMBNAIL,
                        thumbnail_file_type=FileType.PHOTO,
                        thumbnail_size=photo.sizes[0].type,
                        volume_id=0,
                        local_id=0
                    ).encode()
              return m.reply_photo(file_id, caption=text, reply_markup=keyboard)
         else:
           return m.reply(text, disable_web_page_preview=True, reply_markup=keyboard)

@Client.on_message(filters.new_chat_members, group=1)
def addContact(c,m):
  for me in m.new_chat_members:
    if not m.from_user.id == me.id:
      if not r.get(f'{m.chat.id}TotalContacts{m.from_user.id}{Dev_Neptune}'):
        r.set(f'{m.chat.id}TotalContacts{m.from_user.id}{Dev_Neptune}',1)
      else:
        co = int(r.get(f'{m.chat.id}TotalContacts{m.from_user.id}{Dev_Neptune}'))
        r.set(f'{m.chat.id}TotalContacts{m.from_user.id}{Dev_Neptune}',co+1)

# معالج callback للحالة التي لا يملك فيها المستخدم username
@Client.on_callback_query(filters.regex(r'^no_username$'))
def handle_no_username_callback(c, callback_query):
    callback_query.answer("هذا المستخدم لا يملك معرف (@username) لذلك لا يمكن إنشاء رابط مباشر للمحادثة", show_alert=True)

# معالجات callback لأزرار تغيير الهوية
@Client.on_callback_query(filters.regex(r'^id_(prev|next|set):(\d+):(\d+)$'))
def handle_id_template_callback(c, callback_query):
    k = r.get(f'{Dev_Neptune}:botkey')
    action, current_index, user_id = callback_query.data.split(':')
    current_index = int(current_index)
    user_id = int(user_id)

    if callback_query.from_user.id != user_id:
        return callback_query.answer("هذا الأمر ليس لك!", show_alert=True)

    if not mod_pls(callback_query.from_user.id, callback_query.message.chat.id):
        return callback_query.answer("عذراً الامر يخص المدير فقط", show_alert=True)

    if action == 'id_set':
        selected_template = custom_ids[current_index]
        r.set(f'{callback_query.message.chat.id}:customID:{Dev_Neptune}', selected_template)
        callback_query.answer("√ تم تعيين النموذج بنجاح!", show_alert=True)
        new_text = f"{k} √ تم تعيين النموذج رقم ({current_index + 1})\n{k} تكدر تجرب شكل الايدي الجديد هسة"
        return callback_query.edit_message_text(new_text)

    elif action == 'id_prev':
        new_index = (current_index - 1) % len(custom_ids)
    elif action == 'id_next':
        new_index = (current_index + 1) % len(custom_ids)

    m = callback_query.message
    user = callback_query.from_user
    id_template = custom_ids[new_index]

    if hasattr(user, 'usernames') and user.usernames:
       username = ''
       for i in user.usernames: username += f"@{i.username} "
    elif user.username:
       username = f'@{user.username}'
    else:
       username = 'ماكو يوزر'

    rank = get_rank(user.id, m.chat.id)
    msg = int(r.get(f'{Dev_Neptune}{m.chat.id}:TotalMsgs:{user.id}')) if r.get(f'{Dev_Neptune}{m.chat.id}:TotalMsgs:{user.id}') else 0
    msgs = f"{msg}"
    iD = f'`{user.id}`'
    if not r.get(f'{m.chat.id}:TotalEDMsgs:{user.id}{Dev_Neptune}'):
       edits = 0
    else:
       edit= int(r.get(f'{m.chat.id}:TotalEDMsgs:{user.id}{Dev_Neptune}'))
       edits = f"{edit}"
    name = user.first_name
    create = get_creation_date(user.id)
    get_chat = c.get_chat(user.id)
    if get_chat.bio :
       bio = get_chat.bio
    else:
       bio = 'ماكو بايو'
    if msg > 50:
      tfa3l = 'شد حيلك'
    if msg > 500:
      tfa3l = 'يجي منك'
    if msg > 750:
      tfa3l = 'تفاعل متوسط'
    if msg > 2500:
      tfa3l = 'متفاعل'
    if msg > 5000:
      tfa3l = 'اسطورة التفاعل'
    if msg > 10000:
      tfa3l = 'اسطورة التلي'
    else:
      tfa3l = 'تفاعل صفر'
    comment = random.choice(comments)

    preview_text = id_template.replace('{الاسم}', name).replace('{اليوزر}', username).replace('{الرسائل}',str(msgs)).replace('{التعديل}', str(edits)).replace('{الانشاء}', create).replace('{البايو}', f'{bio}').replace('{الايدي}', iD).replace('{الرتبه}', rank).replace('{التفاعل}', tfa3l).replace('{تعليق}', comment)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("•  التالي  •", callback_data=f"id_next:{new_index}:{user.id}"),
            InlineKeyboardButton("•  السابق  •", callback_data=f"id_prev:{new_index}:{user.id}")
        ],
        [
            InlineKeyboardButton("•  تعيين  •", callback_data=f"id_set:{new_index}:{user.id}")
        ]
    ])

    header_text = f"{k} معاينة النموذج ({new_index + 1}/{len(custom_ids)}):\n\n"
    full_text = header_text + preview_text

    try:
        callback_query.edit_message_text(full_text, disable_web_page_preview=True, reply_markup=keyboard)
        callback_query.answer()
    except Exception as e:
        print(f"Error updating message: {e}")
        callback_query.answer("حدث خطأ في تحديث الرسالة", show_alert=True)