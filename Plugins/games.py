import random,re, time, akinator, string
from threading import Thread
from pyrogram import *
from pyrogram.enums import *
from pyrogram.types import *
from config import *
from helpers.Ranks import *
from helpers.games import *
from helpers.Ranks import isLockCommand
from helpers.xo_game import XOGame, get_game_from_redis, save_game_to_redis, delete_game_from_redis, create_new_game
users_demon = {}
def is_what_percent_of(num_a, num_b):
    return (num_a / num_b) * 100

def get_top(users):
   users = [tuple(i.items()) for i in users]
   top = sorted(users, key=lambda i: i[-1][-1], reverse=True)
   top = [dict(i) for i in top]
   return top

@Client.on_message(filters.text & filters.group, group=33)
def gamesHandler(c,m):
    k = r.get(f'{Dev_Neptune}:botkey')
    channel = r.get(f'{Dev_Neptune}:BotChannel') if r.get(f'{Dev_Neptune}:BotChannel') else 'Jack_Vib'
    Thread(target=gamesFunc,args=(c,m,k,channel)).start()

@Client.on_message(filters.dice & filters.group, group=45)
def diceFunc(c,m):
   if r.get(f'{m.chat.id}:disableGames:{Dev_Neptune}'):  return False
   if m.dice.emoji == "🎲":
     k = r.get(f'{Dev_Neptune}:botkey')
     if m.dice.value == 6:
        time.sleep(3)
        ra = 100
        if r.get(f'{m.from_user.id}:Floos'):
           get = int(r.get(f'{m.from_user.id}:Floos'))
           r.set(f'{m.from_user.id}:Floos',get+ra)
           floos = int(r.get(f'{m.from_user.id}:Floos'))
        else:
           floos = ra
           r.set(f'{m.from_user.id}:Floos',ra)
        return m.reply(f'''
صح عليك فزت **[بالنرد]({m.link})** ⁪⁬⁪⁬⁮⁪⁬⁪⁬⁮✔
💸فلوسك: `{floos}` دينار عراقي
☆
''', disable_web_page_preview=True)
     else:
        time.sleep(3)
        return m.reply(f"{k} للأسف خسرت بالنرد")


