import os, random, re, time
from threading import Thread
from pyrogram import *
from pyrogram.enums import *
from pyrogram.types import *
from config import *
from helpers.Ranks import *
from yt_dlp import YoutubeDL

print("YouTube plugin loaded ✅")
print("Custom commands plugin loaded ✅")

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

SOURCE_BUTTON = InlineKeyboardMarkup([
    [InlineKeyboardButton("sᴏᴜʀᴄᴇ ᴊᴀᴄᴋ", url="https://t.me/Jack_Vib")]
])

# ============ YouTube Audio Handler ============
@Client.on_message(
    (filters.private | filters.group) &
    filters.text &
    (
        filters.regex(r".+ !!$") |
        filters.regex(r"^يوت .+")
    )
)
async def youtube_audio(client, message):
    """تحميل الأغاني من اليوتيوب"""
    
    # تفعيل البوت في المجموعة ضروري
    if not r.get(f'{message.chat.id}:enable:{Dev_Neptune}'):
        return
    
    text = message.text.strip()

    if text.endswith(" !!"):
        query = text.replace(" !!", "").strip()
    else:
        query = text.replace("ابحثلي ", "").strip()

    if not query:
        return await message.reply_text("‹: اكتب اسم الأغنية :›")

    wait = await message.reply_text("- جاري البحث، يرجى الإنتظار...")

    ydl_opts = {
        "format": "bestaudio",
        "outtmpl": f"{DOWNLOAD_DIR}/%(id)s.%(ext)s",
        "quiet": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)
            video = info["entries"][0]
            file_path = f"{DOWNLOAD_DIR}/{video['id']}.mp3"

        await wait.delete()

        await message.reply_audio(
            audio=file_path,
            title=video.get("title"),
            performer=video.get("uploader", "YouTube"),
            caption="• By - SOURCE JACK .",
            reply_markup=SOURCE_BUTTON
        )

        # تنظيف الملف بعد الإرسال
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        await wait.edit("× - فشل تحميل الصوت")
        print(f"YouTube Error: {e}")

# ============ Custom Commands Handler ============
@Client.on_message(filters.text & filters.group, group=999)
def customCommandHandler(c,m):
    k = r.get(f'{Dev_Neptune}:botkey')
    Thread(target=addcommand,args=(c,m,k)).start()


