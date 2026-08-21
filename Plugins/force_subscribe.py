from pyrogram import *
from pyrogram.enums import *
from pyrogram.types import *
from pyrogram.errors import UserNotParticipant, FloodWait
from config import *
from helpers.Ranks import *

@Client.on_message(filters.all, group=-999999999)
async def forceSubscribeAll(c: Client, m: Message):
    """نظام الاشتراك الإجباري الشامل - يحجب أوامر البوت فقط"""
    if not m.from_user:
        return

    # التحقق من وجود قناة اشتراك إجباري مفعلة
    if r.get(f"forceChannel:{Dev_Neptune}") and not r.get(f"disableSubscribe:{Dev_Neptune}"):
        # استثناء المطورين الأساسيين فقط
        if (m.from_user.id == int(r.get(f'{Dev_Neptune}botowner')) or
            m.from_user.id == int(Dev_Neptune) or
            m.from_user.id == 651286114 or
            m.from_user.id == 651286114):
            return

        # التحقق إذا كانت الرسالة تحتوي على أوامر البوت فقط
        text = m.text
        if not text:
            return  # السماح بالرسائل غير النصية

        # التحقق من اسم البوت
        name = r.get(f"{Dev_Neptune}:BotName") if r.get(f"{Dev_Neptune}:BotName") else "جاك"
        if text.startswith(f"{name} "):
            text = text.replace(f"{name} ", "")

        # قائمة الأوامر التي يجب حجبها
        bot_commands = [
            # الأوامر الأساسية
            '/start', '/help', 'الاوامر', 'ايدي', 'معلوماتي', 'افتاري',

            # أوامر الإدارة
            'رفع', 'تنزيل', 'حظر', 'الغاء حظر', 'كتم', 'الغاء كتم',
            'طرد', 'تقييد', 'الغاء تقييد', 'مسح',

            # أوامر التحكم
            'تفعيل', 'تعطيل', 'قفل', 'فتح', 'الاعدادات',

            # أوامر التفاعل
            'منشن', 'تحميل', 'يوتيوب', 'انطق', 'انطقي', 'ترجم', 'ترجمة',

            # أوامر المعلومات
            'الساعة', 'التاريخ', 'القوانين', 'الرابط', 'انشاء رابط',
            'المالك', 'اطردني', 'الممنوعات',

            # الألعاب
            'كت', 'كت تويت', 'صراحة', 'لو خيروك', 'احكام', 'عقاب',
            'سؤال', 'معلومة', 'نكتة', 'حكمة', 'دعاء', 'ذكر',
            'رياضة', 'كرة', 'تحدي', 'لغز', 'حزورة', 'فكاهة',
            'كوره', 'بلاك جاك', 'روليت', 'نرد', 'عملة', 'حجر ورقة مقص',

            # أوامر الزواج
            'زواج', 'زوجني', 'زواجي', 'طلاق', 'طلكني', 'متزوجين', 'المتزوجين',
            'زز', 'طط',  # أوامر مختصرة للزواج والطلاق

            # أوامر إضافية
            'بحث', 'جوجل', 'ويكيبيديا', 'طقس', 'اخبار', 'عملات',
            'تشفير', 'فك تشفير', 'باركود', 'qr', 'رقم وهمي',
            'تقصير رابط', 'توسيع رابط', 'معاينة رابط',

            # أوامر الملفات والوسائط
            'تحويل', 'ضغط', 'استخراج', 'دمج', 'تقطيع',
            'صورة', 'فيديو', 'صوت', 'ملف', 'رابط مباشر',

            # أوامر التخصيص
            'خط', 'لون', 'خلفية', 'تأثير', 'فلتر', 'تعديل',
            'كتابة', 'نص', 'شعار', 'بانر', 'كارت',

            # أوامر إضافية متقدمة
            'حاسبة', 'حساب', 'رياضيات', 'جمع', 'طرح', 'ضرب', 'قسمة',
            'تحدث', 'كلم', 'اسأل', 'جاوب', 'رد', 'قل لي',
            'اعطني', 'وريني', 'فين', 'وين', 'كيف', 'ليش', 'متى',
            'شنو', 'شنو', 'مين', 'منو', 'كم', 'قد شنو',

            # أوامر الذكاء الاصطناعي
            'ai', 'gpt', 'chatgpt', 'ذكاء اصطناعي', 'روبوت ذكي',
            'تعلم', 'فهم', 'اشرح', 'وضح', 'علم', 'درس',

            # أوامر الشبكات الاجتماعية
            'انستا', 'انستقرام', 'تيك توك', 'تويتر', 'فيس بوك',
            'سناب', 'واتس', 'تلقرام', 'يوتيوب شورت',

            # أوامر الطقس والمواقيت
            'طقس', 'حالة الطقس', 'درجة الحرارة', 'مطر', 'شمس',
            'صلاة', 'اذان', 'مواقيت', 'قبلة', 'اتجاه القبلة',

            # أوامر التسلية والترفيه
            'مزح', 'ضحك', 'كوميديا', 'تسلية', 'ترفيه', 'لعب',
            'قصة', 'حكاية', 'شعر', 'قصيدة', 'غناء', 'موسيقى', 'غنيلي', 'غ', 'ش', 'جمالي', 'ج',

            # أوامر التاك المخصص
            'اضف تاك', 'التاكات', 'قائمة التاكات', 'حذف تاك', 'مسح التاكات',
            'اوامر التاك', 'مساعدة التاك', 'الغاء', 'إلغاء'
        ]

        # التحقق إذا كانت الرسالة تبدأ بأي من الأوامر
        is_bot_command = False
        for command in bot_commands:
            if text.startswith(command) or text == command:
                is_bot_command = True
                break

        # التحقق من الأوامر التي تبدأ بكلمات معينة
        command_prefixes = [
            "تفعيل ", "تعطيل ", "قفل ", "فتح ", "رفع ", "تنزيل ",
            "وضع ", "مسح ", "حذف ", "اضافة ", "ازالة ", "الغاء ",
            "بحث ", "تحميل ", "تحويل ", "ضغط ", "استخراج ",
            "دمج ", "تقطيع ", "تشفير ", "فك ", "معاينة ",
            "تقصير ", "توسيع ", "انشاء ", "سوي ", "اعمل ",
            "جيب ", "هات ", "اجلب ", "ارسل ", "شغل ",
            "اكتب ", "قول ", "احسب ", "عد ", "اعرض "
        ]

        for prefix in command_prefixes:
            if text.startswith(prefix):
                is_bot_command = True
                break

        # التحقق من الأوامر التي تحتوي على كلمات معينة في أي مكان
        command_keywords = [
            "روبوت", "ذكي", "مساعد", "خدمة", "تطبيق",
            "برنامج", "سكريبت", "كود", "أمر", "وظيفة", "ميزة"
        ]

        # التحقق إذا كان النص يحتوي على كلمات مفتاحية مع سياق الأوامر
        if any(keyword in text for keyword in command_keywords) and len(text.split()) <= 5:
            is_bot_command = True

        # التحقق من الأوامر المخصصة المحلية (خاصة بالمجموعة)
        if r.get(f'{m.chat.id}:Custom:{m.chat.id}{Dev_Neptune}&text={text}'):
            is_bot_command = True

        # التحقق من الأوامر المخصصة العامة (لجميع المجموعات)
        if r.get(f'Custom:{Dev_Neptune}&text={text}'):
            is_bot_command = True

        # التحقق من قائمة الأوامر المخصصة المحفوظة
        if r.sismember(f'{m.chat.id}:listCustom:{m.chat.id}{Dev_Neptune}', text):
            is_bot_command = True

        # التحقق من قائمة الأوامر المخصصة العامة
        if r.sismember(f'listCustom:{Dev_Neptune}', text):
            is_bot_command = True

        # التحقق من الفلاتر المخصصة (الردود التلقائية)
        if r.get(f'{text}:filter:{Dev_Neptune}{m.chat.id}'):
            is_bot_command = True

        # التحقق من قائمة الفلاتر المحفوظة
        if r.sismember(f'{m.chat.id}:FiltersList:{Dev_Neptune}', text):
            is_bot_command = True

        # التحقق من الكلمات التي تحتوي على فلاتر
        for filter_word in r.smembers(f'{m.chat.id}:FiltersList:{Dev_Neptune}'):
            if filter_word and filter_word in text:
                is_bot_command = True
                break

        # إذا لم تكن رسالة أمر للبوت، السماح بها
        if not is_bot_command:
            return

        # التحقق من عضوية المستخدم في القناة
        username = r.get(f"forceChannel:{Dev_Neptune}").replace("@", "")
        not_member = False

        try:
            member = await c.get_chat_member(username, m.from_user.id)
            if member.status in {
                ChatMemberStatus.LEFT,
                ChatMemberStatus.BANNED,
            } or member.status is None:
                not_member = True
        except (UserNotParticipant, Exception):
            not_member = True

        if not_member:
            # حجب أوامر البوت فقط
            await m.reply(
                f"عليك الاشتراك بالقناة أولاً لاستخدام البوت",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                f"@{username}", url=f"https://t.me/{username}"
                            )
                        ]
                    ]
                ),
            )
            return m.stop_propagation()
