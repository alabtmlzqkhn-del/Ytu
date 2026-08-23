import random
import time
import asyncio
from threading import Thread
from pyrogram import *
from pyrogram.enums import *
from pyrogram.types import *
from config import *
from helpers.Ranks import *

# قاموس لتخزين حالة التاك التلقائي لكل مجموعة
auto_tag_active = {}

# قاموس لتخزين آخر شخص تم عمل له تاك في كل مجموعة
last_tagged_user = {}

# قاموس لتخزين threads النشطة لكل مجموعة
active_threads = {}

# ردود عشوائية للتاك
random_tag_messages = [
    "تعال لك وين طامس",
    "نور الكروب كافي طمس",
    "ها يروحي",
    "وينك ؟",
    "تع",
    "وف",
    "مسيو",
    "لافيو",
    "تع نورنا"
]

@Client.on_message(filters.text & filters.group, group=54)
def auto_tag_commands_handler(c, m):
    """معالج أوامر التاك التلقائي"""
    k = r.get(f'{Dev_Neptune}:botkey') or '⇜'
    Thread(target=handle_auto_tag_commands, args=(c, m, k)).start()

def handle_auto_tag_commands(c, m, k):
    """معالجة أوامر التاك التلقائي"""
    if not r.get(f'{m.chat.id}:enable:{Dev_Neptune}'):
        return

    if r.get(f'{m.chat.id}:mute:{Dev_Neptune}') and not admin_pls(m.from_user.id, m.chat.id):
        return

    if r.get(f'{m.from_user.id}:mute:{m.chat.id}{Dev_Neptune}'):
        return

    if r.get(f'{m.from_user.id}:mute:{Dev_Neptune}'):
        return

    text = m.text
    name = r.get(f'{Dev_Neptune}:BotName') if r.get(f'{Dev_Neptune}:BotName') else 'jack'
    if text.startswith(f'{name} '):
        text = text.replace(f'{name} ', '')

    # تفعيل التاك التلقائي
    if text == 'تفعيل التاك التلقائي':
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f'{k} عذراً الامر يخص ↤〖 المدير 〗فقط .')

        if r.get(f'{m.chat.id}:AutoTag:{Dev_Neptune}'):
            return m.reply(f'{k} التاك التلقائي مفعل من قبل')

        r.set(f'{m.chat.id}:AutoTag:{Dev_Neptune}', 1)

        # بدء التاك التلقائي
        start_auto_tag(c, m.chat.id)

        admin_mention = m.from_user.mention
        return m.reply(f'{k} تم تفعيل التاك التلقائي\n{k} بواسطة : {admin_mention}')

    # تعطيل التاك التلقائي
    elif text == 'تعطيل التاك التلقائي':
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f'{k} عذراً الامر يخص ↤〖 المدير 〗فقط .')

        if not r.get(f'{m.chat.id}:AutoTag:{Dev_Neptune}'):
            return m.reply(f'{k} التاك التلقائي معطل من قبل')

        r.delete(f'{m.chat.id}:AutoTag:{Dev_Neptune}')

        # إيقاف التاك التلقائي
        stop_auto_tag(m.chat.id)

        admin_mention = m.from_user.mention
        return m.reply(f'{k} تم تعطيل التاك التلقائي\n{k} بواسطة : {admin_mention}')

def start_auto_tag(c, chat_id):
    """بدء التاك التلقائي للمجموعة"""
    # التحقق من وجود thread نشط للمجموعة
    if chat_id in active_threads and active_threads[chat_id].is_alive():
        print(f"التاك التلقائي يعمل بالفعل للمجموعة {chat_id}")
        return

    # إيقاف التاك السابق إن وجد
    stop_auto_tag(chat_id)

    # تعيين حالة التاك كنشط
    auto_tag_active[chat_id] = True

    # إنشاء وبدء thread جديد
    thread = Thread(target=auto_tag_loop, args=(c, chat_id))
    thread.daemon = True  # جعل الـ thread daemon لإنهائه عند إغلاق البرنامج
    active_threads[chat_id] = thread
    thread.start()
    print(f"تم بدء التاك التلقائي للمجموعة {chat_id}")