def addcommand(c,m,k):
   if not r.get(f'{m.chat.id}:enable:{Dev_Neptune}'):  return
   if r.get(f'{m.from_user.id}:mute:{m.chat.id}{Dev_Neptune}'):  return
   if r.get(f'{m.from_user.id}:mute:{Dev_Neptune}'):  return
   if r.get(f'{m.chat.id}:mute:{Dev_Neptune}') and not admin_pls(m.from_user.id,m.chat.id):  return
   text = m.text
   name = r.get(f'{Dev_Neptune}:BotName') if r.get(f'{Dev_Neptune}:BotName') else 'jack'
   if text.startswith(f'{name} '):
      text = text.replace(f'{name} ','')
   if r.get(f'{m.chat.id}:Custom:{m.chat.id}{Dev_Neptune}&text={text}'):
       text = r.get(f'{m.chat.id}:Custom:{m.chat.id}{Dev_Neptune}&text={text}')
   if r.get(f'Custom:{Dev_Neptune}&text={text}'):
       text = r.get(f'Custom:{Dev_Neptune}&text={text}')
   if isLockCommand(m.from_user.id, m.chat.id, text): return
   if r.get(f'{m.chat.id}:addCustom:{m.from_user.id}{Dev_Neptune}') and text == 'الغاء':
     r.delete(f'{m.chat.id}:addCustom:{m.from_user.id}{Dev_Neptune}')
     return m.reply(quote=True,text=f'{k} من عيوني لغيت اضافة امر ')

   if r.get(f'{m.chat.id}:addCustom2:{m.from_user.id}{Dev_Neptune}') and text == 'الغاء':
     r.delete(f'{m.chat.id}:addCustom2:{m.from_user.id}{Dev_Neptune}')
     return m.reply(quote=True,text=f'{k} من عيوني لغيت اضافة امر ')

   if re.search("^ترتيب الاوامر$", text):
      if not owner_pls(m.from_user.id, m.chat.id):
          return m.reply(quote=True,text=f'{k} هذا الامر يخص ( المالك وفوق ) وبس')
      else:
          ar = {
              "ا":"ايدي",
              "م":"رفع مميز",
              "اد":"رفع ادمن",
              "مد":"رفع مدير",
              "تعط":"تعطيل الايدي بالصوره",
              "تفع":"تفعيل الايدي بالصوره",
              "ر":"الرابط",
              "تغ":"تغيير الايدي",
              "رف":"رفع القيود",
              "مع":"معاني",
              "حذ":"حذف رد",
              "رد":"اضف رد",
              "رر":"الردود",
              "ق ك":"قفل الكل",
              "ف ت":"فتح الكل",
              "ام":"امسح",
              "ت":"تثبيت",
              "،،":"مسح المكتومين",
              "الغ":"الغاء الحظر",
              "رس":"مسح رسائلي",
              "تك":"تنزيل الكل",
              "فف":"فتح الاشعارات",
              "قق":"قفل الاشعارات",
              "ك":"كشف",
              "ند":"نداء",
              "ثن":"ثنائي",
              "اساسي":"رفع مطور اساسي",
              "ثانوي":"رفع مطور ثانوي",
              "زز":"زوجني",
              "طط":"طلاق",
              "ز":"زواج",
          }

          # إضافة الأوامر المختصرة
          added_commands = []
          for short_cmd, full_cmd in ar.items():
              r.set(f'{m.chat.id}:Custom:{m.chat.id}{Dev_Neptune}&text={short_cmd}', full_cmd)
              r.sadd(f'{m.chat.id}:listCustom:{m.chat.id}{Dev_Neptune}', short_cmd)
              added_commands.append(f'{short_cmd} - {full_cmd} -')

          response_text = f'{k} تم ترتيب الاوامر التالية:\n\n'
          for i, cmd in enumerate(added_commands, 1):
              response_text += f'{i}) {cmd}\n'
          response_text += '•'

          return m.reply(quote=True, text=response_text)

   if text == 'الاوامر المضافه' or text == 'الاوامر المضافة':
      if not owner_pls(m.from_user.id, m.chat.id):
          return m.reply(quote=True,text=f'{k} هذا الامر يخص ( المالك وفوق ) وبس')
      else:
          if not r.smembers(f'{m.chat.id}:listCustom:{m.chat.id}{Dev_Neptune}'):
            return m.reply(quote=True,text=f'{k} ماكو اوامر مضافه')
          else:
              text = 'الاوامر المضافة:\n'
              count = 0
              for cmnd in r.smembers(f'{m.chat.id}:listCustom:{m.chat.id}{Dev_Neptune}'):
                 count += 1
                 command = cmnd
                 cc = r.get(f'{m.chat.id}:Custom:{m.chat.id}{Dev_Neptune}&text={command}')
                 old_c = cc
                 text += f'{count}) {command} ~ ( {old_c} )\n'
              text += '\n༄'
              return m.reply(quote=True,text=text)

   if text == 'اضف امر' or text == 'تغيير امر':
     if not r.get(f'{m.chat.id}:addCustom:{m.from_user.id}{Dev_Neptune}'):
       if not owner_pls(m.from_user.id, m.chat.id):
          return m.reply(quote=True,text=f'{k} هذا الامر يخص ( المالك وفوق ) وبس')
       else:
          r.set(f'{m.chat.id}:addCustom:{m.from_user.id}{Dev_Neptune}',1)
          m.reply(quote=True,text=f'{k} تمام عيني ، ارسل الامر القديم علمود اغيره')
          return

   if r.get(f'{m.chat.id}:addCustom:{m.from_user.id}{Dev_Neptune}') and admin_pls(m.from_user.id, m.chat.id) and len(m.text) < 50:
      r.delete(f'{m.chat.id}:addCustom:{m.from_user.id}{Dev_Neptune}')
      r.set(f'{m.chat.id}:addCustom2:{m.from_user.id}{Dev_Neptune}', m.text)
      m.reply(quote=True,text=f'{k} حلو علمود تغيير امر ( {m.text} )\n{k} ارسل الامر الجديد هسة √')
      return

   if r.get(f'{m.chat.id}:addCustom2:{m.from_user.id}{Dev_Neptune}') and admin_pls(m.from_user.id, m.chat.id) and len(m.text) < 50:
      command_o = r.get(f'{m.chat.id}:addCustom2:{m.from_user.id}{Dev_Neptune}')
      command_n = m.text
      r.delete(f'{m.chat.id}:addCustom2:{m.from_user.id}{Dev_Neptune}')
      r.set(f'{m.chat.id}:Custom:{m.chat.id}{Dev_Neptune}&text={command_n}', command_o)
      r.sadd(f'{m.chat.id}:listCustom:{m.chat.id}{Dev_Neptune}', command_n)
      m.reply(quote=True,text=f'{k} غيرت الامر القديم {command_o}\n{k} الى الامر الجديد ( {command_n} )')
      return

   # أمر النداء
   if text == 'نداء':
      if not admin_pls(m.from_user.id, m.chat.id):
         return m.reply(quote=True, text=f'{k} ⇜ هذا الأمر يخص ( الادمن وفوق ) بس')

      call_messages = [
         "يـا قمـري ❤️‍🔥",
         "حنسوي العاب تعا 🌚💗",
         "وين طامس يحلو 🌚❤️‍🔥 : ~ 💕💕",
         "تعا نورنه 😉🤍 : ~",
         "مس يحلو 🌚🤍 : ~",
         "تعال لك وين طامس : ~",
         "الطف مخلوق حياتي 💖 : ~",
         "تعا نورنه 😉🤍 : ~"
      ]

      try:
         members_list = []
         for member in m.chat.get_members(limit=200):
            if (member.user and
                not member.user.is_deleted and
                not member.user.is_bot and
                member.user.id != m.from_user.id):
               members_list.append(member.user)

         if not members_list:
            return m.reply(quote=True, text=f'{k} ماكو أعضاء متاحين للنداء')

         random_member = random.choice(members_list)
         random_message = random.choice(call_messages)

         if random_member.username:
            mention = f"@{random_member.username}"
         else:
            mention = f"[{random_member.first_name}](tg://user?id={random_member.id})"

         m.reply(quote=True, text=f"• {random_message} {mention}")

      except Exception as e:
         print(f"خطأ في أمر النداء: {e}")
         return m.reply(quote=True, text=f'{k} حدث خطأ في تنفيذ الأمر')

      return

   # أمر ثنائي
   if text == 'ثنائي':
      if not mod_pls(m.from_user.id, m.chat.id):
         return m.reply(quote=True, text=f'{k} ⇜ هذا الأمر يخص ( المدير وفوق ) بس')

      try:
         members_list = []
         for member in m.chat.get_members(limit=200):
            if (member.user and
                not member.user.is_deleted and
                not member.user.is_bot and
                member.user.id != m.from_user.id):
               members_list.append(member.user)

         if len(members_list) < 2:
            return m.reply(quote=True, text=f'{k} يجب وجود عضوين على الأقل في المجموعة')

         selected_members = random.sample(members_list, 2)
         member1 = selected_members[0]
         member2 = selected_members[1]

         if member1.username:
            mention1 = f"@{member1.username}"
         else:
            mention1 = f"[{member1.first_name}](tg://user?id={member1.id})"

         if member2.username:
            mention2 = f"@{member2.username}"
         else:
            mention2 = f"[{member2.first_name}](tg://user?id={member2.id})"

         response_text = f"- ثنائي اليوم\n - {mention1} + {mention2}"
         m.reply(quote=True, text=response_text)

      except Exception as e:
         print(f"خطأ في أمر ثنائي: {e}")
         return m.reply(quote=True, text=f'{k} حدث خطأ في تنفيذ الأمر')

      return