def gamesFunc(c,m,k,channel):
   if not r.get(f'{m.chat.id}:enable:{Dev_Neptune}'):
       return
   if r.get(f'{m.from_user.id}:gbangames:{Dev_Neptune}'):  return
   if r.get(f'{m.from_user.id}:mute:{m.chat.id}{Dev_Neptune}'):  return
   if r.get(f'{m.chat.id}:addCustom:{m.from_user.id}{Dev_Neptune}'):  return
   if r.get(f'{m.chat.id}addCustomG:{m.from_user.id}{Dev_Neptune}'):  return
   if r.get(f'{m.chat.id}:delCustom:{m.from_user.id}{Dev_Neptune}') or r.get(f'{m.chat.id}:delCustomG:{m.from_user.id}{Dev_Neptune}'):  return
   if r.get(f'{m.chat.id}:mute:{Dev_Neptune}') and not admin_pls(m.from_user.id,m.chat.id):  return
   if r.get(f'{m.from_user.id}:mute:{Dev_Neptune}'):  return


   text = m.text
   name = r.get(f'{Dev_Neptune}:BotName') if r.get(f'{Dev_Neptune}:BotName') else 'فوق'
   if text.startswith(f'{name} '):
      text = text.replace(f'{name} ','')
   if r.get(f'{m.chat.id}:Custom:{m.chat.id}{Dev_Neptune}&text={text}'):
     text = r.get(f'{m.chat.id}:Custom:{m.chat.id}{Dev_Neptune}&text={text}')
   if r.get(f'Custom:{Dev_Neptune}&text={text}'):
     text = r.get(f'Custom:{Dev_Neptune}&text={text}')
   if r.get(f'{m.chat.id}:disableGames:{Dev_Neptune}'):  return

   if r.get(f'{m.from_user.id}:toTrans:{m.chat.id}{Dev_Neptune}'):
      if not re.findall('[0-9]+', text):
        r.delete(f'{m.from_user.id}:toTrans:{m.chat.id}{Dev_Neptune}')
        return m.reply(f'{k} لازم يكون ارقام')
      acc_id = int(re.findall('[0-9]+', text)[0])
      acc_id_from = int(r.get(f'{m.from_user.id}:bankID'))
      if acc_id == acc_id_from:
        r.delete(f'{m.from_user.id}:toTrans:{m.chat.id}{Dev_Neptune}')
        return m.reply(f'{k} مابيك تحول لنفسك')
      floos_to_trans = int(r.get(f'{m.from_user.id}:toTrans:{m.chat.id}{Dev_Neptune}'))
      r.delete(f'{m.from_user.id}:toTrans:{m.chat.id}{Dev_Neptune}')
      if not r.sismember('BankList', m.from_user.id):
        return m.reply(f'{k} ماعندك حساب بنكي ارسل ↢ ( `انشاء حساب بنكي` )')
      if not r.get(f'{m.from_user.id}:Floos'):
        floos = 0
      else:
        floos = int(r.get(f'{m.from_user.id}:Floos'))
      if floos_to_trans > floos:
        return m.reply(f'{k} فلوسك ماتكفي')
      else:
        if not r.get(f'{acc_id}:getAccBank'):
          return m.reply(f'{k} ماكو حساب بنكي هيج')
        else:
          id_to = int(r.get(f'{acc_id}:getAccBank'))
          if not r.sismember('BankList', id_to):
            return m.reply(f'{k} ماعنده حساب بأي بنك')
          if r.get(f'{id_to}:bankName'):
            name_to = r.get(f'{id_to}:bankName')[:10]
          else:
            gett = c.get_users(int(r.get(f'{acc_id}:getAccBank')))
            name_to = gett.first_name[:10]
            r.set(f'{id_to}:bankName',name_to)
          if floos_to_trans == floos:
            r.delete(f'{m.from_user.id}:Floos')
          else:
            r.set(f'{m.from_user.id}:Floos',floos-floos_to_trans)
          bank_to = r.get(f'{id_to}:bankType')
          bank_from = r.get(f'{m.from_user.id}:bankType')
          name_from = r.get(f'{m.from_user.id}:bankName')[:10] or m.from_user.first_name[:10]
          mention_from = f'[{name_from}](tg://user?id={m.from_user.id})'
          mention_to = f'[{name_to}](tg://user?id={id_to})'
          if not r.get(f'{id_to}:Floos'):
            floos_to = 0
          else:
            floos_to = int(r.get(f'{id_to}:Floos'))
          txt = 'حوالة صادرة\n\nمن: {}\nحساب رقم: {}\nبنك: {}\nالى: {}\nحساب رقم: {}\nبنك: {}'.format(mention_from,acc_id_from,bank_from,mention_to,acc_id,bank_to)
          if bank_from != bank_to:
             floos_to_tran = int(floos_to_trans-floos_to_trans/10)
             txt += '\nخصمت 10% ضريبة بنك الى بنك'
             txt += f'\nالمبلغ: {floos_to_tran} دينار عراقي 💸'
          else:
             floos_to_tran = floos_to_trans
             txt += f'\nالمبلغ: {floos_to_tran} دينار عراقي 💸'
          r.set(f'{id_to}:Floos',floos_to+floos_to_tran)
          return m.reply(txt, disable_web_page_preview=True)

   if r.get(f'{m.from_user.id}:createBank:{m.chat.id}'):
     r.delete(f'{m.from_user.id}:createBank:{m.chat.id}')
     if r.get(f'{m.from_user.id}:bankID'):
       bank_id = int(r.get(f'{m.from_user.id}:bankID'))
       floos_to_add = 0
     else:
       bank_id = '4'
       floos_to_add = 2000
       for a in range(15):
         bank_id += str(random.randint(1,9))
     if not r.get(f'{m.from_user.id}:Floos'):
       floos = 0
     else:
       floos = int(r.get(f'{m.from_user.id}:Floos'))
     '''
     if not text in ['الرشيد','الرافدين', 'الاهلي','عبد الفتاح السيسي']:
       return m.reply(f'{k} ماكو بنك بهالاسم')
     '''
     if not text in ['الرشيد','الرافدين', 'الاهلي']:
       return m.reply(f'{k} ماكو بنك بهالاسم')
     card = random.choice(['ماستر كارد','فيزا كارد','ماستر كارد','فيزا كارد'])
     if text == 'الرشيد':
        r.set(f'{m.from_user.id}:bankType', 'الرشيد')
        r.set(f'{m.from_user.id}:bankID', int(bank_id))
        r.set(f'{m.from_user.id}:bankCard',card)
     if text == 'الرافدين':
        r.set(f'{m.from_user.id}:bankType', 'الرافدين')
        r.set(f'{m.from_user.id}:bankID', int(bank_id))
        r.set(f'{m.from_user.id}:bankCard',card)
     if text == 'الاهلي':
        r.set(f'{m.from_user.id}:bankType', 'الاهلي')
        r.set(f'{m.from_user.id}:bankID', int(bank_id))
        r.set(f'{m.from_user.id}:bankCard',card)
     '''
     if text == 'عبد الفتاح السيسي':
        r.set(f'{m.from_user.id}:bankType', 'بلحة الدولي')
        r.set(f'{m.from_user.id}:bankID', int(bank_id))
        r.set(f'{m.from_user.id}:bankCard','بطاقة تموين')
        card = 'بطاقة تموين'
        r.sadd('BankList', m.from_user.id)
        r.set(f'{bank_id}:getAccBank', m.from_user.id)
        fff = floos + floos_to_add
        r.set(f'{m.from_user.id}:Floos',fff)
        r.set(f'{m.from_user.id}:bankName',m.from_user.first_name)
        m.reply(f'• وسوينا لك حساب في بنك {text}\n\n{k} رقم حسابك ↢ ( `{bank_id}` )\n{k} نوع البطاقة ↢ ( {card} )\n{k} فلوسك ↢ ( {fff} دينار عراقي 💸 )\n\n{k} هتدفع!! هتشوف الي مشفتهشنو، دا لو هتدفع!، انما ببلاش دا انا معرفش حاجة اسمها ببلاش')
        if r.get(f'DevGroup:{Dev_Neptune}'):
          return c.send_message(int(r.get(f'DevGroup:{Dev_Neptune}')),
           f' ⟨ {m.from_user.mention} ⟩\n{k} سوى حساب بالبنك\n{k} رقم حسابه ( `{bank_id}` )')
        else:
          return
     '''
     r.sadd('BankList', m.from_user.id)
     r.set(f'{bank_id}:getAccBank', m.from_user.id)
     fff = floos + floos_to_add
     r.set(f'{m.from_user.id}:Floos',fff)
     r.set(f'{m.from_user.id}:bankName',m.from_user.first_name)
     m.reply(f'• وسوينا لك حساب في بنك {text}\n\n{k} رقم حسابك ↢ ( `{bank_id}` )\n{k} نوع البطاقة ↢ ( {card} )\n{k} فلوسك ↢ ( {fff} دينار عراقي 💸 )')
     if r.get(f'DevGroup:{Dev_Neptune}'):
         c.send_message(int(r.get(f'DevGroup:{Dev_Neptune}')),
           f' ⟨ {m.from_user.mention} ⟩\n{k} سوى حساب بالبنك\n{k} رقم حسابه ( `{bank_id}` )')

   if text == 'توب' or text == 'التوب':
     m.reply(f'{k} اهلين بيك في قوائم التوب\nللاستفسار - @{channel}',
     reply_markup=InlineKeyboardMarkup (
       [
       [
         InlineKeyboardButton ('توب الفلوس 💸', callback_data=f'topfloos:{m.from_user.id}'),
         InlineKeyboardButton ('توب الحرامية 💰', callback_data=f'topzrf:{m.from_user.id}'),
       ],
       [
        InlineKeyboardButton ('sᴏᴜʀᴄᴇ ᴍɪᴋᴇʏ',url=f't.me/{channel}')
       ]
       ]
     ))

   if text == 'توب الفلوس':
     if not r.smembers('BankList'):
       return m.reply(f'{k} ماكو حسابات بالبنك')
     else:
       rep = InlineKeyboardMarkup (
         [[InlineKeyboardButton ('sᴏᴜʀᴄᴇ ᴍɪᴋᴇʏ', url=f't.me/{channel}')]]
       )
       if r.get('BankTop'):
          text = r.get('BankTop')
          if not r.get(f'{m.from_user.id}:Floos'):
            floos = 0
          else:
            floos = int(r.get(f'{m.from_user.id}:Floos'))
          get = r.ttl('BankTop')
          wait = time.strftime('%M:%S', time.gmtime(get))
          text += '\n━━━━━━━━━'
          text += f'\n# You ) {floos:,} 💸 l {m.from_user.first_name}'
          text += f'\n\n[قوانين التُوب](https://t.me/{botUsername}?start=rules)'
          text += f'\n\nالقائمة تتحدث بعد {wait} دقيقة'
          return m.reply(text, disable_web_page_preview=True,reply_markup=rep)
       else:
          users = []
          ccc = 0
          for user in r.smembers('BankList'):
            ccc += 1
            id = int(user)
            if r.get(f'{id}:bankName'):
              name = r.get(f'{id}:bankName')[:10]
            else:
              try:
                name = c.get_chat(id).first_name
                r.set(f'{id}:bankName',name)
              except:
                name = 'INVALID_NAME'
                r.set(f'{id}:bankName',name)
            if not r.get(f'{id}:Floos'):
              floos = 0
            else:
              floos = int(r.get(f'{id}:Floos'))
            users.append({'name':name, 'money':floos})
          top = get_top(users)
          text = 'توب 20 اغنى اشخاص:\n\n'
          count = 0
          for user in top:
            count += 1
            if count == 21:
              break
            emoji = get_emoji_bank(count)
            floos = user['money']
            name = user ['name']
            text += f'**{emoji}{floos:,}** 💸 l {name.replace("*","").replace("`","").replace("|","").replace("#","").replace("<","").replace(">","").replace("_","")}\n'
          r.set('BankTop',text,ex=300)
          if not r.get(f'{m.from_user.id}:Floos'):
            floos_from_user = 0
          else:
            floos_from_user = int(r.get(f'{m.from_user.id}:Floos'))
          text += '\n━━━━━━━━━'
          text += f'\n# You ) {floos_from_user:,} 💸 l {m.from_user.first_name}'
          text += f'\n\n[قوانين التُوب](https://t.me/{botUsername}?start=rules)'
          get = r.ttl('BankTop')
          wait = time.strftime('%M:%S', time.gmtime(get))
          text += f'\n\nالقائمة تتحدث بعد {wait} دقيقة'
          return m.reply(text,disable_web_page_preview=True,reply_markup=rep)


   if text == 'توب الحراميه' or text == 'توب الحرامية' or text == 'توب الخمط':
     if not r.smembers('BankList'):
       return m.reply(f'{k} ماكو حسابات بالبنك')
     else:
       rep = InlineKeyboardMarkup (
         [[InlineKeyboardButton ('sᴏᴜʀᴄᴇ ᴍɪᴋᴇʏ', url=f't.me/{channel}')]]
       )
       if r.get('BankTopZRF'):
          text = r.get('BankTopZRF')
          if not r.get(f'{m.from_user.id}:Zrf'):
            zrf = 0
          else:
            zrf = int(r.get(f'{m.from_user.id}:Zrf'))
          get = r.ttl('BankTopZRF')
          wait = time.strftime('%M:%S', time.gmtime(get))
          text += '\n━━━━━━━━━'
          text += f'\n# You ) {zrf:,} 💰 l {m.from_user.first_name}'
          text += f'\n\n[قوانين التُوب](https://t.me/{botUsername}?start=rules)'
          text += f'\n\nالقائمة تتحدث بعد {wait} دقيقة'
          return m.reply(text, disable_web_page_preview=True,reply_markup=rep)
       else:
          users = []
          ccc = 0
          for user in r.smembers('BankList'):
            ccc += 1
            id = int(user)
            if r.get(f'{id}:bankName'):
              name = r.get(f'{id}:bankName')[:10]
            else:
              try:
                name = c.get_chat(id).first_name
                r.set(f'{id}:bankName',name)
              except:
                name = 'INVALID_NAME'
                r.set(f'{id}:bankName',name)
            if not r.get(f'{id}:Zrf'):
              zrf = 0
            else:
              zrf = int(r.get(f'{id}:Zrf'))
            users.append({'name':name, 'money':zrf})
          top = get_top(users)
          text = 'توب 20 اكثر الحراميه خمطًا:\n\n'
          count = 0
          for user in top:
            count += 1
            if count == 21:
              break
            emoji = get_emoji_bank(count)
            floos = user['money']
            name = user ['name']
            text += f'**{emoji}{floos:,}** 💰 l⁪⁬⁪⁬⁮⁪⁬⁪⁬⁮{name.replace("*","").replace("`","").replace("|","").replace("#","").replace("<","").replace(">","").replace("_","")}\n'
          r.set('BankTopZRF',text,ex=300)
          if not r.get(f'{m.from_user.id}:Zrf'):
            floos_from_user = 0
          else:
            floos_from_user = int(r.get(f'{m.from_user.id}:Zrf'))
          text += '\n━━━━━━━━━'
          text += f'\n# You ) {floos_from_user:,} 💰 l {m.from_user.first_name}'
          text += f'\n\n[قوانين التُوب](https://t.me/{botUsername}?start=rules)'
          get = r.ttl('BankTopZRF')
          wait = time.strftime('%M:%S', time.gmtime(get))
          text += f'\n\nالقائمة تتحدث بعد {wait} دقيقة'
          m.reply(text,disable_web_page_preview=True,reply_markup=rep)

   if text == 'متزوجين' or text == 'المتزوجين':
     if not r.smembers(f'{m.chat.id}:zwag:{Dev_Neptune}'):
        return m.reply(f'{k} محد متزوج بالكروب')
     else:
        users = []
        ccc = 0
        for marriage in r.smembers(f'{m.chat.id}:zwag:{Dev_Neptune}'):
           user_id_1 = int(marriage.split('--')[0])
           user_id_2 = int(marriage.split('--')[1].split('&&')[0])
           mahr_info = marriage.split('&&floos=')[1]
           ccc += 1

           # الحصول على اسم المستخدم الأول
           try:
               user_1 = c.get_users(user_id_1)
               if user_1.first_name:
                 # تنظيف الاسم من الرموز الخاصة
                 name_1 = user_1.first_name[:10].replace("*","").replace("`","").replace("|","").replace("#","").replace("<","").replace(">","").replace("_","").replace("[","").replace("]","").replace("(","").replace(")","")
               else:
                 name_1 = "مستخدم"
           except:
               name_1 = 'مستخدم محذوف'

           # الحصول على اسم المستخدم الثاني
           try:
               user_2 = c.get_users(user_id_2)
               if user_2.first_name:
                 # تنظيف الاسم من الرموز الخاصة
                 name_2 = user_2.first_name[:10].replace("*","").replace("`","").replace("|","").replace("#","").replace("<","").replace(">","").replace("_","").replace("[","").replace("]","").replace("(","").replace(")","")
               else:
                 name_2 = "مستخدم"
           except:
               name_2 = 'مستخدم محذوف'

           # حفظ بيانات المستخدمين
           user_1_obj = None
           user_2_obj = None
           try:
             user_1_obj = c.get_users(user_id_1)
           except:
             pass
           try:
             user_2_obj = c.get_users(user_id_2)
           except:
             pass

           users.append({'name_1':name_1, 'name_2':name_2,'mahr':mahr_info, 'count':ccc, 'user_1_obj':user_1_obj, 'user_2_obj':user_2_obj})

        text = f'{k} قائمة المتزوجين في الكروب:\n\n'
        count = 0
        for user in users:
          count += 1
          if count > 20:  # عرض أول 20 زواج فقط
            break
          emoji = get_emoji_bank(count)
          mahr = user['mahr']
          name_1 = user['name_1']
          name_2 = user['name_2']

          # إضافة الأسماء مع الروابط
          if user.get('user_1_obj'):
            # إنشاء mention صحيح للمستخدم الأول
            if user['user_1_obj'].username:
              name_1_display = f"@{user['user_1_obj'].username}"
            else:
              name_1_display = f"[{name_1}](tg://user?id={user['user_1_obj'].id})"
          else:
            name_1_display = name_1

          if user.get('user_2_obj'):
            # إنشاء mention صحيح للمستخدم الثاني
            if user['user_2_obj'].username:
              name_2_display = f"@{user['user_2_obj'].username}"
            else:
              name_2_display = f"[{name_2}](tg://user?id={user['user_2_obj'].id})"
          else:
            name_2_display = name_2

          text += f'**{emoji}** 👫 {name_1_display} 💕 {name_2_display}\n**💸 المهر:** {mahr}\n\n'

        return m.reply(text, disable_web_page_preview=True)


   '''
   if text == 'تصفير التوب':
     if devp_pls(m.from_user.id,m.chat.id):
       if not r.get('BankTop'):
         return m.reply('اكتب توب الفلوس وارجع حاول')
       if not r.get('BankTopZRF'):
         return m.reply('اكتب توب الحراميه وارجع حاول')
       else:
         m.reply(f'{k} تمام صفرت التوب')
         users = []
         ccc = 0
         for user in r.smembers('BankList'):
            ccc += 1
            id = int(user)
            if r.get(f'{id}:bankName'):
              name = r.get(f'{id}:bankName')[:10]
            else:
              try:
                name = c.get_chat(id).first_name
                r.set(f'{id}:bankName',name)
              except:
                name = 'INVALID_NAME'
                r.set(f'{id}:bankName',name)
            if not r.get(f'{id}:Zrf'):
              zrf = 0
            else:
              zrf = int(r.get(f'{id}:Zrf'))
            users.append({'name':name, 'money':zrf})
         top = get_top(users)
         text = ''
         count = 0
         for user in top:
            count += 1
            if count == 3:
              break
            emoji = get_emoji_bank(count)
            floos = user['money']
            name = user ['name']
            text += f'{emoji}{floos} 💰 l {name}\n'
         r.set(f'BankTopLastZrf',text)
         users = []
         ccc = 0
         for user in r.smembers('BankList'):
            ccc += 1
            id = int(user)
            if r.get(f'{id}:bankName'):
              name = r.get(f'{id}:bankName')[:10]
            else:
              try:
                name = c.get_chat(id).first_name
                r.set(f'{id}:bankName',name)
              except:
                name = 'INVALID_NAME'
                r.set(f'{id}:bankName',name)
            if not r.get(f'{id}:Floos'):
              floos = 0
            else:
              floos = int(r.get(f'{id}:Floos'))
         users.append({'name':name, 'money':floos})
         top = get_top(users)
         text = ''
         count = 0
         for user in top:
            count += 1
            if count == 3:
              break
            emoji = get_emoji_bank(count)
            floos = user['money']
            name = user ['name']
            text += f'**{emoji}{floos}** 💸 l {name}\n'
         r.set(f'BankTopLast',text)
         keys = r.keys('*:Floos')
         for a in keys:
           r.delete(a)
   '''

   if text == 'حسابي':
     if not r.sismember('BankList', m.from_user.id):
       return m.reply(f'{k} ماعندك حساب بنكي ارسل ↢ ( `انشاء حساب بنكي` )')
     else:
       card = r.get(f'{m.from_user.id}:bankCard')
       id = int(r.get(f'{m.from_user.id}:bankID'))
       bank = r.get(f'{m.from_user.id}:bankType')
       if not r.get(f'{m.from_user.id}:Floos'):
         floos = 0
       else:
         floos = int(r.get(f'{m.from_user.id}:Floos'))
       if r.get(f'{m.from_user.id}:bankName'):
         name = r.get(f'{m.from_user.id}:bankName')
       else:
         name = m.from_user.first_name
       m.reply(f'''{k} الاسم ↢ ⁪⁬⁪⁬⁮⁪⁬⁪⁬⁮{name.replace("*","").replace("`","").replace("|","").replace("#","").replace("<","").replace(">","").replace("_","")}
{k} الحساب ↢ `{id}`
{k} بنك ↢ ( {bank} )
{k} نوع ↢ ( {card} )
{k} الرصيد ↢ ( {floos} دينار عراقي 💸 )
☆''')

   if text == 'انشاء حساب بنكي':
     if r.sismember('BankList', m.from_user.id):
       bank = r.get(f'{m.from_user.id}:bankType')
       acc_id = int(r.get(f'{m.from_user.id}:bankID'))
       return m.reply(f'{k} عندك حساب في بنك {bank}\n\n{k} لتفاصيل اكثر اكتب\n{k} `حساب {acc_id}`')
     else:
       r.set(f'{m.from_user.id}:createBank:{m.chat.id}',1,ex=300)
       '''
       return m.reply(f'– علمود تسوي حساب لازم تختار بنك\n\n{k} `الرشيد`\n{k} `الرافدين`\n{k} `الاهلي`\n{k} `عبد الفتاح السيسي`\n\n- اضغط للنسخ')
       '''
       return m.reply(f'– علمود تسوي حساب لازم تختار بنك\n\n{k} `الرشيد`\n{k} `الرافدين`\n{k} `الاهلي`\n\n- اضغط للنسخ')


   if text == 'مسح حسابي' or text == 'مسح حساب بنكي' or text == 'مسح الحساب البنكي':
     if not r.sismember('BankList', m.from_user.id):
       return m.reply(f'{k} ماعندك حساب بنكي')
     else:
       # حذف المستخدم من قائمة البنك
       r.srem('BankList', m.from_user.id)

       # حذف جميع البيانات المرتبطة بالحساب البنكي
       user_id = m.from_user.id

       # حذف رقم الحساب من الربط
       if r.get(f'{user_id}:bankID'):
         bank_id = r.get(f'{user_id}:bankID')
         r.delete(f'{bank_id}:getAccBank')

       # حذف بيانات الحساب الأساسية
       r.delete(f'{user_id}:bankID')
       r.delete(f'{user_id}:bankName')
       r.delete(f'{user_id}:bankType')
       r.delete(f'{user_id}:bankCard')
       r.delete(f'{user_id}:Floos')
       r.delete(f'{user_id}:Zrf')

       # حذف مفاتيح الانتظار للألعاب البنكية
       r.delete(f'{user_id}:BankWait')
       r.delete(f'{user_id}:BankWaitB5')
       r.delete(f'{user_id}:BankWaitZRF')
       r.delete(f'{user_id}:BankWaitEST')
       r.delete(f'{user_id}:BankWaitHZ')
       r.delete(f'{user_id}:BankWait3JL')
       r.delete(f'{user_id}:BankWaitKNZ')
       r.delete(f'{user_id}:BankWaitMZROF')
       r.delete(f'{user_id}:BankWaitKSHT:{Dev_Neptune}')

       # حذف بيانات الزواج المرتبطة بالبنك
       r.delete(f'{user_id}:MARRYTEXT:{m.chat.id}{Dev_Neptune}')
       r.delete(f'{user_id}:MARRYMONEY:{m.chat.id}{Dev_Neptune}')
       r.delete(f'{user_id}:marriedMan:{m.chat.id}{Dev_Neptune}')
       r.delete(f'{user_id}:marriedWomen:{m.chat.id}{Dev_Neptune}')

       # إزالة المستخدم من قوائم البنك الأخرى
       r.srem('BankZrf', user_id)

       m.reply(f'{k} تم حذف حسابك البنكي وجميع البيانات المرتبطة به بنجاح')

   if text.startswith('حساب ') and len(text.split()) == 2 and re.findall('[0-9]+', text):
      acc_id = int(re.findall('[0-9]+', text)[0])
      if r.get(f'{acc_id}:getAccBank'):
         id = int(r.get(f'{acc_id}:getAccBank'))
         if r.get(f'{id}:bankName'):
           name = r.get(f'{id}:bankName')[:10]
         else:
           gett = c.get_users(int(r.get(f'{acc_id}:getAccBank')))
           name = gett.first_name
           r.set(f'{id}:bankName',name)
         bank = r.get(f'{id}:bankType')
         card = r.get(f'{id}:bankCard')
         if not r.get(f'{id}:Floos'):
           floos = 0
         else:
           floos = int(r.get(f'{id}:Floos'))
         m.reply(f'''
{k} الاسم ↢ ⁪⁬⁪⁬⁮⁪⁬⁪⁬⁮{name.replace("*","").replace("`","").replace("|","").replace("#","").replace("<","").replace(">","").replace("_","")}
{k} الحساب ↢ `{acc_id}`
{k} بنك ↢ ( {bank} )
{k} نوع ↢ ( {card} )
{k} الرصيد ↢ ( `{floos}` دينار عراقي 💸 )
☆
''')

   if text.startswith('تحويل ') and len(text.split()) == 2 and re.findall('[0-9]+', text):
      floos_to_trans = int(re.findall('[0-9]+', text)[0])
      if not r.get(f'{m.from_user.id}:Floos'):
        floos = 0
      else:
        floos = int(r.get(f'{m.from_user.id}:Floos'))
      if floos_to_trans < 200:
        return m.reply(f'{k} الحد الادنى المسموح هو 200 دينار عراقي')
      else:
        if floos_to_trans > floos:
          return m.reply(f'{k} فلوسك ماتكفي')
        if not r.sismember('BankList', m.from_user.id):
          return m.reply(f'{k} ماعندك حساب بنكي ارسل ↢ ( `انشاء حساب بنكي` )')
        else:
          r.set(f'{m.from_user.id}:toTrans:{m.chat.id}{Dev_Neptune}',floos_to_trans, ex=600)
          return m.reply(f'{k} ارسل هسة رقم حساب البنكي الي تريد تحول له')



   if text.startswith('حظ ') and len(text.split()) == 2 and re.findall('[0-9]+', text):
     if not r.sismember('BankList', m.from_user.id):
       return m.reply(f'{k} ماعندك حساب بنكي ارسل ↢ ( `انشاء حساب بنكي` )')
     if r.get(f'{m.from_user.id}:BankWaitHZ'):
       get = r.ttl(f'{m.from_user.id}:BankWaitHZ')
       wait = time.strftime('%M:%S', time.gmtime(get))
       return m.reply(f'{k} ما تكدر تلعب لعبة الحظ هسة ! \n{k} تعال بعد {wait} دقيقة')
     else:
       if not r.get(f'{m.from_user.id}:Floos'):
         floos = 0
       else:
         floos = int(r.get(f'{m.from_user.id}:Floos'))
       floos_to_hz = int(re.findall('[0-9]+', text)[0])
       if floos_to_hz == 0:
         return m.reply(f'{k} ما تكدر تلعب بالصفر')
       if floos_to_hz > floos:
         return m.reply(f'{k} فلوسك ماتكفي')
       else:
         r.set(f'{m.from_user.id}:BankWaitHZ',1,ex=600)
         hzz = random.choice(['yes','no'])
         if hzz == 'yes':
           fls = floos_to_hz
           floos_com = floos+fls
           r.set(f'{m.from_user.id}:Floos', floos+fls)
           return m.reply(f'{k} مبروك فزت بالحظ !\n{k} فلوسك قبل ↢ ( **{floos}** دينار عراقي 💸 )\n{k} فلوسك هسة ↢ ( **{floos_com}** دينار عراقي 💸 )')
         else:
           fls = floos-floos_to_hz
           if fls == 0:
              r.delete(f'{m.from_user.id}:Floos')
           else:
              r.set(f'{m.from_user.id}:Floos', fls)
           return m.reply(f'{k} للأسف خسرت بالحظ !\n{k} فلوسك قبل ↢ ( **{floos}** دينار عراقي 💸 )\n{k} فلوسك هسة ↢ ( **{fls}** دينار عراقي 💸 )')


   if text == "حظ فلوسي":
     if not r.sismember('BankList', m.from_user.id):
       return m.reply(f'{k} ماعندك حساب بنكي ارسل ↢ ( `انشاء حساب بنكي` )')
     if r.get(f'{m.from_user.id}:BankWaitHZ'):
       get = r.ttl(f'{m.from_user.id}:BankWaitHZ')
       wait = time.strftime('%M:%S', time.gmtime(get))
       return m.reply(f'{k} ما تكدر تلعب لعبة الحظ هسة ! \n{k} تعال بعد {wait} دقيقة')
     else:
       if not r.get(f'{m.from_user.id}:Floos'):
         floos = 0
       else:
         floos = int(r.get(f'{m.from_user.id}:Floos'))
       floos_to_hz = floos
       if floos_to_hz == 0:
         return m.reply(f'{k} ما تكدر تلعب بالصفر')
       else:
         r.set(f'{m.from_user.id}:BankWaitHZ',1,ex=600)
         hzz = random.choice(['yes','no'])
         if hzz == 'yes':
           fls = floos_to_hz
           floos_com = floos+fls
           r.set(f'{m.from_user.id}:Floos', floos+fls)
           return m.reply(f'{k} مبروك فزت بالحظ !\n{k} فلوسك قبل ↢ ( **{floos}** دينار عراقي 💸 )\n{k} فلوسك هسة ↢ ( **{floos_com}** دينار عراقي 💸 )')
         else:
           fls = floos-floos_to_hz
           if fls == 0:
              r.delete(f'{m.from_user.id}:Floos')
           else:
              r.set(f'{m.from_user.id}:Floos', fls)
           return m.reply(f'{k} للأسف خسرت بالحظ !\n{k} فلوسك قبل ↢ ( "**{floos}** دينار عراقي 💸 )\n{k} فلوسك هسة ↢ ( **{fls}** دينار عراقي 💸 )')

   if text == 'عجله' or text == 'عجلة':
     if not r.sismember('BankList', m.from_user.id):
       return m.reply(f'{k} ماعندك حساب بنكي ارسل ↢ ( `انشاء حساب بنكي` )')
     else:
       if r.get(f'{m.from_user.id}:BankWait3JL'):
         get = r.ttl(f'{m.from_user.id}:BankWait3JL')
         wait = time.strftime('%M:%S', time.gmtime(get))
         return m.reply(f'{k} ما تكدر تلعب عجلة هسة ! \n{k} تعال بعد {wait} دقيقة')
       else:
         r.set(f'{m.from_user.id}:BankWait3JL',1,ex=300)
         rep = m.reply(f'{k} حلف العجلة بعد ٣ ثواني',reply_markup=InlineKeyboardMarkup ([[InlineKeyboardButton ('³',callback_data='None')]]))
         time.sleep(1)
         rep.edit_text(f'{k} حلف العجلة بعد ثانيتين',reply_markup=InlineKeyboardMarkup ([[InlineKeyboardButton ('²',callback_data='None')]]))
         time.sleep(1)
         rep.edit_text(f'{k} حلف العجلة بعد ثانية',reply_markup=InlineKeyboardMarkup ([[InlineKeyboardButton ('¹',callback_data='None')]]))
         time.sleep(1)
         emojis_3jl = [
         '💸','💸','💸','💸','💸','💸','💸',
         '💸','💸','💸','💸','💸','💸','💸',
         '⚡','⚡','⚡','⚡','⚡','⚡','⚡',
         '⚡','⚡','⚡','⚡','⚡','⚡','⚡',
         '💣','💣','💣','💣','💣','💣','💣',
         '💣','💣','💣','💣','💣','💣','💣',
         '🍒','🍒','🍒','🍒','🍒','🍒','🍒',
         '🍒','🍒','🍒','🍒','🍒','🍒','🍒',
         '💎','💎','💎','💎','💎','💎','💎',
         '💎','💎','💎','💎','💎','💎','💎'
         ]
         emoji1 = random.choice(emojis_3jl)
         emoji2 = random.choice(emojis_3jl)
         emoji3 = random.choice(emojis_3jl)
         reply_ma = InlineKeyboardMarkup (
           [
             [
               InlineKeyboardButton (emoji1, callback_data='None'),
               InlineKeyboardButton (emoji2, callback_data='None'),
               InlineKeyboardButton (emoji3, callback_data='None'),
             ],
             [
               InlineKeyboardButton ('🫦', url=f't.me/{channel}')
             ]
           ]
         )
         if emoji1 == emoji2 and emoji2 == emoji3:
            chance = random.choice([100000, 200000, 300000])
            if not r.get(f'{m.from_user.id}:Floos'):
              floos = 0
            else:
              floos = int(r.get(f'{m.from_user.id}:Floos'))
            rep.edit_text(f'{k} فزت بعجلة الحظ!\n\n{k} مبلغ الربح ( {chance} دينار عراقي 💸 )\n{k} فلوسك قبل ( `{floos}` دينار عراقي 💸 )\n{k} فلوسك هسة ( `{floos+chance}` دينار عراقي 💸 )',reply_markup=reply_ma)
            r.set(f'{m.from_user.id}:Floos', floos+chance)
         else:
            chance = random.randint(100,1000)
            if not r.get(f'{m.from_user.id}:Floos'):
              floos = 0
            else:
              floos = int(r.get(f'{m.from_user.id}:Floos'))
            rep.edit_text(f'{k} للأسف خسرت بعجلة الحظ!\n\n{k} خذ {chance} دينار عراقي علمود ماتصيح\n{k} فلوسك قبل ( `{floos}` دينار عراقي 💸 )\n{k} فلوسك هسة ( `{floos+chance}` دينار عراقي 💸 )',reply_markup=reply_ma)
            r.set(f'{m.from_user.id}:Floos', floos+chance)

   if text.startswith('استثمار ') and len(text.split()) == 2 and re.findall('[0-9]+', text):
     if not r.sismember('BankList', m.from_user.id):
       return m.reply(f'{k} ماعندك حساب بنكي ارسل ↢ ( `انشاء حساب بنكي` )')
     if r.get(f'{m.from_user.id}:BankWaitEST'):
       get = r.ttl(f'{m.from_user.id}:BankWaitEST')
       wait = time.strftime('%M:%S', time.gmtime(get))
       return m.reply(f'{k} ما تكدر تستثمر هسة ! \n{k} تعال بعد {wait} دقيقة')
     else:
       if not r.get(f'{m.from_user.id}:Floos'):
         floos = 0
       else:
         floos = int(r.get(f'{m.from_user.id}:Floos'))
       floos_to_est = int(re.findall('[0-9]+', text)[0])
       if floos_to_est == 0:
         return m.reply(f'{k} ما تكدر تلعب بالصفر')
       if floos_to_est > floos:
         return m.reply(f'{k} فلوسك ماتكفي')
       if floos_to_est < 2000:
         return m.reply(f'{k} للأسف لازم تستثمر ب 2000 دينار عراقي عالأقل')
       else:
         r.set(f'{m.from_user.id}:BankWaitEST',1,ex=300)
         one = int(floos_to_est/random.randint(1,9))
         rb7 = int(is_what_percent_of(one,floos_to_est))
         r.set(f'{m.from_user.id}:Floos',floos+one)
         m.reply(f'''
{k}  استثمار ناجح!
{k} نسبة الربح ↢ {rb7}%
{k} مبلغ الربح ↢ ( `{one}` دينار عراقي )
{k} فلوسك صارت ↢ ( `{floos+one}` دينار عراقي 💸 )
''')

   if text == "استثمار فلوسي":
     if not r.sismember('BankList', m.from_user.id):
       return m.reply(f'{k} ماعندك حساب بنكي ارسل ↢ ( `انشاء حساب بنكي` )')
     if r.get(f'{m.from_user.id}:BankWaitEST'):
       get = r.ttl(f'{m.from_user.id}:BankWaitEST')
       wait = time.strftime('%M:%S', time.gmtime(get))
       return m.reply(f'{k} ما تكدر تستثمر هسة ! \n{k} تعال بعد {wait} دقيقة')
     else:
       if not r.get(f'{m.from_user.id}:Floos'):
         floos = 0
       else:
         floos = int(r.get(f'{m.from_user.id}:Floos'))
       floos_to_est = floos
       if floos_to_est == 0:
         return m.reply(f'{k} ما تكدر تستثمر بالصفر')
       if floos_to_est < 2000:
         return m.reply(f'{k} للأسف لازم تستثمر ب 2000 دينار عراقي عالأقل')
       else:
         r.set(f'{m.from_user.id}:BankWaitEST',1,ex=300)
         one = int(floos_to_est/random.randint(1,9))
         rb7 = int(is_what_percent_of(one,floos_to_est))
         r.set(f'{m.from_user.id}:Floos',floos+one)
         m.reply(f'''
{k}  استثمار ناجح!
{k} نسبة الربح ↢ {rb7}%
{k} مبلغ الربح ↢ ( `{one}` دينار عراقي )
{k} فلوسك صارت ↢ ( `{floos+one}` دينار عراقي 💸 )
''')

   if text == 'كنز':
     if not r.sismember('BankList', m.from_user.id):
       return m.reply(f'{k} ماعندك حساب بنكي ارسل ↢ ( `انشاء حساب بنكي` )')
     if r.get(f'{m.from_user.id}:BankWaitKNZ'):
       get = r.ttl(f'{m.from_user.id}:BankWaitKNZ')
       wait = time.strftime('%M:%S', time.gmtime(get))
       return m.reply(f'{k} كنزك بينزل بعد {wait} دقيقة')
     else:
       if not r.get(f'{m.from_user.id}:Floos'):
          floos = 0
       else:
          floos = int(r.get(f'{m.from_user.id}:Floos'))
       knz = random.choice(knzs)
       money = knz['credit']
       name = knz['name']
       r.set(f'{m.from_user.id}:BankWaitKNZ',1, ex=600)
       r.set(f'{m.from_user.id}:Floos', floos+money)
       fls = floos+money
       return m.reply(f'اشعار ايداع {m.from_user.mention(m.from_user.first_name[:10])}⁪⁬⁪⁬⁮⁪⁬⁪\nالمبلغ: **{money}** دينار عراقي\nالكنز: {name}\nنوع العملية: ربح كنز\nرصيدك هسة: **{fls}** دينار عراقي 💸')

   if text == 'بخشيش':
     if not r.sismember('BankList', m.from_user.id):
       return m.reply(f'{k} ماعندك حساب بنكي ارسل ↢ ( `انشاء حساب بنكي` )')
     if r.get(f'{m.from_user.id}:BankWaitB5'):
       get = r.ttl(f'{m.from_user.id}:BankWaitB5')
       wait = time.strftime('%M:%S', time.gmtime(get))
       return m.reply(f'{k} ما تكدر اعطيك بخشيش هسة\n{k} تعال بعد {wait} دقيقة')
     else:
       b5 = random.randint(5,1000)
       r.set(f'{m.from_user.id}:BankWaitB5',1, ex=300)
       if not r.get(f'{m.from_user.id}:Floos'):
          floos = 0
       else:
          floos = int(r.get(f'{m.from_user.id}:Floos'))
       r.set(f'{m.from_user.id}:Floos', floos+b5)
       m.reply(f'{k} دلعتك ونطيتك {b5} دينار عراقي 💸')

   if text == 'راتب':
     if not r.sismember('BankList', m.from_user.id):
       return m.reply(f'{k} ماعندك حساب بنكي ارسل ↢ ( `انشاء حساب بنكي` )')
     if r.get(f'{m.from_user.id}:BankWait'):
       get = r.ttl(f'{m.from_user.id}:BankWait')
       wait = time.strftime('%M:%S', time.gmtime(get))
       return m.reply(f'{k} راتبك بينزل بعد {wait} دقيقة')
     else:
       job = random.choice(jobs)
       money = job['credit']
       name = job['name']
       r.set(f'{m.from_user.id}:BankWait',1, ex=300)
       if not r.get(f'{m.from_user.id}:Floos'):
          floos = 0
       else:
          floos = int(r.get(f'{m.from_user.id}:Floos'))
       r.set(f'{m.from_user.id}:Floos', floos+money)
       fls = floos+money
       m.reply(f'اشعار ايداع⁪⁬⁪⁬⁮⁪⁬⁪ {m.from_user.mention(m.from_user.first_name[:10])}\nالمبلغ: **{money}** دينار عراقي\nوظيفتك: {name}\nنوع العملية: اضافة راتب\nرصيدك هسة: **{fls}** دينار عراقي 💸')

   if text == 'خمط' and m.reply_to_message and m.reply_to_message.from_user:
     if m.reply_to_message.from_user.id == int(Dev_Neptune):
       return m.reply('?')
     if not r.sismember('BankList', m.from_user.id):
       return m.reply(f'{k} ماعندك حساب بنكي ارسل ↢ ( `انشاء حساب بنكي` )')
     if not r.sismember('BankList', m.reply_to_message.from_user.id):
       return m.reply(f'{k} ماعنده حساب بنكي')
     if m.reply_to_message.from_user.id == m.from_user.id:
       return m.reply('تريد تخمط نفسك؟')
     if r.get(f'{m.from_user.id}:BankWaitZRF'):
       get = r.ttl(f'{m.from_user.id}:BankWaitZRF')
       wait = time.strftime('%M:%S', time.gmtime(get))
       return m.reply(f'{k} يولد اشرد الشرطة لهسة تدور عليك\n{k} تكدر تخمط مره ثانيه بعد {wait}')
     if r.get(f'{m.reply_to_message.from_user.id}:BankWaitMZROF'):
       get = r.ttl(f'{m.reply_to_message.from_user.id}:BankWaitMZROF')
       wait = time.strftime('%M:%S', time.gmtime(get))
       return m.reply(f'{k} هذا المسكين مبيوك قبل شوي\n{k} تكدر تخمطه بعد {wait}')
     if not r.get(f'{m.reply_to_message.from_user.id}:Floos'):
       return m.reply(f'{k} مفلس ماعنده ولا دينار عراقي')
     if int(r.get(f'{m.reply_to_message.from_user.id}:Floos')) < 2000:
       return m.reply(f'{k} ما تكدر تخمطه لان فلوسه اقل من 2000 دينار عراقي')
     else:
       zrf = random.randint(50,1000)
       r.set(f'{m.from_user.id}:BankWaitZRF',1,ex=300)
       r.set(f'{m.reply_to_message.from_user.id}:BankWaitMZROF',1,ex=300)
       floos = int(r.get(f'{m.reply_to_message.from_user.id}:Floos'))
       r.set(f'{m.reply_to_message.from_user.id}:Floos',floos-zrf)
       m.reply(f'{k} هاك يالحرامي خمطته {zrf} دينار عراقي 💸')
       if not r.get(f'{m.from_user.id}:Floos'):
         floos_from_user = 0
       else:
         floos_from_user = int(r.get(f'{m.from_user.id}:Floos'))
       r.set(f'{m.from_user.id}:Floos',floos_from_user+zrf)
       r.sadd('BankZrf',m.from_user.id)
       if r.get(f'{m.from_user.id}:Zrf'):
          zrff = int(r.get(f'{m.from_user.id}:Zrf'))
       else:
          zrff = 0
       r.set(f'{m.from_user.id}:Zrf',zrff+zrf)
       try:
         c.send_message(
           m.reply_to_message.from_user.id,
           f'الحق الحق حلالك!!\nهذا الحرامي {m.from_user.mention}\nسرق منك ( {zrf} دينار عراقي 💸 )\n༄',
           reply_markup=InlineKeyboardMarkup (
             [[
               InlineKeyboardButton (m.chat.title, url=m.link)
             ]]
           )
           )
       except:
         pass


   if text == 'تصفير البنك':
     if devp_pls(m.from_user.id,m.chat.id):
        return m.reply(f'{k} متأكد تريد تصفر البنك ؟',reply_markup=InlineKeyboardMarkup ([[InlineKeyboardButton ('اي', callback_data='yes:del:bank')],[InlineKeyboardButton ('لا', callback_data='no:del:bank')]]))

   if text == 'فلوسي':
     if not r.get(f'{m.from_user.id}:Floos'):
        m.reply(f'{k} ماعندك فلوس ارسل الالعاب وابدا جمع الفلوس')
     else:
        floos = int(r.get(f'{m.from_user.id}:Floos'))
        return m.reply(f'{k} فلوسك `{floos}` دينار عراقي 💸')

   if text == 'فلوس':
     if not m.reply_to_message:
       if not r.get(f'{m.from_user.id}:Floos'):
         return m.reply(f'{k} ماعندك فلوس ارسل الالعاب وابدا جمع الفلوس')
       else:
         floos = int(r.get(f'{m.from_user.id}:Floos'))
       return m.reply(f'{k} فلوسك `{floos}` دينار عراقي 💸')
     else:
       if not r.get(f'{m.reply_to_message.from_user.id}:Floos'):
         floos = 0
       else:
         floos = int(r.get(f'{m.reply_to_message.from_user.id}:Floos'))
       return m.reply(f'{k} فلوسه ↢ ( {floos} دينار عراقي 💸 )')

   if text.startswith('بيع فلوسي ') and len(text.split()) == 3 and re.findall('[0-9]+', text):
     if not r.get(f'{m.from_user.id}:Floos'):
        m.reply(f'{k} للاسف انت مفلس عندك 0 دينار عراقي')
     else:
        floos_to_sale = int(re.findall('[0-9]+', text)[0])
        floos = int(r.get(f'{m.from_user.id}:Floos'))
        if floos_to_sale == 0:
         return m.reply(f'{k} ما تكدر تريدع صفر')
        if floos_to_sale > floos:
          return m.reply(f'{k} للاسف انت مفلس عندك {floos} دينار عراقي')
        if floos_to_sale == floos:
           r.delete(f'{m.from_user.id}:Floos')
        else:
           r.set(f'{m.from_user.id}:Floos',floos-floos_to_sale)
        get = int(r.get(f'{m.chat.id}:TotalMsgs:{m.from_user.id}{Dev_Neptune}'))
        rsayl = floos_to_sale * 20
        r.set(f'{m.chat.id}:TotalMsgs:{m.from_user.id}{Dev_Neptune}', get+rsayl)
        m.reply(f'{k} بعت ( {floos_to_sale} دينار عراقي 💸 ) من فلوسك\n{k} مجموع رسايلك هسة ( {get + rsayl} ) ♭')

   if text.startswith('اضف فلوس ') and len(text.split()) == 3 and re.findall('[0-9]+', text):
     if dev2_pls(m.from_user.id,m.chat.id):
       if m.reply_to_message and m.reply_to_message.from_user:
          floos_to_add = int(re.findall('[0-9]+', text)[0])
          if not r.get(f'{m.reply_to_message.from_user.id}:Floos'):
             r.set(f'{m.reply_to_message.from_user.id}:Floos',floos_to_add)
          else:
             floos = int(r.get(f'{m.reply_to_message.from_user.id}:Floos'))
             r.set(f'{m.reply_to_message.from_user.id}:Floos',floos_to_add+floos)
          m.reply(f'「 {m.reply_to_message.from_user.mention} 」\n{k} ضفت له ( {floos_to_add} ) دينار عراقي 💸')


   if text == 'استخراج الاكواد':
      if devp_pls(m.from_user.id,m.chat.id):
         if r.get(f'{Dev_Neptune}:codeWait'):
           t = r.ttl(f'{Dev_Neptune}:codeWait')
           wait = time.strftime('%H:%M:%S', time.gmtime(t))
           return m.reply(f'{k} استخرجت اكواد الكشط من شوي تعال بعد {wait}')
         else:
           txt = 'اكواد الكشط:\n'
           ccc = 1
           for none in range(10):
             code = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(10)])
             r.set(f'{code}:CodeBank:{Dev_Neptune}',1,ex=7200)
             txt += f'{ccc} ) `{code}`\n'
             ccc += 1
           r.set(f'{Dev_Neptune}:codeWait',1,ex=7200)
           txt += '\n~ الأكواد صالحة لساعتين فقط .'
           txt += '\n༄'
           return m.reply(txt)

   if text.startswith('كشط ') and len(text.split()) == 2:
     code = text.split()[1]
     if not r.get(f'{code}:CodeBank:{Dev_Neptune}'):
       return m.reply(f'{k} الكود منتهي الصلاحيه او تابع لبوت ثاني')
     if r.get(f'{m.from_user.id}:BankWaitKSHT:{Dev_Neptune}'):
       t = r.ttl(f'{m.from_user.id}:BankWaitKSHT:{Dev_Neptune}')
       wait = time.strftime('%H:%M:%S', time.gmtime(t))
       return m.reply(f'{k} كشطت كود من شوي تعال بعد {wait}')
     else:
       r.delete(f'{code}:CodeBank:{Dev_Neptune}')
     if not r.get(f'{m.from_user.id}:Floos'):
       floos_from_user = 0
     else:
       floos_from_user = int(r.get(f'{m.from_user.id}:Floos'))
     chance = random.choice([1000000000, 2000000000, 3000000000])
     r.set(f'{m.from_user.id}:Floos',floos_from_user+chance)
     m.reply(f'{k} مبرووووك 🏆\n{k} كشطت الكود واخذت ( {chance} دينار عراقي 💸 )\n{k} فلوسك قبل ( `{floos_from_user}` دينار عراقي 💸 )\n{k} فلوسك هسة ( `{floos_from_user+chance}` دينار عراقي 💸 )')
     r.set(f'{m.from_user.id}:BankWaitKSHT:{Dev_Neptune}',1,ex=7200)
     if r.get(f'DevGroup:{Dev_Neptune}'):
       alert = f'𖡋 𝐍𝐀𝐌𝐄 ⌯ {m.from_user.mention}\n𖡋 𝐈𝐃 ⌯ `{m.from_user.id}`\n\nكشط الكود `{code}` وأخذ {chance} دينار عراقي 💸'
       c.send_message(int(r.get(f'DevGroup:{Dev_Neptune}')),alert)

   # أمر الزواج المجاني مع الموافقة
   if text == 'زواج' and m.reply_to_message and m.reply_to_message.from_user:
     if m.reply_to_message.from_user.id == c.me.id or m.reply_to_message.from_user.id == m.from_user.id:
       return m.reply('?')
     if m.reply_to_message.from_user.is_bot:
       return False
     if r.get(f'{m.from_user.id}:marriedMan:{m.chat.id}{Dev_Neptune}'):
       try:
         getUser = c.get_users(int(r.get(f'{m.from_user.id}:marriedMan:{m.chat.id}{Dev_Neptune}')))
         mention = getUser.mention
         return m.reply(f'「 {mention} 」 \n{k} تعاليييي زوجك بيخونك')
       except:
         # حذف بيانات الزواج إذا كان الحساب محذوف
         r.delete(f'{m.from_user.id}:marriedMan:{m.chat.id}{Dev_Neptune}')
         r.delete(f'{m.from_user.id}:MARRYTEXT:{m.chat.id}{Dev_Neptune}')
         r.delete(f'{m.from_user.id}:MARRYMONEY:{m.chat.id}{Dev_Neptune}')
     if r.get(f'{m.from_user.id}:marriedWomen:{m.chat.id}{Dev_Neptune}'):
       try:
         getUser = c.get_users(int(r.get(f'{m.from_user.id}:marriedWomen:{m.chat.id}{Dev_Neptune}')))
         mention = getUser.mention
         return m.reply(f'「 {mention} 」 \n{k} تعال زوجتك بتخونك')
       except:
         # حذف بيانات الزواج إذا كان الحساب محذوف
         r.delete(f'{m.from_user.id}:marriedWomen:{m.chat.id}{Dev_Neptune}')
         r.delete(f'{m.from_user.id}:MARRYTEXT:{m.chat.id}{Dev_Neptune}')
         r.delete(f'{m.from_user.id}:MARRYMONEY:{m.chat.id}{Dev_Neptune}')

     # التحقق من حالة الشخص المراد الزواج منه
     if r.get(f'{m.reply_to_message.from_user.id}:marriedWomen:{m.chat.id}{Dev_Neptune}'):
       return m.reply('「 {} 」 \n{} مو سنقل دورلك غيرها\n༄'.format(m.reply_to_message.from_user.mention,k))
     if r.get(f'{m.reply_to_message.from_user.id}:marriedMan:{m.chat.id}{Dev_Neptune}'):
       return m.reply('「 {} 」 \n{} مو سنقل دورلك غيره\n༄'.format(m.reply_to_message.from_user.mention,k))

     # حفظ بيانات طلب الزواج مؤقتاً (مجاني)
     r.set(f'marriage_request:{m.chat.id}:{m.from_user.id}:{m.reply_to_message.from_user.id}:{Dev_Neptune}',
           'قرآن', ex=300)

     # إنشاء أزرار الموافقة والرفض
     keyboard = InlineKeyboardMarkup([
         [
             InlineKeyboardButton("قبول",
                                callback_data=f"accept_marriage:{m.from_user.id}:{m.reply_to_message.from_user.id}:قرآن:{m.chat.id}"),
             InlineKeyboardButton("رفض",
                                callback_data=f"reject_marriage:{m.from_user.id}:{m.reply_to_message.from_user.id}:قرآن:{m.chat.id}")
         ]
     ])

     return m.reply(f'''
💍 طلب زواج

{k} 🤵 العريس ↢ ( {m.from_user.mention} )
{k} 👰 العروس ↢ ( {m.reply_to_message.from_user.mention} )
{k} 💸 المهر ↢ ( قرآن )

{k} العروس عليها الرد خلال 5 دقائق
☆
''', reply_markup=keyboard)

   # أمر الزواج العشوائي التلقائي
   if text == 'زوجني':
     # التحقق من حالة الزواج للمستخدم
     if r.get(f'{m.from_user.id}:marriedMan:{m.chat.id}{Dev_Neptune}'):
       try:
         getUser = c.get_users(int(r.get(f'{m.from_user.id}:marriedMan:{m.chat.id}{Dev_Neptune}')))
         mention = getUser.mention
         return m.reply(f'「 {mention} 」 \n{k} تعاليييي زوجك بيخونك')
       except:
         # حذف بيانات الزواج إذا كان الحساب محذوف
         r.delete(f'{m.from_user.id}:marriedMan:{m.chat.id}{Dev_Neptune}')
         r.delete(f'{m.from_user.id}:MARRYTEXT:{m.chat.id}{Dev_Neptune}')
         r.delete(f'{m.from_user.id}:MARRYMONEY:{m.chat.id}{Dev_Neptune}')
     if r.get(f'{m.from_user.id}:marriedWomen:{m.chat.id}{Dev_Neptune}'):
       try:
         getUser = c.get_users(int(r.get(f'{m.from_user.id}:marriedWomen:{m.chat.id}{Dev_Neptune}')))
         mention = getUser.mention
         return m.reply(f'「 {mention} 」 \n{k} تعال زوجتك بتخونك')
       except:
         # حذف بيانات الزواج إذا كان الحساب محذوف
         r.delete(f'{m.from_user.id}:marriedWomen:{m.chat.id}{Dev_Neptune}')
         r.delete(f'{m.from_user.id}:MARRYTEXT:{m.chat.id}{Dev_Neptune}')
         r.delete(f'{m.from_user.id}:MARRYMONEY:{m.chat.id}{Dev_Neptune}')

     # التحقق الإضافي من قائمة المتزوجين
     if r.smembers(f'{m.chat.id}:zwag:{Dev_Neptune}'):
       for marriage in r.smembers(f'{m.chat.id}:zwag:{Dev_Neptune}'):
         try:
           user_id_1 = int(marriage.split('--')[0])
           user_id_2 = int(marriage.split('--')[1].split('&&')[0])
           if m.from_user.id == user_id_1 or m.from_user.id == user_id_2:
             # المستخدم متزوج في قائمة zwag لكن ليس في البيانات المباشرة
             # نحذف من قائمة zwag ونكمل
             r.srem(f'{m.chat.id}:zwag:{Dev_Neptune}', marriage)
             break
         except:
           continue

     # الحصول على قائمة الأعضاء المتاحين للزواج
     try:
       available_members = []

       # البحث في جميع أعضاء المجموعة (نفس طريقة أمر نداء)
       for member in m.chat.get_members(limit=200):
         if (member.user and
             not member.user.is_deleted and
             not member.user.is_bot and
             member.user.id != m.from_user.id and  # استبعاد المرسل
             member.user.id != c.me.id):  # استبعاد البوت

           # التحقق من أن العضو غير متزوج
           is_married = False

           # التحقق من حالة الزواج المباشرة
           if (r.get(f'{member.user.id}:marriedMan:{m.chat.id}{Dev_Neptune}') or
               r.get(f'{member.user.id}:marriedWomen:{m.chat.id}{Dev_Neptune}')):
             is_married = True

           # التحقق من قائمة المتزوجين
           if not is_married and r.smembers(f'{m.chat.id}:zwag:{Dev_Neptune}'):
             for marriage in r.smembers(f'{m.chat.id}:zwag:{Dev_Neptune}'):
               try:
                 user_id_1 = int(marriage.split('--')[0])
                 user_id_2 = int(marriage.split('--')[1].split('&&')[0])
                 if member.user.id == user_id_1 or member.user.id == user_id_2:
                   is_married = True
                   break
               except:
                 continue

           # إضافة العضو إذا لم يكن متزوج
           if not is_married:
             available_members.append(member.user)

       # إذا لم نجد أي أعضاء متاحين، نرفض العملية
       if not available_members:
         return m.reply(f'{k} ما في أعضاء متاحين للزواج في المجموعة حالياً\n{k} جميع الأعضاء إما متزوجين أو بوتات')

       # اختيار عضو عشوائي من الأعضاء الحقيقيين فقط
       random_partner = random.choice(available_members)

       # تسجيل الزواج مباشرة بدون موافقة
       r.set(f'{m.from_user.id}:marriedMan:{m.chat.id}{Dev_Neptune}', random_partner.id)
       r.set(f'{random_partner.id}:marriedWomen:{m.chat.id}{Dev_Neptune}', m.from_user.id)

       # إنشاء mention صحيح للشريك
       partner_name = random_partner.first_name[:10] if random_partner.first_name else "مستخدم"
       if random_partner.username:
         partner_mention = f"@{random_partner.username}"
       else:
         partner_mention = f"[{partner_name}](tg://user?id={random_partner.id})"

       # إنشاء mention صحيح للمستخدم
       user_name = m.from_user.first_name[:10] if m.from_user.first_name else "مستخدم"
       if m.from_user.username:
         user_mention = f"@{m.from_user.username}"
       else:
         user_mention = f"[{user_name}](tg://user?id={m.from_user.id})"

       # إنشاء وثيقة الزواج
       to_marry = f'''
💒 وثيقة زواج

{k} 👰 العروس ↢ ( {partner_mention} )
{k} 🤵 العريس ↢ ( {user_mention} )

{k} 💸 المهر ↢ ( قرآن )
༄'''

       r.set(f'{m.from_user.id}:MARRYTEXT:{m.chat.id}{Dev_Neptune}', to_marry)
       r.set(f'{random_partner.id}:MARRYTEXT:{m.chat.id}{Dev_Neptune}', to_marry)
       r.set(f'{m.from_user.id}:MARRYMONEY:{m.chat.id}{Dev_Neptune}', 'قرآن')
       r.set(f'{random_partner.id}:MARRYMONEY:{m.chat.id}{Dev_Neptune}', 'قرآن')
       r.sadd(f'{m.chat.id}:zwag:{Dev_Neptune}', f'{random_partner.id}--{m.from_user.id}&&floos=قرآن')

       # الرسالة الجديدة بالتنسيق المطلوب
       return m.reply(f'الف مبروك الزواج من {partner_mention}')

     except Exception as e:
       print(f"خطأ في الزواج العشوائي: {e}")
       return m.reply(f'{k} حدث خطأ في العثور على شريك للزواج')


   if text == 'زواجي':
     if not r.get(f'{m.from_user.id}:MARRYTEXT:{m.chat.id}{Dev_Neptune}'):
       return m.reply(f'{k} انت سنقل')
     else:
       if r.get(f'{m.from_user.id}:marriedMan:{m.chat.id}{Dev_Neptune}'):
         try:
           getUser = c.get_users(int(r.get(f'{m.from_user.id}:marriedMan:{m.chat.id}{Dev_Neptune}')))
           txt = r.get(f'{m.from_user.id}:MARRYTEXT:{m.chat.id}{Dev_Neptune}').format(k=k,two=m.from_user.mention(m.from_user.first_name[:10]),one=getUser.mention(getUser.first_name[:10]))
           return m.reply(txt)
         except:
           # حذف بيانات الزواج إذا كان الحساب محذوف
           r.delete(f'{m.from_user.id}:marriedMan:{m.chat.id}{Dev_Neptune}')
           r.delete(f'{m.from_user.id}:MARRYTEXT:{m.chat.id}{Dev_Neptune}')
           r.delete(f'{m.from_user.id}:MARRYMONEY:{m.chat.id}{Dev_Neptune}')
           return m.reply(f'{k} تم حذف بيانات الزواج لأن الحساب غير متاح')
       if r.get(f'{m.from_user.id}:marriedWomen:{m.chat.id}{Dev_Neptune}'):
         try:
           getUser = c.get_users(int(r.get(f'{m.from_user.id}:marriedWomen:{m.chat.id}{Dev_Neptune}')))
           txt = r.get(f'{m.from_user.id}:MARRYTEXT:{m.chat.id}{Dev_Neptune}').format(k=k,two=getUser.mention(getUser.first_name[:10]),one=m.from_user.mention(m.from_user.first_name[:10]))
           return m.reply(txt)
         except:
           # حذف بيانات الزواج إذا كان الحساب محذوف
           r.delete(f'{m.from_user.id}:marriedWomen:{m.chat.id}{Dev_Neptune}')
           r.delete(f'{m.from_user.id}:MARRYTEXT:{m.chat.id}{Dev_Neptune}')
           r.delete(f'{m.from_user.id}:MARRYMONEY:{m.chat.id}{Dev_Neptune}')
           return m.reply(f'{k} تم حذف بيانات الزواج لأن الحساب غير متاح')

   if text == 'زوجتي':
     # إذا كان المستخدم رجل متزوج (marriedMan) فسيعرض زوجته
     if r.get(f'{m.from_user.id}:marriedMan:{m.chat.id}{Dev_Neptune}'):
       try:
         partner_id = int(r.get(f'{m.from_user.id}:marriedMan:{m.chat.id}{Dev_Neptune}'))
         getUser = c.get_users(partner_id)
         partner_name = getUser.first_name[:10] if getUser.first_name else "زوجتك"

         # إنشاء mention صحيح
         if getUser.username:
           partner_mention = f"@{getUser.username}"
         else:
           partner_mention = f"[{partner_name}](tg://user?id={getUser.id})"

         return m.reply(f'{k} زوجتك هي ↢ ( {partner_mention} ) 👰‍♀️💕')
       except Exception as e:
         # في حالة وجود خطأ (مثل حساب محذوف)، نحذف بيانات الزواج
         r.delete(f'{m.from_user.id}:marriedMan:{m.chat.id}{Dev_Neptune}')
         r.delete(f'{m.from_user.id}:MARRYTEXT:{m.chat.id}{Dev_Neptune}')
         r.delete(f'{m.from_user.id}:MARRYMONEY:{m.chat.id}{Dev_Neptune}')
         return m.reply(f'{k} تم حذف بيانات الزواج لأن الحساب غير متاح')
     else:
       return m.reply(f'{k} انت غير متزوج')

   if text == 'زوجي':
     # إذا كانت المستخدمة امرأة متزوجة (marriedWomen) فستعرض زوجها
     if r.get(f'{m.from_user.id}:marriedWomen:{m.chat.id}{Dev_Neptune}'):
       try:
         partner_id = int(r.get(f'{m.from_user.id}:marriedWomen:{m.chat.id}{Dev_Neptune}'))
         getUser = c.get_users(partner_id)
         partner_name = getUser.first_name[:10] if getUser.first_name else "زوجك"

         # إنشاء mention صحيح
         if getUser.username:
           partner_mention = f"@{getUser.username}"
         else:
           partner_mention = f"[{partner_name}](tg://user?id={getUser.id})"

         return m.reply(f'{k} زوجك هو ↢ ( {partner_mention} ) 🤵‍♂️💙')
       except Exception as e:
         # في حالة وجود خطأ (مثل حساب محذوف)، نحذف بيانات الزواج
         r.delete(f'{m.from_user.id}:marriedWomen:{m.chat.id}{Dev_Neptune}')
         r.delete(f'{m.from_user.id}:MARRYTEXT:{m.chat.id}{Dev_Neptune}')
         r.delete(f'{m.from_user.id}:MARRYMONEY:{m.chat.id}{Dev_Neptune}')
         return m.reply(f'{k} تم حذف بيانات الزواج لأن الحساب غير متاح')
     # إذا كان المستخدم رجل متزوج لكن يكتب "زوجي" (خطأ) فسنعرض زوجته
     elif r.get(f'{m.from_user.id}:marriedMan:{m.chat.id}{Dev_Neptune}'):
       try:
         partner_id = int(r.get(f'{m.from_user.id}:marriedMan:{m.chat.id}{Dev_Neptune}'))
         getUser = c.get_users(partner_id)
         partner_name = getUser.first_name[:10] if getUser.first_name else "زوجتك"

         # إنشاء mention صحيح
         if getUser.username:
           partner_mention = f"@{getUser.username}"
         else:
           partner_mention = f"[{partner_name}](tg://user?id={getUser.id})"

         return m.reply(f'{k} زوجتك هي ↢ ( {partner_mention} ) 👰‍♀️💕')
       except Exception as e:
         # في حالة وجود خطأ (مثل حساب محذوف)، نحذف بيانات الزواج
         r.delete(f'{m.from_user.id}:marriedMan:{m.chat.id}{Dev_Neptune}')
         r.delete(f'{m.from_user.id}:MARRYTEXT:{m.chat.id}{Dev_Neptune}')
         r.delete(f'{m.from_user.id}:MARRYMONEY:{m.chat.id}{Dev_Neptune}')
         return m.reply(f'{k} تم حذف بيانات الزواج لأن الحساب غير متاح')
     else:
       return m.reply(f'{k} انتِ غير متزوجة')

   if text == "سورس" or text == "السورس":
    return m.reply_photo(
        "https://t.me/siznr/54",
        caption=".𝕎𝕝𝕔𝕠𝕞𝕖 𝕥𝕠 𝕊𝕆𝕌ℝℂ𝔼 ℕ𝔼ℙ𝕋𝕌ℕ𝔼:",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("- sᴏᴜʀᴄᴇ ᴊᴀᴄᴋ .", url="https://t.me/Jack_Vib")],
                [InlineKeyboardButton("- التحديثات .", url="https://t.me/Jack_Vib")],
                [InlineKeyboardButton("- شراء بوت .", url="https://t.me/iJUCK")]
            ]
        )
    )

   if text== 'طلاق':
     # التحقق من الرجال المتزوجين
     if r.get(f'{m.from_user.id}:marriedMan:{m.chat.id}{Dev_Neptune}'):
       try:
         getUser = c.get_users(int(r.get(f'{m.from_user.id}:marriedMan:{m.chat.id}{Dev_Neptune}')))
         mahr = r.get(f'{m.from_user.id}:MARRYMONEY:{m.chat.id}{Dev_Neptune}') or 'قرآن'

         # إنشاء mention صحيح
         partner_name = getUser.first_name[:10] if getUser.first_name else "الشريك"
         if getUser.username:
           partner_mention = f"@{getUser.username}"
         else:
           partner_mention = f"[{partner_name}](tg://user?id={getUser.id})"

         r.srem(f'{m.chat.id}:zwag:{Dev_Neptune}', f'{getUser.id}--{m.from_user.id}&&floos={mahr}')
         r.delete(f'{m.from_user.id}:marriedMan:{m.chat.id}{Dev_Neptune}')
         r.delete(f'{getUser.id}:marriedWomen:{m.chat.id}{Dev_Neptune}')
         r.delete(f'{getUser.id}:MARRYTEXT:{m.chat.id}{Dev_Neptune}')
         r.delete(f'{m.from_user.id}:MARRYTEXT:{m.chat.id}{Dev_Neptune}')
         r.delete(f'{m.from_user.id}:MARRYMONEY:{m.chat.id}{Dev_Neptune}')
         r.delete(f'{getUser.id}:MARRYMONEY:{m.chat.id}{Dev_Neptune}')
         return m.reply(f'{k} طلقتك من 「 {partner_mention} 」\n{k} المهر كان ( {mahr} )')
       except:
         # حذف بيانات الزواج إذا كان الحساب محذوف
         r.delete(f'{m.from_user.id}:marriedMan:{m.chat.id}{Dev_Neptune}')
         r.delete(f'{m.from_user.id}:MARRYTEXT:{m.chat.id}{Dev_Neptune}')
         r.delete(f'{m.from_user.id}:MARRYMONEY:{m.chat.id}{Dev_Neptune}')
         return m.reply(f'{k} تم حذف بيانات الزواج لأن الحساب غير متاح')

     # التحقق من النساء المتزوجات
     elif r.get(f'{m.from_user.id}:marriedWomen:{m.chat.id}{Dev_Neptune}'):
       try:
         getUser = c.get_users(int(r.get(f'{m.from_user.id}:marriedWomen:{m.chat.id}{Dev_Neptune}')))
         mahr = r.get(f'{m.from_user.id}:MARRYMONEY:{m.chat.id}{Dev_Neptune}') or 'قرآن'
         r.srem(f'{m.chat.id}:zwag:{Dev_Neptune}', f'{m.from_user.id}--{getUser.id}&&floos={mahr}')
         r.delete(f'{getUser.id}:marriedMan:{m.chat.id}{Dev_Neptune}')
         r.delete(f'{m.from_user.id}:marriedWomen:{m.chat.id}{Dev_Neptune}')
         r.delete(f'{getUser.id}:MARRYTEXT:{m.chat.id}{Dev_Neptune}')
         r.delete(f'{m.from_user.id}:MARRYTEXT:{m.chat.id}{Dev_Neptune}')
         r.delete(f'{m.from_user.id}:MARRYMONEY:{m.chat.id}{Dev_Neptune}')
         r.delete(f'{getUser.id}:MARRYMONEY:{m.chat.id}{Dev_Neptune}')
         return m.reply(f'{k} طلقتك من 「 {getUser.mention} 」\n{k} المهر كان ( {mahr} )')
       except:
         # حذف بيانات الزواج إذا كان الحساب محذوف
         r.delete(f'{m.from_user.id}:marriedWomen:{m.chat.id}{Dev_Neptune}')
         r.delete(f'{m.from_user.id}:MARRYTEXT:{m.chat.id}{Dev_Neptune}')
         r.delete(f'{m.from_user.id}:MARRYMONEY:{m.chat.id}{Dev_Neptune}')
         return m.reply(f'{k} تم حذف بيانات الزواج لأن الحساب غير متاح')

     # إذا لم يكن متزوج
     else:
       return m.reply(f'{k} انت غير متزوج')


   if text== 'طلكني' and r.get(f'{m.from_user.id}:marriedWomen:{m.chat.id}{Dev_Neptune}'):
     try:
       getUser = c.get_users(int(r.get(f'{m.from_user.id}:marriedWomen:{m.chat.id}{Dev_Neptune}')))
       mahr = r.get(f'{m.from_user.id}:MARRYMONEY:{m.chat.id}{Dev_Neptune}') or 'قرآن'
       r.srem(f'{m.chat.id}:zwag:{Dev_Neptune}', f'{m.from_user.id}--{getUser.id}&&floos={mahr}')
       r.delete(f'{getUser.id}:marriedMan:{m.chat.id}{Dev_Neptune}')
       r.delete(f'{m.from_user.id}:marriedWomen:{m.chat.id}{Dev_Neptune}')
       r.delete(f'{getUser.id}:MARRYTEXT:{m.chat.id}{Dev_Neptune}')
       r.delete(f'{m.from_user.id}:MARRYTEXT:{m.chat.id}{Dev_Neptune}')
       r.delete(f'{m.from_user.id}:MARRYMONEY:{m.chat.id}{Dev_Neptune}')
       r.delete(f'{getUser.id}:MARRYMONEY:{m.chat.id}{Dev_Neptune}')
       # إنشاء mention صحيح
       partner_name = getUser.first_name[:10] if getUser.first_name else "الشريك"
       if getUser.username:
         partner_mention = f"@{getUser.username}"
       else:
         partner_mention = f"[{partner_name}](tg://user?id={getUser.id})"

       return m.reply(f'{k} طلقك 「 {partner_mention} 」\n{k} المهر كان ( {mahr} )')
     except:
       # حذف بيانات الزواج إذا كان الحساب محذوف
       r.delete(f'{m.from_user.id}:marriedWomen:{m.chat.id}{Dev_Neptune}')
       r.delete(f'{m.from_user.id}:MARRYTEXT:{m.chat.id}{Dev_Neptune}')
       r.delete(f'{m.from_user.id}:MARRYMONEY:{m.chat.id}{Dev_Neptune}')
       return m.reply(f'{k} تم حذف بيانات الزواج لأن الحساب غير متاح')

   if text == 'كت' or text == 'تويت' or text == 'كت تويت':
      return m.reply(random.choice(cut))

   if text == 'جمل':
     gmla = random.choice(gomal)
     r.set(f'{m.chat.id}:game:{Dev_Neptune}', gmla.replace(" '",""), ex=600)
     m.reply(f'الجملة ↢ ( {gmla} )\n{k} اكتبها بدون فواصل')

   if r.get(f'{m.chat.id}:gameEmoji:{Dev_Neptune}'):
     if text == r.get(f'{m.chat.id}:gameEmoji:{Dev_Neptune}'):
        ra = random.randint(1,5)
        t = r.ttl(f'{m.chat.id}:gameEmoji:{Dev_Neptune}')
        timeo = f"{20 - int(t)}.{random.randint(1,9)}"
        r.delete(f'{m.chat.id}:gameEmoji:{Dev_Neptune}')
        if r.get(f'{m.from_user.id}:Floos'):
           get = int(r.get(f'{m.from_user.id}:Floos'))
           r.set(f'{m.from_user.id}:Floos',get+ra)
           floos = int(r.get(f'{m.from_user.id}:Floos'))
        else:
           floos = ra
           r.set(f'{m.from_user.id}:Floos',ra)
        return m.reply(f'''
صح عليك ⁪⁬⁪⁬⁮⁪⁬⁪⁬⁮✔
⏰الوقت: {timeo} ثانية
💸فلوسك: {floos} دينار عراقي
☆
''')

   if r.get(f'{m.chat.id}:game5tm:{m.from_user.id}{Dev_Neptune}'):
    try:
     if int(text) == r.get(f'{m.chat.id}:game5tm:{m.from_user.id}{Dev_Neptune}'):
        ra = random.randint(1,5)
        t = r.ttl(f'{m.chat.id}:game5tm:{m.from_user.id}{Dev_Neptune}')
        timeo = f"{600 - int(t)}.{random.randint(1,9)}"
        r.delete(f'{m.chat.id}:game5tm:{m.from_user.id}{Dev_Neptune}')
        if r.get(f'{m.from_user.id}:Floos'):
           get = int(r.get(f'{m.from_user.id}:Floos'))
           r.set(f'{m.from_user.id}:Floos',get+ra)
           floos = int(r.get(f'{m.from_user.id}:Floos'))
        else:
           floos = ra
           r.set(f'{m.from_user.id}:Floos',ra)
        return m.reply(f'''
صح عليك ⁪⁬⁪⁬⁮⁪⁬⁪⁬⁮✔
⏰الوقت: {timeo} ثانية
💸فلوسك: {floos} دينار عراقي
☆
''')
     else:
        r.delete(f'{m.chat.id}:game5tm:{m.from_user.id}{Dev_Neptune}')
        return m.reply(f'{k} اجابتك خطأ')
    except:
     pass

   if r.get(f'{m.chat.id}:game:{Dev_Neptune}'):
     if text == r.get(f'{m.chat.id}:game:{Dev_Neptune}'):
        ra = random.randint(1,5)
        t = r.ttl(f'{m.chat.id}:game:{Dev_Neptune}')
        timeo = f"{600 - int(t)}.{random.randint(1,9)}"
        r.delete(f'{m.chat.id}:game:{Dev_Neptune}')
        if r.get(f'{m.from_user.id}:Floos'):
           get = int(r.get(f'{m.from_user.id}:Floos'))
           r.set(f'{m.from_user.id}:Floos',get+ra)
           floos = int(r.get(f'{m.from_user.id}:Floos'))
        else:
           floos = ra
           r.set(f'{m.from_user.id}:Floos',ra)
        m.reply(f'''
صح عليك ⁪⁬⁪⁬⁮⁪⁬⁪⁬⁮✔
⏰الوقت: {timeo} ثانية
💸فلوسك: {floos} دينار عراقي
☆
''')
        return True


   if text == 'ترتيب':
     name = random.choice(trteep)
     name1 = name
     name = re.sub('سحور', 'س ر و ح', name)
     name = re.sub('سياره', 'ه ر س ي ا', name)
     name = re.sub('استقبال', 'ل ب ا ت ق س ا', name)
     name = re.sub('قنافه', 'ه ق ا ن ف', name)
     name = re.sub('ايفون', 'و ن ف ا', name)
     name = re.sub('بطاطس', 'ب ط ا ط س', name)
     name = re.sub('مطبخ', 'خ ب ط م', name)
     name = re.sub('كرستيانو', 'س ت ا ن و ك ر ي', name)
     name = re.sub('دجاجه', 'ج ج ا د ه', name)
     name = re.sub('مدرسه', 'ه م د ر س', name)
     name = re.sub('الوان', 'ن ا و ا ل', name)
     name = re.sub('غرفه', 'غ ه ر ف', name)
     name = re.sub('ثلاجه', 'ج ه ت ل ا', name)
     name = re.sub('قهوه', 'ه ق ه و', name)
     name = re.sub('سفينه', 'ه ن ف ي س', name)
     name = re.sub('مصر', 'ر م ص', name)
     name = re.sub('محطه', 'ه ط م ح', name)
     name = re.sub('طياره', 'ر ا ط ي ه', name)
     name = re.sub('رادار', 'ر ا ر ا د', name)
     name = re.sub('منزل', 'ن ز م ل', name)
     name = re.sub('مستشفى', 'ى ش س ف ت م', name)
     name = re.sub('كهرباء', 'ر ب ك ه ا ء', name)
     name = re.sub('تفاحه', 'ح ه ا ت ف', name)
     name = re.sub('اخطبوط', 'ط ب و ا خ ط', name)
     name = re.sub('سنترال', 'ن ر ت ل ا س', name)
     name = re.sub('فرنسا', 'ن ف ر س ا', name)
     name = re.sub('برتقاله', 'ر ت ق ب ا ه ل', name)
     name = re.sub('تفاح', 'ح ف ا ت', name)
     name = re.sub('مطرقه', 'ه ط م ر ق', name)
     name = re.sub('هريسه', 'س ه ر ي ه', name)
     name = re.sub('لبانه', 'ب ن ل ه ا', name)
     name = re.sub('شباك', 'ب ش ا ك', name)
     name = re.sub('باص', 'ص ا ب', name)
     name = re.sub('سمكه', 'ك س م ه', name)
     name = re.sub('ذباب', 'ب ا ب ذ', name)
     name = re.sub('تلفاز', 'ت ف ل ز ا', name)
     name = re.sub('حاسوب', 'س ا ح و ب', name)
     name = re.sub('انترنت', 'ا ت ن ر ن ت', name)
     name = re.sub('ساحه', 'ح ا ه س', name)
     name = re.sub('جسر', 'ر ج س', name)
     r.set(f'{m.chat.id}:game:{Dev_Neptune}', name1,ex=600)
     m.reply(f'رتب ↢ {name}')
     return True

   if text == 'ايموجي':
      if r.get(f'{m.chat.id}:gameEmoji:{Dev_Neptune}'):
        return m.reply(f'{k} معليش في لعبة ايموجي شغالة هسة حاول بعد 20 ثانية\n\n{k} في حال ماتريد تكملها ارسل سكب')
      ran = random.choice(emojis_pics)
      emoji = ran['emoji']
      photo = ran['photo']
      a = m.reply_photo(photo,caption='اسرع واحد يرسل الايموجي')
      r.delete(f'{m.chat.id}:game:{Dev_Neptune}')
      time.sleep(3)
      r.set(f'{m.chat.id}:gameEmoji:{Dev_Neptune}', emoji,ex=20)
      a.edit_media(media=InputMediaPhoto (media='https://telegra.ph/file/b53b14951a50d7f75c39e.jpg', caption='ارسل الايموجي هسة'))
      return True

   if text == 'سكب':
      if r.get(f'{m.chat.id}:gameEmoji:{Dev_Neptune}'):
         r.delete(f'{m.chat.id}:gameEmoji:{Dev_Neptune}')
         m.reply(f'{k} سكبت لعبه الايموجي')
         return True

   if text == 'انقليزي':
     name = random.choice(english)
     name1 = name
     name = re.sub("ذئب", "wolf", name)
     name = re.sub("معلومات", "information", name)
     name = re.sub("قنوات", "channels", name)
     name = re.sub("مجموعات", "groups", name)
     name = re.sub("كتاب", "book", name)
     name = re.sub("تفاحه", "apple", name)
     name = re.sub("مصر", "egypt", name)
     name = re.sub("فلوس", "money", name)
     name = re.sub("اعلم", "i know", name)
     name = re.sub("تمساح", "crocodile", name)
     name = re.sub("مختلف", "different", name)
     name = re.sub("ذكي", "intelligent", name)
     name = re.sub("كلب", "dog", name)
     name = re.sub("صقر", "falcon", name)
     name = re.sub("مشكله", "error", name)
     name = re.sub("كمبيوتر", "computer", name)
     name = re.sub("اصدقاء", "friends", name)
     name = re.sub("منضده", "table", name)
     r.set(f'{m.chat.id}:game:{Dev_Neptune}', name1,ex=600)
     m.reply(f'اكتب معنى ↢ ( {name} )')
     return True

   if text == 'معاني':
     name = random.choice(m3any)
     name1 = name
     name = re.sub("قرد", "🐒", name)
     name = re.sub("دجاجه", "🐔", name)
     name = re.sub("بطريق", "🐧", name)
     name = re.sub("ضفدع", "🐸", name)
     name = re.sub("بومه", "🦉", name)
     name = re.sub("نحله", "🐝", name)
     name = re.sub("ديك", "🐓", name)
     name = re.sub("جمل", "🐫", name)
     name = re.sub("بقره", "🐄", name)
     name = re.sub("دولفين", "🐳", name)
     name = re.sub("تمساح", "🐊", name)
     name = re.sub("قرش", "🦈", name)
     name = re.sub("نمر", "🐅", name)
     name = re.sub("اخطبوط", "🐙", name)
     name = re.sub("سمكه", "🐟", name)
     name = re.sub("خفاش", "🦇", name)
     name = re.sub("اسد", "🦁", name)
     name = re.sub("فأر", "🐭", name)
     name = re.sub("ذئب", "🐺", name)
     name = re.sub("فراشه", "🦋", name)
     name = re.sub("عقرب", "🦂", name)
     name = re.sub("زرافه", "🦒", name)
     name = re.sub("قنفذ", "🦔", name)
     name = re.sub("تفاحه", "🍎", name)
     name = re.sub("باذنجان", "🍆", name)
     name = re.sub("قوس قزح", "🌈", name)
     name = re.sub("بزازه", "🍼", name)
     name = re.sub("بطيخ", "🍉", name)
     name = re.sub("وزه", "🦆", name)
     name = re.sub("كتكوت", "🐣", name)
     r.set(f'{m.chat.id}:game:{Dev_Neptune}', name1,ex=600)
     m.reply(f'شنو معنى الايموجي ↢ ( {name} )')
     return True

   if text == 'احسب':
     name = random.choice(Maths)
     name1 = name
     name = re.sub("200", "250 - 50 = ?", name)
     name = re.sub("605", "655 - 50 = ?", name)
     name = re.sub("210", "247 - 37 = ?", name)
     name = re.sub("128", "168 - 40 = ?", name)
     name = re.sub("126", "202 - 76 = ?", name)
     name = re.sub("263", "31297 ÷ 119 = ?", name)
     name = re.sub("150", "246 - 96 = ?", name)
     name = re.sub("2000", "200 × 10 = ?", name)
     name = re.sub("40", "95 - 55 = ?", name)
     name = re.sub("242", "276 - 34 = ?", name)
     name = re.sub("14", "29 - 15 = ?", name)
     name = re.sub("13", "16 - 3 = ?", name)
     name = re.sub("1000", "956 + 44 = ?", name)
     name = re.sub("810", "767 + 43 = ?", name)
     name = re.sub("110", "77 + 33 = ?", name)
     name = re.sub("830", "745 + 85 = ?", name)
     name = re.sub("111", "66 + 45 = ?", name)
     name = re.sub("92", "61 + 31 = ?", name)
     name = re.sub("1110", "988 + 122 = ?", name)
     name = re.sub("6800", "85 × 80 = ?", name)
     name = re.sub("1554", "777 × 2 = ?", name)
     name = re.sub("920", "92 × 10 = ?", name)
     name = re.sub("1740", "87 × 20 = ?", name)
     name = re.sub("1140", "76 × 15 = ?", name)
     name = re.sub("1056", "88 × 12 = ?", name)
     name = re.sub("331", "243 + 88 = ?", name)
     name = re.sub("162", "250 - 88 = ?", name)
     name = re.sub("245", "290 - 45 = ?", name)
     name = re.sub("900", "975 - 75 = ?", name)
     name = re.sub("791", "878 - 87= ?", name)
     name = re.sub("0", "99 - 99 = ?", name)
     name = re.sub("57", "77 - 20 = ?", name)
     name = re.sub("220", "250 - 30 = ?", name)
     r.set(f'{m.chat.id}:game:{Dev_Neptune}', name1,ex=600)
     m.reply(f'{name}')
     return True

   if text == 'عربي':
     name = random.choice(Arab)
     name1 = name
     name = re.sub("اناث", "انثى", name)
     name = re.sub("ثيران", "ثور", name)
     name = re.sub("دروس", "درس", name)
     name = re.sub("فحص", "فحوص", name)
     name = re.sub("رجال", "رجل", name)
     name = re.sub("كتب", "كتاب", name)
     name = re.sub("ضغوط", "ضغط", name)
     name = re.sub("صف", "صفوف", name)
     name = re.sub("عصفور", "عصافير", name)
     name = re.sub("لصوص", "لص", name)
     name = re.sub("تماسيح", "تمساح", name)
     name = re.sub("ملك", "ملوك", name)
     name = re.sub("فصل", "فصول", name)
     name = re.sub("كلاب", "كلب", name)
     name = re.sub("صقور", "صقر", name)
     name = re.sub("عقد", "عقود", name)
     name = re.sub("بحور", "بحر", name)
     name = re.sub("هاتف", "هواتف", name)
     name = re.sub("حدائق", "حديقه", name)
     name = re.sub("مسرح", "مسارح", name)
     name = re.sub("جرائم", "جريمة", name)
     name = re.sub("مدارس", "مدرسة", name)
     name = re.sub("منزل", "منازل", name)
     name = re.sub("كرسي", "كراسي", name)
     name = re.sub("مناطق", "منطقة", name)
     name = re.sub("بيوت", "بيت", name)
     name = re.sub("بنك", "بنوك", name)
     name = re.sub("علم", "علوم", name)
     name = re.sub("وظائف", "وظيفة", name)
     name = re.sub("طلاب", "طالب", name)
     name = re.sub("مراحل", "مرحلة", name)
     name = re.sub("فنانين", "فنان", name)
     name = re.sub("صواريخ", "صاروخ", name)
     r.set(f'{m.chat.id}:game:{Dev_Neptune}', name1,ex=600)
     m.reply(f'اكتب جمع او مفرد ↢ ( {name} )')
     return True

   if text == 'كلمات':
     name = random.choice(words)
     '''
     name1 = name
     name = re.sub("ذئب", "ذئب", name)
     name = re.sub("معلومات", "معلومات", name)
     name = re.sub("قنوات", "قنوات", name)
     name = re.sub("مجموعات", "مجموعات", name)
     name = re.sub("كتاب", "كتاب", name)
     name = re.sub("تفاحه", "تفاحه", name)
     name = re.sub("مصر", "مصر", name)
     name = re.sub("فلوس", "فلوس", name)
     name = re.sub("اعلم", "اعلم", name)
     name = re.sub("تمساح", "تمساح", name)
     name = re.sub("مختلف", "مختلف", name)
     name = re.sub("ذكي", "ذكي", name)
     name = re.sub("كلب", "كلب", name)
     name = re.sub("صقر", "صقر", name)
     name = re.sub("مشكله", "مشكله", name)
     name = re.sub("كمبيوتر", "كمبيوتر", name)
     name = re.sub("اصدقاء", "اصدقاء", name)
     name = re.sub("منضده", "منضده", name)
     name = re.sub("سائق", "سائق", name)
     name = re.sub("جبل", "جبل", name)
     name = re.sub("مفتاح", "مفتاح", name)
     name = re.sub("يساوي", "يساوي", name)
     name = re.sub("انتبه", "انتبه", name)
     name = re.sub("موقد", "موقد", name)
     name = re.sub("مكتئب", "مكتئب", name)
     name = re.sub("انسان", "انسان", name)
     name = re.sub("ضفدع", "ضفدع", name)
     name = re.sub("عشق", "عشق", name)
     name = re.sub("منزل", "منزل", name)
     name = re.sub("طلاب", "طلاب", name)
     name = re.sub("فنان", "فنان", name)
     name = re.sub("صاروخ", "صاروخ", name)
     '''
     r.set(f'{m.chat.id}:game:{Dev_Neptune}', name,ex=600)
     m.reply(f'الكلمة ↢ ( {name} )')
     return True

   if text == 'تفكيك':
     tfkeek = random.choice(trteep)
     name = ' '.join(a for a in tfkeek)
     r.set(f'{m.chat.id}:game:{Dev_Neptune}', name,ex=600)
     m.reply(f'فكك ↢ ( {tfkeek} )')
     return True


   if text == 'عواصم':
     country=random.choice(countries)
     name = country['name']
     capital=country['capital']
     r.set(f'{m.chat.id}:game:{Dev_Neptune}', capital,ex=600)
     m.reply(f'{k} شنو عاصمة {name} ؟')
     return True

   if text == 'اكمل':
     name = random.choice(mthal)
     name1 = name
     name = re.sub("اخوات", "لو قلبك مات متجيش على اتنين ... ", name)
     name = re.sub("زيهم", "اى ياعمهم اشتكيلك منهم تعمل ... ", name)
     name = re.sub("شمعتك", "دارى على ... تقيد", name)
     name = re.sub("داره", "من خرج من ... قل مقداره", name)
     name = re.sub("الوالدين", "رضا ... احسن من ابوك وامك", name)
     name = re.sub("الرءوس", "اذا تطاول الايدي تساوت ... ", name)
     name = re.sub("مرايه", "فى الشنو ... وفى القفه سلايه", name)
     name = re.sub("حدو", "الشئ اللى يزيد عن ...  ينقلب لضدو", name)
     name = re.sub("رجالها", "مايجبها الا  ... ", name)
     name = re.sub("عدوك", "امشى عدل يحتار ... بيك", name)
     name = re.sub("الزبيب", "ضرب الحبيب زى اكل  ... ", name)
     name = re.sub("الغراب", "ياما جاب ...  لامه", name)
     name = re.sub("ماتو", "اللى اغتشو ... ", name)
     name = re.sub("اتمكن", "اتمسكن لحد ما ... ", name)
     name = re.sub("زجاج", "اللى بيتو من ... مايحدفش الناس بالطوب", name)
     name = re.sub("فار", "لو غاب القط العب يا ... ", name)
     name = re.sub("شهر", "امشي ... ولا تعدى نهر", name)
     name = re.sub("القتيل", "يقتل ... ويمشى فى جنازته", name)
     name = re.sub("الغطاس", "المايه تكدب ... ", name)
     name = re.sub("يكحلها", "جه ... عماها", name)
     name = re.sub("امه", "القرد فى عين ... غزال", name)
     r.set(f'{m.chat.id}:game:{Dev_Neptune}', name1 ,ex=600)
     m.reply(f'اكمل ↢ ( {name} ؟ )')
     return True

   if text == 'احكام':
     if r.get(f'{m.chat.id}:AHKAMGAME:{Dev_Neptune}'):
       return m.reply(f"{k} معليش في لعبة احكام شغالة هسة حاول بعد دقيقة")
     m.reply(f'''
{k} بدينا لعبة احكام واضفت اسمك
{k} اللي يبي يلعب يرسل كلمة ( انا )

{k} اللي عليك انت صاحب اللعبة ترسل ( تم ) اذا اكتمل العدد
☆
''')
     r.delete(f'{m.chat.id}:ListAhkam:{Dev_Neptune}')
     r.set(f'{m.chat.id}:AHKAMGAME:{Dev_Neptune}',m.from_user.id,ex=120)
     r.sadd(f'{m.chat.id}:ListAhkam:{Dev_Neptune}',m.from_user.id)
     return True

   if text == 'انا' and r.get(f'{m.chat.id}:AHKAMGAME:{Dev_Neptune}'):
     if r.sismember(f'{m.chat.id}:ListAhkam:{Dev_Neptune}',m.from_user.id):
       return m.reply(f"{k} اسمك موجود بالقائمة")
     else:
       m.reply(f"{k} ضفت اسمك للقائمة")
       r.sadd(f'{m.chat.id}:ListAhkam:{Dev_Neptune}',m.from_user.id)
       return True

   if text == 'تم' and r.get(f'{m.chat.id}:AHKAMGAME:{Dev_Neptune}') and m.from_user.id == int(r.get(f'{m.chat.id}:AHKAMGAME:{Dev_Neptune}')):
     if len(r.smembers(f'{m.chat.id}:ListAhkam:{Dev_Neptune}')) == 1:
       return m.reply(f"{k} ماكو لاعبين")
     else:
       ids = [elem for elem in r.smembers(f'{m.chat.id}:ListAhkam:{Dev_Neptune}')]
       id = random.choice(ids)
       try:
         getUser = c.get_users(int(id))
         m.reply(f"{k} تم اختيار ( ⁪⁬⁪⁬{getUser.mention} ) للحكم عليه")
       except:
         m.reply(f"{k} تم اختيار مستخدم محذوف للحكم عليه")
       r.delete(f'{m.chat.id}:ListAhkam:{Dev_Neptune}')
       r.delete(f'{m.chat.id}:AHKAMGAME:{Dev_Neptune}')
       return True


   if text == 'روليت':
     if r.get(f'{m.chat.id}:ROLETGAME:{Dev_Neptune}'):
       return m.reply(f"{k} معليش في لعبة روليت شغالة هسة حاول بعد دقيقة")
     m.reply(f'''
{k} بدينا لعبة الروليت واضفت اسمك
{k} اللي يبي يلعب يرسل كلمة ( انا )

{k} اللي عليك انت صاحب اللعبة ترسل ( تم ) اذا اكتمل العدد
☆
''')
     r.delete(f'{m.chat.id}:ListRolet:{Dev_Neptune}')
     r.set(f'{m.chat.id}:ROLETGAME:{Dev_Neptune}',m.from_user.id,ex=120)
     r.sadd(f'{m.chat.id}:ListRolet:{Dev_Neptune}',m.from_user.id)
     return True

   if text == 'انا' and r.get(f'{m.chat.id}:ROLETGAME:{Dev_Neptune}'):
     if r.sismember(f'{m.chat.id}:ListRolet:{Dev_Neptune}',m.from_user.id):
       return m.reply(f"{k} اسمك موجود بالقائمة")
     else:
       m.reply(f"{k} ضفت اسمك للقائمة")
       r.sadd(f'{m.chat.id}:ListRolet:{Dev_Neptune}',m.from_user.id)
       return True

   if text == 'تم' and r.get(f'{m.chat.id}:ROLETGAME:{Dev_Neptune}') and m.from_user.id == int(r.get(f'{m.chat.id}:ROLETGAME:{Dev_Neptune}')):
     if len(r.smembers(f'{m.chat.id}:ListRolet:{Dev_Neptune}')) == 1:
       return m.reply(f"{k} ماكو لاعبين")
     else:
       ids = [elem for elem in r.smembers(f'{m.chat.id}:ListRolet:{Dev_Neptune}')]
       id = random.choice(ids)
       try:
         getUser = c.get_users(int(id))
         m.reply(f"{k} مبروك اخترت اللاعب ( {getUser.mention} ) واخذ 3 مجوهرات")
       except:
         m.reply(f"{k} تم اختيار مستخدم محذوف")
       if not r.get(f'{getUser.id}:Floos'):
         floos = 0
       else:
         floos = int(r.get(f'{getUser.id}:Floos'))
       r.set(f"{getUser.id}:Floos",floos+10)
       r.delete(f'{m.chat.id}:ListRolet:{Dev_Neptune}')
       r.delete(f'{m.chat.id}:ROLETGAME:{Dev_Neptune}')
       return True


   if text == 'خواتم':
     name = random.randint(1,6)
     r.set(f'{m.chat.id}:game5tm:{m.from_user.id}{Dev_Neptune}', name ,ex=600)
     r.delete(f'{m.chat.id}:game:{Dev_Neptune}')
     return m.reply('''
１    ２      ３     ４    ５     ６
  ↓     ↓      ↓     ↓     ↓     ↓
  ✋🏼 ‹› ✋🏼 ‹› ✋🏼 ‹› ✋🏼 ‹› ✋🏼 ‹› ✋🏼


⚘ اختار اليد اللي تتوقع فيها الخاتم
     ''')

   if text == 'اعلام':
     country=random.choice(countries_)
     name = country['name']
     flag=country['flag']
     r.set(f'{m.chat.id}:game:{Dev_Neptune}', name,ex=600)
     m.reply_photo(flag, caption='شنو اسم الدولة ؟')
     return True

   if text == 'دين':
     dee = random.choice(deen)
     question = dee['question']
     answer = dee['answer']
     r.set(f'{m.chat.id}:game:{Dev_Neptune}', answer ,ex=600)
     m.reply(question)
     return True

   if text == 'سيارات':
     car = random.choice(cars)
     brand = car["brand"]
     r.set(f'{m.chat.id}:game:{Dev_Neptune}', brand ,ex=600)
     m.reply_photo(car['photo'], caption='شنو اسم السيارة ؟')
     return True

   if text == 'ارقام':
     num = ''
     for a in range(random.randint(5,15)):
       num += str(random.randint(1,9))
     r.set(f'{m.chat.id}:game:{Dev_Neptune}', num ,ex=600)
     m.reply(f'الرقم ↢ ( {num} )', protect_content=True)
     return True

   if text == 'انمي':
     anim = random.choice(anime)
     r.set(f'{m.chat.id}:game:{Dev_Neptune}', anim['anime'] ,ex=600)
     m.reply_photo(anim['photo'], caption='شنو اسم شخصية الانمي ؟')
     return True

   if text == 'صور':
     ph = random.choice(pics)
     r.set(f'{m.chat.id}:game:{Dev_Neptune}', ph['answer'] ,ex=600)
     if not ph['caption']:
       caption = 'شنو الي فالصورة؟'
     else:
       caption = ph['caption']
     m.reply_photo(ph['photo'], caption=caption)
     return True

   if text == 'كرة قدم' or text == 'كره قدم':
     ph = random.choice(football)
     r.set(f'{m.chat.id}:game:{Dev_Neptune}', ph['answer'] ,ex=600)
     if not ph['caption']:
       caption = 'شنو اسم الاعب ؟'
     else:
       caption = ph['caption']
     m.reply_photo(ph['photo'], caption=caption)
     return True

   if text == 'تشفير':
     ph = random.choice(tashfeer)
     r.set(f'{m.chat.id}:game:{Dev_Neptune}', ph['answer'] ,ex=600)
     if not ph['caption']:
       caption = 'فك التشفير ؟'
     else:
       caption = ph['caption']
     m.reply_photo(ph['photo'], caption=caption)
     return True

   if text == 'تركيب':
     name = random.choice(tarkeeb)
     name1 = name
     name = re.sub("اناث", "ا ن ا ث", name)
     name = re.sub("ثيران", "ث ي ر ا ن", name)
     name = re.sub("دروس", "د ر و س", name)
     name = re.sub("فحص", "ف ح ص", name)
     name = re.sub("رجال", "ر ج ا ل", name)
     name = re.sub("انستا", "ا ن س ت ا", name)
     name = re.sub("ضغوط", "ض غ و ط", name)
     name = re.sub("صف", "ص ف", name)
     name = re.sub("رجب", "ر ج ب", name)
     name = re.sub("اسد", "ا س د", name)
     name = re.sub("وقع", "و ق ع", name)
     name = re.sub("ملك", "م ل ك", name)
     name = re.sub("فصل", "ف ص ل", name)
     name = re.sub("كلاب", "ك ل ا ب", name)
     name = re.sub("صقور", "ص ق و ر", name)
     name = re.sub("عقد", "ع ق د", name)
     name = re.sub("بحور", "ب ح و ر", name)
     name = re.sub("هاتف", "ه ا ت ف", name)
     name = re.sub("حدائق", "ح د ا ئ ق", name)
     name = re.sub("مسرح", "م س ر ح", name)
     name = re.sub("جرائم", "ج ر ا ئ م", name)
     name = re.sub("مدارس", "م د ا ر س", name)
     name = re.sub("منزل", "م ن ز ل", name)
     name = re.sub("كرسي", "ك ر س ي", name)
     name = re.sub("مناطق", "م ن ا ط ق", name)
     name = re.sub("بيوت", "ب ي و ت", name)
     name = re.sub("بنك", "ب ن ك", name)
     name = re.sub("علم", "ع ل م", name)
     name = re.sub("وظائف", "و ظ ا ئ ف", name)
     name = re.sub("طلاب", "ط ل ا ب", name)
     name = re.sub("مراحل", "م ر ا ح ل", name)
     name = re.sub("فنانين", "ف ن ا ن ي ن", name)
     name = re.sub("صواريخ", "ص و ا ر ي خ", name)
     r.set(f'{m.chat.id}:game:{Dev_Neptune}', name1,ex=600)
     m.reply(f'ركب ↢ ( {name} )')

   if text == "سكب ديمون":
    if m.from_user.id in users_demon:
        del users_demon[m.from_user.id]
        return m.reply("⇜ تمام الغيت اللعبة")
    else:
        return m.reply("⇜ ماكو لعبة ديمون شغالة")

   if text == 'حجره' or text == 'حجرة':
     return m.reply('- اختار حجره / ورقة / مقص',reply_markup=InlineKeyboardMarkup (
     [
     [
       InlineKeyboardButton ('🪨', callback_data=f'RPS:rock++{m.from_user.id}'),
       InlineKeyboardButton ('📃', callback_data=f'RPS:paper++{m.from_user.id}'),
       InlineKeyboardButton ('✂️', callback_data=f'RPS:scissors++{m.from_user.id}'),
     ]
     ]
     ))

   if text == 'نرد':
     dice = c.send_dice(m.chat.id,"🎲",reply_to_message_id=m.id,
     reply_markup=InlineKeyboardMarkup (
       [[
         InlineKeyboardButton ("ꜱᴏᴜʀᴄᴇ ɴᴇᴘᴛᴜɴᴇ",url=f"t.me/{channel}")
       ]]
     ))
     if dice.dice.value == 6:
        ra = 10
        if r.get(f'{m.from_user.id}:Floos'):
           get = int(r.get(f'{m.from_user.id}:Floos'))
           r.set(f'{m.from_user.id}:Floos',get+ra)
           floos = int(r.get(f'{m.from_user.id}:Floos'))
        else:
           floos = ra
           r.set(f'{m.from_user.id}:Floos',ra)
        return m.reply(f'''
صح عليك فزت **[بالنرد]({dice.link})** ⁪⁬⁪⁬⁮⁪⁬⁪⁬⁮✔
💸فلوسك: `{floos}` دينار عراقي
☆
''', disable_web_page_preview=True)
     else:
        return m.reply(f"{k} للأسف خسرت بالنرد")


   if text == 'ديمون':
     if m.from_user.id in users_demon:
        return m.reply("⇜ في لعبة ديمون شغالة استخدم امر <code>سكب ديمون</code>")
     else:
        return m.reply(f'''بوو 👻
انا ديمون 🧛🏻‍♀️ اقدر اعرف مين الشخصية الي فبالك !

- فكر بشخص واضغط بدء وجاوب على اسئلتي''',
     reply_markup=InlineKeyboardMarkup (
       [
       [
        InlineKeyboardButton ('بدء 🧛🏻‍♀️',callback_data=f'start_aki:{m.from_user.id}')
       ]
       ]
     ))

   if text == 'اكس او' or text == 'XO' or text == 'xo':
     # إنشاء معرف فريد للعبة
     game_id = f"{m.chat.id}_{m.from_user.id}_{int(time.time())}"

     # إنشاء لعبة جديدة
     player1 = {
         "id": m.from_user.id,
         "name": m.from_user.first_name
     }
     game = create_new_game(r, game_id, player1)

     # إرسال رسالة التحدي مفتوحة لأي شخص
     challenge_text = f"🎮 **{m.from_user.first_name}** بدأ لعبة إكس أو!\n\n⭕ أي شخص يكدر يلعب ويا\n🎯 اضغط \"العب معي\" للانضمام"

     return m.reply(
         challenge_text,
         reply_markup=InlineKeyboardMarkup([
             [InlineKeyboardButton("🎮 العب معي", callback_data=f"XO:accept:{game_id}")]
         ])
     )

