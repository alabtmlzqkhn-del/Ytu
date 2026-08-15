import random, re, time
from threading import Thread
from pyrogram import *
from pyrogram.enums import *
from pyrogram.types import *
from config import *
from helpers.Ranks import *
from helpers.Ranks import isLockCommand

@Client.on_message(filters.text & filters.group, group=12)
def getRanksHandler(c,m):
    k = r.get(f'{Dev_Neptune}:botkey')
    channel = r.get(f'{Dev_Neptune}:BotChannel') if r.get(f'{Dev_Neptune}:BotChannel') else 'Jack_Vib'
    Thread(target=get_ranks_func,args=(c,m,k,channel)).start()

def get_ranks_func(c,m,k,channel):
   if not r.get(f'{m.chat.id}:enable:{Dev_Neptune}'):  return
   if r.get(f'{m.from_user.id}:mute:{m.chat.id}{Dev_Neptune}'):  return
   if r.get(f'{m.from_user.id}:mute:{Dev_Neptune}'):  return
   if r.get(f'{m.chat.id}:addCustom:{m.from_user.id}{Dev_Neptune}'):  return
   if r.get(f'{m.chat.id}:delCustom:{m.from_user.id}{Dev_Neptune}') or r.get(f'{m.chat.id}:delCustomG:{m.from_user.id}{Dev_Neptune}'):  return
   if r.get(f'{m.chat.id}:mute:{Dev_Neptune}') and not admin_pls(m.from_user.id,m.chat.id):  return

   if r.get(f'{m.chat.id}addCustomG:{m.from_user.id}{Dev_Neptune}'):  return
   text = m.text
   name = r.get(f'{Dev_Neptune}:BotName') if r.get(f'{Dev_Neptune}:BotName') else 'Neptune'
   if text.startswith(f'{name} '):
      text = text.replace(f'{name} ','')
   if r.get(f'{m.chat.id}:Custom:{m.chat.id}{Dev_Neptune}&text={text}'):
       text = r.get(f'{m.chat.id}:Custom:{m.chat.id}{Dev_Neptune}&text={text}')
   if r.get(f'Custom:{Dev_Neptune}&text={text}'):
       text = r.get(f'Custom:{Dev_Neptune}&text={text}')
   if isLockCommand(m.from_user.id, m.chat.id, text): return
   if text == 'قائمه Dev':
      if not devp_pls(m.from_user.id,m.chat.id):
        return m.reply(f'{k} هذا الامر يخص ( مبرمج🎖️) بس')
      else:
        if not r.smembers(f'{Dev_Neptune}DEV2'):
           return m.reply(f'{k} ماكو قائمة مطورين ثانويين')
        else:
          text = '- قائمة المطورين الثانويين:\n\n'
          count = 1
          for dev2 in r.smembers(f'{Dev_Neptune}DEV2'):
             if count == 101: break
             try:
               user = c.get_users(int(dev2))
               mention = user.mention
               id = user.id
               username = user.username
               if user.username:
                 text += f'{count} ➣ @{username}   - ( `{id}` )\n'
               else:
                 text += f'{count} ➣ {mention}   - ( `{id}` )\n'
               count += 1
             except:
               mention = f'[@{channel}](tg://user?id={int(dev2)})'
               id = int(dev2)
               text += f'{count} ➣ {mention}   - ( `{id}` )\n'
               count += 1
          text += '..'
          m.reply(text)



   if text == 'قائمه مطور اساسي':
      if not devp_pls(m.from_user.id,m.chat.id):
        return m.reply(f'{k} هذا الامر يخص (المطور الاساسي🪐) بس')
      else:
        if not r.smembers(f'{Dev_Neptune}DEV2'):
           return m.reply(f'{k} ماكو قائمة مطور اساسي🎖')
        else:
          text = '- قائمة مطور اساسي🎖:\n\n'
          count = 1
          for dev2 in r.smembers(f'{Dev_Neptune}DEV2'):
             if count == 101: break
             try:
               user = c.get_users(int(dev2))
               mention = user.mention
               id = user.id
               username = user.username
               if user.username:
                 text += f'{count} ➣ @{username}   - ( `{id}` )\n'
               else:
                 text += f'{count} ➣ {mention}   - ( `{id}` )\n'
               count += 1
             except:
               mention = f'[@{channel}](tg://user?id={int(dev2)})'
               id = int(dev2)
               text += f'{count} ➣ {mention}   - ( `{id}` )\n'
               count += 1
          text += '.'
          m.reply(text)

   if text == 'قائمه مطور ثانوي':
      if not dev2_pls(m.from_user.id,m.chat.id):
        return m.reply(f'{k} هذا الامر يخص ( مطور اساسي🎖 وفوق ) بس')
      else:
        if not r.smembers(f'{Dev_Neptune}DEV'):
          return m.reply(f'{k}  ماكو مطور ثانوي🎖️ ')
        else:
          text = '- قائمة مطور ثانوي🎖️:\n\n'
          count = 1
          for dev in r.smembers(f'{Dev_Neptune}DEV'):
             if count == 101: break
             try:
               user = c.get_users(int(dev))
               mention = user.mention
               id = user.id
               username = user.username
               if user.username:
                 text += f'{count} ➣ @{username}   - ( `{id}` )\n'
               else:
                 text += f'{count} ➣ {mention}   - ( `{id}` )\n'
               count += 1
             except:
               mention = f'[@{channel}](tg://user?id={int(dev)})'
               id = int(dev)
               text += f'{count} ➣ {mention}   - ( `{id}` )\n'
               count += 1
          text += '..'
          m.reply(text)

   cid = m.chat.id
   if text == 'المالكين الاساسيين':
      if not dev_pls(m.from_user.id,m.chat.id):
        return m.reply(f'{k} هذا الامر يخص ( المطور وفوق ) بس')
      else:
        if not r.smembers(f'{cid}:listGOWNER:{Dev_Neptune}'):
          return m.reply(f'{k} ماكو مالكين اساسيين ')
        else:
          text = '- المالكين الاساسيين:\n\n'
          count = 1
          for gowner in r.smembers(f'{cid}:listGOWNER:{Dev_Neptune}'):
             if count == 101: break
             try:
               user = c.get_users(int(gowner))
               mention = user.mention
               id = user.id
               username = user.username
               if user.username:
                 text += f'{count} ➣ @{username}   - ( `{id}` )\n'
               else:
                 text += f'{count} ➣ {mention}   - ( `{id}` )\n'
               count += 1
             except:
               mention = f'[@{channel}](tg://user?id={int(gowner)})'
               id = int(gowner)
               text += f'{count} ➣ {mention}   - ( `{id}` )\n'
               count += 1
          text += '..'
          m.reply(text)

   if text == 'المالكين':
      if not gowner_pls(m.from_user.id,m.chat.id):
        return m.reply(f'{k} هذا الامر يخص ( المالك الاساسي ) بس')
      else:
        if not r.smembers(f'{cid}:listOWNER:{Dev_Neptune}'):
          return m.reply(f'{k} ماكو مالكيين ')
        else:
          text = '- المالكيين:\n\n'
          count = 1
          for owner in r.smembers(f'{cid}:listOWNER:{Dev_Neptune}'):
             if count == 101: break
             try:
               user = c.get_users(int(owner))
               mention = user.mention
               id = user.id
               username = user.username
               if user.username:
                 text += f'{count} ➣ @{username}   - ( `{id}` )\n'
               else:
                 text += f'{count} ➣ {mention}   - ( `{id}` )\n'
               count += 1
             except:
               mention = f'[@{channel}](tg://user?id={int(owner)})'
               id = int(owner)
               text += f'{count} ➣ {mention}   - ( `{id}` )\n'
               count += 1
          text += '..'
          m.reply(text)

   if text == 'المدراء':
      if not owner_pls(m.from_user.id,m.chat.id):
        return m.reply(f'{k} هذا الامر يخص ( المالك وفوق ) بس')
      else:
        if not r.smembers(f'{cid}:listMOD:{Dev_Neptune}'):
          return m.reply(f'{k} ماكو مدراء ')
        else:
          text = '- المدراء:\n\n'
          count = 1
          for mod in r.smembers(f'{cid}:listMOD:{Dev_Neptune}'):
             if count == 101: break
             try:
               user = c.get_users(int(mod))
               mention = user.mention
               id = user.id
               username = user.username
               if user.username:
                 text += f'{count} ➣ @{username}   - ( `{id}` )\n'
               else:
                 text += f'{count} ➣ {mention}   - ( `{id}` )\n'
               count += 1
             except:
               mention = f'[@{channel}](tg://user?id={int(mod)})'
               id = int(mod)
               text += f'{count} ➣ {mention}   - ( `{id}` )\n'
               count += 1
          text += '..'
          m.reply(text)

   if text == 'الادمنيه':
      if not mod_pls(m.from_user.id,m.chat.id):
        return m.reply(f'{k} هذا الامر يخص ( المدير وفوق ) بس')
      else:
        if not r.smembers(f'{cid}:listADMIN:{Dev_Neptune}'):
          return m.reply(f'{k} ماكو ادمن ')
        else:
          text = '- الادمنيه:\n\n'
          count = 1
          for ADM in r.smembers(f'{cid}:listADMIN:{Dev_Neptune}'):
             if count == 101: break
             try:
               user = c.get_users(int(ADM))
               mention = user.mention
               id = user.id
               username = user.username
               if user.username:
                 text += f'{count} ➣ @{username}   - ( `{id}` )\n'
               else:
                 text += f'{count} ➣ {mention}   - ( `{id}` )\n'
               count += 1
             except:
               mention = f'[@{channel}](tg://user?id={int(ADM)})'
               id = int(ADM)
               text += f'{count} ➣ {mention}   - ( `{id}` )\n'
               count += 1
          text += '..'
          m.reply(text)

   if text == 'المشرفين':
      if not owner_pls(m.from_user.id,m.chat.id):
        return m.reply(f'{k} هذا الامر يخص ( المالك وفوق ) بس')
      else:
          text = '- المشرفين:\n\n'
          count = 1
          for mm in m.chat.get_members(filter=ChatMembersFilter.ADMINISTRATORS):
            if count == 101: break
            if not mm.user.is_deleted and not mm.user.is_bot:
               id = mm.user.id
               username = mm.user.username
               if mm.user.username:
                 text += f'{count} ➣ @{username}   - ( `{id}` )\n'
               else:
                 text += f'{count} ➣ [@{channel}](tg://user?id={id})   - ( `{id}` )\n'
               count += 1
          text += '..'
          m.reply(text)

   if text == 'المميزين':
      if not admin_pls(m.from_user.id,m.chat.id):
        return m.reply(f'{k} هذا الامر يخص ( الادمن وفوق ) بس')
      else:
        if not r.smembers(f'{cid}:listPRE:{Dev_Neptune}'):
          return m.reply(f'{k} ماكو مميزين ')
        else:
          text = '- المميزين:\n\n'
          count = 1
          for PRE in r.smembers(f'{cid}:listPRE:{Dev_Neptune}'):
             if count == 101: break
             try:
               user = c.get_users(int(PRE))
               mention = user.mention
               id = user.id
               username = user.username
               if user.username:
                 text += f'{count} ➣ @{username}   - ( `{id}` )\n'
               else:
                 text += f'{count} ➣ {mention}   - ( `{id}` )\n'
               count += 1
             except:
               mention = f'[@{channel}](tg://user?id={int(PRE)})'
               id = int(PRE)
               text += f'{count} ➣ {mention}   - ( `{id}` )\n'
               count += 1
          text += '..'
          m.reply(text)

   if text == 'المكتومين':
      if not mod_pls(m.from_user.id,m.chat.id):
        return m.reply(f'{k} هذا الامر يخص ( المدير وفوق ) بس')
      else:
        if not r.smembers(f'{cid}:listMUTE:{Dev_Neptune}'):
          return m.reply(f'{k} ماكو مكتومين ')
        else:
          text = '- المكتومين:\n\n'
          count = 1
          for PRE in r.smembers(f'{cid}:listMUTE:{Dev_Neptune}'):
             if count == 101: break
             try:
               user = c.get_users(int(PRE))
               mention = user.mention
               id = user.id
               username = user.username
               if user.username:
                 text += f'{count} ➣ @{username} - ( `{id}` )\n'
               else:
                 text += f'{count} ➣ {mention} - ( `{id}` )\n'
               count += 1
             except:
               mention = f'[@{channel}](tg://user?id={PRE})'
               id = PRE
               text += f'{count} ➣ {mention} - ( `{id}` )\n'
               count += 1
          text += '..'
          m.reply(text)





