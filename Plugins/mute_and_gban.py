import random, re, time
from threading import Thread
from pyrogram import *
from pyrogram.enums import *
from pyrogram.types import *
from pyrogram.errors import *
from config import *
from helpers.Ranks import *
from helpers.Ranks import isLockCommand


@Client.on_message(filters.text & filters.group, group=20)
def mutesHandler(c,m):
    k = r.get(f'{Dev_Neptune}:botkey')
    Thread(target=mute_func,args=(c,m,k)).start()
    
    
def mute_func(c,m,k):
   if not r.get(f'{m.chat.id}:enable:{Dev_Neptune}'):  return
   if r.get(f'{m.chat.id}:mute:{Dev_Neptune}') and not admin_pls(m.from_user.id,m.chat.id):  return
   if r.get(f'{m.chat.id}:addCustom:{m.from_user.id}{Dev_Neptune}'):  return 
   if r.get(f'{m.chat.id}:addCustomG:{m.from_user.id}{Dev_Neptune}'):  return
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


   if text == 'كتم' and m.reply_to_message and m.reply_to_message.from_user:
        id = m.reply_to_message.from_user.id
        mention = m.reply_to_message.from_user.mention
        if not mod_pls(m.from_user.id,m.chat.id):
           return m.reply(f'{k} هذا الامر يخص ( المدير وفوق ) بس')
        if id == m.from_user.id:
           return m.reply('شبيك تريد تنزل نفسك')
        if pre_pls(id, m.chat.id):
           rank = get_rank(id,m.chat.id)
           return m.reply(f'{k} هييه ما تكدر تكتم {rank} ياغبي!')
        if r.get(f'{id}:mute:{m.chat.id}{Dev_Neptune}'):
          return m.reply(f'「 {mention} 」\n{k} مكتوم من قبل ✔')
        else:
          r.set(f'{id}:mute:{m.chat.id}{Dev_Neptune}', 1)
          r.sadd(f'{m.chat.id}:listMUTE:{Dev_Neptune}', id)
          return m.reply(f'「 {mention} 」\n{k} كتمته ✔')
   
   if re.match("^كتم عام (.*?)$", text) and len(text.split()) ==  3:
      if not '@' in text and not re.findall('[0-9]+', text):
          return
      if not dev_pls(m.from_user.id,m.chat.id):
           return m.reply(f'{k} هذا الامر يخص ( المطور وفوق ) بس')      
      user = text.split()[2]
      try:
        id = int(user)
      except:
        id = user.replace('@','')
      try:
         get = c.get_chat(user)
         mention = f'[{get.first_name}](tg://user?id={get.id})'
         id = get.id
      except:
         return m.reply(f'{k} ماكو يوزر هيج')
      if dev_pls(id, m.chat.id):
         rank = get_rank(id,m.chat.id)
         return m.reply(f'{k} هييه ما تكدر تكتم {rank} ياغبي!')
      if r.get(f'{id}:mute:{Dev_Neptune}'):
          return m.reply(f'「 {mention} 」\n{k} مكتوم عام من قبل ✔')
      else:
          r.set(f'{id}:mute:{Dev_Neptune}', 1)
          r.sadd(f'listMUTE:{Dev_Neptune}', id)
          return m.reply(f'「 {mention} 」\n{k} كتمته عام ✔')

   if re.match("^كتم (.*?)$", text) and len(text.split()) == 2:
      if not '@' in text and not re.findall('[0-9]+', text):
          return
      if not admin_pls(m.from_user.id,m.chat.id):
         return m.reply(f'{k} هذا الامر يخص ( الادمن وفوق ) بس')
      user = text.split()[1]
      try:
        id = int(user)
      except:
        id = user.replace('@','')
      try:
         get = c.get_chat(user)
         mention = f'[{get.first_name}](tg://user?id={get.id})'
         id = get.id
      except:
         return m.reply(f'{k} ماكو يوزر هيج')
      if id == m.from_user.id:
        return m.reply('شبيك تريد تنزل نفسك')
      if r.get(f'{id}:mute:{m.chat.id}{Dev_Neptune}'):
         return m.reply(f'「 {mention} 」\n{k} مكتوم من قبل ✔')
      if pre_pls(id, m.chat.id):
         rank = get_rank(id,m.chat.id)
         return m.reply(f'{k} هييه ما تكدر تكتم {rank} ياغبي!')
      r.set(f'{id}:mute:{m.chat.id}{Dev_Neptune}', 1)
      r.sadd(f'{m.chat.id}:listMUTE:{Dev_Neptune}', id)
      return m.reply(f'「 {mention} 」\n{k} كتمته ✔')
   
   if text == 'الغاء الكتم' and m.reply_to_message and m.reply_to_message.from_user:
        id = m.reply_to_message.from_user.id
        mention = m.reply_to_message.from_user.mention
        if not admin_pls(m.from_user.id,m.chat.id):
           return m.reply(f'{k} هذا الامر يخص ( الادمن وفوق ) بس')
        if not r.get(f'{id}:mute:{m.chat.id}{Dev_Neptune}'):
          return m.reply(f'「 {mention} 」\n{k} مو مكتوم قبل ✔')
        else:
          r.delete(f'{id}:mute:{m.chat.id}{Dev_Neptune}')
          r.srem(f'{m.chat.id}:listMUTE:{Dev_Neptune}', id)
          return m.reply(f'「 {mention} 」\n{k} تمام الغيت كتمه\n༄')
   
   if re.match("^الغاء الكتم العام (.*?)$", text) and len(text.split()) ==  4:
      if not '@' in text and not re.findall('[0-9]+', text):
          return
      if not dev_pls(m.from_user.id,m.chat.id):
           return m.reply(f'{k} هذا الأمر يخص ( مطور اساسي🎖 وفوق ) بس')
      user = text.split()[3]
      try:
        id = int(user)
      except:
        id = user.replace('@','')
      try:
         get = c.get_chat(user)
         mention = f'[{get.first_name}](tg://user?id={get.id})'
         id = get.id
      except:
         id = re.findall('[0-9]+', text)[0] if re.findall('[0-9]+', text) else None
         if not id:  return m.reply(f"{k} ماكو مستخدم هيج")
         mention = f'[{id}](tg://user?id={id})'
      if not r.get(f'{id}:mute:{Dev_Neptune}'):
          return m.reply(f'「 {mention} 」\n{k} مو مكتوم عام من قبل ✔')
      else:
          r.delete(f'{id}:mute:{Dev_Neptune}')
          r.srem(f'listMUTE:{Dev_Neptune}',id)
          return m.reply(f'「 {mention} 」\n{k} لغيت كتمته عام ✔')

   if re.match("^الغاء الكتم (.*?)$", text) and len(text.split()) ==  3:
      if not '@' in text and not re.findall('[0-9]+', text):
          return
      if not mod_pls(m.from_user.id,m.chat.id):
         return m.reply(f'{k} هذا الامر يخص ( المدير وفوق ) بس')
      user = text.split()[2]
      try:
        id = int(user)
      except:
        id = user.replace('@','')
      try:
         get = c.get_chat(user)
         mention = f'[{get.first_name}](tg://user?id={get.id})'
         id = get.id
      except:
         id = re.findall('[0-9]+', text)[0] if re.findall('[0-9]+', text) else None
         if not id:  return m.reply(f"{k} ماكو مستخدم هيج")
         mention = f'[{id}](tg://user?id={id})'
      if not r.get(f'{id}:mute:{m.chat.id}{Dev_Neptune}'):
         return m.reply(f'「 {mention} 」\n{k} مو مكتوم من قبل ✔')
      r.delete(f'{id}:mute:{m.chat.id}{Dev_Neptune}')
      r.srem(f'{m.chat.id}:listMUTE:{Dev_Neptune}', id)
      return m.reply(f'「 {mention} 」\n{k} أبشر الغيت كتمه ✔')
   
   if re.match("^حظر عام (.*?)$", text) and len(text.split()) ==  3:
      if not '@' in text and not re.findall('[0-9]+', text):
          return
      if not dev_pls(m.from_user.id,m.chat.id):
           return m.reply(f'{k} هذا الامر يخص ( المطور وفوق ) بس')      
      user = text.split()[2]
      try:
        id = int(user)
      except:
        id = user.replace('@','')
      try:
         get = c.get_chat(user)
         mention = f'[{get.first_name}](tg://user?id={get.id})'
         id = get.id
      except:
         return m.reply(f'{k} ماكو يوزر هيج')
      if dev_pls(id, m.chat.id):
         rank = get_rank(id,m.chat.id)
         return m.reply(f'{k} هييه ما تكدر تحظر {rank} ياغبي!')
      if r.get(f'{id}:gban:{Dev_Neptune}'):
          return m.reply(f'{k} الحمار「 {mention} 」\n{k} محظور عام من قبل ✔')
      else:
          r.set(f'{id}:gban:{Dev_Neptune}', 1)
          r.sadd(f'listGBAN:{Dev_Neptune}', id)
          return m.reply(f'{k} الحمار「 {mention} 」\n{k} حظرته عام ✔')
   
   if re.match("^حظر عام من الالعاب (.*?)$", text) and len(text.split()) ==  5:
      if not '@' in text and not re.findall('[0-9]+', text):
          return
      if not dev_pls(m.from_user.id,m.chat.id):
           return m.reply(f'{k} هذا الأمر يخص ( مطور اساسي🎖 وفوق ) بس')
      user = text.split()[4]
      try:
        id = int(user)
      except:
        id = user.replace('@','')
      try:
         get = c.get_chat(user)
         mention = f'[{get.first_name}](tg://user?id={get.id})'
         id = get.id
      except:
         return m.reply(f'{k} ماكو يوزر هيج')
      if dev_pls(id, m.chat.id):
         rank = get_rank(id,m.chat.id)
         return m.reply(f'{k} هييه ما تكدر تحظر {rank} ياغبي!')
      if r.get(f'{id}:gbangames:{Dev_Neptune}'):
          return m.reply(f'{k} الحمار「 {mention} 」\n{k} محظور من الالعاب من قبل ✔')
      else:
          r.set(f'{id}:gbangames:{Dev_Neptune}', 1)
          r.sadd(f'listGBANGAMES:{Dev_Neptune}', id)
          r.delete(f'{id}:Floos')
          r.srem("BankList",id)
          return m.reply(f'{k} الحمار「 {mention} 」\n{k} حظرته عام من الالعاب ✔')
   
   if re.match("^الغاء الحظر العام من الالعاب (.*?)$", text) and len(text.split()) ==  6:
      if not '@' in text and not re.findall('[0-9]+', text):
          return
      if not dev_pls(m.from_user.id,m.chat.id):
           return m.reply(f'{k} هذا الأمر يخص ( مطور اساسي🎖 وفوق ) بس')
      user = text.split()[5]
      try:
        id = int(user)
      except:
        id = user.replace('@','')
      try:
         get = c.get_chat(user)
         mention = f'[{get.first_name}](tg://user?id={get.id})'
         id = get.id
      except:
         id = re.findall('[0-9]+', text)[0] if re.findall('[0-9]+', text) else None
         if not id:  return m.reply(f"{k} ماكو مستخدم هيج")
         mention = f'[{id}](tg://user?id={id})'
      if not r.get(f'{id}:gbangames:{Dev_Neptune}'):
          return m.reply(f'「 {mention} 」\n{k} مو محظور من الالعاب من قبل ✔')
      else:
          r.delete(f'{id}:gbangames:{Dev_Neptune}')
          r.srem(f'listGBANGAMES:{Dev_Neptune}',id)
          return m.reply(f'「 {mention} 」\n{k} لغيت حظره من الالعاب عام ✔')

   if re.match("^الغاء الحظر العام (.*?)$", text) and len(text.split()) ==  4:
      if not '@' in text and not re.findall('[0-9]+', text):
          return
      if not dev_pls(m.from_user.id,m.chat.id):
           return m.reply(f'{k} هذا الأمر يخص ( مطور اساسي🎖 وفوق ) بس')
      user = text.split()[3]
      try:
        id = int(user)
      except:
        id = user.replace('@','')
      try:
         get = c.get_chat(user)
         mention = f'[{get.first_name}](tg://user?id={get.id})'
         id = get.id
      except:
         id = re.findall('[0-9]+', text)[0] if re.findall('[0-9]+', text) else None
         if not id:  return m.reply(f"{k} ماكو مستخدم هيج")
         mention = f'[{id}](tg://user?id={id})'
      if not r.get(f'{id}:gban:{Dev_Neptune}'):
          return m.reply(f'「 {mention} 」\n{k} مو محظور عام من قبل ✔')
      else:
          r.delete(f'{id}:gban:{Dev_Neptune}')
          r.srem(f'listGBAN:{Dev_Neptune}',id)
          return m.reply(f'「 {mention} 」\n{k} لغيت حظره عام ✔')