@Client.on_message(filters.text & filters.group, group=1000)
def delCustomCommandHandler(c,m):
    k = r.get(f'{Dev_Neptune}:botkey')
    Thread(target=delcommand,args=(c,m,k)).start()


def delcommand(c,m,k):
   if not r.get(f'{m.chat.id}:enable:{Dev_Neptune}'):  return
   if r.get(f'{m.from_user.id}:mute:{m.chat.id}{Dev_Neptune}'):  return
   if r.get(f'{m.from_user.id}:mute:{Dev_Neptune}'):  return
   if r.get(f'{m.chat.id}:mute:{Dev_Neptune}') and not admin_pls(m.from_user.id,m.chat.id):  return
   if r.get(f'{m.chat.id}addCustomG:{m.from_user.id}{Dev_Neptune}'):  return
   text = m.text
   if r.get(f'{m.chat.id}:Custom:{m.chat.id}{Dev_Neptune}&text={m.text}'):
       text = r.get(f'{m.chat.id}:Custom:{m.chat.id}{Dev_Neptune}&text={m.text}')

   if r.get(f'Custom:{Dev_Neptune}&text={m.text}'):
       text = r.get(f'Custom:{Dev_Neptune}&text={m.text}')

   if isLockCommand(m.from_user.id, m.chat.id, text): return
   if r.get(f'{m.chat.id}:delCustom:{m.from_user.id}{Dev_Neptune}') and text == 'الغاء':
     r.delete(f'{m.chat.id}:delCustom:{m.from_user.id}{Dev_Neptune}')
     return m.reply(quote=True,text=f'{k} من عيوني لغيت مسح امر ')

   if text == 'مسح الاوامر' or text == 'مسح الاوامر المضافة':
     if not mod_pls(m.from_user.id, m.chat.id):
       return m.reply(quote=True,text=f'{k} هذا الامر يخص ( المدير وفوق ) وبس')
     else:
       if not r.smembers(f'{m.chat.id}:listCustom:{m.chat.id}{Dev_Neptune}'):
         return m.reply(quote=True,text=f'{k} ماكو اوامر مضافه')
       else:
         count = 0
         for cmnd in r.smembers(f'{m.chat.id}:listCustom:{m.chat.id}{Dev_Neptune}'):
           command = cmnd
           r.delete(f'{m.chat.id}:Custom:{m.chat.id}{Dev_Neptune}&text={command}')
           r.srem(f'{m.chat.id}:listCustom:{m.chat.id}{Dev_Neptune}', command)
           count += 1
         text = f'من「 {m.from_user.mention} 」\n{k} تمام مسحت {count} أمر √'
         return m.reply(quote=True,text=text)


   if text == 'مسح امر':
     if not r.get(f'{m.chat.id}:delCustom:{m.from_user.id}{Dev_Neptune}'):
       if not mod_pls(m.from_user.id, m.chat.id):
          return m.reply(quote=True,text=f'{k} هذا الامر يخص ( المدير وفوق ) وبس')
       else:
          r.set(f'{m.chat.id}:delCustom:{m.from_user.id}{Dev_Neptune}',1)
          m.reply(quote=True,text=f'{k} ارسل الامر هسة')
          return


   if r.get(f'{m.chat.id}:delCustom:{m.from_user.id}{Dev_Neptune}') and admin_pls(m.from_user.id, m.chat.id) and len(m.text) < 50:
      r.delete(f'{m.chat.id}:delCustom:{m.from_user.id}{Dev_Neptune}')
      if not r.get(f'{m.chat.id}:Custom:{m.chat.id}{Dev_Neptune}&text={m.text}'):
         return m.reply(quote=True,text=f'{k} هذا الأمر مو مضاف')
      r.srem(f'{m.chat.id}:listCustom:{m.chat.id}{Dev_Neptune}', m.text)
      r.delete(f'{m.chat.id}:Custom:{m.chat.id}{Dev_Neptune}&text={m.text}')
      m.reply(quote=True,text=f'{k} من「 {m.from_user.mention} 」\n{k} تمام مسحت الأمر √')
      return