@Client.on_callback_query(filters.regex('marriage'))
def marriage_callback_handler(c, m):
    """معالج أزرار الزواج"""
    k = r.get(f'{Dev_Neptune}:botkey') or '⇜'

    try:
        if m.data.startswith('accept_marriage:'):
            # استخراج البيانات من callback_data
            data_parts = m.data.split(':')
            groom_id = int(data_parts[1])
            bride_id = int(data_parts[2])
            mahr = data_parts[3]  # قرآن بدلاً من المبلغ
            chat_id = int(data_parts[4])

            # التحقق من أن الشخص الذي ضغط الزر هو العروس
            if m.from_user.id != bride_id:
                return m.answer('هذا الزر خاص بالعروس فقط!', show_alert=True)

            # التحقق من وجود طلب الزواج
            if not r.get(f'marriage_request:{chat_id}:{groom_id}:{bride_id}:{Dev_Neptune}'):
                return m.answer('انتهت صلاحية طلب الزواج!', show_alert=True)

            # تسجيل الزواج
            r.set(f'{groom_id}:marriedMan:{chat_id}{Dev_Neptune}', bride_id)
            r.set(f'{bride_id}:marriedWomen:{chat_id}{Dev_Neptune}', groom_id)

            # إنشاء وثيقة الزواج
            try:
                groom_user = c.get_users(groom_id)
                bride_user = c.get_users(bride_id)
            except:
                return m.answer('خطأ في الحصول على بيانات المستخدمين', show_alert=True)

            to_marry = f'''
💒 وثيقة زواج

{k} 👰 العروس ↢ ( {bride_user.mention(bride_user.first_name[:10])} )
{k} 🤵 العريس ↢ ( {groom_user.mention(groom_user.first_name[:10])} )

{k} 💸 المهر ↢ ( {mahr} )
༄'''

            r.set(f'{groom_id}:MARRYTEXT:{chat_id}{Dev_Neptune}', to_marry)
            r.set(f'{bride_id}:MARRYTEXT:{chat_id}{Dev_Neptune}', to_marry)
            r.set(f'{groom_id}:MARRYMONEY:{chat_id}{Dev_Neptune}', mahr)
            r.set(f'{bride_id}:MARRYMONEY:{chat_id}{Dev_Neptune}', mahr)
            r.sadd(f'{chat_id}:zwag:{Dev_Neptune}', f'{bride_id}--{groom_id}&&floos={mahr}')

            # حذف طلب الزواج
            r.delete(f'marriage_request:{chat_id}:{groom_id}:{bride_id}:{Dev_Neptune}')

            # تحديث الرسالة
            return m.edit_message_text(f'''
{k} باركووو للعرسان 🎉

{k} 👰 العروس ↢ ( {bride_user.mention} )
{k} 🤵 العريس ↢ ( {groom_user.mention} )

{k} 💸 المهر ↢ ( {mahr} )
☆
''')

        elif m.data.startswith('reject_marriage:'):
            # استخراج البيانات من callback_data
            data_parts = m.data.split(':')
            groom_id = int(data_parts[1])
            bride_id = int(data_parts[2])
            mahr = data_parts[3]  # قرآن
            chat_id = int(data_parts[4])

            # التحقق من أن الشخص الذي ضغط الزر هو العروس
            if m.from_user.id != bride_id:
                return m.answer('هذا الزر خاص بالعروس فقط!', show_alert=True)

            # التحقق من وجود طلب الزواج
            if not r.get(f'marriage_request:{chat_id}:{groom_id}:{bride_id}:{Dev_Neptune}'):
                return m.answer('انتهت صلاحية طلب الزواج!', show_alert=True)

            # حذف طلب الزواج
            r.delete(f'marriage_request:{chat_id}:{groom_id}:{bride_id}:{Dev_Neptune}')

            # تحديث الرسالة برسالة الرفض
            return m.edit_message_text(f'''
{k} تم رفض الزواج روح دورلك عروس غيرها يا مسكين 💔

{k} العروس رفضت الزواج من العريس
☆
''')

    except Exception as e:
        print(f"خطأ في معالج أزرار الزواج: {e}")
        return m.answer('حدث خطأ في معالجة الطلب!', show_alert=True)

