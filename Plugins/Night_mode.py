from threading import Thread
from pyrogram import *
from pyrogram.types import *
from pyrogram.enums import *
from config import *
from helpers.Ranks import *

# أمر الوضع اليلي الرئيسي
@Client.on_message(filters.group & filters.text, group=150)
def nightmode_handler(c, m):
    if not r.get(f"{m.chat.id}:enable:{Dev_Neptune}"):
        return

    text = m.text
    k = r.get(f"{Dev_Neptune}:botkey")

    if text == "الوضع اليلي":
        if not gowner_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الأمر يخص ( المالك الأساسي وفوق ) بس")

        # التحقق من حالة الوضع اليلي
        is_enabled = r.get(f"{m.chat.id}:nightmode:enabled:{Dev_Neptune}")
        status_text = "✓" if is_enabled else "〤"
        status_word = "مفعل" if is_enabled else "غير مفعل"

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"الحالة: {status_text}",
                    callback_data=f"nightmode_toggle:{m.from_user.id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "الإعدادات",
                    callback_data=f"nightmode_settings:{m.from_user.id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "〤",
                    callback_data=f"nightmode_hide:{m.from_user.id}"
                )
            ]
        ])

        return m.reply(
            f"عزيزي {m.from_user.mention}\n"
            f"أنت الآن في الوضع اليلي\n\n"
            f"الحالة الحالية: {status_word}",
            reply_markup=keyboard
        )

# معالج الأزرار
@Client.on_callback_query(filters.regex("^nightmode_"), group=150)
def nightmode_callback_handler(c, m):
    data = m.data
    user_id = m.from_user.id
    chat_id = m.message.chat.id
    k = r.get(f"{Dev_Neptune}:botkey")

    # التحقق من الصلاحيات
    if not gowner_pls(user_id, chat_id):
        return m.answer("هذا الأمر يخص ( المالك الأساسي وفوق ) بس", show_alert=True)

    # تبديل حالة الوضع اليلي
    if data.startswith("nightmode_toggle:"):
        callback_user_id = int(data.split(":")[1])
        if user_id != callback_user_id:
            return m.answer("دنجيب هذا الزر مو الك", show_alert=True)

        is_enabled = r.get(f"{chat_id}:nightmode:enabled:{Dev_Neptune}")

        if is_enabled:
            # تعطيل الوضع اليلي
            r.delete(f"{chat_id}:nightmode:enabled:{Dev_Neptune}")
            status_text = "〤"
            status_word = "غير مفعل"
            message_text = "تم تعطيل الوضع اليلي بنجاح"
        else:

            r.set(f"{chat_id}:nightmode:enabled:{Dev_Neptune}", "1")
            status_text = "✓"
            status_word = "مفعل"
            message_text = "تم تفعيل الوضع اليلي بنجاح"

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "←",
                    callback_data=f"nightmode_back:{user_id}"
                )
            ]
        ])

        return m.edit_message_text(
            message_text,
            reply_markup=keyboard
        )

    # الوضع اليلي
    elif data.startswith("nightmode_settings:"):
        callback_user_id = int(data.split(":")[1])
        if user_id != callback_user_id:
            return m.answer("هذا الزر ليس لك", show_alert=True)

        # الحصول على حالة كل نوع من المحتوى
        links_status = "✓" if r.get(f"{chat_id}:nightmode:links:{Dev_Neptune}") else "〤"
        forward_status = "✓" if r.get(f"{chat_id}:nightmode:forward:{Dev_Neptune}") else "〤"
        contacts_status = "✓" if r.get(f"{chat_id}:nightmode:contacts:{Dev_Neptune}") else "〤"
        photos_status = "✓" if r.get(f"{chat_id}:nightmode:photos:{Dev_Neptune}") else "〤"
        videos_status = "✓" if r.get(f"{chat_id}:nightmode:videos:{Dev_Neptune}") else "〤"
        animations_status = "✓" if r.get(f"{chat_id}:nightmode:animations:{Dev_Neptune}") else "〤"
        stickers_status = "✓" if r.get(f"{chat_id}:nightmode:stickers:{Dev_Neptune}") else "〤"
        files_status = "✓" if r.get(f"{chat_id}:nightmode:files:{Dev_Neptune}") else "〤"

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"الروابط {links_status}",
                    callback_data=f"nightmode_toggle_links:{user_id}"
                ),
                InlineKeyboardButton(
                    f"التوجيه {forward_status}",
                    callback_data=f"nightmode_toggle_forward:{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    f"الجهات {contacts_status}",
                    callback_data=f"nightmode_toggle_contacts:{user_id}"
                ),
                InlineKeyboardButton(
                    f"الصور {photos_status}",
                    callback_data=f"nightmode_toggle_photos:{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    f"الفيديو {videos_status}",
                    callback_data=f"nightmode_toggle_videos:{user_id}"
                ),
                InlineKeyboardButton(
                    f"المتحركات {animations_status}",
                    callback_data=f"nightmode_toggle_animations:{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    f"الملصقات {stickers_status}",
                    callback_data=f"nightmode_toggle_stickers:{user_id}"
                ),
                InlineKeyboardButton(
                    f"الملفات {files_status}",
                    callback_data=f"nightmode_toggle_files:{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "رجوع",
                    callback_data=f"nightmode_back:{user_id}"
                )
            ]
        ])

        return m.edit_message_text(
            f"عزيزي {m.from_user.mention}\n"
            f"أنت الآن في الوضع اليلي\n\n"
            f"اختر نوع المحتوى للتحكم به:",
            reply_markup=keyboard
        )

    # تبديل حالة أنواع المحتوى المختلفة
    elif data.startswith("nightmode_toggle_"):
        parts = data.split(":")
        content_type = parts[0].replace("nightmode_toggle_", "")
        callback_user_id = int(parts[1])

        if user_id != callback_user_id:
            return m.answer("دنجب هذا الزر مو الك", show_alert=True)

        key = f"{chat_id}:nightmode:{content_type}:{Dev_Neptune}"

        if r.get(key):
            r.delete(key)
            status = "تم إلغاء منع"
        else:
            r.set(key, "1")
            status = "تم منع"

        content_names = {
            "links": "الروابط",
            "forward": "التوجيه",
            "contacts": "الجهات",
            "photos": "الصور",
            "videos": "الفيديو",
            "animations": "المتحركات",
            "stickers": "الملصقات",
            "files": "الملفات"
        }

        content_name = content_names.get(content_type, content_type)

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "←",
                    callback_data=f"nightmode_settings:{user_id}"
                )
            ]
        ])

        return m.edit_message_text(
            f"{status} {content_name} في الوضع اليلي",
            reply_markup=keyboard
        )

    # الرجوع للقائمة الرئيسية
    elif data.startswith("nightmode_back:"):
        callback_user_id = int(data.split(":")[1])
        if user_id != callback_user_id:
            return m.answer("دنجب هذا الزر مو الك", show_alert=True)

        is_enabled = r.get(f"{chat_id}:nightmode:enabled:{Dev_Neptune}")
        status_text = "✓" if is_enabled else "〤"
        status_word = "مفعل" if is_enabled else "غير مفعل"

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"الحالة: {status_text}",
                    callback_data=f"nightmode_toggle:{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "الإعدادات",
                    callback_data=f"nightmode_settings:{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "〤",
                    callback_data=f"nightmode_hide:{user_id}"
                )
            ]
        ])

        return m.edit_message_text(
            f"عزيزي {m.from_user.mention}\n"
            f"أنت الآن في الوضع اليلي\n\n"
            f"الوضع الحالي: {status_word}",
            reply_markup=keyboard
        )

    # إخفاء القائمة
    elif data.startswith("nightmode_hide:"):
        callback_user_id = int(data.split(":")[1])
        if user_id != callback_user_id:
            return m.answer("دنجب هذا الزر مو الك", show_alert=True)

        return m.message.delete()