############ global CustomCommand

@Client.on_message(filters.text, group=1001)
def customCommandGlobalHandler(c,m):
    k = r.get(f'{Dev_Neptune}:botkey')
    Thread(target=addcommandg,args=(c,m,k)).start()


def addcommandg(c,m,k):
   if r.get(f'{m.from_user.id}:mute:{m.chat.id}{Dev_Neptune}'):  return
   if r.get(f'{m.from_user.id}:mute:{Dev_Neptune}'):  return
   if r.get(f'{m.chat.id}:mute:{Dev_Neptune}') and not admin_pls(m.from_user.id,m.chat.id):  return
   text = m.text
   if r.get(f'Custom:{Dev_Neptune}&text={m.text}'):
       text = r.get(f'Custom:{Dev_Neptune}&text={m.text}')

   if r.get(f'{m.chat.id}addCustomG:{m.from_user.id}{Dev_Neptune}') and text == 'الغاء':
     r.delete(f'{m.chat.id}addCustomG:{m.from_user.id}{Dev_Neptune}')
     return m.reply(quote=True,text=f'{k} من عيوني لغيت اضف امر عام')

   if r.get(f'{m.chat.id}:addCustom2G:{m.from_user.id}{Dev_Neptune}') and text == 'الغاء':
     r.delete(f'{m.chat.id}:addCustom2G:{m.from_user.id}{Dev_Neptune}')
     return m.reply(quote=True,text=f'{k} من عيوني لغيت اضف امر عام')

   if text == 'الاوامر العامه' or text == 'الاوامر المضافه العامه' and not m.chat.type == ChatType.PRIVATE:
      if not dev_pls(m.from_user.id, m.chat.id):
          return m.reply(quote=True,text=f'{k} هذا الامر يخص ( المطور وفوق ) وبس')
      else:
          if not r.smembers(f'listCustom:{Dev_Neptune}'):
            return m.reply(quote=True,text=f'{k} ماكو اوامر عامه مضافه')
          else:
              text = 'الاوامر العامه:\n'
              count = 0
              for cmnd in r.smembers(f'listCustom:{Dev_Neptune}'):
                 count += 1
                 command = cmnd
                 cc = r.get(f'Custom:{Dev_Neptune}&text={command}')
                 old_c = cc
                 text += f'{count}) {command} ~ ( {old_c} )\n'
              text += '•'
              return m.reply(quote=True,text=text)

   if text == 'اضف امر عام' or text == 'تغيير امر عام':
     if not r.get(f'{m.chat.id}addCustomG:{m.from_user.id}{Dev_Neptune}'):
       if not dev_pls(m.from_user.id, m.chat.id):
          return m.reply(quote=True,text=f'{k} هذا الامر يخص ( المطور وفوق ) وبس')
       else:
          r.set(f'{m.chat.id}addCustomG:{m.from_user.id}{Dev_Neptune}',1)
          m.reply(quote=True,text=f'{k} تمام عيني ، ارسل الامر القديم علمود اغيره')
          return

   if r.get(f'{m.chat.id}addCustomG:{m.from_user.id}{Dev_Neptune}') and dev_pls(m.from_user.id, m.chat.id) and len(m.text) < 50:
      r.delete(f'{m.chat.id}addCustomG:{m.from_user.id}{Dev_Neptune}')
      r.set(f'{m.chat.id}:addCustom2G:{m.from_user.id}{Dev_Neptune}', m.text)
      m.reply(quote=True,text=f'{k} حلو علمود تغيير امر ( {m.text} )\n{k} ارسل الامر الجديد هسة √')
      return

   if r.get(f'{m.chat.id}:addCustom2G:{m.from_user.id}{Dev_Neptune}') and dev_pls(m.from_user.id, m.chat.id) and len(m.text) < 50:
      command_o = r.get(f'{m.chat.id}:addCustom2G:{m.from_user.id}{Dev_Neptune}')
      command_n = m.text
      r.delete(f'{m.chat.id}:addCustom2G:{m.from_user.id}{Dev_Neptune}')
      r.set(f'Custom:{Dev_Neptune}&text={command_n}', command_o)
      r.sadd(f'listCustom:{Dev_Neptune}', command_n)
      m.reply(quote=True,text=f'{k} غيرت الامر القديم {command_o}\n{k} الى الامر الجديد ( {command_n} )')
      return


