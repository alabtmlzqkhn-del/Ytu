import re
from threading import Thread
from pyrogram import *
from pyrogram.enums import *
from pyrogram.types import *
from config import *
from helpers.Ranks import *

# دالة للبحث عن الروابط في النص
def find_links(text):
    """البحث عن الروابط في النص"""
    if not text:
        return False

    # البحث عن أنماط الروابط المختلفة
    patterns = [
        r'http[s]?://',
        r'www\.',
        r't\.me/',
        r'@[a-zA-Z0-9_]+',
        r'[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    ]

    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

# دالة لحساب عدد الميديا في المجموعة
def count_media_messages(chat_id):
    """حساب عدد رسائل الميديا في المجموعة"""
    total = 0

    # حساب كل نوع من الميديا
    photos = int(r.get(f'{Dev_Neptune}:MediaCount:{chat_id}:photos') or 0)
    videos = int(r.get(f'{Dev_Neptune}:MediaCount:{chat_id}:videos') or 0)
    animations = int(r.get(f'{Dev_Neptune}:MediaCount:{chat_id}:animations') or 0)
    stickers = int(r.get(f'{Dev_Neptune}:MediaCount:{chat_id}:stickers') or 0)
    documents = int(r.get(f'{Dev_Neptune}:MediaCount:{chat_id}:documents') or 0)
    custom_emojis = int(r.get(f'{Dev_Neptune}:MediaCount:{chat_id}:custom_emojis') or 0)
    links = int(r.get(f'{Dev_Neptune}:MediaCount:{chat_id}:links') or 0)

    total = photos + videos + animations + stickers + documents + custom_emojis + links
    return total

# دالة لمسح جميع الميديا (العدادات والرسائل)
def clear_all_media(chat_id, client=None):
    """مسح جميع عدادات الميديا والرسائل الفعلية"""
    try:
        deleted_messages = 0

        # حذف الرسائل الفعلية إذا توفر العميل
        if client:
            messages_key = f'{Dev_Neptune}:MediaMessages:{chat_id}'
            message_ids = r.smembers(messages_key)

            if message_ids:
                # تحويل معرفات الرسائل إلى أرقام
                try:
                    message_ids = [int(msg_id.decode() if isinstance(msg_id, bytes) else msg_id)
                                 for msg_id in message_ids
                                 if (msg_id.decode() if isinstance(msg_id, bytes) else str(msg_id)).isdigit()]
                except Exception as e:
                    print(f"خطأ في تحويل معرفات الرسائل: {e}")
                    message_ids = []

                # حذف الرسائل بمجموعات (تليجرام يسمح بحذف 100 رسالة في المرة الواحدة)
                for i in range(0, len(message_ids), 100):
                    batch = message_ids[i:i+100]
                    try:
                        client.delete_messages(chat_id, batch)
                        deleted_messages += len(batch)
                        print(f"تم حذف {len(batch)} رسالة من المحادثة {chat_id}")
                    except Exception as e:
                        print(f"خطأ في حذف مجموعة رسائل: {e}")

                # مسح قائمة معرفات الرسائل
                r.delete(messages_key)

        # مسح العدادات
        media_keys = [
            f'{Dev_Neptune}:MediaCount:{chat_id}:photos',
            f'{Dev_Neptune}:MediaCount:{chat_id}:videos',
            f'{Dev_Neptune}:MediaCount:{chat_id}:animations',
            f'{Dev_Neptune}:MediaCount:{chat_id}:stickers',
            f'{Dev_Neptune}:MediaCount:{chat_id}:documents',
            f'{Dev_Neptune}:MediaCount:{chat_id}:custom_emojis',
            f'{Dev_Neptune}:MediaCount:{chat_id}:links'
        ]

        deleted_count = 0
        for key in media_keys:
            if r.exists(key):
                r.delete(key)
                deleted_count += 1

        print(f"تم مسح {deleted_count} مفاتيح من أصل {len(media_keys)} و {deleted_messages} رسالة من المحادثة {chat_id}")
        return deleted_count, deleted_messages
    except Exception as e:
        print(f"خطأ في مسح الميديا: {e}")
        return 0, 0

# دالة لزيادة عداد الميديا وحفظ معرف الرسالة
def increment_media_count(chat_id, media_type, message_id=None):
    """زيادة عداد نوع معين من الميديا وحفظ معرف الرسالة"""
    key = f'{Dev_Neptune}:MediaCount:{chat_id}:{media_type}'
    current = int(r.get(key) or 0)
    r.set(key, current + 1)

    # حفظ معرف الرسالة للحذف لاحقاً
    if message_id:
        messages_key = f'{Dev_Neptune}:MediaMessages:{chat_id}'
        r.sadd(messages_key, message_id)

# مراقب الميديا لحساب الرسائل
@Client.on_message(filters.group, group=15)
def media_counter(c, m):
    """مراقب لحساب رسائل الميديا والروابط"""
    try:
        if not r.get(f'{m.chat.id}:enable:{Dev_Neptune}'):
            return

        # تجاهل رسائل البوت نفسه
        if m.from_user and m.from_user.is_bot:
            return

        # حساب الميديا
        media_counted = False

        if m.photo:
            increment_media_count(m.chat.id, 'photos', m.id)
            media_counted = True
        elif m.video:
            increment_media_count(m.chat.id, 'videos', m.id)
            media_counted = True
        elif m.animation:
            increment_media_count(m.chat.id, 'animations', m.id)
            media_counted = True
        elif m.sticker:
            increment_media_count(m.chat.id, 'stickers', m.id)
            media_counted = True
        elif m.document:
            increment_media_count(m.chat.id, 'documents', m.id)
            media_counted = True
        elif m.entities:
            # فحص الإيموجيات المميزة
            for entity in m.entities:
                if hasattr(entity, 'type') and str(entity.type) == 'MessageEntityType.CUSTOM_EMOJI':
                    increment_media_count(m.chat.id, 'custom_emojis', m.id)
                    media_counted = True
                    break

        # حساب الروابط (فقط إذا لم يكن هناك ميديا)
        if not media_counted and m.text and find_links(m.text):
            increment_media_count(m.chat.id, 'links', m.id)
            media_counted = True

        # فحص المسح التلقائي فقط إذا تم حساب ميديا
        if media_counted and r.get(f'{m.chat.id}:AutoClear:{Dev_Neptune}'):
            auto_clear_limit = int(r.get(f'{m.chat.id}:AutoClearLimit:{Dev_Neptune}') or 100)
            current_count = count_media_messages(m.chat.id)

            if current_count >= auto_clear_limit:
                deleted_count, deleted_messages = clear_all_media(m.chat.id, c)
                k = r.get(f'{Dev_Neptune}:botkey') or '⇜'
                try:
                    c.send_message(m.chat.id, f'{k} تم مسح جميع الميديا تلقائياً\n{k} تم مسح ( {deleted_messages} ) من الميديا والروابط\n{k} تم الوصول للحد المسموح ( {auto_clear_limit} )')
                except:
                    pass
    except Exception as e:
        print(f"خطأ في مراقبة الميديا: {e}")

@Client.on_message(filters.text & filters.group, group=51)
def clear_commands_handler(c, m):
    """معالج أوامر المسح"""
    k = r.get(f'{Dev_Neptune}:botkey') or '⇜'
    Thread(target=handle_clear_commands, args=(c, m, k)).start()

def handle_clear_commands(c, m, k):
    """معالجة أوامر المسح"""
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

    # أمر مسح الميديا
    if text == 'امسح':
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f'{k} عذراً الامر يخص ↤ الميدر فقط .')

        media_count = count_media_messages(m.chat.id)
        if media_count == 0:
            return m.reply(f'{k} لا توجد ميديا لمسحها')

        # مسح الميديا والرسائل
        deleted_count, deleted_messages = clear_all_media(m.chat.id, c)
        return m.reply(f'بواسطة {m.from_user.mention}\n✅꒐ تم حذف {deleted_messages} ميديا')

    # أمر اختبار العد
    elif text == 'عدد الميديا':
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f'{k} عذراً الامر يخص ↤〖 المدير 〗فقط .')

        media_count = count_media_messages(m.chat.id)
        photos = int(r.get(f'{Dev_Neptune}:MediaCount:{m.chat.id}:photos') or 0)
        videos = int(r.get(f'{Dev_Neptune}:MediaCount:{m.chat.id}:videos') or 0)
        animations = int(r.get(f'{Dev_Neptune}:MediaCount:{m.chat.id}:animations') or 0)
        stickers = int(r.get(f'{Dev_Neptune}:MediaCount:{m.chat.id}:stickers') or 0)
        documents = int(r.get(f'{Dev_Neptune}:MediaCount:{m.chat.id}:documents') or 0)
        custom_emojis = int(r.get(f'{Dev_Neptune}:MediaCount:{m.chat.id}:custom_emojis') or 0)
        links = int(r.get(f'{Dev_Neptune}:MediaCount:{m.chat.id}:links') or 0)

        return m.reply(f'''
{k} إحصائيات الميديا:
{k} الصور: {photos}
{k} الفيديوهات: {videos}
{k} المتحركات: {animations}
{k} الملصقات: {stickers}
{k} الملفات: {documents}
{k} الإيموجيات المميزة: {custom_emojis}
{k} الروابط: {links}
{k} المجموع: {media_count}
''')



    # تفعيل المسح التلقائي
    elif text == 'تفعيل المسح التلقائي':
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f'{k} عذراً الامر يخص ↤〖 المدير 〗فقط .')

        if r.get(f'{m.chat.id}:AutoClear:{Dev_Neptune}'):
            return m.reply(f'{k} المسح التلقائي مفعل من قبل')

        r.set(f'{m.chat.id}:AutoClear:{Dev_Neptune}', 1)
        if not r.get(f'{m.chat.id}:AutoClearLimit:{Dev_Neptune}'):
            r.set(f'{m.chat.id}:AutoClearLimit:{Dev_Neptune}', 100)

        limit = r.get(f'{m.chat.id}:AutoClearLimit:{Dev_Neptune}')
        return m.reply(f'{k} تم تفعيل المسح التلقائي\n{k} سيتم مسح الميديا عند الوصول لـ ( {limit} ) ميديا')

    # تعطيل المسح التلقائي
    elif text == 'تعطيل المسح التلقائي':
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f'{k} عذراً الامر يخص ↤ المدير فقط')

        if not r.get(f'{m.chat.id}:AutoClear:{Dev_Neptune}'):
            return m.reply(f'{k} المسح التلقائي معطل من قبل')

        r.delete(f'{m.chat.id}:AutoClear:{Dev_Neptune}')
        return m.reply(f'{k} تم تعطيل المسح التلقائي')

    # تعيين عدد المسح التلقائي
    elif text.startswith('ضع عدد المسح '):
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f'{k} عذراً الامر يخص ↤ المدير فقط.')

        try:
            parts = text.split(' ')
            if len(parts) < 4:
                return m.reply(f'{k} استخدم الأمر بالشكل الصحيح\n{k} مثال: تعيين المسح التلقائي 50')

            limit = int(parts[3])
            if limit < 1:
                return m.reply(f'{k} العدد يجب أن يكون أكبر من صفر')

            if limit > 1000:
                return m.reply(f'{k} العدد يجب أن يكون أقل من 1000')

            r.set(f'{m.chat.id}:AutoClearLimit:{Dev_Neptune}', limit)

            if r.get(f'{m.chat.id}:AutoClear:{Dev_Neptune}'):
                status = 'مفعل'
            else:
                status = 'معطل'

            return m.reply(f'{k} تم تعيين حد المسح التلقائي إلى ( {limit} )\n{k} حالة المسح التلقائي: {status}')

        except ValueError:
            return m.reply(f'{k} يجب أن يكون العدد رقماً صحيحاً\n{k} مثال: تعيين المسح التلقائي 50')
        except Exception as e:
            return m.reply(f'{k} حدث خطأ في تعيين العدد')

    # عرض إعدادات المسح
    elif text == 'اعدادات المسح':
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f'{k} عذراً الامر يخص ↤ المدير فقط.')

        media_count = count_media_messages(m.chat.id)
        auto_clear_status = 'مفعل' if r.get(f'{m.chat.id}:AutoClear:{Dev_Neptune}') else 'معطل'
        auto_clear_limit = r.get(f'{m.chat.id}:AutoClearLimit:{Dev_Neptune}') or 100

        photos = r.get(f'{Dev_Neptune}:MediaCount:{m.chat.id}:photos') or 0
        videos = r.get(f'{Dev_Neptune}:MediaCount:{m.chat.id}:videos') or 0
        animations = r.get(f'{Dev_Neptune}:MediaCount:{m.chat.id}:animations') or 0
        stickers = r.get(f'{Dev_Neptune}:MediaCount:{m.chat.id}:stickers') or 0
        documents = r.get(f'{Dev_Neptune}:MediaCount:{m.chat.id}:documents') or 0
        custom_emojis = r.get(f'{Dev_Neptune}:MediaCount:{m.chat.id}:custom_emojis') or 0
        links = r.get(f'{Dev_Neptune}:MediaCount:{m.chat.id}:links') or 0

        settings_text = f'''
{k} إعدادات المسح:

📊 إحصائيات الميديا:
{k} الصور: {photos}
{k} الفيديوهات: {videos}
{k} المتحركات: {animations}
{k} الملصقات: {stickers}
{k} الملفات: {documents}
{k} الإيموجيات المميزة: {custom_emojis}
{k} الروابط: {links}
{k} المجموع: {media_count}

⚙️ إعدادات المسح التلقائي:
{k} الحالة: {auto_clear_status}
{k} الحد الأقصى: {auto_clear_limit}

📝 الأوامر المتاحة:
{k} امسح - لمسح جميع الميديا
{k} تعيين المسح التلقائي [عدد]
'''
        return m.reply(settings_text)
