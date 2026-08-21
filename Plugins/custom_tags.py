import re
import time
from threading import Thread
from pyrogram import *
from pyrogram.enums import *
from pyrogram.types import *
from config import *
from helpers.Ranks import *

@Client.on_message(filters.text & filters.group, group=55)
def custom_tags_handler(c, m):
    """معالج أوامر التاك المخصص"""
    k = r.get(f'{Dev_Neptune}:botkey') or '⇜'
    Thread(target=handle_custom_tags, args=(c, m, k)).start()

def handle_custom_tags(c, m, k):
    """معالجة أوامر التاك المخصص"""
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

    # أمر الإلغاء
    if text == 'الغاء' or text == 'إلغاء':
        # إلغاء عملية إضافة تاك
        if r.get(f'{m.chat.id}:addCustomTag:{m.from_user.id}{Dev_Neptune}'):
            r.delete(f'{m.chat.id}:addCustomTag:{m.from_user.id}{Dev_Neptune}')
            return m.reply(f'{k} تم إلغاء عملية إضافة التاك')

        if r.get(f'{m.chat.id}:addCustomTag2:{m.from_user.id}{Dev_Neptune}'):
            r.delete(f'{m.chat.id}:addCustomTag2:{m.from_user.id}{Dev_Neptune}')
            return m.reply(f'{k} تم إلغاء عملية إضافة التاك')

        # إلغاء عملية حذف تاك
        if r.get(f'{m.chat.id}:delCustomTag:{m.from_user.id}{Dev_Neptune}'):
            r.delete(f'{m.chat.id}:delCustomTag:{m.from_user.id}{Dev_Neptune}')
            return m.reply(f'{k} تم إلغاء عملية حذف التاك')

    # أمر إضافة تاك جديد
    if text == 'اضف تاك':
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f'{k} هذا الامر يخص ( المدير وفوق ) بس')

        if r.get(f'{m.chat.id}:addCustomTag:{m.from_user.id}{Dev_Neptune}') or r.get(f'{m.chat.id}:addCustomTag2:{m.from_user.id}{Dev_Neptune}'):
            return m.reply(f'{k} انت بالفعل في عملية إضافة تاك\n{k} ارسل "الغاء" لإلغاء العملية')

        r.set(f'{m.chat.id}:addCustomTag:{m.from_user.id}{Dev_Neptune}', 1, ex=300)  # انتهاء صلاحية بعد 5 دقائق
        return m.reply(f'{k} ارسل الان اسم التاك .\n{k} ارسل "الغاء" لإلغاء العملية')

    # استقبال اسم التاك
    if r.get(f'{m.chat.id}:addCustomTag:{m.from_user.id}{Dev_Neptune}') and mod_pls(m.from_user.id, m.chat.id):
        if len(text.split()) == 1 and len(text) <= 30 and text not in ['الغاء', 'إلغاء']:  # التأكد من أن الاسم كلمة واحدة وليس طويل جداً
            # التحقق من عدم وجود التاك مسبقاً
            if r.hexists(f'{m.chat.id}:CustomTags:{Dev_Neptune}', text):
                return m.reply(f'{k} التاك "{text}" موجود مسبقاً\n{k} اختر اسم آخر أو احذف التاك الموجود أولاً')

            r.delete(f'{m.chat.id}:addCustomTag:{m.from_user.id}{Dev_Neptune}')
            r.set(f'{m.chat.id}:addCustomTag2:{m.from_user.id}{Dev_Neptune}', text, ex=300)  # انتهاء صلاحية بعد 5 دقائق
            return m.reply(f'{k} تم حفظ الاسم ارسل الان المعرف\n{k} ارسل "الغاء" لإلغاء العملية')
        else:
            return m.reply(f'{k} يجب أن يكون اسم التاك كلمة واحدة فقط وأقل من 30 حرف')

    # استقبال المعرف
    if r.get(f'{m.chat.id}:addCustomTag2:{m.from_user.id}{Dev_Neptune}') and mod_pls(m.from_user.id, m.chat.id):
        tag_name = r.get(f'{m.chat.id}:addCustomTag2:{m.from_user.id}{Dev_Neptune}')
        
        # التحقق من صحة المعرف
        if text.startswith('@') and len(text) > 1:
            username = text
            r.delete(f'{m.chat.id}:addCustomTag2:{m.from_user.id}{Dev_Neptune}')
            
            # حفظ التاك في Redis
            r.hset(f'{m.chat.id}:CustomTags:{Dev_Neptune}', tag_name, username)
            
            return m.reply(f'{k} تم حفظ التاك بنجاح .\n{k} اسم التاك: {tag_name}\n{k} المعرف: {username}')
        else:
            return m.reply(f'{k} يجب أن يبدأ المعرف بـ @ مثل @usrname')

    # أمر عرض التاكات المحفوظة
    if text == 'التاكات' or text == 'قائمة التاكات':
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f'{k} هذا الامر يخص ( المدير وفوق ) بس')
        
        tags = r.hgetall(f'{m.chat.id}:CustomTags:{Dev_Neptune}')
        if not tags:
            return m.reply(f'{k} لا توجد تاكات محفوظة في هذه المجموعة')
        
        tags_list = f'{k} قائمة التاكات المحفوظة:\n\n'
        for tag_name, username in tags.items():
            tags_list += f'• {tag_name} ← {username}\n'
        
        return m.reply(tags_list)

    # أمر حذف تاك
    if text == 'حذف تاك':
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f'{k} هذا الامر يخص ( المدير وفوق ) بس')
        
        if r.get(f'{m.chat.id}:delCustomTag:{m.from_user.id}{Dev_Neptune}'):
            return m.reply(f'{k} انت بالفعل في عملية حذف تاك')
        
        r.set(f'{m.chat.id}:delCustomTag:{m.from_user.id}{Dev_Neptune}', 1)
        return m.reply(f'{k} ارسل اسم التاك المراد حذفه')

    # استقبال اسم التاك للحذف
    if r.get(f'{m.chat.id}:delCustomTag:{m.from_user.id}{Dev_Neptune}') and mod_pls(m.from_user.id, m.chat.id):
        r.delete(f'{m.chat.id}:delCustomTag:{m.from_user.id}{Dev_Neptune}')
        
        if r.hexists(f'{m.chat.id}:CustomTags:{Dev_Neptune}', text):
            username = r.hget(f'{m.chat.id}:CustomTags:{Dev_Neptune}', text)
            r.hdel(f'{m.chat.id}:CustomTags:{Dev_Neptune}', text)
            return m.reply(f'{k} تم حذف التاك بنجاح\n{k} اسم التاك: {text}\n{k} المعرف: {username}')
        else:
            return m.reply(f'{k} التاك "{text}" غير موجود')

    # أمر مسح جميع التاكات
    if text == 'مسح التاكات':
        if not owner_pls(m.from_user.id, m.chat.id):
            return m.reply(f'{k} هذا الامر يخص ( المالك وفوق ) بس')

        tags_count = r.hlen(f'{m.chat.id}:CustomTags:{Dev_Neptune}')
        if tags_count == 0:
            return m.reply(f'{k} لا توجد تاكات محفوظة للحذف')

        r.delete(f'{m.chat.id}:CustomTags:{Dev_Neptune}')
        return m.reply(f'{k} تم مسح جميع التاكات ({tags_count} تاك)')

    # أمر المساعدة
    if text == 'اوامر التاك' or text == 'مساعدة التاك':
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f'{k} هذا الامر يخص ( المدير وفوق ) بس')

        help_text = f"""
{k} أوامر التاك المخصص:

• اضف تاك ← لإضافة تاك جديد
• التاكات ← لعرض قائمة التاكات
• حذف تاك ← لحذف تاك معين
• مسح التاكات ← لمسح جميع التاكات (المالك فقط)
• الغاء ← لإلغاء العملية الحالية

{k} ملاحظة: التاك يعمل عند كتابة الاسم ككلمة منفصلة في أي رسالة
        """
        return m.reply(help_text.strip())