def stop_auto_tag(chat_id):
    """إيقاف التاك التلقائي للمجموعة"""
    auto_tag_active[chat_id] = False

    # مسح ذاكرة آخر شخص تم عمل له تاك
    if chat_id in last_tagged_user:
        del last_tagged_user[chat_id]

    # تنظيف الـ thread المنتهي
    if chat_id in active_threads:
        del active_threads[chat_id]

    print(f"تم إيقاف التاك التلقائي للمجموعة {chat_id}")

def auto_tag_loop(c, chat_id):
    """حلقة التاك التلقائي"""
    while auto_tag_active.get(chat_id, False):
        try:
            # التحقق من أن التاك التلقائي ما زال مفعل في قاعدة البيانات
            if not r.get(f'{chat_id}:AutoTag:{Dev_Neptune}'):
                auto_tag_active[chat_id] = False
                break

            # الحصول على أعضاء المجموعة
            members = []
            try:
                for member in c.get_chat_members(chat_id, limit=700):
                    # استثناء البوتات والحسابات المحذوفة
                    if (not member.user.is_bot and
                        not member.user.is_deleted and
                        member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]):
                        members.append(member.user)
            except Exception as e:
                print(f"خطأ في الحصول على أعضاء المجموعة {chat_id}: {e}")
                time.sleep(10)
                continue

            # اختيار عضو عشوائي (تجنب تكرار نفس الشخص)
            if members:
                # إزالة آخر شخص تم عمل له تاك من القائمة إذا كان موجود
                available_members = members.copy()
                if chat_id in last_tagged_user and last_tagged_user[chat_id] in [m.id for m in members]:
                    available_members = [m for m in members if m.id != last_tagged_user[chat_id]]

                # إذا لم يبق أحد بعد إزالة آخر شخص، استخدم القائمة الكاملة
                if not available_members:
                    available_members = members

                random_member = random.choice(available_members)
                random_message = random.choice(random_tag_messages)

                # حفظ ID آخر شخص تم عمل له تاك
                last_tagged_user[chat_id] = random_member.id

                # إرسال رسالة التاك
                try:
                    c.send_message(
                        chat_id,
                        f"{random_message} {random_member.mention}"
                    )
                except Exception as e:
                    print(f"خطأ في إرسال رسالة التاك للمجموعة {chat_id}: {e}")

            # انتظار 10 ثواني قبل التاك التالي
            time.sleep(10)

        except Exception as e:
            print(f"خطأ في حلقة التاك التلقائي للمجموعة {chat_id}: {e}")
            time.sleep(10)

    # تنظيف عند انتهاء الحلقة
    auto_tag_active[chat_id] = False
    if chat_id in active_threads:
        del active_threads[chat_id]
    print(f"انتهت حلقة التاك التلقائي للمجموعة {chat_id}")

# معالج لإيقاف التاك التلقائي عند مغادرة البوت للمجموعة
@Client.on_message(filters.left_chat_member, group=55)
def handle_bot_left_chat(c, m):
    """معالج مغادرة البوت للمجموعة"""
    if m.left_chat_member and m.left_chat_member.id == int(Dev_Neptune):
        # إيقاف التاك التلقائي عند مغادرة البوت
        stop_auto_tag(m.chat.id)
        r.delete(f'{m.chat.id}:AutoTag:{Dev_Neptune}')

# معالج لإعادة تشغيل التاك التلقائي عند بدء البوت
@Client.on_message(filters.text, group=56)
def restore_auto_tags(c, m):
    """إعادة تشغيل التاك التلقائي للمجموعات المفعلة عند بدء البوت"""
    # هذا المعالج يعمل مرة واحدة فقط عند أول رسالة
    if not hasattr(restore_auto_tags, 'executed'):
        restore_auto_tags.executed = True

        # البحث عن المجموعات التي لديها تاك تلقائي مفعل
        try:
            for key in r.scan_iter(match=f"*:AutoTag:{Dev_Neptune}"):
                chat_id = int(key.split(':')[0])
                if r.get(key):  # التأكد من أن التاك مفعل
                    start_auto_tag(c, chat_id)
                    print(f"تم إعادة تشغيل التاك التلقائي للمجموعة: {chat_id}")
        except Exception as e:
            print(f"خطأ في إعادة تشغيل التاك التلقائي: {e}")