@Client.on_message(filters.text , group=1002)
def delCustomCommandGHandler(c,m):
    k = r.get(f'{Dev_Neptune}:botkey')
    Thread(target=delcommandg,args=(c,m,k)).start()


def delcommandg(c,m,k):
   if r.get(f'{m.from_user.id}:mute:{m.chat.id}{Dev_Neptune}'):  return
   if r.get(f'{m.chat.id}:mute:{Dev_Neptune}') and not admin_pls(m.from_user.id,m.chat.id):  return
   if r.get(f'{m.from_user.id}:mute:{Dev_Neptune}'):  return
   text = m.text
   if r.get(f'Custom:{Dev_Neptune}&text={m.text}'):
       text = r.get(f'Custom:{Dev_Neptune}&text={m.text}')

   if r.get(f'{m.chat.id}:delCustomG:{m.from_user.id}{Dev_Neptune}') and text == 'الغاء':
     r.delete(f'{m.chat.id}:delCustomG:{m.from_user.id}{Dev_Neptune}')
     return m.reply(quote=True,text=f'{k} من عيوني لغيت مسح امر عام')

   if text == 'مسح الاوامر العامه':
     if not dev_pls(m.from_user.id, m.chat.id):
       return m.reply(quote=True,text=f'{k} هذا الامر يخص ( المطور وفوق ) وبس')
     else:
       if not r.smembers(f'listCustom:{Dev_Neptune}'):
         return m.reply(quote=True,text=f'{k} ماكو اوامر عامه مضافه')
       else:
         count = 0
         for cmnd in r.smembers(f'listCustom:{Dev_Neptune}'):
           command = cmnd
           r.delete(f'Custom:{Dev_Neptune}&text={command}')
           r.srem(f'listCustom:{Dev_Neptune}', command)
           count += 1
         text = f'من「 {m.from_user.mention} 」\n{k} تمام مسحت {count} أمر عام √'
         return m.reply(quote=True,text=text)


   if text == 'مسح امر عام':
     if not r.get(f'{m.chat.id}:delCustomG:{m.from_user.id}{Dev_Neptune}'):
       if not dev_pls(m.from_user.id, m.chat.id):
          return m.reply(quote=True,text=f'{k} هذا الامر يخص ( المطور وفوق ) وبس')
       else:
          r.set(f'{m.chat.id}:delCustomG:{m.from_user.id}{Dev_Neptune}',1)
          m.reply(quote=True,text=f'{k} ارسل الامر هسة')
          return

   if re.match("^فتح امر ",text):
     if not gowner_pls(m.from_user.id, m.chat.id):
       return m.reply(quote=True,text=f'{k} هذا الامر يخص ( المالك الاساسي وفوق ) وبس')
     else:
       txt=text.split(None,2)[2]
       if not r.hget(Dev_Neptune+f"locks-{m.chat.id}", txt):
         return m.reply("الامر مو مقفول من قبل")
       r.hdel(Dev_Neptune+f"locks-{m.chat.id}", txt)
       return m.reply("تم فتح الامر بنجاح")

   if text == "الاوامر المقفوله":
      if not gowner_pls(m.from_user.id, m.chat.id):
       return m.reply(quote=True,text=f'{k} هذا الامر يخص ( المالك الاساسي وفوق ) وبس')
      else:
        if not r.hgetall(Dev_Neptune+f"locks-{m.chat.id}"):
          return m.reply(f"{k} ماكو اوامر مقفولة")
        else:
          commands = r.hgetall(Dev_Neptune+f"locks-{m.chat.id}")
          txt = "الاوامر المقفوله:\n\n"
          count = 1
          for command in commands:
            cc = int(commands[command])
            if cc == 0:
              rank = "مالك اساسي"
            elif cc == 1:
              rank = "مالك وفوق"
            elif cc == 2:
              rank = "مدير و فوق"
            elif cc == 3:
              rank = "ادمن وفوق"
            elif cc == 4:
              rank = "مميز و فوق"
            txt += f"{count} ) {command} - ( {rank} )\n"
            count += 1
          return m.reply(txt, disable_web_page_preview=True)

   if text == "مسح الاوامر المقفوله":
      if not gowner_pls(m.from_user.id, m.chat.id):
       return m.reply(quote=True,text=f'{k} هذا الامر يخص ( المالك الاساسي وفوق ) وبس')
      else:
        if not r.hgetall(Dev_Neptune+f"locks-{m.chat.id}"):
          return m.reply(f"{k} ماكو اوامر مقفولة")
        else:
          count = len(list(r.hgetall(Dev_Neptune+f"locks-{m.chat.id}").keys()))
          r.delete(Dev_Neptune+f"locks-{m.chat.id}")
          return m.reply(f"{k} تمام مسحت ( {count} )")

   if re.match("^قفل امر ",text):
     if not gowner_pls(m.from_user.id, m.chat.id):
       return m.reply(quote=True,text=f'{k} هذا الامر يخص ( المالك الاساسي وفوق ) وبس')
     else:
       txt=text.split(None,2)[2]
       return m.reply(
          f"{k} حسناً عزيزي اختار نوع الرتبه :\n{k} سيتم وضع امر ↤︎( {txt} ) له فقط",
          reply_markup=InlineKeyboardMarkup(
            [
              [
                InlineKeyboardButton (
                   "مالك اساسي",
                   callback_data=f"gowner+{m.from_user.id}"
                )
              ],
              [
                InlineKeyboardButton (
                   "مالك",
                   callback_data=f"owner+{m.from_user.id}"
                )
              ],
              [
                InlineKeyboardButton (
                   "مدير",
                   callback_data=f"mod+{m.from_user.id}"
                )
              ],
              [
                InlineKeyboardButton (
                   "ادمن",
                   callback_data=f"admin+{m.from_user.id}"
                )
              ],
              [
                InlineKeyboardButton (
                   "مميز",
                   callback_data=f"pre+{m.from_user.id}"
                )
              ]
            ]
          )
       )

   if r.get(f'{m.chat.id}:delCustomG:{m.from_user.id}{Dev_Neptune}') and dev_pls(m.from_user.id, m.chat.id) and len(m.text) < 50:
      r.delete(f'{m.chat.id}:delCustomG:{m.from_user.id}{Dev_Neptune}')
      if not r.get(f'Custom:{Dev_Neptune}&text={m.text}'):
         return m.reply(quote=True,text=f'{k} هذا الأمر مو مضاف')
      r.srem(f'listCustom:{Dev_Neptune}', m.text)
      r.delete(f'Custom:{Dev_Neptune}&text={m.text}')
      m.reply(quote=True,text=f'{k} من「 {m.from_user.mention} 」\n{k} تمام مسحت الأمر العا √')
      return