@Client.on_message(filters.group & ~filters.service & ~filters.bot, group=0)
def muteResponse(c,m):
    # التحقق من وجود المستخدم
    if not m.from_user:
        return
    # تجاهل رسائل البوت نفسه
    if m.from_user.id == c.me.id:
        return

    # فحص الحظر العام أولاً
    if r.get(f'{m.from_user.id}:gban:{Dev_Neptune}'):
        try:
            c.ban_chat_member(m.chat.id, m.from_user.id)
        except:
            try:
                c.delete_messages(m.chat.id, m.id)
            except:
                pass
        return

    # فحص الكتم مع استثناء لحالة إنشاء الحساب البنكي
    if r.get(f'{m.from_user.id}:mute:{m.chat.id}{Dev_Neptune}') or r.get(f'{m.from_user.id}:mute:{Dev_Neptune}'):
        # السماح بإنشاء الحساب البنكي حتى لو كان المستخدم مكتوم
        if not r.get(f'{m.from_user.id}:createBank:{m.chat.id}'):
            try:
                c.delete_messages(m.chat.id, m.id)
                return  # إيقاف معالجة الرسالة هنا
            except:
                try:
                    m.delete()
                    return
                except:
                    pass

    # التحقق من تفعيل البوت في المجموعة (بعد فحص الكتم)
    if not r.get(f'{m.chat.id}:enable:{Dev_Neptune}'):
        return

