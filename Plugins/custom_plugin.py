import random, re, time
from threading import Thread
from pyrogram import *
from pyrogram.enums import *
from pyrogram.types import *
from config import *
from helpers.Ranks import *


@Client.on_message(filters.text & filters.group, group=31)
def addPluginHandler(c,m):
    k = r.get(f'{Dev_Neptune}:botkey')
    Thread(target=plugin_func,args=(c,m,k)).start()
    
def plugin_func(c,m,k):
   if not r.get(f'{m.chat.id}:enable:{Dev_Neptune}'):
        return
   if r.get(f'{m.from_user.id}:mute:{m.chat.id}{Dev_Neptune}'):  return 
   if r.get(f'{m.chat.id}:mute:{Dev_Neptune}') and not admin_pls(m.from_user.id,m.chat.id):  return
   if r.get(f'{m.from_user.id}:mute:{Dev_Neptune}'):  return 
   
   if r.get(f'{m.chat.id}addCustomG:{m.from_user.id}{Dev_Neptune}'):  return
   if r.get(f'{m.chat.id}:addCustom:{m.from_user.id}{Dev_Neptune}'):  return 
   if r.get(f'{m.chat.id}:delCustom:{m.from_user.id}{Dev_Neptune}') or r.get(f'{m.chat.id}:delCustomG:{m.from_user.id}{Dev_Neptune}'):  return 
   text = m.text
   name = r.get(f'{Dev_Neptune}:BotName') if r.get(f'{Dev_Neptune}:BotName') else 'jack'
   if text.startswith(f'{name} '):
      text = text.replace(f'{name} ','')
   if r.get(f'{m.chat.id}:Custom:{m.chat.id}{Dev_Neptune}&text={text}'):
       text = r.get(f'{m.chat.id}:Custom:{m.chat.id}{Dev_Neptune}&text={text}')
   if r.get(f'Custom:{Dev_Neptune}&text={text}'):
       text = r.get(f'Custom:{Dev_Neptune}&text={text}')
   
   if r.get(f'{m.from_user.id}:setAddP4:{m.chat.id}{Dev_Neptune}') or r.get(f'{m.from_user.id}:setAddP:{m.chat.id}{Dev_Neptune}') or r.get(f'{m.from_user.id}:setAddP2:{m.chat.id}{Dev_Neptune}') or r.get(f'{m.from_user.id}:setAddP3:{m.chat.id}{Dev_Neptune}') or r.get(f'{m.from_user.id}:setAddP4:{m.chat.id}{Dev_Neptune}') or r.get(f'{m.from_user.id}:setDelp:{m.chat.id}{Dev_Neptune}'):
     if text == 'الغاء':
       m.reply(f'{k} تمام ياعيني لغيت كلشي')
       r.delete(f'{m.from_user.id}:setAddP:{m.chat.id}{Dev_Neptune}')
       r.delete(f'{m.from_user.id}:setAddP2:{m.chat.id}{Dev_Neptune}')
       r.delete(f'{m.from_user.id}:setAddP3:{m.chat.id}{Dev_Neptune}')
       r.delete(f'{m.from_user.id}:setAddP4:{m.chat.id}{Dev_Neptune}')
       r.delete(f'{m.from_user.id}:setDelp:{m.chat.id}{Dev_Neptune}')
       return 
     
   if text == 'اضف ميزة' or text == 'اضف ميزه':
     if devp_pls(m.from_user.id,m.chat.id):
        r.set(f'{m.from_user.id}:setAddP:{m.chat.id}{Dev_Neptune}',1)
        return m.reply(f'{k} هلا عيني ارسل اسم الميزة هسة')
   
   if r.get(f'{m.from_user.id}:setAddP:{m.chat.id}{Dev_Neptune}') and devp_pls(m.from_user.id,m.chat.id) and len(m.text.split()) == 1:
      r.delete(f'{m.from_user.id}:setAddP:{m.chat.id}{Dev_Neptune}')
      r.set(f'{m.from_user.id}:setAddP2:{m.chat.id}{Dev_Neptune}',m.text)
      return m.reply(f'{k} تمام عيني ارسل نوع الميزة هسة ( صوره,فيديو,متحركه,بصمه,صوت)\n☆')
   
   if text in ['صوره','فيديو','متحركه','بصمه','صوت'] and r.get(f'{m.from_user.id}:setAddP2:{m.chat.id}{Dev_Neptune}') and devp_pls(m.from_user.id,m.chat.id):
      miza = r.get(f'{m.from_user.id}:setAddP2:{m.chat.id}{Dev_Neptune}')
      r.delete(f'{m.from_user.id}:setAddP2:{m.chat.id}{Dev_Neptune}')
      r.set(f'{m.from_user.id}:setAddP3:{m.chat.id}{Dev_Neptune}',f'miza={miza}&&type={m.text}')
      return m.reply(f'{k} ارسل يوزر القناة هسة')
   
   if r.get(f'{m.from_user.id}:setAddP3:{m.chat.id}{Dev_Neptune}') and devp_pls(m.from_user.id,m.chat.id):
      miza = r.get(f'{m.from_user.id}:setAddP3:{m.chat.id}{Dev_Neptune}')
      miza += f'&&channel={m.text.replace("@","")}'
      r.delete(f'{m.from_user.id}:setAddP3:{m.chat.id}{Dev_Neptune}')
      r.set(f'{m.from_user.id}:setAddP4:{m.chat.id}{Dev_Neptune}', miza)
      return m.reply(f'{k} ارسل هسة ايديات الرسايل العشوائية\n{k} مثال 1 - 100')
   
   if r.get(f'{m.from_user.id}:setAddP4:{m.chat.id}{Dev_Neptune}') and devp_pls(m.from_user.id,m.chat.id):
      miza = r.get(f'{m.from_user.id}:setAddP4:{m.chat.id}{Dev_Neptune}')
      id1 = int(m.text.split('-')[0])
      id2 = int(m.text.split('-')[1])
      r.delete(f'{m.from_user.id}:setAddP4:{m.chat.id}{Dev_Neptune}')
      miza_name = miza.split('miza=')[1].split('&&')[0]
      miza_type = miza.split('&&type=')[1].split('&&')[0]
      miza_channel = miza.split('&&channel=')[1].split('&&')[0]
      r.set(f'{miza_name}:customPlugin:{Dev_Neptune}', f'type={miza_type}&&channel={miza_channel}&&random={id1}_{id2}')
      r.sadd(f'customPlugins:{Dev_Neptune}', miza_name)
      return m.reply(f'{k} تمام ضفت الميزة ( {miza_name} )\n{k} نوع الميزة {miza_type}\n{k} قناة الميزة ( @{miza_channel} )')
   
   if text == 'مسح ميزة' or text == 'مسح ميزه':
     if devp_pls(m.from_user.id,m.chat.id):
        r.set(f'{m.from_user.id}:setDelp:{m.chat.id}{Dev_Neptune}',1)
        return m.reply(f'{k} هلا عيني ارسل اسم الميزة هسة')
        
   if r.get(f'{m.from_user.id}:setDelp:{m.chat.id}{Dev_Neptune}') and devp_pls(m.from_user.id,m.chat.id):
     if not r.get(f'{m.text}:customPlugin:{Dev_Neptune}'):
       r.delete(f'{m.from_user.id}:setDelp:{m.chat.id}{Dev_Neptune}')
       return m.reply(f'{k} ماكو ميزة بهالأسم')
     else:
       r.srem(f'customPlugins:{Dev_Neptune}', m.text)
       r.delete(f'{m.text}:customPlugin:{Dev_Neptune}')
       r.delete(f'{m.from_user.id}:setDelp:{m.chat.id}{Dev_Neptune}')
       r.delete(f'{m.text}:customPluginD:{Dev_Neptune}{m.chat.id}')
       return m.reply(f'{k} الميزة ( {m.text} ) مسحتها .')
   
   if text == 'المميزات المضافه':
     if devp_pls(m.from_user.id,m.chat.id):
       if not r.smembers(f'customPlugins:{Dev_Neptune}'):
         return m.reply(f'{k} ماكو ولا ميزة مضافة')
       else:
         text = 'المميزات المضافه:\n\n'
         count = 1
         for miza in r.smembers(f'customPlugins:{Dev_Neptune}'):
            text += f'{count}) - {miza}\n'
            count += 1
         text += '\n☆'
         return m.reply(text)
   
   if r.get(f'{m.text}:customPlugin:{Dev_Neptune}'):
      if r.get(f'{m.text}:customPluginD:{Dev_Neptune}{m.chat.id}'):
         return
      else:
         miza = r.get(f'{m.text}:customPlugin:{Dev_Neptune}')
         type = miza.split('type=')[1].split('&&')[0]
         channel = miza.split('&&channel=')[1].split('&&')[0]
         random1 = int(miza.split('&&random=')[1].split('_')[0])
         random2 = int(miza.split('&&random=')[1].split('_')[1])
         rand = random.randint(random1,random2)
         if type == 'صوره':
            m.reply_photo(f'https://t.me/{channel}/{rand}')
         
         if type == 'فيديو':
            m.reply_video(f'https://t.me/{channel}/{rand}')
        
         if type == 'متحركه':
            m.reply_animation(f'https://t.me/{channel}/{rand}')
         
         if type == 'بصمه':
            m.reply_voice(f'https://t.me/{channel}/{rand}')
         
         if type == 'صوت':
            m.reply_audio(f'https://t.me/{channel}/{rand}')
   
   if text.startswith('تعطيل ') and len(text.split()) == 2:
      miza = text.split()[1]
      if r.get(f'{miza}:customPlugin:{Dev_Neptune}'):
        if not owner_pls(m.from_user.id,m.chat.id):
          return m.reply(f'{k} هذا الامر يخص ( المالك وفوق ) بس') 
        else:
          if r.get(f'{miza}:customPluginD:{Dev_Neptune}{m.chat.id}'):
            return m.reply(f'{k} من「 {m.from_user.mention} 」\n{k} ميزة {miza} معطله من قبل\n☆')
          else:
            r.set(f'{miza}:customPluginD:{Dev_Neptune}{m.chat.id}',1)
            return m.reply(f'من「 {m.from_user.mention} 」\n{k} تمام عطلت ميزة {miza}\n☆')
   
   if text.startswith('تفعيل ') and len(text.split()) == 2:
      miza = text.split()[1]
      if r.get(f'{miza}:customPlugin:{Dev_Neptune}'):
        if not owner_pls(m.from_user.id,m.chat.id):
          return m.reply(f'{k} هذا الامر يخص ( المالك وفوق ) بس') 
        else:
          if not r.get(f'{miza}:customPluginD:{Dev_Neptune}{m.chat.id}'):
            return m.reply(f'{k} من「 {m.from_user.mention} 」\n{k} ميزة {miza} مفعله من قبل\n☆')
          else:
            r.delete(f'{miza}:customPluginD:{Dev_Neptune}{m.chat.id}')
            return m.reply(f'من「 {m.from_user.mention} 」\n{k} تمام فعلت ميزة {miza}\n☆')
   
            
            
          
   
   
   
   
      
   