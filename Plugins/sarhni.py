import random, re, time, os, sys, pytz, string 
from threading import Thread
from pyrogram import *
from pyrogram.enums import *
from pyrogram.types import *
from datetime import datetime 
from config import *
from helpers.Ranks import *
from helpers.Ranks import isLockCommand
def get_sarhni_id():
   rndm = ''.join([random.choice(string.ascii_letters
            + string.digits) for n in range(10)])
   return rndm
   
@Client.on_message(filters.text & filters.group, group=37)
def sarhniHandler(c,m):
    k = r.get(f'{Dev_Neptune}:botkey')
    Thread(target=sarhniFunc,args=(c,m,k)).start()
    
def sarhniFunc(c,m,k):
   if not r.get(f'{m.chat.id}:enable:{Dev_Neptune}'):  return
   if r.get(f'{m.from_user.id}:mute:{m.chat.id}{Dev_Neptune}'):  return 
   if r.get(f'{m.from_user.id}:mute:{Dev_Neptune}'):  return 
   if r.get(f'{m.chat.id}:addCustom:{m.from_user.id}{Dev_Neptune}'):  return
   if r.get(f'{m.chat.id}:delCustom:{m.from_user.id}{Dev_Neptune}') or r.get(f'{m.chat.id}:delCustomG:{m.from_user.id}{Dev_Neptune}'):  return 
   if r.get(f'{m.chat.id}:mute:{Dev_Neptune}') and not admin_pls(m.from_user.id,m.chat.id):  return  
   if r.get(f'{m.chat.id}addCustomG:{m.from_user.id}{Dev_Neptune}'):  return 
   text = m.text
   name = r.get(f'{Dev_Neptune}:BotName') if r.get(f'{Dev_Neptune}:BotName') else 'jack'
   if text.startswith(f'{name} '):
      text = text.replace(f'{name} ','')
      
   if r.get(f'{m.chat.id}:Custom:{m.chat.id}{Dev_Neptune}&text={text}'):
       text = r.get(f'{m.chat.id}:Custom:{m.chat.id}{Dev_Neptune}&text={text}')
   if r.get(f'Custom:{Dev_Neptune}&text={text}'):
       text = r.get(f'Custom:{Dev_Neptune}&text={text}')
   
   if text == 'صارحني':
     if not r.get(f'{m.from_user.id}:sar7ni:{Dev_Neptune}'):
       id = get_sarhni_id()
       r.set(f'{m.from_user.id}:sar7ni:{Dev_Neptune}',id)
       r.set(f'{id}:sarhni:{Dev_Neptune}',m.from_user.id)
     else:
       id = r.get(f'{m.from_user.id}:sar7ni:{Dev_Neptune}')
     r.set(f'{m.from_user.id}:sarhniname', m.from_user.first_name)
     return m.reply(f'{k} أهلين عيني「 ⁪⁬⁪⁬{m.from_user.mention} 」\n{k} هذا رابط صارحني الخاص بيك', reply_markup=InlineKeyboardMarkup ([[InlineKeyboardButton ('📩',url=f't.me/{botUsername}?start=sarhni{id}')]]))
@Client.on_message(filters.private, group=2)
def sarhniHandlerP(c,m):
    k = r.get(f'{Dev_Neptune}:botkey')
    channel = r.get(f'{Dev_Neptune}:BotChannel') if r.get(f'{Dev_Neptune}:BotChannel') else 'iJUCK'
    Thread(target=sarhniFuncP,args=(c,m,k,channel)).start()