# معالج إضافي للتأكد من حذف رسائل المكتومين
@Client.on_message(filters.all & filters.group, group=-1)
def muteResponseAll(c,m):
    if not m.from_user:
        return
    if m.from_user.id == c.me.id:
        return

    # فحص الحظر العام أولاً
    if r.get(f'{m.from_user.id}:gban:{Dev_Neptune}'):
        try:
            c.ban_chat_member(m.chat.id, m.from_user.id)
        except:
            try:
                c.delete_messages(m.chat.id, m.id)
            except:
                pass
        return

    # فحص الكتم على جميع أنواع الرسائل مع استثناء لحالة إنشاء الحساب البنكي
    if r.get(f'{m.from_user.id}:mute:{m.chat.id}{Dev_Neptune}') or r.get(f'{m.from_user.id}:mute:{Dev_Neptune}'):
        # السماح بإنشاء الحساب البنكي حتى لو كان المستخدم مكتوم
        if not r.get(f'{m.from_user.id}:createBank:{m.chat.id}'):
            try:
                c.delete_messages(m.chat.id, m.id)
            except:
                try:
                    m.delete()
                except:
                    pass
    





@Client.on_message(filters.text & filters.group, group=16)
def mutesHandlerG(c,m):
    k = r.get(f'{Dev_Neptune}:botkey')
    Thread(target=mute_funcg,args=(c,m,k)).start()
    
    