@Client.on_message(filters.text & filters.group, group=57)
def custom_tags_monitor(c, m):
    """مراقب الرسائل للبحث عن التاكات المخصصة"""
    Thread(target=monitor_custom_tags, args=(c, m)).start()

def monitor_custom_tags(c, m):
    """مراقبة الرسائل للبحث عن أسماء التاك المحفوظة"""
    try:
        if not r.get(f'{m.chat.id}:enable:{Dev_Neptune}'):
            return

        # تجاهل رسائل البوت نفسه
        if m.from_user and m.from_user.is_bot:
            return

        # تجاهل الرسائل المكتومة
        if r.get(f'{m.chat.id}:mute:{Dev_Neptune}') and not admin_pls(m.from_user.id, m.chat.id):
            return

        if r.get(f'{m.from_user.id}:mute:{m.chat.id}{Dev_Neptune}'):
            return

        if r.get(f'{m.from_user.id}:mute:{Dev_Neptune}'):
            return

        text = m.text
        if not text:
            return

        # إزالة اسم البوت من بداية الرسالة إن وجد
        name = r.get(f'{Dev_Neptune}:BotName') if r.get(f'{Dev_Neptune}:BotName') else 'Neptune'
        if text.startswith(f'{name} '):
            text = text.replace(f'{name} ', '')

        # الحصول على جميع التاكات المحفوظة للمجموعة
        tags = r.hgetall(f'{m.chat.id}:CustomTags:{Dev_Neptune}')
        if not tags:
            return

        # البحث عن أسماء التاك في النص
        for tag_name, username in tags.items():
            # البحث عن اسم التاك ككلمة منفصلة (ليس جزء من كلمة أخرى)
            pattern = r'\b' + re.escape(tag_name) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                # إرسال رسالة المنشن
                mention_text = f"- ذكروك يا عيني : {username}"
                try:
                    m.reply(mention_text, quote=False)
                    break  # إرسال منشن واحد فقط حتى لو كان هناك أكثر من تاك في الرسالة
                except Exception as e:
                    print(f"خطأ في إرسال منشن التاك المخصص: {e}")

    except Exception as e:
        print(f"خطأ في مراقب التاك المخصص: {e}")