@Client.on_callback_query(filters.regex('aki'))
def akinatorHandler(c,m):
   channel = r.get(f'{Dev_Neptune}:BotChannel') if r.get(f'{Dev_Neptune}:BotChannel') else 'php101'
   if m.data == f'start_aki:{m.from_user.id}':
    rep = InlineKeyboardMarkup (
         [[InlineKeyboardButton ('ꜱᴏᴜʀᴄᴇ ɴᴇᴘᴛᴜɴᴇ', url=f't.me/{channel}')]]
       )
    m.edit_message_text("⇜ جاري بدء اللعبة...",reply_markup=rep)
    aki= akinator.Akinator()
    q = aki.start_game(language="ar")
    users_demon.update({m.from_user.id:[aki,q]})
    return m.edit_message_text(users_demon[m.from_user.id][1],
     reply_markup=InlineKeyboardMarkup (
       [
       [
         InlineKeyboardButton ('لا', callback_data=f'aki_c:n++{m.from_user.id}'),
         InlineKeyboardButton ('اي', callback_data=f'aki_c:y++{m.from_user.id}'),
       ],
       [
        InlineKeyboardButton ('ممكن',callback_data=f'aki_c:p++{m.from_user.id}')
       ]
       ]
     ))
   if m.data == f'aki_c:n++{m.from_user.id}':
    users_demon[m.from_user.id][1] = users_demon[m.from_user.id][0].answer("n")
    if users_demon[m.from_user.id][0].progression >= 65:
        users_demon[m.from_user.id][0].win()
        str_to_send = users_demon[m.from_user.id][0].first_guess
        print(str_to_send)
        m.message.delete()
        rep = InlineKeyboardMarkup (
         [[InlineKeyboardButton ('ꜱᴏᴜʀᴄᴇ ɴᴇᴘᴛᴜɴᴇ', url=f't.me/{channel}')]]
         )
        try: c.send_photo(m.message.chat.id,str_to_send['absolute_picture_path'],caption=f"{str_to_send['name']} - {str_to_send['description']}",reply_markup=rep)
        except: c.send_message(m.message.chat.id,f"{str_to_send['name']} - {str_to_send['description']}",reply_markup=rep)
        del users_demon[m.from_user.id]
    else:
        return m.edit_message_text(users_demon[m.from_user.id][1],
     reply_markup=InlineKeyboardMarkup (
       [
       [
         InlineKeyboardButton ('لا', callback_data=f'aki_c:n++{m.from_user.id}'),
         InlineKeyboardButton ('اي', callback_data=f'aki_c:y++{m.from_user.id}'),
       ],
       [
        InlineKeyboardButton ('ممكن',callback_data=f'aki_c:p++{m.from_user.id}')
       ]
       ]
     ))
   if m.data == f'aki_c:y++{m.from_user.id}':
    users_demon[m.from_user.id][1] = users_demon[m.from_user.id][0].answer("y")
    if users_demon[m.from_user.id][0].progression >= 65:
        users_demon[m.from_user.id][0].win()
        str_to_send = users_demon[m.from_user.id][0].first_guess
        print(str_to_send)
        m.message.delete()
        rep = InlineKeyboardMarkup (
         [[InlineKeyboardButton ('ꜱᴏᴜʀᴄᴇ ɴᴇᴘᴛᴜɴᴇ', url=f't.me/{channel}')]]
         )
        try: c.send_photo(m.message.chat.id,str_to_send['absolute_picture_path'],caption=f"{str_to_send['name']} - {str_to_send['description']}",reply_markup=rep)
        except: c.send_message(m.message.chat.id,f"{str_to_send['name']} - {str_to_send['description']}",reply_markup=rep)
        del users_demon[m.from_user.id]
    else:
        return m.edit_message_text(users_demon[m.from_user.id][1],
     reply_markup=InlineKeyboardMarkup (
       [
       [
         InlineKeyboardButton ('لا', callback_data=f'aki_c:n++{m.from_user.id}'),
         InlineKeyboardButton ('اي', callback_data=f'aki_c:y++{m.from_user.id}'),
       ],
       [
        InlineKeyboardButton ('ممكن',callback_data=f'aki_c:p++{m.from_user.id}')
       ]
       ]
     ))
   if m.data == f'aki_c:p++{m.from_user.id}':
    users_demon[m.from_user.id][1] = users_demon[m.from_user.id][0].answer("p")
    if users_demon[m.from_user.id][0].progression >= 65:
        users_demon[m.from_user.id][0].win()
        str_to_send = users_demon[m.from_user.id][0].first_guess
        print(str_to_send)
        m.message.delete()
        rep = InlineKeyboardMarkup (
         [[InlineKeyboardButton ('ꜱᴏᴜʀᴄᴇ ɴᴇᴘᴛᴜɴᴇ', url=f't.me/{channel}')]]
         )
        try: c.send_photo(m.message.chat.id,str_to_send['absolute_picture_path'],caption=f"{str_to_send['name']} - {str_to_send['description']}",reply_markup=rep)
        except: c.send_message(m.message.chat.id,f"{str_to_send['name']} - {str_to_send['description']}",reply_markup=rep)
        del users_demon[m.from_user.id]
    else:
        return m.edit_message_text(users_demon[m.from_user.id][1],
     reply_markup=InlineKeyboardMarkup (
       [
       [
         InlineKeyboardButton ('لا', callback_data=f'aki_c:n++{m.from_user.id}'),
         InlineKeyboardButton ('اي', callback_data=f'aki_c:y++{m.from_user.id}'),
       ],
       [
        InlineKeyboardButton ('ممكن',callback_data=f'aki_c:p++{m.from_user.id}')
       ]
       ]
     ))


def get_emoji_bank(count):
  if count == 1:
     return '🥇 ) '
  if count == 2:
     return '🥈 ) '
  if count == 3:
     return '🥉 ) '
  else:
     return f' {count}  ) '