# نظام مراقبة الرسائل للوضع الليلي
@Client.on_message(filters.group, group=99)
def nightmode_monitor(c, m):
    try:
        # التحقق من تفعيل البوت في المجموعة
        if not r.get(f"{m.chat.id}:enable:{Dev_Neptune}"):
            return

        # التحقق من تفعيل الوضع اليلي
        if not r.get(f"{m.chat.id}:nightmode:enabled:{Dev_Neptune}"):
            return

        # تجاهل رسائل البوت نفسه
        if m.from_user and m.from_user.is_bot:
            return

        # تجاهل رسائل المالك الأساسي وما فوق
        if m.from_user and gowner_pls(m.from_user.id, m.chat.id):
            return

        k = r.get(f"{Dev_Neptune}:botkey") or "⇜"

        # فحص الروابط
        if (r.get(f"{m.chat.id}:nightmode:links:{Dev_Neptune}") and
            m.text and
            any(url in m.text.lower() for url in ['http://', 'https://', 'www.', 't.me/', 'telegram.me/'])):
            try:
                m.delete()
            except:
                pass
            return

        # فحص التوجيه
        if (r.get(f"{m.chat.id}:nightmode:forward:{Dev_Neptune}") and
            m.forward_from):
            try:
                m.delete()
            except:
                pass
            return

        # فحص الجهات
        if (r.get(f"{m.chat.id}:nightmode:contacts:{Dev_Neptune}") and
            m.contact):
            try:
                m.delete()
            except:
                pass
            return

        # فحص الصور
        if (r.get(f"{m.chat.id}:nightmode:photos:{Dev_Neptune}") and
            m.photo):
            try:
                m.delete()
            except:
                pass
            return

        # فحص الفيديو
        if (r.get(f"{m.chat.id}:nightmode:videos:{Dev_Neptune}") and
            m.video):
            try:
                m.delete()
            except:
                pass
            return

        # فحص المتحركات
        if (r.get(f"{m.chat.id}:nightmode:animations:{Dev_Neptune}") and
            m.animation):
            try:
                m.delete()
            except:
                pass
            return

        # فحص الملصقات
        if (r.get(f"{m.chat.id}:nightmode:stickers:{Dev_Neptune}") and
            m.sticker):
            try:
                m.delete()
            except:
                pass
            return

        # فحص الملفات
        if (r.get(f"{m.chat.id}:nightmode:files:{Dev_Neptune}") and
            m.document):
            try:
                m.delete()
            except:
                pass
            return

    except Exception as e:
        print(f"خطأ في مراقب الوضع اليلي: {e}")
