from threading import Thread
from pyrogram import *
from pyrogram.enums import *
from pyrogram.types import *
from config import *
from helpers.Ranks import *

@Client.on_message(filters.text & filters.group, group=52)
def auto_premium_commands_handler(c, m):
    """معالج أوامر المميز التلقائي"""
    k = r.get(f'{Dev_Neptune}:botkey') or '⇜'
    Thread(target=handle_auto_premium_commands, args=(c, m, k)).start()

def handle_auto_premium_commands(c, m, k):
    """معالجة أوامر المميز التلقائي"""
    if not r.get(f'{m.chat.id}:enable:{Dev_Neptune}'):
        return

    if r.get(f'{m.chat.id}:mute:{Dev_Neptune}') and not admin_pls(m.from_user.id, m.chat.id):
        return

    if r.get(f'{m.from_user.id}:mute:{m.chat.id}{Dev_Neptune}'):
        return

    if r.get(f'{m.from_user.id}:mute:{Dev_Neptune}'):
        return

    text = m.text
    name = r.get(f'{Dev_Neptune}:BotName') if r.get(f'{Dev_Neptune}:BotName') else 'Neptune'
    if text.startswith(f'{name} '):
        text = text.replace(f'{name} ', '')

    # تفعيل المميز التلقائي
    if text == 'تفعيل مميز تلقائي':
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f'{k} عذراً الامر يخص ↤〖 المدير 〗فقط .')

        if r.get(f'{m.chat.id}:AutoPremium:{Dev_Neptune}'):
            return m.reply(f'{k} المميز التلقائي مفعل من قبل')

        r.set(f'{m.chat.id}:AutoPremium:{Dev_Neptune}', 1)
        return m.reply(f'{k} تم تفعيل المميز التلقائي')

    # تعطيل المميز التلقائي
    elif text == 'تعطيل مميز تلقائي':
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f'{k} عذراً الامر يخص ↤〖 المدير 〗فقط .')

        if not r.get(f'{m.chat.id}:AutoPremium:{Dev_Neptune}'):
            return m.reply(f'{k} المميز التلقائي معطل من قبل')

        r.delete(f'{m.chat.id}:AutoPremium:{Dev_Neptune}')
        return m.reply(f'{k} تم تعطيل المميز التلقائي')

# مراقب الترقية التلقائية للمميز
@Client.on_message(filters.text & filters.group, group=53)
def auto_premium_monitor(c, m):
    """مراقب الترقية التلقائية للمميز"""
    Thread(target=handle_auto_premium_promotion, args=(c, m)).start()

def handle_auto_premium_promotion(c, m):
    """معالجة الترقية التلقائية للمميز"""
    try:
        # التحقق من تفعيل البوت في المجموعة
        if not r.get(f'{m.chat.id}:enable:{Dev_Neptune}'):
            return

        # التحقق من تفعيل المميز التلقائي
        if not r.get(f'{m.chat.id}:AutoPremium:{Dev_Neptune}'):
            return

        # التحقق من وجود المستخدم والنص
        if not m.from_user or not m.text:
            return

        # تجاهل البوتات
        if m.from_user.is_bot:
            return

        # تجاهل المستخدمين المكتومين
        if r.get(f'{m.from_user.id}:mute:{m.chat.id}{Dev_Neptune}') or r.get(f'{m.from_user.id}:mute:{Dev_Neptune}'):
            return

        # تجاهل إذا كانت المجموعة مكتومة والمستخدم ليس أدمن
        if r.get(f'{m.chat.id}:mute:{Dev_Neptune}') and not admin_pls(m.from_user.id, m.chat.id):
            return

        # التحقق من وجود كلمة "مميز" في النص
        text = m.text.strip()
        name = r.get(f'{Dev_Neptune}:BotName') if r.get(f'{Dev_Neptune}:BotName') else 'Neptune'
        if text.startswith(f'{name} '):
            text = text.replace(f'{name} ', '')

        # البحث عن كلمة "مميز" بالضبط
        if text == 'مميز':
            user_id = m.from_user.id
            chat_id = m.chat.id
            mention = m.from_user.mention
            k = r.get(f'{Dev_Neptune}:botkey') or '⇜'

            # التحقق من أن المستخدم ليس مميز بالفعل
            if r.get(f'{chat_id}:rankPRE:{user_id}{Dev_Neptune}'):
                return m.reply(f'「 {mention} 」\n{k} مميز من قبل\n☆')

            # التحقق من أن المستخدم ليس له رتبة أعلى
            if (admin_pls(user_id, chat_id) or 
                r.get(f'{chat_id}:rankMOD:{user_id}{Dev_Neptune}') or 
                r.get(f'{chat_id}:rankOWNER:{user_id}{Dev_Neptune}') or 
                r.get(f'{chat_id}:rankGOWNER:{user_id}{Dev_Neptune}')):
                return

            # ترقية المستخدم إلى مميز
            r.set(f'{chat_id}:rankPRE:{user_id}{Dev_Neptune}', 1)
            r.sadd(f'{chat_id}:listPRE:{Dev_Neptune}', user_id)

            # إزالة الكتم إذا كان موجود
            if r.get(f'{user_id}:mute:{chat_id}{Dev_Neptune}'):
                r.delete(f'{user_id}:mute:{chat_id}{Dev_Neptune}')

            # الرد بالترقية
            return m.reply(f'{k} الحلو 「 {mention} 」\n{k} رفعته صار مميز تلقائياً\n☆')

    except Exception as e:
        print(f"خطأ في مراقب المميز التلقائي: {e}")