def sarhniFuncP(c,m,k,channel):
   if m.text:
      text = m.text
      if text.startswith('/start sarhni'):
        id = text.split('sarhni')[1]
        if not r.get(f'{id}:sarhni:{Dev_Neptune}'):
          return m.reply(f'{k} رابط صارحني غلط')
        else:
          user_id = int(r.get(f'{id}:sarhni:{Dev_Neptune}'))
          if m.from_user.id == user_id:
            return m.reply('انت زمال تدخل رابط صراحة مالك؟')
          get = c.get_chat(user_id)
          r.set(f'{m.from_user.id}:sarhni',get.id,ex=300)
          a = m.reply(f'{k} دخلت هسة رابط صارحني مع 「 ⁪⁬⁪⁬{get.first_name} 」\n{k} اي رسالة ترسلها لي راح احولها له بسرية تامة بدون مايعرفك\n༄',reply_markup=InlineKeyboardMarkup ([[InlineKeyboardButton ('الغاء', callback_data='sarhni:bye')],[InlineKeyboardButton ('ꜱᴏᴜʀᴄᴇ ɴᴇᴘᴛᴜɴᴇ',url=f't.me/{channel}')]]),quote=True)
          return a.pin(both_sides=True)
      
      if r.get(f'{m.from_user.id}:sarhni') and len(text) < 1000:
        user_id = int(r.get(f'{m.from_user.id}:sarhni'))
        name = r.get(f'{user_id}:sarhniname')
        TIME_ZONE = "Asia/Riyadh"
        ZONE = pytz.timezone(TIME_ZONE)
        TIME = datetime.now(ZONE)
        clock = TIME.strftime("%I:%M %p")
        date = TIME.strftime("%d/%m/%Y")
        txt = f'{k} وصلتك رسالة مصارحة جديدة\n{k} التاريخ : {date}\n{k} الساعة : {clock}\n\n{k} الرسالة :\n\n{text}\n☆'
        try:
          c.send_message(user_id, txt, disable_web_page_preview=True,reply_markup=InlineKeyboardMarkup ([
            [
              InlineKeyboardButton ('رد', callback_data=f'sarhni+rep{m.from_user.id}'),
            ],
            [
              InlineKeyboardButton ('sᴏᴜʀᴄᴇ ᴊᴀᴄᴋ',url=f't.me/{channel}')
            ]
          ]))
          return m.reply(f'{k} تمام ارسلت رسالتك بسرية تامة لـ {name}',quote=True)
        except Exception as e:  
          print(e)
          return m.reply('مقدر ارسله شيء يمكن حاظرني',quote=True)
   
   if r.get(f'{m.from_user.id}:sarhni'):
     user_id = int(r.get(f'{m.from_user.id}:sarhni'))
     name = r.get(f'{user_id}:sarhniname')
     TIME_ZONE = "Asia/Riyadh"
     ZONE = pytz.timezone(TIME_ZONE)
     TIME = datetime.now(ZONE)
     clock = TIME.strftime("%I:%M %p")
     date = TIME.strftime("%d/%m/%Y")
     txt = f'{k} وصلتك رسالة مصارحة جديدة\n{k} التاريخ : {date}\n{k} الساعة : {clock}\n\n{k} الرسالة :'
     try:
       c.send_message(user_id, txt, disable_web_page_preview=True)
       m.copy(user_id,
       reply_markup=InlineKeyboardMarkup ([
            [
              InlineKeyboardButton ('رد', callback_data=f'sarhni+rep{m.from_user.id}'),
            ],
            [
              InlineKeyboardButton ('sᴏᴜʀᴄᴇ ᴊᴀᴄᴋ',url=f't.me/{channel}')
            ]
          ])
       )
       return m.reply(f'{k} تمام ارسلت رسالتك بسرية تامة لـ {name}',quote=True)
     except Exception as e:
       print(e)
       return m.reply('مقدر ارسله شيء يمكن حاظرني',quote=True)
   
   if r.get(f'{m.from_user.id}:sarhnirep'):
     user_id = int(r.get(f'{m.from_user.id}:sarhnirep'))
     r.delete(f'{m.from_user.id}:sarhnirep')
     m.reply(f'{k} تمام ارسلت له ردك',quote=True)
     return m.copy(user_id)

@Client.on_callback_query(filters.regex('sarhni'))
async def sarhni_callback(c,m):
   if m.data == 'sarhni:bye':
     r.delete(f'{m.from_user.id}:sarhni')
     await m.message.delete()
     return await m.answer('تمام طلعتك من كل جلسة صارحني', show_alert=True)
   
   if m.data.startswith('sarhni+rep'):
     user_id = int(m.data.split('rep')[1])
     if not r.get(f'{user_id}:sarhni'):
       return await m.answer('ما تكدر ترد عليه لأنه طلع من جلسة صارحني', show_alert=True)
     if not int(r.get(f'{user_id}:sarhni')) == m.from_user.id:
       return await m.answer('ما تكدر ترد عليه لأنه طلع من جلسة صارحني', show_alert=True)
     else:
       r.set(f'{m.from_user.id}:sarhnirep', user_id,ex=300)
       return await c.send_message(m.from_user.id, 'ارسل الرد هسة')
       
     


   
   
   
   