def mute_funcg(c,m,k):
   if not r.get(f'{m.chat.id}:enable:{Dev_Neptune}'):  return
   if r.get(f'{m.chat.id}:mute:{Dev_Neptune}') and not admin_pls(m.from_user.id,m.chat.id):  return
   if r.get(f'{m.chat.id}:addCustom:{m.from_user.id}{Dev_Neptune}'):  return 
   if r.get(f'{m.chat.id}:addCustomG:{m.from_user.id}{Dev_Neptune}'):  return
   if r.get(f'{m.chat.id}:delCustom:{m.from_user.id}{Dev_Neptune}') or r.get(f'{m.chat.id}:delCustomG:{m.from_user.id}{Dev_Neptune}'):  return 
   text = m.text
   name = r.get(f'{Dev_Neptune}:BotName') if r.get(f'{Dev_Neptune}:BotName') else 'Neptune'
   if text.startswith(f'{name} '):
      text = text.replace(f'{name} ','')
   if r.get(f'{m.chat.id}:Custom:{m.chat.id}{Dev_Neptune}&text={text}'):
       text = r.get(f'{m.chat.id}:Custom:{m.chat.id}{Dev_Neptune}&text={text}')
   if r.get(f'Custom:{Dev_Neptune}&text={text}'):
       text = r.get(f'Custom:{Dev_Neptune}&text={text}')
       
   if text == 'كتم عام' and m.reply_to_message and m.reply_to_message.from_user:
        if not dev_pls(m.from_user.id,m.chat.id):
          return m.reply(f'{k} هذا الأمر يخص ( مطور اساسي🎖 وفوق ) بس')
        id = m.reply_to_message.from_user.id
        mention = m.reply_to_message.from_user.mention
        if dev_pls(id, m.chat.id):
           rank = get_rank(id,m.chat.id)
           return m.reply(f'{k} هييه ما تكدر تكتم {rank} ياغبي!')
        if r.get(f'{id}:mute:{Dev_Neptune}'):
          return m.reply(f'「 {mention} 」\n{k} مكتوم عام من قبل ✔')
        else:
          r.set(f'{id}:mute:{Dev_Neptune}', 1)
          r.sadd(f'listMUTE:{Dev_Neptune}', id)
          return m.reply(f'「 {mention} 」\n{k} كتمته عام ✔')
      
   if text == 'حظر عام' and m.reply_to_message and m.reply_to_message.from_user:
        if not dev_pls(m.from_user.id,m.chat.id):
          return m.reply(f'{k} هذا الأمر يخص ( مطور اساسي🎖 وفوق ) بس')
        id = m.reply_to_message.from_user.id
        mention = m.reply_to_message.from_user.mention
        if dev_pls(id, m.chat.id):
           rank = get_rank(id,m.chat.id)
           return m.reply(f'{k} هييه ما تكدر تحظر {rank} ياغبي!')
        if r.get(f'{id}:gban:{Dev_Neptune}'):
          return m.reply(f'{k} الحمار「 {mention} 」\n{k} محظور عام من قبل ✔')
        else:
          r.set(f'{id}:gban:{Dev_Neptune}', 1)
          r.sadd(f'listGBAN:{Dev_Neptune}', id)
          return m.reply(f'{k} الحمار「 {mention} 」\n{k} حظرته عام ✔')
   
   if text == 'حظر عام من الالعاب' and m.reply_to_message and m.reply_to_message.from_user:
        if not dev_pls(m.from_user.id,m.chat.id):
          return m.reply(f'{k} هذا الامر يخص ( المطور وفوق ) بس')
        id = m.reply_to_message.from_user.id
        mention = m.reply_to_message.from_user.mention
        if dev_pls(id, m.chat.id):
           rank = get_rank(id,m.chat.id)
           return m.reply(f'{k} هييه ما تكدر تحظر {rank} ياغبي!')
        if r.get(f'{id}:gbangames:{Dev_Neptune}'):
          return m.reply(f'{k} الحمار「 {mention} 」\n{k} محظور من الالعاب من قبل ✔')
        else:
          r.set(f'{id}:gbangames:{Dev_Neptune}', 1)
          r.sadd(f'listGBANGAMES:{Dev_Neptune}', id)
          r.delete(f'{id}:Floos')
          r.srem("BankList",id)
          return m.reply(f'{k} الحمار「 {mention} 」\n{k} حظرته عام من الالعاب ✔')

   if text == 'الغاء الكتم العام' and m.reply_to_message and m.reply_to_message.from_user:
        if not dev_pls(m.from_user.id,m.chat.id):
          return m.reply(f'{k} هذا الامر يخص ( المطور وفوق ) بس')
        id = m.reply_to_message.from_user.id
        mention = m.reply_to_message.from_user.mention
        if dev_pls(id, m.chat.id):
           rank = get_rank(id,m.chat.id)
           return m.reply(f'{k} هييه ما تكدر تكتم {rank} ياغبي!')
        if not r.get(f'{id}:mute:{Dev_Neptune}'):
          return m.reply(f'「 {mention} 」\n{k} مو مكتوم عام من قبل ✔')
        else:
          r.delete(f'{id}:mute:{Dev_Neptune}')
          r.srem(f'listMUTE:{Dev_Neptune}', id)
          return m.reply(f'「 {mention} 」\n{k} لغيت كتمته عام ✔')
   
   if text == 'الغاء الحظر العام من الالعاب' and m.reply_to_message and m.reply_to_message.from_user:
        if not dev_pls(m.from_user.id,m.chat.id):
          return m.reply(f'{k} هذا الأمر يخص ( مطور اساسي🎖 وفوق ) بس')
        id = m.reply_to_message.from_user.id
        mention = m.reply_to_message.from_user.mention
        if dev_pls(id, m.chat.id):
           rank = get_rank(id,m.chat.id)
           return m.reply(f'{k} هييه ما تكدر تكتم {rank} ياغبي!')
        if not r.get(f'{id}:gbangames:{Dev_Neptune}'):
          return m.reply(f'「 {mention} 」\n{k} مو محظور من الالعاب من قبل ✔')
        else:
          r.delete(f'{id}:gbangames:{Dev_Neptune}')
          r.srem(f'listGBANGAMES:{Dev_Neptune}', id)
          return m.reply(f'「 {mention} 」\n{k} لغيت حظره من الالعاب ✔')

   if text == 'الغاء الحظر العام' and m.reply_to_message and m.reply_to_message.from_user:
        if not dev_pls(m.from_user.id,m.chat.id):
          return m.reply(f'{k} هذا الأمر يخص ( مطور اساسي🎖 وفوق ) بس')
        id = m.reply_to_message.from_user.id
        mention = m.reply_to_message.from_user.mention
        if dev_pls(id, m.chat.id):
           rank = get_rank(id,m.chat.id)
           return m.reply(f'{k} هييه ما تكدر تكتم {rank} ياغبي!')
        if not r.get(f'{id}:gban:{Dev_Neptune}'):
          return m.reply(f'「 {mention} 」\n{k} مو محظور عام من قبل ✔')
        else:
          r.delete(f'{id}:gban:{Dev_Neptune}')
          r.srem(f'listGBAN:{Dev_Neptune}', id)
          return m.reply(f'「 {mention} 」\n{k} لغيت حظره عام ✔')
   