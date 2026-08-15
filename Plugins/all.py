import random, re, time, pytz, os, gtts, requests
import speech_recognition as sr
from pydub import AudioSegment
from hijri_converter import Hijri, Gregorian
from datetime import datetime
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
import hashlib
from pyrogram import *
from pyrogram.enums import *
from pyrogram.types import *
from config import *
from helpers.Ranks import *
from helpers.persianData import persianInformation
from .welcome_and_rules import *
from .games import *
from PIL import Image
from asyncio import run as RUN
from Python_ARQ import ARQ
from aiohttp import ClientSession

# from googletrans import Translator as googletranstr
from mutagen.mp3 import MP3 as mutagenMP3
# from main import TelegramBot

ARQ_API_KEY = "OZJRWV-SAURXD-PMBUKF-GMVSNS-ARQ"
ARQ_API_URL = "https://arq.hamker.dev"

# إنشاء ThreadPool للمعالجة السريعة
nsfw_executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="NSFW_Scanner")

# Cache للنتائج لتجنب فحص نفس الصور مرة أخرى
nsfw_cache = {}
CACHE_SIZE_LIMIT = 1000

# إحصائيات بسيطة للأداء (للمراقبة الداخلية فقط)
nsfw_stats = {
    "instant_deletes": 0,
    "cache_hits": 0,
    "total_processed": 0
}

# قائمة كلمات مفتاحية محسنة للحذف الفوري
INSTANT_DELETE_KEYWORDS = [
    # English keywords
    'porn', 'sex', 'nude', 'naked', 'xxx', 'adult', 'nsfw', 'explicit',
    'hot', 'sexy', 'erotic', 'boobs', 'ass', 'dick', 'pussy', 'fuck',
    'shit', 'bitch', 'slut', 'whore', 'cum', 'orgasm', 'masturbate',
    'blowjob', 'anal', 'vagina', 'penis', 'breast', 'nipple',
    # Arabic keywords
    'جنس', 'عاري', 'اباحي', 'إباحي', 'عارية', 'سكس', 'ساخن', 'مثير',
    'عاهرة', 'زانية', 'قحبة', 'شرموطة', 'كس', 'زب', 'طيز', 'صدر', 'عير بطيزك', 'كسختك', 'كسمك', 'كس اختك', 'كس امك', 'ابن التنيم', 'اخت التنيم', 'بلاع العير', 'بنت الكحبه'
]

# translator = googletranstr()


def get_file_hash(file_id, file_size=None):
    """إنشاء hash للملف للاستخدام في الـ cache"""
    hash_input = f"{file_id}_{file_size}" if file_size else file_id
    return hashlib.md5(hash_input.encode()).hexdigest()


def instant_delete_check(m):
    """فحص فوري للكلمات المفتاحية - حذف مباشر بدون انتظار"""
    if not m.caption and not (m.text):
        return False

    text_to_check = ""
    if m.caption:
        text_to_check += m.caption.lower()
    if m.text:
        text_to_check += " " + m.text.lower()

    # فحص سريع للكلمات المفتاحية
    for keyword in INSTANT_DELETE_KEYWORDS:
        if keyword in text_to_check:
            print(f"⚡ INSTANT DELETE: Keyword '{keyword}' detected")
            nsfw_stats["instant_deletes"] += 1
            nsfw_stats["total_processed"] += 1
            try:
                m.delete()
                if not r.get(f"{m.chat.id}:disableWarn:{Dev_Neptune}"):
                    k = r.get(f"{Dev_Neptune}:botkey") or "⇜"
                    m.reply(f"「 {m.from_user.mention} 」\n{k} تم حذف رسالتك فوراً لإحتوائها على محتوى إباحي .\n✔")
                return True
            except Exception as e:
                print(f"Error in instant delete: {e}")
                return False
    return False


def clean_cache():
    """تنظيف الـ cache عند امتلائه"""
    global nsfw_cache
    if len(nsfw_cache) > CACHE_SIZE_LIMIT:
        # حذف النصف الأول من الـ cache
        items_to_remove = len(nsfw_cache) // 2
        keys_to_remove = list(nsfw_cache.keys())[:items_to_remove]
        for key in keys_to_remove:
            del nsfw_cache[key]
        print(f"🧹 Cache cleaned: Removed {items_to_remove} entries")


list_UwU = [
    "كس",
    "كسمك",
    "كسختك",
    "عير",
    "كسخالتك",
    "خرا بالله",
    "عير بالله",
    "كسخواتكم",
    "كحاب",
    "مناويج",
    "مناويج",
    "كحبه",
    "ابن الكحبه",
    "فرخ",
    "فروخ",
    "طيزك",
    "طيزختك",
    "كسمك",
    "يا ابن الخول",
    "المتناك",
    "شرموط",
    "شرموطه",
    "ابن الشرموطه",
    "ابن الخول",
    "ابن العرص",
    "منايك",
    "متناك",
    "ابن المتناكه",
    "زبك",
    "عرص",
    "زبي",
    "خول",
    "لبوه",
    "لباوي",
    "ابن اللبوه",
    "منيوك",
    "كسمكك",
    "متناكه",
    "يا عرص",
    "يا خول",
    "قحبه",
    "القحبه",
    "شراميط",
    "العلق",
    "العلوق",
    "العلقه",
    "كسمك",
    "يا ابن الخول",
    "المتناك",
    "شرموط",
    "شرموطه",
    "ابن الشرموطه",
    "ابن الخول",
    "االمنيوك",
    "كسمككك",
    "الشرموطه",
    "ابن العرث",
    "ابن الحيضانه",
    "زبك",
    "خول",
    "زبي",
    "قاحب",
]

list_Shiaa = [
    "يا ابن عمر",
    "يا شمر",
    "ياعمر",
    "ياسمر",
    "عمر ولي الله",
    "عمر ابن الخطاب ولي الله",
    "خرب ربك",
    "خرب الله",
    "يلعن ربك",
    "يلعن الله",
    "يا عمر",
    "ياعمر",
    "يا محمد",
    "يامحمد",
    "زوجات الرسول",
    "عير بالسنة",
    "عير بالسنه",
    "خرب السنه",
    "خرا بالسنه",
    "خرب السنة",
    "خرا بالسنة",
    "والحسين",
    "والعباس",
    "وعلي",
    "والامام علي",
    "ربنا علي",
    "علي الله",
    "الله علي",
    "رب علي",
    "علي رب",
]


def Find(text):
    m = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(m, text)
    return [x[0] for x in url]


"""
         r.get(f'{m.chat.id}:mute:{Dev_Neptune}')
         r.get(f'{m.chat.id}:lockJoin:{Dev_Neptune}')
         r.get(f'{m.chat.id}:lockChannels:{Dev_Neptune}')
         r.get(f'{m.chat.id}:lockEdit:{Dev_Neptune}')
         r.get(f'{m.chat.id}:lockEditM:{Dev_Neptune}')
         r.get(f'{m.chat.id}:lockVoice:{Dev_Neptune}')
         r.get(f'{m.chat.id}:lockVideo:{Dev_Neptune}')
         r.get(f'{m.chat.id}:lockNot:{Dev_Neptune}')
         r.get(f'{m.chat.id}:lockPhoto:{Dev_Neptune}')
         r.get(f'{m.chat.id}:lockStickers:{Dev_Neptune}')
         r.get(f'{m.chat.id}:lockAnimations:{Dev_Neptune}')
         r.get(f'{m.chat.id}:lockFiles:{Dev_Neptune}')
         r.get(f'{m.chat.id}:lockPersian:{Dev_Neptune}')
         r.get(f'{m.chat.id}:lockUrls:{Dev_Neptune}')
         r.get(f'{m.chat.id}:lockHashtags:{Dev_Neptune}')
         r.get(f'{m.chat.id}:lockMessages:{Dev_Neptune}')
         r.get(f'{m.chat.id}:lockTags:{Dev_Neptune}')
         r.get(f'{m.chat.id}:lockBots:{Dev_Neptune}')
         r.get(f'{m.chat.id}:lockSpam:{Dev_Neptune}')
         r.get(f'{m.chat.id}:lockInline:{Dev_Neptune}')
         r.get(f'{m.chat.id}:lockForward:{Dev_Neptune}')
         r.get(f'{m.chat.id}:lockAudios:{Dev_Neptune}')
         r.get(f'{m.chat.id}:lockaddContacts:{Dev_Neptune}')
         r.get(f'{m.chat.id}:lockSHTM:{Dev_Neptune}')
"""

from pyrogram.errors import UserNotParticipant, FloodWait



@Client.on_message(filters.group, group=-1111111111111)
async def on_zbi(c: Client, m: Message):
    name = r.get(f"{Dev_Neptune}:BotName") if r.get(f"{Dev_Neptune}:BotName") else "جاك"
    text = m.text
    if text and text.startswith(f"{name} "):
        text = text.replace(f"{name} ", "")
    if r.get(f"{m.chat.id}:Custom:{m.chat.id}{Dev_Neptune}&text={text}"):
        text = r.get(f"{m.chat.id}:Custom:{m.chat.id}{Dev_Neptune}&text={text}")
    if r.get(f"Custom:{Dev_Neptune}&text={text}"):
        text = r.get(f"Custom:{Dev_Neptune}&text={text}")

    if r.get(f"inDontCheck:{Dev_Neptune}"):
        return m.continue_propagation()

    if dev_pls(m.from_user.id, m.chat.id):
        return




@Client.on_message(filters.group, group=27)
def guardLocksResponse(c, m):
    k = r.get(f"{Dev_Neptune}:botkey")
    channel = (
        r.get(f"{Dev_Neptune}:BotChannel") if r.get(f"{Dev_Neptune}:BotChannel") else "iJUCK"
    )
    Thread(target=guardResponseFunction, args=(c, m, k, channel)).start()


@Client.on_edited_message(filters.group, group=27)
def guardLocksResponse2(c, m):
    k = r.get(f"{Dev_Neptune}:botkey")
    channel = (
        r.get(f"{Dev_Neptune}:BotChannel") if r.get(f"{Dev_Neptune}:BotChannel") else "iJUCK"
    )
    Thread(target=guardResponseFunction2, args=(c, m, k, channel)).start()


def guardResponseFunction2(c, m, k, channel):
    if not r.get(f"{m.chat.id}:enable:{Dev_Neptune}"):
        return
    warner = """
「 {} 」
{} ممنوع {}
☆
"""
    warn = False
    reason = False

    if m.sender_chat:
        id = m.sender_chat.id
        mention = f"[{m.sender_chat.title}](t.me/{channel})"
    if m.from_user:
        id = m.from_user.id
        mention = m.from_user.mention

    if (
        r.get(f"{m.chat.id}:lockEdit:{Dev_Neptune}")
        and m.text
        and not pre_pls(id, m.chat.id)
    ):
        m.delete()
        warn = True
        reason = "التعديل"
        if not r.get(f"{m.chat.id}:disableWarn:{Dev_Neptune}") and not r.get(
            f"{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}"
        ):
            r.set(f"{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}", 1, ex=60)
            return m.reply(
                warner.format(mention, k, reason), disable_web_page_preview=True
            )

    if (
        r.get(f"{m.chat.id}:lockEditM:{Dev_Neptune}")
        and m.media
        and not pre_pls(id, m.chat.id)
    ):
        m.delete()
        warn = True
        reason = "تعديل الميديا"
        if not r.get(f"{m.chat.id}:disableWarn:{Dev_Neptune}") and not r.get(
            f"{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}"
        ):
            r.set(f"{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}", 1, ex=60)
            return m.reply(
                warner.format(mention, k, reason), disable_web_page_preview=True
            )


def guardResponseFunction(c, m, k, channel):
    if not r.get(f"{m.chat.id}:enable:{Dev_Neptune}"):
        return
    warner = """
「 {} 」
{} ممنوع {}
☆
"""
    warn = False
    reason = False

    if r.get(f"{m.chat.id}:lockNot:{Dev_Neptune}") and m.service:
        m.delete()

    if (
        r.get(f"{m.chat.id}:lockaddContacts:{Dev_Neptune}")
        and m.from_user
        and m.new_chat_members
    ):
        if pre_pls(m.from_user.id, m.chat.id):
            return
        for me in m.new_chat_members:
            if not me.id == m.from_user.id:
                warn = True
                mention = m.from_user.mention
                m.chat.ban_member(me.id)
                reason = "تضيف حد هنا"
                m.delete()
                if not r.get(f"{m.chat.id}:disableWarn:{Dev_Neptune}"):
                    return m.reply(
                        warner.format(mention, k, reason), disable_web_page_preview=True
                    )

    if m.sender_chat:
        id = m.sender_chat.id
        mention = f"[{m.sender_chat.title}](t.me/{channel})"
    if m.from_user:
        id = m.from_user.id
        mention = m.from_user.mention

    # print(id)

    if m.media:
        rep = m
        if rep.sticker:
            file_id = rep.sticker.file_id
        if rep.animation:
            file_id = rep.animation.file_id
        if rep.photo:
            file_id = rep.photo.file_id
        if rep.video:
            file_id = rep.video.file_id
        if rep.voice:
            file_id = rep.voice.file_id
        if rep.audio:
            file_id = rep.audio.file_id
        if rep.document:
            file_id = rep.document.file_id
        idd = file_id[-6:]
        if r.get(f"{idd}:NotAllow:{m.chat.id}{Dev_Neptune}"):
            if not admin_pls(id, m.chat.id):
                return m.delete()

    if m.text and r.smembers(f"{m.chat.id}:NotAllowedListText:{Dev_Neptune}"):
        if not admin_pls(id, m.chat.id):
            for word in r.smembers(f"{m.chat.id}:NotAllowedListText:{Dev_Neptune}"):
                if word in m.text:
                    return m.delete()

    # فحص الكتم مع استثناء لحالة إنشاء الحساب البنكي
    if r.get(f"{id}:mute:{m.chat.id}{Dev_Neptune}") or r.get(f"{id}:mute:{Dev_Neptune}"):
        # السماح بإنشاء الحساب البنكي حتى لو كان المستخدم مكتوم
        if not r.get(f'{id}:createBank:{m.chat.id}'):
            return False

    if r.get(f"{m.chat.id}:mute:{Dev_Neptune}") and not admin_pls(id, m.chat.id):
        m.delete()
        return False

    if pre_pls(id, m.chat.id):
        return False

    if r.get(f"{m.chat.id}:lockBots:{Dev_Neptune}") and m.new_chat_members:
        for mem in m.new_chat_members:
            if mem.is_bot:
                return m.chat.ban_member(mem.id)

    if r.get(f"{m.chat.id}:lockJoin:{Dev_Neptune}") and m.new_chat_members:
        for mem in m.new_chat_members:
            if not admin_pls(mem.id, m.chat.id):
                m.chat.ban_member(mem.id)
                m.chat.unban_member(mem.id)
                return False

    if r.get(f"{m.chat.id}:lockChannels:{Dev_Neptune}") and m.sender_chat:
        if not m.sender_chat.id == m.chat.id:
            m.chat.ban_member(m.sender_chat.id)
            return False

    if r.get(f"{m.chat.id}:lockSpam:{Dev_Neptune}"):
        if not r.get(f"{id}in_spam:{m.chat.id}{Dev_Neptune}"):
            r.set(f"{id}in_spam:{m.chat.id}{Dev_Neptune}", 1, ex=10)
        else:
            if int(r.get(f"{id}in_spam:{m.chat.id}{Dev_Neptune}")) == 10:
                if m.from_user:
                    r.set(f"{id}:mute:{m.chat.id}{Dev_Neptune}", 1)
                    r.sadd(f"{m.chat.id}:listMUTE:{Dev_Neptune}", id)
                    r.delete(f"{id}in_spam:{m.chat.id}{Dev_Neptune}")
                    return m.reply(
                        f"「 {mention} 」 \n{k} كتمتك يالبثر علمود تتعلم تكرر\n✔"
                    )

                if m.sender_chat:
                    m.chat.ban_member(m.sender_chat)
                    return m.reply(
                        f"「 {mention} 」 {k} حظرتك يالبثر علمود تتعلم تكرر\n✔"
                    )
            else:
                get = int(r.get(f"{id}in_spam:{m.chat.id}{Dev_Neptune}"))
                r.set(f"{id}in_spam:{m.chat.id}{Dev_Neptune}", get + 1, ex=10)

    if r.get(f"{m.chat.id}:lockInline:{Dev_Neptune}") and m.via_bot:
        m.delete()
        warn = True
        reason = "ترسل انلاين"
        if not r.get(f"{m.chat.id}:disableWarn:{Dev_Neptune}") and not r.get(
            f"{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}"
        ):
            r.set(f"{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}", 1, ex=60)
            return m.reply(
                warner.format(mention, k, reason), disable_web_page_preview=True
            )

    if r.get(f"{m.chat.id}:lockForward:{Dev_Neptune}") and m.forward_date:
        m.delete()
        warn = True
        reason = "ترسل توجيه"
        if not r.get(f"{m.chat.id}:disableWarn:{Dev_Neptune}") and not r.get(
            f"{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}"
        ):
            r.set(f"{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}", 1, ex=60)
            return m.reply(
                warner.format(mention, k, reason), disable_web_page_preview=True
            )

    """
  if r.get(f'{m.chat.id}:lockForward:{Dev_Neptune}') and m.forward_from_chat:
     m.delete()
     warn = True
     reason = 'ترسل توجيه'
     if not r.get(f'{m.chat.id}:disableWarn:{Dev_Neptune}') and not r.get(f'{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}'):
        r.set(f'{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}',1,ex=60)
        return m.reply(warner.format(mention,k,reason),disable_web_page_preview=True)
  """

    if r.get(f"{m.chat.id}:lockAudios:{Dev_Neptune}") and m.audio:
        m.delete()
        warn = True
        reason = "ترسل صوت"
        if not r.get(f"{m.chat.id}:disableWarn:{Dev_Neptune}") and not r.get(
            f"{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}"
        ):
            r.set(f"{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}", 1, ex=60)
            return m.reply(
                warner.format(mention, k, reason), disable_web_page_preview=True
            )

    if r.get(f"{m.chat.id}:lockVideo:{Dev_Neptune}") and m.video:
        m.delete()
        warn = True
        reason = "ترسل فيديوهات"
        if not r.get(f"{m.chat.id}:disableWarn:{Dev_Neptune}") and not r.get(
            f"{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}"
        ):
            r.set(f"{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}", 1, ex=60)
            return m.reply(
                warner.format(mention, k, reason), disable_web_page_preview=True
            )

    if r.get(f"{m.chat.id}:lockPhoto:{Dev_Neptune}") and m.photo:
        m.delete()
        warn = True
        reason = "ترسل صور"
        if not r.get(f"{m.chat.id}:disableWarn:{Dev_Neptune}") and not r.get(
            f"{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}"
        ):
            r.set(f"{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}", 1, ex=60)
            return m.reply(
                warner.format(mention, k, reason), disable_web_page_preview=True
            )

    if r.get(f"{m.chat.id}:lockStickers:{Dev_Neptune}") and m.sticker:
        m.delete()
        warn = True
        reason = "ترسل ملصقات"
        if not r.get(f"{m.chat.id}:disableWarn:{Dev_Neptune}") and not r.get(
            f"{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}"
        ):
            r.set(f"{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}", 1, ex=60)
            return m.reply(
                warner.format(mention, k, reason), disable_web_page_preview=True
            )

    if r.get(f"{m.chat.id}:lockAnimations:{Dev_Neptune}") and m.animation:
        m.delete()
        warn = True
        reason = "ترسل متحركات"
        if not r.get(f"{m.chat.id}:disableWarn:{Dev_Neptune}") and not r.get(
            f"{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}"
        ):
            r.set(f"{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}", 1, ex=60)
            return m.reply(
                warner.format(mention, k, reason), disable_web_page_preview=True
            )

    if r.get(f"{m.chat.id}:lockFiles:{Dev_Neptune}") and m.document:
        m.delete()
        warn = True
        reason = "ترسل ملفات"
        if not r.get(f"{m.chat.id}:disableWarn:{Dev_Neptune}") and not r.get(
            f"{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}"
        ):
            r.set(f"{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}", 1, ex=60)
            return m.reply(
                warner.format(mention, k, reason), disable_web_page_preview=True
            )

    if r.get(f"{m.chat.id}:lockPersian:{Dev_Neptune}") and m.text:
        if "ه‍" in m.text or "ی" in m.text or "ک" in m.text or "چ" in m.text:
            m.delete()
            warn = True
            reason = "ترسل فارسي"
            if not r.get(f"{m.chat.id}:disableWarn:{Dev_Neptune}"):
                return m.reply(
                    warner.format(mention, k, reason), disable_web_page_preview=True
                )

    if r.get(f"{m.chat.id}:lockPersian:{Dev_Neptune}") and m.caption:
        if "ه‍" in m.caption or "ی" in m.caption or "ک" in m.caption or "چ" in m.caption:
            m.delete()
            warn = True
            reason = "ترسل فارسي"
            if not r.get(f"{m.chat.id}:disableWarn:{Dev_Neptune}"):
                return m.reply(
                    warner.format(mention, k, reason), disable_web_page_preview=True
                )

    if (
        r.get(f"{m.chat.id}:lockUrls:{Dev_Neptune}")
        and m.text
        and len(Find(m.text.html)) > 0
    ):
        m.delete()
        warn = True
        reason = "ترسل روابط"
        if not r.get(f"{m.chat.id}:disableWarn:{Dev_Neptune}") and not r.get(
            f"{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}"
        ):
            r.set(f"{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}", 1, ex=60)
            return m.reply(
                warner.format(mention, k, reason), disable_web_page_preview=True
            )

    if (
        r.get(f"{m.chat.id}:lockHashtags:{Dev_Neptune}")
        and m.text
        and len(re.findall(r"#(\w+)", m.text)) > 0
    ):
        m.delete()
        warn = True
        reason = "ترسل هاشتاق"
        if not r.get(f"{m.chat.id}:disableWarn:{Dev_Neptune}") and not r.get(
            f"{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}"
        ):
            r.set(f"{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}", 1, ex=60)
            return m.reply(
                warner.format(mention, k, reason), disable_web_page_preview=True
            )

    if r.get(f"{m.chat.id}:lockMessages:{Dev_Neptune}") and m.text and len(m.text) > 150:
        m.delete()
        warn = True
        reason = "ترسل كلام كثير"
        if not r.get(f"{m.chat.id}:disableWarn:{Dev_Neptune}") and not r.get(
            f"{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}"
        ):
            r.set(f"{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}", 1, ex=60)
            return m.reply(
                warner.format(mention, k, reason), disable_web_page_preview=True
            )

    if r.get(f"{m.chat.id}:lockVoice:{Dev_Neptune}") and m.voice:
        m.delete()
        warn = True
        reason = "ترسل فويس"
        if not r.get(f"{m.chat.id}:disableWarn:{Dev_Neptune}") and not r.get(
            f"{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}"
        ):
            r.set(f"{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}", 1, ex=60)
            return m.reply(
                warner.format(mention, k, reason), disable_web_page_preview=True
            )

    if r.get(
        f"{m.chat.id}:lockTags:{Dev_Neptune}"
    ) and '"type": "MessageEntityType.MENTION"' in str(m):
        m.delete()
        warn = True
        reason = "ترسل منشنات"
        if not r.get(f"{m.chat.id}:disableWarn:{Dev_Neptune}") and not r.get(
            f"{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}"
        ):
            r.set(f"{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}", 1, ex=60)
            return m.reply(
                warner.format(mention, k, reason), disable_web_page_preview=True
            )

    if r.get(f"{m.chat.id}:lockSHTM:{Dev_Neptune}") and (m.caption or m.text):
        if m.caption:
            txt = m.caption
        if m.text:
            txt = m.text
        for a in list_UwU:
            if txt == a or f" {a} " in txt or a in txt:
                m.delete()
                warn = True
                reason = "السب هنا"
                if not r.get(f"{m.chat.id}:disableWarn:{Dev_Neptune}") and not r.get(
                    f"{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}"
                ):
                    r.set(f"{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}", 1, ex=60)
                    return m.reply(
                        warner.format(mention, k, reason), disable_web_page_preview=True
                    )

    """
  if r.get(f'{m.chat.id}:lockKFR:{Dev_Neptune}') and (m.caption or m.text):
     if m.caption:
         txt = m.caption.replace("*","").replace("`","").replace("|","").replace("#","").replace("<","").replace(">","").replace("_","").replace("ـ","").replace("َ","").replace("ٕ","").replace("ُ","").replace("ِ","").replace("ٰ","").replace("ٖ","").replace("ً","").replace("ّ","").replace("ٌ","").replace("ٍ","").replace("ْ","").replace("ٔ","").replace("'","").replace('"',"")
     if m.text:
         txt = m.text.replace("*","").replace("`","").replace("|","").replace("#","").replace("<","").replace(">","").replace("_","").replace("ـ","").replace("َ","").replace("ٕ","").replace("ُ","").replace("ِ","").replace("ٰ","").replace("ٖ","").replace("ً","").replace("ّ","").replace("ٌ","").replace("ٍ","").replace("ْ","").replace("ٔ","").replace("'","").replace('"',"")
     for kfr in list_Shiaa:
         if kfr in txt:
            m.delete()
            warn = True
            reason = 'الكفر هنا'
            if not r.get(f'{m.chat.id}:disableWarn:{Dev_Neptune}') and not r.get(f'{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}'):
                 r.set(f'{Dev_Neptune}:inWARN:{m.from_user.id}{m.chat.id}',1,ex=60)
                 return m.reply(warner.format(mention,k,reason),disable_web_page_preview=True)
  """

    if r.get(f"{m.chat.id}:lockJoinPersian:{Dev_Neptune}") and m.new_chat_members:
        if m.from_user.first_name:
            if (
                m.from_user.first_name in persianInformation["names"]
                or m.from_user.id in persianInformation["ids"]
                or "ه‍" in m.from_user.first_name
                or "ی" in m.from_user.first_name
                or "ک" in m.from_user.first_name
                or "چ" in m.from_user.first_name
                or "👙" in m.from_user.first_name
            ) and not pre_pls(m.from_user.id, m.chat.id):
                if not r.get(f"{m.chat.id}:disableWarn:{Dev_Neptune}"):
                    m.reply(
                        """
「 {} 」
{} تم حظره لاشتباهه ببوت إيراني
☆
""".format(m.from_user.mention, k)
                    )
                return c.ban_chat_member(m.chat.id, m.from_user.id)

        if m.from_user.last_name:
            if (
                m.from_user.last_name in persianInformation["last_names"]
                or m.from_user.id in persianInformation["ids"]
                or "ه‍" in m.from_user.last_name
                or "ی" in m.from_user.last_name
                or "ک" in m.from_user.last_name
                or "چ" in m.from_user.last_name
                or "👙" in m.from_user.last_name
            ) and not pre_pls(m.from_user.id, m.chat.id):
                if not r.get(f"{m.chat.id}:disableWarn:{Dev_Neptune}"):
                    m.reply(
                        """
「 {} 」
{} تم حظره لاشتباهه ببوت إيراني
☆
""".format(m.from_user.mention, k)
                    )
                return c.ban_chat_member(m.chat.id, m.from_user.id)

    if r.get(f"{m.chat.id}:enableVerify:{Dev_Neptune}") and m.new_chat_members:
        for me in m.new_chat_members:
            if not pre_pls(me.id, m.chat.id):
                c.restrict_chat_member(
                    m.chat.id, me.id, ChatPermissions(can_send_messages=False)
                )
                get_random = get_for_verify(me)
                question = get_random["question"]
                reply_markup = get_random["key"]
                return m.reply(
                    f"{k} قيدناك علمود نتاكد انك شخص حقيقي مو زومبي\n\n{question}",
                    reply_markup=reply_markup,
                )

    # فحص المحتوى الإباحي - محسن للسرعة القصوى
    if r.get(f"{m.chat.id}:lockNSFW:{Dev_Neptune}"):
        # فحص المحتوى الإباحي لجميع المستخدمين عدا المالك الأساسي وما فوق فقط
        if not gowner_pls(id, m.chat.id):
            print("🔍 NSFW Scanner - Fast Mode")

            # الخطوة 1: فحص فوري للكلمات المفتاحية (أسرع طريقة)
            if instant_delete_check(m):
                return  # تم الحذف فوراً

            # الخطوة 2: فحص الوسائط بطريقة محسنة
            if m.media:
                file_id = None
                file_size = None

                try:
                    # تحديد نوع الملف والحصول على معرفه
                    if m.photo:
                        file_id = m.photo.file_id
                        file_size = m.photo.file_size
                    elif m.sticker:
                        # للملصقات: استخدام thumbnail للسرعة
                        if hasattr(m.sticker, 'thumbs') and m.sticker.thumbs:
                            file_id = m.sticker.thumbs[0].file_id
                            file_size = m.sticker.thumbs[0].file_size
                        else:
                            file_id = m.sticker.file_id
                            file_size = m.sticker.file_size
                    elif m.video:
                        # للفيديو: استخدام thumbnail فقط للسرعة
                        if hasattr(m.video, 'thumbs') and m.video.thumbs:
                            file_id = m.video.thumbs[0].file_id
                            file_size = m.video.thumbs[0].file_size
                    elif m.animation:
                        # للمتحركات: استخدام thumbnail فقط للسرعة
                        if hasattr(m.animation, 'thumbs') and m.animation.thumbs:
                            file_id = m.animation.thumbs[0].file_id
                            file_size = m.animation.thumbs[0].file_size
                    elif m.document and m.document.mime_type and m.document.mime_type.startswith('image/'):
                        file_id = m.document.file_id
                        file_size = m.document.file_size

                    if file_id:
                        # فحص الـ cache أولاً
                        file_hash = get_file_hash(file_id, file_size)
                        if file_hash in nsfw_cache:
                            cached_result = nsfw_cache[file_hash]
                            print(f"⚡ Cache hit: {cached_result}")
                            nsfw_stats["cache_hits"] += 1
                            nsfw_stats["total_processed"] += 1
                            if cached_result == "NSFW":
                                print("🚫 Cached NSFW content - deleting immediately")
                                m.delete()
                                if not r.get(f"{m.chat.id}:disableWarn:{Dev_Neptune}"):
                                    k = r.get(f"{Dev_Neptune}:botkey") or "⇜"
                                    m.reply(f"「 {m.from_user.mention} 」\n{k} تم حذف رسالتك لإحتوائها على محتوى إباحي .\n✔")
                                return
                            elif cached_result == "SAFE":
                                print("✅ Cached safe content - skipping scan")
                                return

                        # إذا لم يكن في الـ cache، قم بالفحص باستخدام ThreadPool
                        print(f"🔍 Scanning new file: {file_id}")
                        nsfw_executor.submit(fast_scan_media, c, m, file_id, file_hash)

                except Exception as e:
                    print(f"❌ Error in fast NSFW scanning: {e}")
                    # فحص طارئ في حالة الفشل
                    emergencyNSFWCheck(c, m)

    # فحص سريع للإيموجي المميز الإباحي
    if m.entities and r.get(f"{m.chat.id}:lockNSFW:{Dev_Neptune}"):
        if not gowner_pls(id, m.chat.id):
            for entity in m.entities:
                if hasattr(entity, 'type') and str(entity.type) == 'MessageEntityType.CUSTOM_EMOJI':
                    if hasattr(entity, 'custom_emoji_id'):
                        emoji_id = entity.custom_emoji_id
                        # فحص فوري للإيموجي باستخدام ThreadPool
                        nsfw_executor.submit(checkCustomEmoji, c, m, emoji_id)
                    break


def fast_scan_media(c, m, file_id, file_hash):
    """فحص سريع للوسائط باستخدام ThreadPool"""
    try:
        # تحميل الملف بأصغر حجم ممكن للسرعة
        file_path = c.download_media(file_id)
        if file_path:
            # تشغيل الفحص async
            RUN(ultra_fast_scan(c, m, file_id, file_path, file_hash))
        else:
            print("❌ Failed to download media for fast scan")
            # إضافة إلى الـ cache كـ safe في حالة فشل التحميل
            nsfw_cache[file_hash] = "SAFE"
            clean_cache()
    except Exception as e:
        print(f"❌ Error in fast_scan_media: {e}")


def scanR(c, m, id, file):
    """الدالة القديمة - محتفظ بها للتوافق"""
    RUN(scan4(c, m, id, file))


async def ultra_fast_scan(c, m, file_id, file_path, file_hash):
    """فحص محسن للغاية - أسرع من الطريقة القديمة"""
    session = ClientSession()
    try:
        print(f"⚡ Ultra fast scan starting for: {file_id}")

        # إنشاء ARQ session
        arq = ARQ(ARQ_API_URL, ARQ_API_KEY, session)

        # فحص الملف مباشرة
        if file_path and os.path.exists(file_path):
            resp = await arq.nsfw_scan(file=file_path)

            if resp and hasattr(resp, 'result') and resp.result:
                print(f"⚡ Fast scan result received")

                # فحص سريع ومباشر
                is_nsfw = False

                # فحص is_nsfw المباشر
                if hasattr(resp.result, 'is_nsfw') and resp.result.is_nsfw:
                    is_nsfw = True
                    print("🚫 Direct NSFW detection")

                # فحص النسب بطريقة محسنة
                elif hasattr(resp.result, 'nsfw_score'):
                    nsfw_score = float(resp.result.nsfw_score)
                    if nsfw_score > 0.003:  # أكثر صرامة
                        is_nsfw = True
                        print(f"🚫 NSFW score: {nsfw_score}")

                # فحص سريع للخصائص الأخرى
                else:
                    suspicious_score = 0
                    if hasattr(resp.result, 'porn'):
                        suspicious_score += float(resp.result.porn)
                    if hasattr(resp.result, 'sexy'):
                        suspicious_score += float(resp.result.sexy) * 0.5
                    if hasattr(resp.result, 'hentai'):
                        suspicious_score += float(resp.result.hentai)

                    if suspicious_score > 0.02:  # حد أكثر صرامة
                        is_nsfw = True
                        print(f"🚫 Combined suspicious score: {suspicious_score}")

                # تنفيذ الإجراء
                if is_nsfw:
                    print("🚫 NSFW content detected - deleting immediately")
                    nsfw_cache[file_hash] = "NSFW"
                    nsfw_stats["total_processed"] += 1
                    try:
                        await m.delete()
                        if not r.get(f"{m.chat.id}:disableWarn:{Dev_Neptune}"):
                            k = r.get(f"{Dev_Neptune}:botkey") or "⇜"
                            await m.reply(f"「 {m.from_user.mention} 」\n{k} تم حذف رسالتك لإحتوائها على محتوى إباحي .\n✔")
                    except Exception as e:
                        print(f"❌ Error deleting NSFW message: {e}")
                else:
                    print("✅ Content is safe")
                    nsfw_cache[file_hash] = "SAFE"
                    nsfw_stats["total_processed"] += 1

                clean_cache()
            else:
                print("❌ No valid scan result")
                nsfw_cache[file_hash] = "SAFE"
        else:
            print("❌ File not found for ultra fast scan")
            nsfw_cache[file_hash] = "SAFE"

    except Exception as e:
        print(f"❌ Error in ultra fast scan: {e}")
        nsfw_cache[file_hash] = "SAFE"
    finally:
        # تنظيف سريع
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
        try:
            await session.close()
        except:
            pass


async def scan4(c, m, id, file):
    """الدالة القديمة - محتفظ بها للتوافق"""
    session = ClientSession()
    try:
        # فحص فوري للكلمات المفتاحية في النص المرفق قبل أي شيء آخر
        if m.caption:
            nsfw_keywords = ['porn', 'sex', 'nude', 'naked', 'xxx', 'adult', 'nsfw', 'explicit', 'hot', 'sexy', 'erotic', 'boobs', 'ass', 'dick', 'pussy', 'fuck', 'shit']
            text_lower = m.caption.lower()
            for keyword in nsfw_keywords:
                if keyword in text_lower:
                    print(f"IMMEDIATE NSFW keyword detected in caption: {keyword}")
                    try:
                        await m.delete()
                        k = r.get(f"{Dev_Neptune}:botkey") or "⇜"
                        await m.reply(
                            f"「 {m.from_user.mention} 」\n{k} تم حذف رسالتك لإحتوائها على محتوى إباحي .\n✔"
                        )
                        return
                    except Exception as e:
                        print(f"Error deleting message with NSFW keyword: {e}")

        arq = ARQ(ARQ_API_URL, ARQ_API_KEY, session)
        print(f"Starting NSFW scan for file: {file}")

        # محاولة فحص الملف
        if file and os.path.exists(file):
            resp = await arq.nsfw_scan(file=file)
        else:
            print("File not found, skipping NSFW scan")
            return

        if resp and hasattr(resp, 'result') and resp.result:
            print(f"NSFW scan result: {resp.result}")

            # طباعة تفاصيل أكثر للتشخيص
            print(f"Result type: {type(resp.result)}")
            if hasattr(resp.result, '__dict__'):
                print(f"Result attributes: {vars(resp.result)}")
            else:
                print(f"Result dir: {dir(resp.result)}")

            # فحص أكثر صرامة - نقبل حتى الاحتمالية المنخفضة
            if hasattr(resp.result, 'is_nsfw') and resp.result.is_nsfw:
                print("Content detected as NSFW - deleting")
                try:
                    await m.delete()
                    k = r.get(f"{Dev_Neptune}:botkey") or "⇜"
                    await m.reply(
                        f"「 {m.from_user.mention} 」\n{k} تم حذف رسالتك لإحتوائها على محتوى إباحي .\n✔"
                    )
                except Exception as e:
                    print(f"Error deleting NSFW message: {e}")
                return  # إنهاء الفحص هنا

            # فحص إضافي للنسب المئوية إذا كانت متوفرة
            elif hasattr(resp.result, 'nsfw_score'):
                nsfw_score = float(resp.result.nsfw_score)
                print(f"NSFW score: {nsfw_score}")

                # إذا كانت النسبة أعلى من 0.5% نعتبرها إباحية (أكثر صرامة جداً)
                if nsfw_score > 0.005:
                    print("Content detected as NSFW based on score - deleting")
                    try:
                        await m.delete()
                        k = r.get(f"{Dev_Neptune}:botkey") or "⇜"
                        await m.reply(
                            f"「 {m.from_user.mention} 」\n{k} تم حذف رسالتك لإحتوائها على محتوى إباحي .\n✔"
                        )
                    except Exception as e:
                        print(f"Error deleting NSFW message: {e}")
                else:
                    print(f"Content is safe - NSFW score: {nsfw_score}")

            # فحص إضافي للخصائص الأخرى
            elif hasattr(resp.result, 'neutral') and hasattr(resp.result, 'porn'):
                if hasattr(resp.result, 'porn') and resp.result.porn > 0.03:
                    print("Content detected as pornographic - deleting")
                    try:
                        await m.delete()
                        k = r.get(f"{Dev_Neptune}:botkey") or "⇜"
                        await m.reply(
                            f"「 {m.from_user.mention} 」\n{k} تم حذف رسالتك لإحتوائها على محتوى إباحي .\n✔"
                        )
                    except Exception as e:
                        print(f"Error deleting NSFW message: {e}")
                else:
                    print("Content appears to be safe")

            # فحص شامل لجميع الخصائص المتاحة
            else:
                should_delete = False
                delete_reason = ""

                # طباعة جميع الخصائص المتاحة للتشخيص
                print(f"Available attributes: {dir(resp.result)}")
                if hasattr(resp.result, '__dict__'):
                    print(f"All values: {vars(resp.result)}")

                # فحص sexy
                if hasattr(resp.result, 'sexy'):
                    sexy_score = float(resp.result.sexy)
                    print(f"Sexy score: {sexy_score}")
                    if sexy_score > 0.05:  # أكثر صرامة
                        should_delete = True
                        delete_reason = "Sexy content"

                # فحص hentai
                if hasattr(resp.result, 'hentai'):
                    hentai_score = float(resp.result.hentai)
                    print(f"Hentai score: {hentai_score}")
                    if hentai_score > 0.01:  # أكثر صرامة
                        should_delete = True
                        delete_reason = "Hentai content"

                # فحص porn
                if hasattr(resp.result, 'porn'):
                    porn_score = float(resp.result.porn)
                    print(f"Porn score: {porn_score}")
                    if porn_score > 0.01:  # أكثر صرامة
                        should_delete = True
                        delete_reason = "Pornographic content"

                # فحص drawings مع فحص إضافي
                if hasattr(resp.result, 'drawings'):
                    drawings_score = float(resp.result.drawings)
                    print(f"Drawings score: {drawings_score}")
                    if drawings_score > 0.2:
                        # فحص إضافي للرسوم المشبوهة
                        if (hasattr(resp.result, 'sexy') and float(resp.result.sexy) > 0.05) or \
                           (hasattr(resp.result, 'porn') and float(resp.result.porn) > 0.01) or \
                           (hasattr(resp.result, 'hentai') and float(resp.result.hentai) > 0.01):
                            should_delete = True
                            delete_reason = "Suspicious drawing"

                # فحص إضافي للمحتوى المشبوه حتى بنسب منخفضة
                if not should_delete:
                    total_suspicious_score = 0
                    if hasattr(resp.result, 'sexy'):
                        total_suspicious_score += float(resp.result.sexy)
                    if hasattr(resp.result, 'porn'):
                        total_suspicious_score += float(resp.result.porn)
                    if hasattr(resp.result, 'hentai'):
                        total_suspicious_score += float(resp.result.hentai)

                    print(f"Total suspicious score: {total_suspicious_score}")
                    if total_suspicious_score > 0.05:  # مجموع النسب المشبوهة (أكثر صرامة)
                        should_delete = True
                        delete_reason = "Combined suspicious content"

                if should_delete:
                    print(f"Content detected as inappropriate ({delete_reason}) - deleting")
                    try:
                        await m.delete()
                        k = r.get(f"{Dev_Neptune}:botkey") or "⇜"
                        await m.reply(
                            f"「 {m.from_user.mention} 」\n{k} تم حذف رسالتك لإحتوائها على محتوى إباحي .\n✔"
                        )
                    except Exception as e:
                        print(f"Error deleting NSFW message: {e}")
                else:
                    print("Content appears to be safe")
        else:
            print("Failed to get valid NSFW scan result")

        # فحص إضافي للكلمات المفتاحية الإباحية في النص
        if m.caption:
            nsfw_keywords = ['porn', 'sex', 'nude', 'naked', 'xxx', 'adult', 'nsfw', 'explicit', 'hot', 'sexy', 'erotic']
            text_lower = m.caption.lower()
            for keyword in nsfw_keywords:
                if keyword in text_lower:
                    print(f"NSFW keyword detected in caption: {keyword}")
                    try:
                        await m.delete()
                        k = r.get(f"{Dev_Neptune}:botkey") or "⇜"
                        await m.reply(
                            f"「 {m.from_user.mention} 」\n{k} تم حذف رسالتك لإحتوائها على محتوى إباحي .\n✔"
                        )
                        return
                    except Exception as e:
                        print(f"Error deleting message with NSFW keyword: {e}")

    except Exception as e:
        print(f"Error during NSFW scanning: {e}")
    finally:
        # تنظيف الملف المؤقت
        try:
            if file and os.path.exists(file):
                os.remove(file)
                print(f"Cleaned up temporary file: {file}")
        except Exception as e:
            print(f"Error removing temporary file: {e}")

        # إغلاق الجلسة
        try:
            await session.close()
        except Exception as e:
            print(f"Error closing session: {e}")


def emergencyNSFWCheck(c, m):
    """فحص طارئ محسن للمحتوى الإباحي - أسرع وأكثر شمولية"""
    try:
        print("🚨 Emergency NSFW check activated")

        # فحص النص المرفق والرسالة
        text_to_check = ""
        if m.caption:
            text_to_check += m.caption.lower()
        if m.text:
            text_to_check += " " + m.text.lower()

        if text_to_check:
            for keyword in INSTANT_DELETE_KEYWORDS:
                if keyword in text_to_check:
                    print(f"🚨 Emergency keyword detected: {keyword}")
                    m.delete()
                    if not r.get(f"{m.chat.id}:disableWarn:{Dev_Neptune}"):
                        k = r.get(f"{Dev_Neptune}:botkey") or "⇜"
                        m.reply(f"「 {m.from_user.mention} 」\n{k} تم حذف رسالتك لإحتوائها على محتوى مشبوه .\n✔")
                    return True

        # فحص اسم الملف
        if m.document and m.document.file_name:
            filename_lower = m.document.file_name.lower()
            for keyword in INSTANT_DELETE_KEYWORDS:
                if keyword in filename_lower:
                    print(f"🚨 Emergency filename detection: {keyword}")
                    m.delete()
                    if not r.get(f"{m.chat.id}:disableWarn:{Dev_Neptune}"):
                        k = r.get(f"{Dev_Neptune}:botkey") or "⇜"
                        m.reply(f"「 {m.from_user.mention} 」\n{k} تم حذف رسالتك لإحتوائها على محتوى مشبوه .\n✔")
                    return True

        # فحص إضافي للصور الكبيرة المشبوهة
        if m.photo and m.photo.file_size and m.photo.file_size > 2 * 1024 * 1024:  # أكبر من 2 ميجا
            print("🚨 Large suspicious image detected")
            if text_to_check and any(word in text_to_check for word in ['pic', 'photo', 'image', 'صورة', 'صوره', 'بيك']):
                print("🚨 Large image with suspicious text - emergency delete")
                m.delete()
                if not r.get(f"{m.chat.id}:disableWarn:{Dev_Neptune}"):
                    k = r.get(f"{Dev_Neptune}:botkey") or "⇜"
                    m.reply(f"「 {m.from_user.mention} 」\n{k} تم حذف رسالتك لإحتوائها على صورة مشبوهة .\n✔")
                return True

        return False

    except Exception as e:
        print(f"❌ Error in emergency NSFW check: {e}")
        return False


def checkCustomEmoji(c, m, emoji_id):
    """فحص محسن للإيموجي المميز للمحتوى الإباحي"""
    try:
        print(f"🔍 Checking custom emoji: {emoji_id}")

        # فحص معرف الإيموجي باستخدام القائمة المحسنة
        emoji_str = str(emoji_id).lower()
        for keyword in INSTANT_DELETE_KEYWORDS:
            if keyword in emoji_str:
                print(f"🚫 NSFW emoji detected: {keyword}")
                m.delete()
                if not r.get(f"{m.chat.id}:disableWarn:{Dev_Neptune}"):
                    k = r.get(f"{Dev_Neptune}:botkey") or "⇜"
                    m.reply(f"「 {m.from_user.mention} 」\n{k} تم حذف رسالتك لإحتوائها على إيموجي إباحي .\n✔")
                return

    except Exception as e:
        print(f"❌ Error checking custom emoji: {e}")


def cleanup_nsfw_resources():
    """تنظيف موارد فحص المحتوى الإباحي عند إغلاق البرنامج"""
    try:
        print("🧹 Cleaning up NSFW scanner resources...")
        nsfw_executor.shutdown(wait=True)
        nsfw_cache.clear()
        print("✅ NSFW scanner cleanup completed")
    except Exception as e:
        print(f"❌ Error during NSFW cleanup: {e}")


# تسجيل دالة التنظيف لتعمل عند إغلاق البرنامج
import atexit
atexit.register(cleanup_nsfw_resources)


def get_for_verify(me):
    for_verify = [
        {
            "question": "ماهو الحيوان الذي ينتهي اسمه بحرف الباء ؟",
            "key": InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("فأر", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("شنوق", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("بشار الأسد", callback_data=f"no:{me.id}"),
                    ],
                    [
                        InlineKeyboardButton("حمار", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("كلب", callback_data=f"yes:{me.id}"),
                        InlineKeyboardButton("قطة", callback_data=f"no:{me.id}"),
                    ],
                ]
            ),
        },
        {
            "question": "ماهي عاصمة فرنسا؟",
            "key": InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("دمشق", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("الرياض", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("باريس", callback_data=f"yes:{me.id}"),
                    ],
                    [
                        InlineKeyboardButton("الكويت", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("القاهرة", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("ماشا والدب", callback_data=f"no:{me.id}"),
                    ],
                ]
            ),
        },
        {
            "question": "نادي يبدأ بحرف الباء :",
            "key": InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("برشلونا", callback_data=f"yes:{me.id}"),
                        InlineKeyboardButton("الهلال", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("النصر", callback_data=f"no:{me.id}"),
                    ],
                    [
                        InlineKeyboardButton("الزمالك", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("دينار عراقي مدريد", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("مانشستر", callback_data=f"no:{me.id}"),
                    ],
                ]
            ),
        },
        {
            "question": "دولة يبدأ اسمها بحرف التاء :",
            "key": InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("قطر", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("امريكا", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("سوريا", callback_data=f"no:{me.id}"),
                    ],
                    [
                        InlineKeyboardButton("مصر", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("الصين", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("تركيا", callback_data=f"yes:{me.id}"),
                    ],
                ]
            ),
        },
        {
            "question": "اختر هذا الايموجي - 🤑 -",
            "key": InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🍭", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("🤑", callback_data=f"yes:{me.id}"),
                        InlineKeyboardButton("🏆", callback_data=f"no:{me.id}"),
                    ],
                    [
                        InlineKeyboardButton("🌀", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("🪨", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("💎", callback_data=f"no:{me.id}"),
                    ],
                ]
            ),
        },
        {
            "question": "اختر هذا الايموجي - 🔓 -",
            "key": InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🏆", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("💎", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("🙄", callback_data=f"no:{me.id}"),
                    ],
                    [
                        InlineKeyboardButton("💸", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("💣", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("🔓", callback_data=f"yes:{me.id}"),
                    ],
                ]
            ),
        },
        {
            "question": "اختر هذا الايموجي - 🌠 -",
            "key": InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("☄️", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("🙈", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("🦄", callback_data=f"no:{me.id}"),
                    ],
                    [
                        InlineKeyboardButton("🌠", callback_data=f"yes:{me.id}"),
                        InlineKeyboardButton("🌈", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("🧑‍💻", callback_data=f"no:{me.id}"),
                    ],
                ]
            ),
        },
        {
            "question": "ماهي عاصمة سوريا",
            "key": InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("دمشق", callback_data=f"yes:{me.id}"),
                        InlineKeyboardButton("دير الزور", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("ادلب", callback_data=f"no:{me.id}"),
                    ],
                    [
                        InlineKeyboardButton("ليو ميسي", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("الرياض", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("مزة فيلات", callback_data=f"no:{me.id}"),
                    ],
                ]
            ),
        },
        {
            "question": "ماهي عملة الولايات المتحدة الأمريكية",
            "key": InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("الروبية", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("الجنيه", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("الليرة", callback_data=f"no:{me.id}"),
                    ],
                    [
                        InlineKeyboardButton("الدولار", callback_data=f"yes:{me.id}"),
                        InlineKeyboardButton("الدينار", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("الين", callback_data=f"no:{me.id}"),
                    ],
                ]
            ),
        },
        {
            "question": "اسم مذكر يبدأ بحرف ز",
            "key": InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("زيد", callback_data=f"yes:{me.id}"),
                        InlineKeyboardButton("علي", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("محمد", callback_data=f"no:{me.id}"),
                    ],
                    [
                        InlineKeyboardButton("عمر", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("المريخ", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("احمد", callback_data=f"no:{me.id}"),
                    ],
                ]
            ),
        },
        {
            "question": "اسم مؤنث ينتهي بحرف ي",
            "key": InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("لورين", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("ماجدة", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("علياء", callback_data=f"no:{me.id}"),
                    ],
                    [
                        InlineKeyboardButton("أماني", callback_data=f"yes:{me.id}"),
                        InlineKeyboardButton("فرح", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("أمل", callback_data=f"no:{me.id}"),
                    ],
                ]
            ),
        },
        {
            "question": "اسم مؤنث يبدأ بحرف أ",
            "key": InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("لورين", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("ماجدة", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("علياء", callback_data=f"no:{me.id}"),
                    ],
                    [
                        InlineKeyboardButton("أمل", callback_data=f"yes:{me.id}"),
                        InlineKeyboardButton("فرح", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("يمنى", callback_data=f"no:{me.id}"),
                    ],
                ]
            ),
        },
        {
            "question": "الأسبوع كم يوم؟",
            "key": InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("1", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("2", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("3", callback_data=f"no:{me.id}"),
                    ],
                    [
                        InlineKeyboardButton("4", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("5", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("6", callback_data=f"no:{me.id}"),
                    ],
                    [
                        InlineKeyboardButton("7", callback_data=f"yes:{me.id}"),
                        InlineKeyboardButton("8", callback_data=f"no:{me.id}"),
                        InlineKeyboardButton("9", callback_data=f"no:{me.id}"),
                    ],
                ]
            ),
        },
    ]
    return random.choice(for_verify)


@Client.on_chat_join_request(filters.group, group=100)
def antiPersian(c, m):
    if r.get(f"{m.chat.id}:lockJoinPersian:{Dev_Neptune}"):
        k = r.get(f"{Dev_Neptune}:botkey")
        if not pre_pls(m.from_user.id, m.chat.id):
            if m.from_user.first_name:
                if (
                    m.from_user.first_name in persianInformation["names"]
                    or m.from_user.id in persianInformation["ids"]
                    or "ه‍" in m.from_user.first_name
                    or "ی" in m.from_user.first_name
                    or "ک" in m.from_user.first_name
                    or "چ" in m.from_user.first_name
                    or "👙" in m.from_user.first_name
                ):
                    c.decline_chat_join_request(m.chat.id, m.from_user.id)
                    if not r.get(f"{m.chat.id}:disableWarn:{Dev_Neptune}"):
                        c.send_message(
                            m.chat.id,
                            """
「 {} 」
{} تم رفض طلب انضمامه لاشتباهه ببوت إيراني
☆
""".format(m.from_user.mention, k),
                        )
                    return True
            if m.from_user.last_name:
                if (
                    m.from_user.last_name in persianInformation["last_names"]
                    or m.from_user.id in persianInformation["ids"]
                    or "ه‍" in m.from_user.last_name
                    or "ی" in m.from_user.last_name
                    or "ک" in m.from_user.last_name
                    or "چ" in m.from_user.last_name
                    or "👙" in m.from_user.last_name
                ):
                    c.decline_chat_join_request(m.chat.id, m.from_user.id)
                    if not r.get(f"{m.chat.id}:disableWarn:{Dev_Neptune}"):
                        c.send_message(
                            m.chat.id,
                            """
「 {} 」
{} تم رفض طلب انضمامه لاشتباهه ببوت إيراني
☆
""".format(m.from_user.mention, k),
                        )
                    return True


@Client.on_message(filters.group & filters.text, group=28)
def guardCommandsHandler(c, m):
    k = r.get(f"{Dev_Neptune}:botkey")
    channel = (
        r.get(f"{Dev_Neptune}:BotChannel") if r.get(f"{Dev_Neptune}:BotChannel") else "iJUCK"
    )
    Thread(target=guardCommands, args=(c, m, k, channel)).start()


def guardCommands(c, m, k, channel):
    if not r.get(f"{m.chat.id}:enable:{Dev_Neptune}"):
        return False
    if r.get(f"{m.chat.id}:mute:{Dev_Neptune}") and not admin_pls(
        m.from_user.id, m.chat.id
    ):
        return False
    if r.get(f"{m.from_user.id}:mute:{m.chat.id}{Dev_Neptune}"):
        return False
    if r.get(f"{m.from_user.id}:mute:{Dev_Neptune}"):
        return False
    if r.get(f"{m.chat.id}:addCustom:{m.from_user.id}{Dev_Neptune}"):
        return False
    if r.get(f"{m.chat.id}addCustomG:{m.from_user.id}{Dev_Neptune}"):
        return False
    if r.get(f"{m.chat.id}:delCustom:{m.from_user.id}{Dev_Neptune}") or r.get(
        f"{m.chat.id}:delCustomG:{m.from_user.id}{Dev_Neptune}"
    ):
        return False
    text = m.text
    name = r.get(f"{Dev_Neptune}:BotName") if r.get(f"{Dev_Neptune}:BotName") else "ليو"
    if text.startswith(f"{name} "):
        text = text.replace(f"{name} ", "")
    if r.get(f"{m.chat.id}:Custom:{m.chat.id}{Dev_Neptune}&text={text}"):
        text = r.get(f"{m.chat.id}:Custom:{m.chat.id}{Dev_Neptune}&text={text}")
    if r.get(f"Custom:{Dev_Neptune}&text={text}"):
        text = r.get(f"Custom:{Dev_Neptune}&text={text}")
    if isLockCommand(m.from_user.id, m.chat.id, text):
        return
    Open = """
{} من 「 {} 」
{} تمام فتحت {}
☆
"""
    Openn = """
{} من 「 {} 」
{} {} مفتوح من قبل
☆
"""
    Openn2 = """
{} من 「 {} 」
{} {} مفتوحه من قبل
☆
"""

    lock = """
{} من 「 {} 」
{} تمام قفلت {}
☆
"""

    lockn = """
{} من 「 {} 」
{} {} مقفل من قبل
☆
"""
    locknn = """
{} من 「 {} 」
{} {} مقفله من قبل
☆
"""

    if text == "اععدادات الحمايه":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            x1 = "❌" if r.get(f"{m.chat.id}:lockAudios:{Dev_Neptune}") else "✅"
            x2 = "❌" if r.get(f"{m.chat.id}:lockVideo:{Dev_Neptune}") else "❌"
            x3 = "❌" if r.get(f"{m.chat.id}:lockVoice:{Dev_Neptune}") else "✅"
            x4 = "❌" if r.get(f"{m.chat.id}:lockPhoto:{Dev_Neptune}") else "✅"
            x5 = "❌" if r.get(f"{m.chat.id}:mute:{Dev_Neptune}") else "✅"
            x6 = "❌" if r.get(f"{m.chat.id}:lockInline:{Dev_Neptune}") else "✅"
            x7 = "❌" if r.get(f"{m.chat.id}:lockForward:{Dev_Neptune}") else "✅"
            x8 = "❌" if r.get(f"{m.chat.id}:lockHashtags:{Dev_Neptune}") else "✅"
            x9 = "❌" if r.get(f"{m.chat.id}:lockEdit:{Dev_Neptune}") else "✅"
            x10 = "❌" if r.get(f"{m.chat.id}:lockStickers:{Dev_Neptune}") else "✅"
            x11 = "❌" if r.get(f"{m.chat.id}:lockFiles:{Dev_Neptune}") else "✅"
            x12 = (
                "❌" if r.get(f"{m.chat.id}:lockAnimations:{Dev_Neptune}") else "✅"
            )
            x13 = "❌" if r.get(f"{m.chat.id}:lockUrls:{Dev_Neptune}") else "✅"
            x14 = "❌" if r.get(f"{m.chat.id}:lockBots:{Dev_Neptune}") else "✅"
            x15 = "❌" if r.get(f"{m.chat.id}:lockTags:{Dev_Neptune}") else "✅"
            x16 = "❌" if r.get(f"{m.chat.id}:lockNot:{Dev_Neptune}") else "✅"
            x17 = (
                "❌" if r.get(f"{m.chat.id}:lockaddContacts:{Dev_Neptune}") else "✅"
            )
            x18 = "❌" if r.get(f"{m.chat.id}:lockMessages:{Dev_Neptune}") else "✅"
            x19 = "❌" if r.get(f"{m.chat.id}:lockSHTM:{Dev_Neptune}") else "✅"
            x20 = "❌" if r.get(f"{m.chat.id}:lockSpam:{Dev_Neptune}") else "✅"
            x21 = "❌" if r.get(f"{m.chat.id}:lockChannels:{Dev_Neptune}") else "✅"
            x22 = "❌" if r.get(f"{m.chat.id}:lockEditM:{Dev_Neptune}") else "✅"
            x23 = "❌" if r.get(f"{m.chat.id}:lockJoin:{Dev_Neptune}") else "✅"
            x24 = "❌" if r.get(f"{m.chat.id}:lockPersian:{Dev_Neptune}") else "✅"
            x25 = (
                "❌" if r.get(f"{m.chat.id}:lockJoinPersian:{Dev_Neptune}") else "✅"
            )
            x26 = "❌" if r.get(f"{m.chat.id}:lockNSFW:{Dev_Neptune}") else "✅"
            return m.reply(f"""
اعدادات المجموعة :

{k} الملفات الصوتية ⇠ ( {x1} )
{k} الفيديو ⇠ ( {x2} )
{k} الفويس ⇠ ( {x3} )
{k} الصور ⇠ ( {x4} )

{k} الدردشة ⇠ ( {x5} )
{k} الانلاين ⇠ ( {x6} )
{k} التوجيه ⇠ ( {x7} )
{k} الهشتاق ⇠ ( {x8} )
{k} التعديل ⇠ ( {x9} )
{k} الستيكرات ⇠ ( {x10} )

{k} الملفات ⇠ ( {x11} )
{k} المتحركات ⇠ ( {x12} )
{k} الروابط ⇠ ( {x13} )
{k} البوتات ⇠ ( {x14} )
{k} اليوزرات ⇠ ( {x15} )

{k} الاشعارات ⇠ ( {x16} )
{k} الاضافة ⇠ ( {x17} )

{k} الكلام الكثير ⇠ ( {x18} )
{k} السب ⇠ ( {x19} )
{k} التكرار ⇠ ( {x20} )
{k} القنوات ⇠ ( {x21} )
{k} تعديل الميديا ⇠ ( {x22} )

{k} الدخول ⇠ ( {x23} )
{k} الفارسية ⇠ ( {x24} )
{k} دخول الإيراني ⇠ ( {x25} )
{k} الإباحي ⇠ ( {x26} )

~ @{channel}""")

    if text == "الساعه" or text == "الساعة" or text == "الوقت":
        TIME_ZONE = "Asia/Riyadh"
        ZONE = pytz.timezone(TIME_ZONE)
        TIME = datetime.now(ZONE)
        clock = TIME.strftime("%I:%M %p")
        return m.reply(f"{k} الساعة ( {clock} )")

    if text == "القوانين":
        if r.get(f"{m.chat.id}:CustomRules:{Dev_Neptune}"):
            rules = r.get(f"{m.chat.id}:CustomRules:{Dev_Neptune}")
        else:
            rules = f"""{k} ممنوع نشر الروابط
{k} ممنوع التكلم او نشر صور اباحيه
{k} ممنوع اعاده توجيه
{k} ممنوع العنصرية بكل انواعها
{k} الرجاء احترام المدراء والادمنيه"""
        return m.reply(rules, disable_web_page_preview=True)

    if text == "التاريخ":
        b = Hijri.today().isoformat()
        a = b.split("-")
        year = int(a[0])
        month = int(a[1])
        day = int(a[2])
        hijri = Hijri(year, month, day)
        hijri_date = str(b).replace("-", "/")
        hijri_month = hijri.month_name("ar")

        b = Gregorian.today().isoformat()
        a = b.split("-")
        year = int(a[0])
        month = int(a[1])
        day = int(a[2])
        geo = Gregorian(year, month, day)
        geo_date = str(b).replace("-", "/")
        geo_month = geo.month_name("en")[:3]

        return m.reply(f"""
التاريخ:
{k} هجري ↢ {hijri_date} {hijri_month}
{k} ميلادي ↢ {geo_date} {geo_month}
""")

    if text == "المالك":
        owner = None
        for mm in m.chat.get_members(filter=ChatMembersFilter.ADMINISTRATORS):
            if mm.status == ChatMemberStatus.OWNER:
                owner = mm.user
                break
        if owner:
            if owner.is_deleted:
                m.reply("حساب المالك محذوف")
            else:
                owner_username = owner.username if owner.username else owner.id
                caption = f"• Owner ☆ ↦ {owner.mention}\n\n"
                caption += f"• Owner User ↦ @{owner_username}"
                if owner.photo:
                    file_id = owner.photo.big_file_id
                    photo_path = c.download_media(file_id)
                    button = InlineKeyboardMarkup(
                        [[InlineKeyboardButton(owner.first_name, user_id=owner.id)]]
                    )
                    m.reply_photo(
                        photo=photo_path, caption=caption, reply_markup=button
                    )
                    os.remove(photo_path)
                else:
                    button = InlineKeyboardMarkup(
                        [[InlineKeyboardButton(owner.first_name, user_id=owner.id)]]
                    )
                    m.reply(caption, reply_markup=button)

    if text == "اطردني":
        if r.get(f"{m.chat.id}:enableKickMe:{Dev_Neptune}"):
            get = m.chat.get_member(m.from_user.id)
            if get.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                return m.reply(f"{k} ممنوع طرد الحلوين")
            if admin_pls(m.from_user.id, m.chat.id):
                return m.reply(f"{k} ممنوع طرد الحلوين")
            else:
                m.reply(
                    f"طردتك يانفسية , وارسلت لك الرابط خاص تكدر ترجع متى مابغيت يامعقد"
                )
                m.chat.ban_member(m.from_user.id)
                time.sleep(0.5)
                c.unban_chat_member(m.chat.id, m.from_user.id)
                link = c.get_chat(m.chat.id).invite_link
                try:
                    c.send_message(
                        m.from_user.id,
                        f"{k} حبيبي النفسية رابط الكروب الي طردتك منه: {link}",
                    )
                except:
                    pass
                return False

    if text == "الرابط":
        if not r.get(f"{m.chat.id}:disableLINK:{Dev_Neptune}"):
            link = c.get_chat(m.chat.id).invite_link
            return m.reply(link)

    if text == "انشاء رابط":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        link = c.get_chat(m.chat.id).invite_link
        c.revoke_chat_invite_link(m.chat.id, link)
        return m.reply(f'{k} تمام سويت رابط جديد ارسل "الرابط"')

    if text.startswith("@all"):
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        if r.get(f"{m.chat.id}:disableALL:{Dev_Neptune}"):
            return m.reply("المنشن معطل")
        if r.get(f"{m.chat.id}:inMention:{Dev_Neptune}"):
            return False
        if r.get(f"{m.chat.id}:inMentionWAIT:{Dev_Neptune}"):
            get = r.ttl(f"{m.chat.id}:inMentionWAIT:{Dev_Neptune}")
            tm = time.strftime("%M:%S", time.gmtime(get))
            return m.reply(f"{k} سويت منشن من شوي تعال بعد {tm}")
        else:
            if len(text.split()) > 1:
                reason = text.split(None, 1)[1]
            else:
                reason = ""
            users_list = []
            r.set(f"{m.chat.id}:inMention:{Dev_Neptune}", 1)
            m.reply(f"{k} حسوي منشن يحلو ، اذا تريد توقفه ارسل `/Cancel` او `ايقاف`")
            for mm in m.chat.get_members(limit=150):
                if mm.user and not mm.user.is_deleted and not mm.user.is_bot:
                    users_list.append(mm.user.mention)
            final_list = [users_list[x : x + 5] for x in range(0, len(users_list), 5)]
            ftext = f"{reason}\n\n"
            for a in final_list:
                for i in a:
                    if not r.get(f"{m.chat.id}:inMention:{Dev_Neptune}"):
                        return False
                    ftext += f"{i} , "
                c.send_message(m.chat.id, ftext)
                ftext = f"{reason}\n\n"
            r.delete(f"{m.chat.id}:inMention:{Dev_Neptune}")
            r.set(f"{m.chat.id}:inMentionWAIT:{Dev_Neptune}", 1, ex=1200)

    if text.lower() == "/cancel" or text == "ايقاف":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:inMention:{Dev_Neptune}"):
                return m.reply(f"{k} مجاي اسوي منشن ركز !")
            else:
                r.delete(f"{m.chat.id}:inMention:{Dev_Neptune}")
                return m.reply("تمام وقفت المنشن")

    if text == "منشن":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        return m.reply("استخدم امر\n@all مع الكلام")

    if text == "تعطيل المنشن":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:disableALL:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} المشن معطل من قبل\n✔"
                )
            else:
                r.set(f"{m.chat.id}:disableALL:{Dev_Neptune}", 1)
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام عطلت المنشن\n✔"
                )

    if text == "تفعيل المنشن":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:disableALL:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} المنشن مفعل من قبل\n✔"
                )
            else:
                r.delete(f"{m.chat.id}:disableALL:{Dev_Neptune}")
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام فعلت المنشن\n✔"
                )

    if text == "تعطيل الترحيب":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:disableWelcome:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} الترحيب معطل من قبل\n✔"
                )
            else:
                r.set(f"{m.chat.id}:disableWelcome:{Dev_Neptune}", 1)
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام عطلت الترحيب\n✔"
                )

    if text == "تعطيل الترحيب بالصورة" or text == "تعطيل الترحيب بالصوره":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:disableWelcomep:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} الترحيب بالصورة من قبل\n✔"
                )
            else:
                r.set(f"{m.chat.id}:disableWelcomep:{Dev_Neptune}", 1)
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام عطلت الترحيب بالصورة\n✔"
                )

    if text == "تفعيل الترحيب بالصورة" or text == "تفعيل الترحيب بالصوره":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:disableWelcomep:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} الترحيب بالصورة مفعل من قبل\n✔"
                )
            else:
                r.delete(f"{m.chat.id}:disableWelcomep:{Dev_Neptune}")
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام فعلت الترحيب بالصورة\n✔"
                )

    if text == "تعطيل الرابط":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:disableLINK:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} الرابط معطل من قبل\n✔"
                )
            else:
                r.set(f"{m.chat.id}:disableLINK:{Dev_Neptune}", 1)
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام عطلت الرابط\n✔"
                )

    if text == "تفعيل الرابط":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:disableLINK:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} الرابط مفعل من قبل\n✔"
                )
            else:
                r.delete(f"{m.chat.id}:disableLINK:{Dev_Neptune}")
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام فعلت الرابط\n✔"
                )

    if text == "تعطيل البايو":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:disableBio:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} البايو معطل من قبل\n✔"
                )
            else:
                r.set(f"{m.chat.id}:disableBio:{Dev_Neptune}", 1)
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام عطلت البايو\n✔"
                )

    if text == "تفعيل البايو":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:disableBio:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} البايو مفعل من قبل\n✔"
                )
            else:
                r.delete(f"{m.chat.id}:disableBio:{Dev_Neptune}")
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام فعلت البايو\n✔"
                )

    if text == "تعطيل اطردني":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:enableKickMe:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} اطردني معطل من قبل\n✔"
                )
            else:
                r.delete(f"{m.chat.id}:enableKickMe:{Dev_Neptune}")
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام عطلت اطردني\n✔"
                )

    if text == "تفعيل اطردني":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:enableKickMe:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} اطردني مفعل من قبل\n✔"
                )
            else:
                r.set(f"{m.chat.id}:enableKickMe:{Dev_Neptune}", 1)
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام فعلت اطردني\n✔"
                )

    if text == "تعطيل التحقق":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:enableVerify:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} التحقق معطل من قبل\n✔"
                )
            else:
                r.delete(f"{m.chat.id}:enableVerify:{Dev_Neptune}")
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام عطلت التحقق\n✔"
                )

    if text == "تفعيل التحقق":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:enableVerify:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} التحقق مفعل من قبل\n✔"
                )
            else:
                r.set(f"{m.chat.id}:enableVerify:{Dev_Neptune}", 1)
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام فعلت التحقق\n✔"
                )

    if text == "تعطيل انطقي" or text == "تعطيل انطق":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:disableSay:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} انطقي معطل من قبل\n✔"
                )
            else:
                r.set(f"{m.chat.id}:disableSay:{Dev_Neptune}", 1)
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام عطلت انطقي\n✔"
                )

    if text == "تفعيل انطقي" or text == "تفعيل انطق":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:disableSay:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} انطقي مفعل من قبل\n✔"
                )
            else:
                r.delete(f"{m.chat.id}:disableSay:{Dev_Neptune}")
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام فعلت انطقي\n✔"
                )

    if text.startswith("انطق "):
        if not r.get(f"{m.chat.id}:disableSay:{Dev_Neptune}"):
            txt = text.split(None, 1)[1]
            if len(txt) > 500:
                return m.reply("توكل ما تكدر انطق اكثر من ٥٠٠ حرف بتعب بعدين")

            id = random.randint(999, 10000)
            try:
                # استخدام gtts بدلاً من الموقع الخارجي
                o = gtts.gTTS(text=txt, lang="ar", slow=False)
                o.save(f'Neptune{id}.mp3')

                try:
                    c.send_chat_action(m.chat.id, ChatAction.RECORD_AUDIO)
                except:
                    pass

                # تحويل إلى ogg للتليجرام
                os.system(
                    f"ffmpeg -i Neptune{id}.mp3 -ac 1 -strict -2 -codec:a libopus -b:a 128k -vbr off -ar 24000 Neptune{id}.ogg"
                )

                try:
                    c.send_chat_action(m.chat.id, ChatAction.UPLOAD_AUDIO)
                except:
                    pass

                m.reply_voice(f"Neptune{id}.ogg", caption=f"الكلمة: {txt}")

                # حذف الملفات المؤقتة
                try:
                    os.remove(f"Neptune{id}.ogg")
                    os.remove(f"Neptune{id}.mp3")
                except:
                    pass

            except Exception as e:
                print(f"خطأ في تحويل النص إلى صوت: {e}")
                return m.reply("عذراً، حدث خطأ في تحويل النص إلى صوت")

            return True

    if text.startswith("انطقي "):
        if not r.get(f"{m.chat.id}:disableSay:{Dev_Neptune}"):
            txt = text.split(None, 1)[1]
            if len(txt) > 500:
                return m.reply("توكل ما تكدر انطق اكثر من ٥٠٠ حرف بتعب بعدين")

            id = random.randint(999, 10000)
            try:
                # استخدام gtts بدلاً من الموقع الخارجي (صوت أنثوي)
                o = gtts.gTTS(text=txt, lang="ar", slow=False)
                o.save(f'Neptune{id}.mp3')

                try:
                    c.send_chat_action(m.chat.id, ChatAction.RECORD_AUDIO)
                except:
                    pass

                # تحويل إلى ogg للتليجرام
                os.system(
                    f"ffmpeg -i Neptune{id}.mp3 -ac 1 -strict -2 -codec:a libopus -b:a 128k -vbr off -ar 24000 Neptune{id}.ogg"
                )

                try:
                    c.send_chat_action(m.chat.id, ChatAction.UPLOAD_AUDIO)
                except:
                    pass

                m.reply_voice(f"Neptune{id}.ogg", caption=f"الكلمة: {txt}")

                # حذف الملفات المؤقتة
                try:
                    os.remove(f"Neptune{id}.ogg")
                    os.remove(f"Neptune{id}.mp3")
                except:
                    pass

            except Exception as e:
                print(f"خطأ في تحويل النص إلى صوت: {e}")
                return m.reply("عذراً، حدث خطأ في تحويل النص إلى صوت")

            return True

    if (
        (text == "شنو يكول" or text == "شنو تقول؟")
        and m.reply_to_message
        and m.reply_to_message.voice
    ):
        if m.reply_to_message.voice.file_size > 20971520:
            return m.reply("حجمه اكثر من ٢٠ ميجابايت، توكل")
        id = random.randint(99, 1000)
        voice = m.reply_to_message.download(f"./Neptune{id}.wav")
        s = sr.Recognizer()
        sound = AudioSegment.from_ogg(voice)
        wav_file = sound.export(voice, format="wav")
        with sr.AudioFile(wav_file) as src:
            audio_source = s.record(src)
        try:
            text = s.recognize_google(audio_source, language="ar-SA")
        except Exception as e:
            print(e)
            os.remove(f"Neptune{id}.wav")
            return m.reply("عجزت افهم شنو يكول ")
        os.remove(f"Neptune{id}.wav")
        return m.reply(f"يقول : {text}")

    if (
        (text == "Neptune" or text == "زوز")
        and m.reply_to_message
        and m.reply_to_message.voice
        and m.from_user.id == 6168217372
    ):
        if m.reply_to_message.voice.file_size > 20971520:
            return m.reply("حجمه اكثر من ٢٠ ميجابايت، توكل")
        id = random.randint(99, 1000)
        voice = m.reply_to_message.download(f"./Neptune{id}.wav")
        s = sr.Recognizer()
        sound = AudioSegment.from_ogg(voice)
        wav_file = sound.export(voice, format="wav")
        with sr.AudioFile(wav_file) as src:
            audio_source = s.record(src)
        try:
            text = s.recognize_google(audio_source, language="en-US")
        except Exception as e:
            print(e)
            os.remove(f"Neptune{id}.wav")
            return m.reply("عجزت افهم شنو يكول ")
        os.remove(f"Neptune{id}.wav")
        return m.reply(f"يقول : {text}")

    if text.startswith("منع "):
        if mod_pls(m.from_user.id, m.chat.id):
            noice = text.split(None, 1)[1]
            if r.sismember(f"{m.chat.id}:NotAllowedListText:{Dev_Neptune}", noice):
                return m.reply(
                    f"{k} الكلمة ( {noice} ) موجودة بقائمة المنع",
                    disable_web_page_preview=True,
                )
            else:
                r.sadd(f"{m.chat.id}:NotAllowedListText:{Dev_Neptune}", noice)
                return m.reply(
                    f"{k} الكلمة ( {noice} ) اضفتها الى قائمة المنع",
                    disable_web_page_preview=True,
                )

    if text.startswith("الغاء منع ") and len(text.split()) > 2:
        if mod_pls(m.from_user.id, m.chat.id):
            noice = text.split(None, 2)[2]
            if not r.sismember(f"{m.chat.id}:NotAllowedListText:{Dev_Neptune}", noice):
                return m.reply(
                    f"{k} الكلمة ( {noice} ) مو مضافة بقائمة المنع",
                    disable_web_page_preview=True,
                )
            else:
                r.srem(f"{m.chat.id}:NotAllowedListText:{Dev_Neptune}", noice)
                return m.reply(
                    f"{k} تمام مسحت ( {noice} ) من قائمة المنع",
                    disable_web_page_preview=True,
                )

    if text == "منع" and m.reply_to_message and m.reply_to_message.media:
        if mod_pls(m.from_user.id, m.chat.id):
            rep = m.reply_to_message
            if rep.sticker:
                file_id = rep.sticker.file_id
                type = "sticker"
            if rep.animation:
                file_id = rep.animation.file_id
                type = "animation"
            if rep.photo:
                file_id = rep.photo.file_id
                type = "photo"
            if rep.video:
                file_id = rep.photo.file_id
                type = "video"
            if rep.voice:
                file_id = rep.voice.file_id
                type = "voice"
            if rep.audio:
                file_id = rep.audio.file_id
                type = "audio"
            if rep.document:
                file_id = rep.document.file_id
                type = "document"

            id = file_id[-6:]
            if r.get(f"{id}:NotAllow:{m.chat.id}{Dev_Neptune}"):
                return m.reply(f"{k} موجودة بقائمة المنع")
            else:
                r.set(f"{id}:NotAllow:{m.chat.id}{Dev_Neptune}", 1)
                r.sadd(
                    f"{m.chat.id}:NotAllowedList:{Dev_Neptune}",
                    f"file={id}&by={m.from_user.id}&type={type}&file_id={file_id}",
                )
                return m.reply(f"{k} واضفناها لقائمة المنع")

    if text == "الغاء منع" and m.reply_to_message and m.reply_to_message.media:
        if mod_pls(m.from_user.id, m.chat.id):
            rep = m.reply_to_message
            if rep.sticker:
                file_id = rep.sticker.file_id
                type = "sticker"
            if rep.animation:
                file_id = rep.animation.file_id
                type = "animation"
            if rep.photo:
                file_id = rep.photo.file_id
                type = "photo"
            if rep.video:
                file_id = rep.photo.file_id
                type = "video"
            if rep.voice:
                file_id = rep.voice.file_id
                type = "voice"
            if rep.audio:
                file_id = rep.audio.file_id
                type = "audio"
            if rep.document:
                file_id = rep.document.file_id
                type = "document"

            id = file_id[-6:]
            if not r.get(f"{id}:NotAllow:{m.chat.id}{Dev_Neptune}"):
                return m.reply(f"{k} مو موجودة بقائمة المنع")
            else:
                r.delete(f"{id}:NotAllow:{m.chat.id}{Dev_Neptune}")
                r.srem(
                    f"{m.chat.id}:NotAllowedList:{Dev_Neptune}",
                    f"file={id}&by={m.from_user.id}&type={type}&file_id={file_id}",
                )
                return m.reply(f"{k} تمام شلتها من قائمه المنع")

    if text == "منع" and m.reply_to_message and not m.reply_to_message.media:
        if mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} المنع بالرد فقط للوسائط")

    if text == "قائمه المنع" or text == "قائمة المنع":
        text1 = "الكلمات الممنوعة:\n"
        text2 = "الوسائط الممنوعة:\n"
        count = 1
        count2 = 1
        if mod_pls(m.from_user.id, m.chat.id):
            if not r.smembers(
                f"{m.chat.id}:NotAllowedListText:{Dev_Neptune}"
            ) and not r.smembers(f"{m.chat.id}:NotAllowedList:{Dev_Neptune}"):
                return m.reply(f"{k} ماكو شي ممنوع")
            else:
                if not r.smembers(f"{m.chat.id}:NotAllowedListText:{Dev_Neptune}"):
                    text1 += "لايوجد"
                else:
                    for a in r.smembers(f"{m.chat.id}:NotAllowedListText:{Dev_Neptune}"):
                        text1 += f"{count} - {a}\n"
                        count += 1
                if not r.smembers(f"{m.chat.id}:NotAllowedList:{Dev_Neptune}"):
                    text2 += "لايوجد"
                else:
                    for a in r.smembers(f"{m.chat.id}:NotAllowedList:{Dev_Neptune}"):
                        g = a
                        id = g.split("file=")[1].split("&")[0]
                        by = g.split("by=")[1].split("&")[0]
                        type = g.split("type=")[1].split("&")[0]
                        text2 += (
                            f"{count2} - (`{id}`) ࿓ ( [{type}](tg://user?id={by}) )\n"
                        )
                return m.reply(f"{text1}\n{text2}", disable_web_page_preview=True)

    if text == "مسح قائمه المنع" or text == "مسح قائمة المنع":
        if mod_pls(m.from_user.id, m.chat.id):
            if not r.smembers(
                f"{m.chat.id}:NotAllowedListText:{Dev_Neptune}"
            ) and not r.smembers(f"{m.chat.id}:NotAllowedList:{Dev_Neptune}"):
                return m.reply(f"{k} ماكو شي ممنوع")
            else:
                if r.smembers(f"{m.chat.id}:NotAllowedListText:{Dev_Neptune}"):
                    r.delete(f"{m.chat.id}:NotAllowedListText:{Dev_Neptune}")
                if r.smembers(f"{m.chat.id}:NotAllowedList:{Dev_Neptune}"):
                    for a in r.smembers(f"{m.chat.id}:NotAllowedList:{Dev_Neptune}"):
                        file_id = a.split("file=")[1].split("&by=")[0]
                        r.delete(f"{file_id}:NotAllow:{m.chat.id}{Dev_Neptune}")
                r.delete(f"{m.chat.id}:NotAllowedList:{Dev_Neptune}")
                return m.reply(f"{k} تمام مسحت قائمة المنع")

    if text == "قفل الكل":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if (
                r.get(f"{m.chat.id}:mute:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockEdit:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockEditM:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockVoice:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockVideo:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockNot:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockPhoto:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockPersian:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockStickers:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockFiles:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockAnimations:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockUrls:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockHashtags:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockBots:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockTags:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockMessages:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockSpam:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockForward:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockSHTM:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockaddContacts:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockAudios:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockChannels:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockJoin:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockInline:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockNSFW:{Dev_Neptune}")
            ):
                return m.reply(
                    f"{k} من 「 {m.from_user.mention} 」 \n{k} كل شي مقفل يالطيب!\n✔"
                )
            else:
                m.reply(f"{k} من 「 {m.from_user.mention} 」 \n{k} تمام قفلت كل شي\n✔")
                r.set(f"{m.chat.id}:mute:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockJoin:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockChannels:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockEdit:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockEditM:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockVoice:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockVideo:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockNot:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockPhoto:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockStickers:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockAnimations:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockFiles:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockPersian:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockUrls:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockHashtags:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockMessages:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockTags:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockBots:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockSpam:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockInline:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockForward:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockAudios:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockaddContacts:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockSHTM:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockNSFW:{Dev_Neptune}", 1)
                return False

    if text == "فتح الكل":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if (
                not r.get(f"{m.chat.id}:mute:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockEdit:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockEditM:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockVoice:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockVideo:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockNot:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockPhoto:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockPersian:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockStickers:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockFiles:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockAnimations:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockUrls:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockHashtags:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockBots:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockTags:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockMessages:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockSpam:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockForward:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockSHTM:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockaddContacts:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockAudios:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockChannels:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockJoin:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockInline:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockNSFW:{Dev_Neptune}")
            ):
                return m.reply(
                    f"{k} من 「 {m.from_user.mention} 」 \n{k} كل شي مفتوح يالطيب!\n✔"
                )
            else:
                m.reply(f"{k} من 「 {m.from_user.mention} 」 \n{k} تمام فتحت كل شي\n✔")
                r.delete(f"{m.chat.id}:mute:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockJoin:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockChannels:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockEdit:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockEditM:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockVoice:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockVideo:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockNot:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockPhoto:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockStickers:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockAnimations:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockFiles:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockPersian:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockUrls:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockHashtags:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockMessages:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockTags:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockBots:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockSpam:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockInline:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockForward:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockAudios:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockaddContacts:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockSHTM:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockKFR:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockNSFW:{Dev_Neptune}")
                return False

    if text == "تفعيل الحماية" or text == "تفعيل الحمايه":
        if not owner_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المالك وفوق ) بس")
        else:
            if (
                r.get(f"{m.chat.id}:lockEditM:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockVoice:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockVideo:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockPhoto:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockPersian:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockStickers:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockFiles:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockAnimations:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockUrls:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockTags:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockMessages:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockSpam:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockForward:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockSHTM:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockAudios:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockChannels:{Dev_Neptune}")
                and r.get(f"{m.chat.id}:lockNSFW:{Dev_Neptune}")
            ):
                return m.reply(
                    f"{k} من 「 {m.from_user.mention} 」 \n{k} الحماية مفعله من قبل\n✔"
                )
            else:
                m.reply(
                    f"{k} من 「 {m.from_user.mention} 」 \n{k} تمام فعلت الحمايه\n✔"
                )

                r.set(f"{m.chat.id}:lockChannels:{Dev_Neptune}", 1)
                r.delete(f"{m.chat.id}:disableWarn:{Dev_Neptune}")
                r.set(f"{m.chat.id}:lockVoice:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockVideo:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockPhoto:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockStickers:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockAnimations:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockFiles:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockPersian:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockUrls:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockTags:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockSpam:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockForward:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockAudios:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockSHTM:{Dev_Neptune}", 1)
                r.set(f"{m.chat.id}:lockNSFW:{Dev_Neptune}", 1)
                return False

    if text == "تعطيل الحماية" or text == "تعطيل الحمايه":
        if not owner_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المالك وفوق ) بس")
        else:
            if (
                r.get(f"{m.chat.id}:lockEditM:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockVoice:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockVideo:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockPhoto:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockPersian:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockStickers:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockFiles:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockAnimations:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockUrls:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockTags:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockMessages:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockSpam:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockForward:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockSHTM:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockAudios:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockChannels:{Dev_Neptune}")
                and not r.get(f"{m.chat.id}:lockNSFW:{Dev_Neptune}")
            ):
                return m.reply(
                    f"{k} من 「 {m.from_user.mention} 」 \n{k} الحماية معطله من قبل\n✔"
                )
            else:
                m.reply(
                    f"{k} من 「 {m.from_user.mention} 」 \n{k} تمام عطلت الحمايه\n✔"
                )

                r.delete(f"{m.chat.id}:lockChannels:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockVoice:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockVideo:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockPhoto:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockStickers:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockAnimations:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockFiles:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockPersian:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockUrls:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockTags:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockSpam:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockForward:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockAudios:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockSHTM:{Dev_Neptune}")
                r.delete(f"{m.chat.id}:lockNSFW:{Dev_Neptune}")
                return False

    if text == "قفل الدردشة" or text == "قفل الدردشه" or text == "قفل الشات":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:mute:{Dev_Neptune}"):
                return m.reply(lockn.format(k, m.from_user.mention, k, "الشات"))
            else:
                r.set(f"{m.chat.id}:mute:{Dev_Neptune}", 1)
                return m.reply(lock.format(k, m.from_user.mention, k, "الشات"))

    if text == "فتح الدردشة" or text == "فتح الدردشه" or text == "فتح الشات":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:mute:{Dev_Neptune}"):
                return m.reply(Openn.format(k, m.from_user.mention, k, "الشات"))
            else:
                r.delete(f"{m.chat.id}:mute:{Dev_Neptune}")
                return m.reply(Open.format(k, m.from_user.mention, k, "الشات"))

    if text == "قفل التعديل":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:lockEdit:{Dev_Neptune}"):
                return m.reply(lockn.format(k, m.from_user.mention, k, "التعديل"))
            else:
                r.set(f"{m.chat.id}:lockEdit:{Dev_Neptune}", 1)
                return m.reply(lock.format(k, m.from_user.mention, k, "التعديل"))

    if text == "فتح التعديل":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:lockEdit:{Dev_Neptune}"):
                return m.reply(Openn.format(k, m.from_user.mention, k, "التعديل"))
            else:
                r.delete(f"{m.chat.id}:lockEdit:{Dev_Neptune}")
                return m.reply(Open.format(k, m.from_user.mention, k, "التعديل"))

    if text == "قفل تعديل الميديا":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:lockEditM:{Dev_Neptune}"):
                return m.reply(lockn.format(k, m.from_user.mention, k, "تعديل الميديا"))
            else:
                r.set(f"{m.chat.id}:lockEditM:{Dev_Neptune}", 1)
                return m.reply(lock.format(k, m.from_user.mention, k, "تعديل الميديا"))

    if text == "فتح تعديل الميديا":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:lockEditM:{Dev_Neptune}"):
                return m.reply(Openn.format(k, m.from_user.mention, k, "تعديل الميديا"))
            else:
                r.delete(f"{m.chat.id}:lockEditM:{Dev_Neptune}")
                return m.reply(Open.format(k, m.from_user.mention, k, "تعديل الميديا"))

    if text == "قفل الفويسات" or text == "قفل البصمات":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:lockVoice:{Dev_Neptune}"):
                return m.reply(lockn.format(k, m.from_user.mention, k, "الفويس"))
            else:
                r.set(f"{m.chat.id}:lockVoice:{Dev_Neptune}", 1)
                return m.reply(lock.format(k, m.from_user.mention, k, "الفويس"))

    if text == "فتح الفويسات" or text == "فتح البصمات":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:lockVoice:{Dev_Neptune}"):
                return m.reply(Openn.format(k, m.from_user.mention, k, "الفويس"))
            else:
                r.delete(f"{m.chat.id}:lockVoice:{Dev_Neptune}")
                return m.reply(Open.format(k, m.from_user.mention, k, "الفويس"))

    if text == "قفل الفيديو" or text == "قفل الفيديوهات":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:lockVideo:{Dev_Neptune}"):
                return m.reply(lockn.format(k, m.from_user.mention, k, "الفيديو"))
            else:
                r.set(f"{m.chat.id}:lockVideo:{Dev_Neptune}", 1)
                return m.reply(lock.format(k, m.from_user.mention, k, "الفيديو"))

    if text == "فتح الفيديو" or text == "فتح الفيديوهات":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:lockVideo:{Dev_Neptune}"):
                return m.reply(Openn.format(k, m.from_user.mention, k, "الفيديو"))
            else:
                r.delete(f"{m.chat.id}:lockVideo:{Dev_Neptune}")
                return m.reply(Open.format(k, m.from_user.mention, k, "الفيديو"))

    if text == "قفل الاشعارات":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:lockNot:{Dev_Neptune}"):
                return m.reply(locknn.format(k, m.from_user.mention, k, "الاشعارات"))
            else:
                r.set(f"{m.chat.id}:lockNot:{Dev_Neptune}", 1)
                return m.reply(lock.format(k, m.from_user.mention, k, "الاشعارات"))

    if text == "فتح الاشعارات":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:lockNot:{Dev_Neptune}"):
                return m.reply(Openn2.format(k, m.from_user.mention, k, "الاشعارات"))
            else:
                r.delete(f"{m.chat.id}:lockNot:{Dev_Neptune}")
                return m.reply(Open.format(k, m.from_user.mention, k, "الاشعارات"))

    if text == "قفل الصور":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:lockPhoto:{Dev_Neptune}"):
                return m.reply(locknn.format(k, m.from_user.mention, k, "الصور"))
            else:
                r.set(f"{m.chat.id}:lockPhoto:{Dev_Neptune}", 1)
                return m.reply(lock.format(k, m.from_user.mention, k, "الصور"))

    if text == "فتح الصور":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:lockPhoto:{Dev_Neptune}"):
                return m.reply(Openn2.format(k, m.from_user.mention, k, "الصور"))
            else:
                r.delete(f"{m.chat.id}:lockPhoto:{Dev_Neptune}")
                return m.reply(Open.format(k, m.from_user.mention, k, "الصور"))

    if text == "قفل الملصقات":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:lockStickers:{Dev_Neptune}"):
                return m.reply(locknn.format(k, m.from_user.mention, k, "الملصقات"))
            else:
                r.set(f"{m.chat.id}:lockStickers:{Dev_Neptune}", 1)
                return m.reply(lock.format(k, m.from_user.mention, k, "الملصقات"))

    if text == "فتح الملصقات":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:lockStickers:{Dev_Neptune}"):
                return m.reply(Openn2.format(k, m.from_user.mention, k, "الملصقات"))
            else:
                r.delete(f"{m.chat.id}:lockStickers:{Dev_Neptune}")
                return m.reply(Open.format(k, m.from_user.mention, k, "الملصقات"))

    if text == "قفل الفارسيه":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:lockPersian:{Dev_Neptune}"):
                return m.reply(locknn.format(k, m.from_user.mention, k, "الفارسيه"))
            else:
                r.set(f"{m.chat.id}:lockPersian:{Dev_Neptune}", 1)
                return m.reply(lock.format(k, m.from_user.mention, k, "الفارسيه"))

    if text == "فتح الفارسيه":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:lockPersian:{Dev_Neptune}"):
                return m.reply(Openn2.format(k, m.from_user.mention, k, "الفارسيه"))
            else:
                r.delete(f"{m.chat.id}:lockPersian:{Dev_Neptune}")
                return m.reply(Open.format(k, m.from_user.mention, k, "الفارسيه"))

    if text == "قفل الملفات":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:lockFiles:{Dev_Neptune}"):
                return m.reply(locknn.format(k, m.from_user.mention, k, "الملفات"))
            else:
                r.set(f"{m.chat.id}:lockFiles:{Dev_Neptune}", 1)
                return m.reply(lock.format(k, m.from_user.mention, k, "الملفات"))

    if text == "فتح الملفات":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:lockFiles:{Dev_Neptune}"):
                return m.reply(Openn2.format(k, m.from_user.mention, k, "الملفات"))
            else:
                r.delete(f"{m.chat.id}:lockFiles:{Dev_Neptune}")
                return m.reply(Open.format(k, m.from_user.mention, k, "الملفات"))

    if text == "قفل المتحركات" or text == "قفل المتحركه":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:lockAnimations:{Dev_Neptune}"):
                return m.reply(locknn.format(k, m.from_user.mention, k, "المتحركات"))
            else:
                r.set(f"{m.chat.id}:lockAnimations:{Dev_Neptune}", 1)
                return m.reply(lock.format(k, m.from_user.mention, k, "المتحركات"))

    if text == "فتح المتحركات" or text == "فتح المتحركه":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:lockAnimations:{Dev_Neptune}"):
                return m.reply(Openn2.format(k, m.from_user.mention, k, "المتحركات"))
            else:
                r.delete(f"{m.chat.id}:lockAnimations:{Dev_Neptune}")
                return m.reply(Open.format(k, m.from_user.mention, k, "المتحركات"))

    if text == "قفل الروابط":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:lockUrls:{Dev_Neptune}"):
                return m.reply(locknn.format(k, m.from_user.mention, k, "الروابط"))
            else:
                r.set(f"{m.chat.id}:lockUrls:{Dev_Neptune}", 1)
                return m.reply(lock.format(k, m.from_user.mention, k, "الروابط"))

    if text == "فتح الروابط":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:lockUrls:{Dev_Neptune}"):
                return m.reply(Openn2.format(k, m.from_user.mention, k, "الروابط"))
            else:
                r.delete(f"{m.chat.id}:lockUrls:{Dev_Neptune}")
                return m.reply(Open.format(k, m.from_user.mention, k, "الروابط"))

    if text == "قفل الهشتاق" or text == "قفل الهاشتاق":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:lockHashtags:{Dev_Neptune}"):
                return m.reply(lockn.format(k, m.from_user.mention, k, "الهاشتاق"))
            else:
                r.set(f"{m.chat.id}:lockHashtags:{Dev_Neptune}", 1)
                return m.reply(lock.format(k, m.from_user.mention, k, "الهاشتاق"))

    if text == "فتح الهشتاق" or text == "فتح الهاشتاق":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:lockHashtags:{Dev_Neptune}"):
                return m.reply(Openn.format(k, m.from_user.mention, k, "الهاشتاق"))
            else:
                r.delete(f"{m.chat.id}:lockHashtags:{Dev_Neptune}")
                return m.reply(Open.format(k, m.from_user.mention, k, "الهاشتاق"))

    if text == "قفل البوتات":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:lockBots:{Dev_Neptune}"):
                return m.reply(locknn.format(k, m.from_user.mention, k, "البوتات"))
            else:
                r.set(f"{m.chat.id}:lockBots:{Dev_Neptune}", 1)
                return m.reply(lock.format(k, m.from_user.mention, k, "البوتات"))

    if text == "فتح البوتات":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:lockBots:{Dev_Neptune}"):
                return m.reply(Openn2.format(k, m.from_user.mention, k, "البوتات"))
            else:
                r.delete(f"{m.chat.id}:lockBots:{Dev_Neptune}")
                return m.reply(Open.format(k, m.from_user.mention, k, "البوتات"))

    if text == "قفل اليوزرات" or text == "قفل المنشن":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:lockTags:{Dev_Neptune}"):
                return m.reply(locknn.format(k, m.from_user.mention, k, "اليوزرات"))
            else:
                r.set(f"{m.chat.id}:lockTags:{Dev_Neptune}", 1)
                return m.reply(lock.format(k, m.from_user.mention, k, "اليوزرات"))

    if text == "فتح اليوزرات" or text == "فتح المنشن":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:lockTags:{Dev_Neptune}"):
                return m.reply(Openn2.format(k, m.from_user.mention, k, "اليوزرات"))
            else:
                r.delete(f"{m.chat.id}:lockTags:{Dev_Neptune}")
                return m.reply(Open.format(k, m.from_user.mention, k, "اليوزرات"))

    """
   if text == 'قفل الكفر' or text == 'قفل الشيعه' or text == 'قفل الشيعة':
     if not admin_pls(m.from_user.id,m.chat.id):
       return m.reply(f'{k} هذا الامر يخص ( الادمن وفوق ) بس')
     else:
       if r.get(f'{m.chat.id}:lockKFR:{Dev_Neptune}'):
         return m.reply(locknn.format(k,m.from_user.mention,k,'الكفر'))
       else:
         r.set(f'{m.chat.id}:lockKFR:{Dev_Neptune}',1)
         return m.reply(lock.format(k,m.from_user.mention,k,'الكفر'))

   if text == 'فتح الكفر' or text == 'فتح الشيعه' or text == 'فتح الشيعة':
     if not admin_pls(m.from_user.id,m.chat.id):
       return m.reply(f'{k} هذا الامر يخص ( الادمن وفوق ) بس')
     else:
       if not r.get(f'{m.chat.id}:lockKFR:{Dev_Neptune}'):
         return m.reply(Openn2.format(k,m.from_user.mention,k,'الكفر'))
       else:
         r.delete(f'{m.chat.id}:lockKFR:{Dev_Neptune}')
         return m.reply(Open.format(k,m.from_user.mention,k,'الكفر'))
   """

    if text == "قفل الإباحي" or text == "قفل الاباحي":
        if not owner_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المالك وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:lockNSFW:{Dev_Neptune}"):
                return m.reply(lockn.format(k, m.from_user.mention, k, "الإباحي"))
            else:
                r.set(f"{m.chat.id}:lockNSFW:{Dev_Neptune}", 1)
                return m.reply(lock.format(k, m.from_user.mention, k, "الإباحي"))



    if text == "فتح الإباحي" or text == "فتح الاباحي":
        if not owner_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المالك وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:lockNSFW:{Dev_Neptune}"):
                return m.reply(Openn.format(k, m.from_user.mention, k, "االإباحي"))
            else:
                r.delete(f"{m.chat.id}:lockNSFW:{Dev_Neptune}")
                return m.reply(Open.format(k, m.from_user.mention, k, "الإباحي"))

    if text == "قفل الكلام الكثير" or text == "قفل الكلشنو":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:lockMessages:{Dev_Neptune}"):
                return m.reply(lockn.format(k, m.from_user.mention, k, "الكلام الكثير"))
            else:
                r.set(f"{m.chat.id}:lockMessages:{Dev_Neptune}", 1)
                return m.reply(lock.format(k, m.from_user.mention, k, "الكلام الكثير"))

    if text == "فتح الكلام الكثير" or text == "فتح الكلشنو":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:lockMessages:{Dev_Neptune}"):
                return m.reply(Openn.format(k, m.from_user.mention, k, "الكلام الكثير"))
            else:
                r.delete(f"{m.chat.id}:lockMessages:{Dev_Neptune}")
                return m.reply(Open.format(k, m.from_user.mention, k, "الكلام الكثير"))

    if text == "قفل التكرار":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:lockSpam:{Dev_Neptune}"):
                return m.reply(lockn.format(k, m.from_user.mention, k, "التكرار"))
            else:
                r.set(f"{m.chat.id}:lockSpam:{Dev_Neptune}", 1)
                return m.reply(lock.format(k, m.from_user.mention, k, "التكرار"))

    if text == "فتح التكرار":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:lockSpam:{Dev_Neptune}"):
                return m.reply(Openn.format(k, m.from_user.mention, k, "التكرار"))
            else:
                r.delete(f"{m.chat.id}:lockSpam:{Dev_Neptune}")
                return m.reply(Open.format(k, m.from_user.mention, k, "التكرار"))

    if text == "قفل التوجيه":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:lockForward:{Dev_Neptune}"):
                return m.reply(lockn.format(k, m.from_user.mention, k, "التوجيه"))
            else:
                r.set(f"{m.chat.id}:lockForward:{Dev_Neptune}", 1)
                return m.reply(lock.format(k, m.from_user.mention, k, "التوجيه"))

    if text == "فتح التوجيه":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:lockForward:{Dev_Neptune}"):
                return m.reply(Openn.format(k, m.from_user.mention, k, "التوجيه"))
            else:
                r.delete(f"{m.chat.id}:lockForward:{Dev_Neptune}")
                return m.reply(Open.format(k, m.from_user.mention, k, "التوجيه"))

    if text == "قفل الانلاين":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:lockInline:{Dev_Neptune}"):
                return m.reply(lockn.format(k, m.from_user.mention, k, "الانلاين"))
            else:
                r.set(f"{m.chat.id}:lockInline:{Dev_Neptune}", 1)
                return m.reply(lock.format(k, m.from_user.mention, k, "الانلاين"))

    if text == "فتح الانلاين":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:lockInline:{Dev_Neptune}"):
                return m.reply(Openn.format(k, m.from_user.mention, k, "الانلاين"))
            else:
                r.delete(f"{m.chat.id}:lockInline:{Dev_Neptune}")
                return m.reply(Open.format(k, m.from_user.mention, k, "الانلاين"))

    if text == "قفل السب":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:lockSHTM:{Dev_Neptune}"):
                return m.reply(lockn.format(k, m.from_user.mention, k, "السب"))
            else:
                r.set(f"{m.chat.id}:lockSHTM:{Dev_Neptune}", 1)
                return m.reply(lock.format(k, m.from_user.mention, k, "السب"))

    if text == "فتح السب":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:lockSHTM:{Dev_Neptune}"):
                return m.reply(Openn.format(k, m.from_user.mention, k, "السب"))
            else:
                r.delete(f"{m.chat.id}:lockSHTM:{Dev_Neptune}")
                return m.reply(Open.format(k, m.from_user.mention, k, "السب"))

    if text == "قفل الاضافه" or text == "قفل الاضافة" or text == "قفل الجهات":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:lockaddContacts:{Dev_Neptune}"):
                return m.reply(locknn.format(k, m.from_user.mention, k, "الاضافه"))
            else:
                r.set(f"{m.chat.id}:lockaddContacts:{Dev_Neptune}", 1)
                return m.reply(lock.format(k, m.from_user.mention, k, "الاضافه"))

    if text == "فتح الاضافه" or text == "فتح الاضافة" or text == "فتح الجهات":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:lockaddContacts:{Dev_Neptune}"):
                return m.reply(Openn2.format(k, m.from_user.mention, k, "الاضافه"))
            else:
                r.delete(f"{m.chat.id}:lockaddContacts:{Dev_Neptune}")
                return m.reply(Open.format(k, m.from_user.mention, k, "الاضافه"))

    if text == "قفل دخول البوتات" or text == "قفل الوهمي" or text == "قفل الايراني":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:lockJoinPersian:{Dev_Neptune}"):
                return m.reply(locknn.format(k, m.from_user.mention, k, "دخول البوتات"))
            else:
                r.set(f"{m.chat.id}:lockJoinPersian:{Dev_Neptune}", 1)
                return m.reply(lock.format(k, m.from_user.mention, k, "دخول البوتات"))

    if text == "فتح دخول البوتات" or text == "فتح الوهمي" or text == "فتح الايراني":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:lockJoinPersian:{Dev_Neptune}"):
                return m.reply(Openn2.format(k, m.from_user.mention, k, "دخول البوتات"))
            else:
                r.delete(f"{m.chat.id}:lockJoinPersian:{Dev_Neptune}")
                return m.reply(Open.format(k, m.from_user.mention, k, "دخول البوتات"))

    if text == "قفل الصوت":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:lockAudios:{Dev_Neptune}"):
                return m.reply(lockn.format(k, m.from_user.mention, k, "الصوت"))
            else:
                r.set(f"{m.chat.id}:lockAudios:{Dev_Neptune}", 1)
                return m.reply(lock.format(k, m.from_user.mention, k, "الصوت"))

    if text == "فتح الصوت":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:lockAudios:{Dev_Neptune}"):
                return m.reply(Openn.format(k, m.from_user.mention, k, "الصوت"))
            else:
                r.delete(f"{m.chat.id}:lockAudios:{Dev_Neptune}")
                return m.reply(Open.format(k, m.from_user.mention, k, "الصوت"))

    if text == "قفل القنوات":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:lockChannels:{Dev_Neptune}"):
                return m.reply(locknn.format(k, m.from_user.mention, k, "القنوات"))
            else:
                r.set(f"{m.chat.id}:lockChannels:{Dev_Neptune}", 1)
                return m.reply(lock.format(k, m.from_user.mention, k, "القنوات"))

    if text == "فتح القنوات":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:lockChannels:{Dev_Neptune}"):
                return m.reply(Openn2.format(k, m.from_user.mention, k, "القنوات"))
            else:
                r.delete(f"{m.chat.id}:lockChannels:{Dev_Neptune}")
                return m.reply(Open.format(k, m.from_user.mention, k, "القنوات"))

    if text == "قفل الدخول":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:lockJoin:{Dev_Neptune}"):
                return m.reply(lockn.format(k, m.from_user.mention, k, "الدخول"))
            else:
                r.set(f"{m.chat.id}:lockJoin:{Dev_Neptune}", 1)
                return m.reply(lock.format(k, m.from_user.mention, k, "الدخول"))

    if text == "فتح الدخول":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:lockJoin:{Dev_Neptune}"):
                return m.reply(Openn.format(k, m.from_user.mention, k, "الدخول"))
            else:
                r.delete(f"{m.chat.id}:lockJoin:{Dev_Neptune}")
                return m.reply(Open.format(k, m.from_user.mention, k, "الدخول"))

    if text == "تعطيل التحذير":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:disableWarn:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} التحذير معطل من قبل\n✔"
                )
            else:
                r.set(f"{m.chat.id}:disableWarn:{Dev_Neptune}", 1)
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام عطلت التحذير\n✔"
                )

    if text == "تفعيل التحذير":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:disableWarn:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} التحذير مفعل من قبل\n✔"
                )
            else:
                r.delete(f"{m.chat.id}:disableWarn:{Dev_Neptune}")
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام فعلت التحذير\n✔"
                )

    if text == "تعطيل اليوتيوب":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:disableYT:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} اليوتيوب معطل من قبل\n✔"
                )
            else:
                r.set(f"{m.chat.id}:disableYT:{Dev_Neptune}", 1)
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام عطلت اليوتيوب\n✔"
                )

    if text == "تفعيل اليوتيوب":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:disableYT:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} اليوتيوب مفعل من قبل\n✔"
                )
            else:
                r.delete(f"{m.chat.id}:disableYT:{Dev_Neptune}")
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام فعلت اليوتيوب\n✔"
                )

    if text == "تعطيل الساوند":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:disableSound:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} الساوند معطل من قبل\n✔"
                )
            else:
                r.set(f"{m.chat.id}:disableSound:{Dev_Neptune}", 1)
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام عطلت الساوند\n✔"
                )

    if text == "تفعيل الساوند":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:disableSound:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} الساوند مفعل من قبل\n✔"
                )
            else:
                r.delete(f"{m.chat.id}:disableSound:{Dev_Neptune}")
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام فعلت الساوند\n✔"
                )

    if text == "تعطيل الانستا":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:disableINSTA:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} الانستا معطل من قبل\n✔"
                )
            else:
                r.set(f"{m.chat.id}:disableINSTA:{Dev_Neptune}", 1)
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام عطلت الانستا\n✔"
                )

    if text == "تفعيل الانستا":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:disableINSTA:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} الانستا مفعل من قبل\n✔"
                )
            else:
                r.delete(f"{m.chat.id}:disableINSTA:{Dev_Neptune}")
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام فعلت الانستا\n✔"
                )

    if text == "تعطيل اهمس":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:disableWHISPER:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} اهمس معطل من قبل\n✔"
                )
            else:
                r.set(f"{m.chat.id}:disableWHISPER:{Dev_Neptune}", 1)
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام عطلت اهمس\n✔"
                )

    if text == "تفعيل اهمس":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:disableWHISPER:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} اهمس مفعل من قبل\n✔"
                )
            else:
                r.delete(f"{m.chat.id}:disableWHISPER:{Dev_Neptune}")
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام فعلت اهمس\n✔"
                )

    if text == "تعطيل التيك":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:disableTik:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} التيك معطل من قبل\n✔"
                )
            else:
                r.set(f"{m.chat.id}:disableTik:{Dev_Neptune}", 1)
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام عطلت التيك\n✔"
                )

    if text == "تفعيل التيك":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:disableTik:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} التيك مفعل من قبل\n✔"
                )
            else:
                r.delete(f"{m.chat.id}:disableTik:{Dev_Neptune}")
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام فعلت التيك\n✔"
                )

    if text == "تعطيل شازام":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:disableShazam:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} شازام معطل من قبل\n✔"
                )
            else:
                r.set(f"{m.chat.id}:disableShazam:{Dev_Neptune}", 1)
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام عطلت شازام\n✔"
                )

    if text == "تفعيل شازام":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:disableShazam:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} شازام مفعل من قبل\n✔"
                )
            else:
                r.delete(f"{m.chat.id}:disableShazam:{Dev_Neptune}")
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام فعلت شازام\n✔"
                )

    if text == "تعطيل الالعاب":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:disableGames:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} الالعاب معطله من قبل\n✔"
                )
            else:
                r.set(f"{m.chat.id}:disableGames:{Dev_Neptune}", 1)
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام عطلت الالعاب\n✔"
                )

    if text == "تفعيل الالعاب":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:disableGames:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} الالعاب مفعله من قبل\n✔"
                )
            else:
                r.delete(f"{m.chat.id}:disableGames:{Dev_Neptune}")
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام فعلت الالعاب\n✔"
                )

    if text == "الالعاب":
        return m.reply(
            """
☤ تفعيل الالعاب
☤ تعطيل الالعاب
    ╼╾
✽ جمل
✽ كلمات
✽ اغاني
✽ دين
✽ عربي
✽ اكمل
✽ صور
✽ كت تويت
✽ مؤقت
✽ اعلام
✽ معاني
✽ تخمين
✽ احكام
✽ ارقام
✽ احسب
✽ خواتم
✽ انقليزي
✽ ترتيب
✽ انمي
✽ تركيب
✽ تفكيك
✽ عواصم
✽ روليت
✽ سيارات
✽ ايموجي
✽ حجره
✽ تشفير
✽ كره قدم
✽ ديمون
✽ اكس او
╼╾
❖ فلوسي ↼ علمود تشوف فلوسك
❖ بيع فلوسي + العدد ↼ للأستبدال
""",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "1", callback_data=f"commands1:{m.from_user.id}"
                        ),
                        InlineKeyboardButton(
                            "2", callback_data=f"commands2:{m.from_user.id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "3", callback_data=f"commands3:{m.from_user.id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton("الالعاب ‣", callback_data="None"),
                        InlineKeyboardButton(
                            "التسليه", callback_data=f"commands5:{m.from_user.id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "اليوتيوب", callback_data=f"commands6:{m.from_user.id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "البنك", callback_data=f"commands7:{m.from_user.id}"
                        ),
                        InlineKeyboardButton(
                            "زواج", callback_data=f"commands8:{m.from_user.id}"
                        ),
                    ],
                ]
            ),
        )

    if text == "تعطيل الترجمة" or text == "تعطيل الترجمه":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:disableTrans:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} الترجمه معطله من قبل\n✔"
                )
            else:
                r.set(f"{m.chat.id}:disableTrans:{Dev_Neptune}", 1)
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام عطلت الترجمه\n✔"
                )

    if text == "تفعيل الترجمة" or text == "تفعيل الترجمه":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:disableTrans:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} الترجمه مفعله من قبل\n✔"
                )
            else:
                r.delete(f"{m.chat.id}:disableTrans:{Dev_Neptune}")
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام فعلت الترجمه\n✔"
                )

    if text == "تعطيل التسلية" or text == "تعطيل التسليه":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if r.get(f"{m.chat.id}:disableFun:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} التسلية معطله من قبل\n✔"
                )
            else:
                r.set(f"{m.chat.id}:disableFun:{Dev_Neptune}", 1)
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام عطلت التسلية\n✔"
                )

    if text == "تفعيل التسلية" or text == "تفعيل التسليه":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الامر يخص ( المدير وفوق ) بس")
        else:
            if not r.get(f"{m.chat.id}:disableFun:{Dev_Neptune}"):
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} التسلية مفعله من قبل\n✔"
                )
            else:
                r.delete(f"{m.chat.id}:disableFun:{Dev_Neptune}")
                return m.reply(
                    f"{k} من「 {m.from_user.mention} 」\n{k} تمام فعلت التسلية\n✔"
                )



    if (
        text == "/ar"
        and m.reply_to_message
        and (m.reply_to_message.text or m.reply_to_message.caption)
    ):
        if not r.get(f"{m.chat.id}:disableTrans:{Dev_Neptune}"):
            text = m.reply_to_message.text or m.reply_to_message.caption
            translation = requests.get(
                f"https://hozory.com/translate/?target=ar&text={text}"
            ).json()["result"]["translate"]
            m.reply(f"`{translation}`")

    if (
        text == "/en"
        and m.reply_to_message
        and (m.reply_to_message.text or m.reply_to_message.caption)
    ):
        if not r.get(f"{m.chat.id}:disableTrans:{Dev_Neptune}"):
            text = m.reply_to_message.text or m.reply_to_message.caption
            translation = requests.get(
                f"https://hozory.com/translate/?target=en&text={text}"
            ).json()["result"]["translate"]
            m.reply(f"`{translation}`")

    if (
        text == "ترجمه"
        and m.reply_to_message
        and (m.reply_to_message.text or m.reply_to_message.caption)
    ):
        if not r.get(f"{m.chat.id}:disableTrans:{Dev_Neptune}"):
            text = m.reply_to_message.text or m.reply_to_message.caption
            en = requests.get(
                f"https://hozory.com/translate/?target=en&text={text}"
            ).json()["result"]["translate"]
            ar = requests.get(
                f"https://hozory.com/translate/?target=ar&text={text}"
            ).json()["result"]["translate"]
            ru = requests.get(
                f"https://hozory.com/translate/?target=ru&text={text}"
            ).json()["result"]["translate"]
            zh = requests.get(
                f"https://hozory.com/translate/?target=zh&text={text}"
            ).json()["result"]["translate"]
            fr = requests.get(
                f"https://hozory.com/translate/?target=fr&text={text}"
            ).json()["result"]["translate"]
            du = requests.get(
                f"https://hozory.com/translate/?target=nl&text={text}"
            ).json()["result"]["translate"]
            tr = requests.get(
                f"https://hozory.com/translate/?target=tr&text={text}"
            ).json()["result"]["translate"]
            txt = f"🇷🇺 : \n {ru}\n\n🇨🇳 : \n {zh}\n\n🇫🇷 :\n {fr}\n\n🇩🇪 :\n {du}\n\n🇹🇷 : \n{tr}"
            return m.reply(txt)

    if (
        text.startswith("ترجمه ")
        and m.reply_to_message
        and (m.reply_to_message.text or m.reply_to_message.caption)
    ):
        if not r.get(f"{m.chat.id}:disableTrans:{Dev_Neptune}"):
            lang = text.split()[1]
            text = m.reply_to_message.text or m.reply_to_message.caption
            translation = requests.get(
                f"https://hozory.com/translate/?target={lang}&text={text}"
            ).json()["result"]["translate"]
            m.reply(f"`{translation}`")

    if text == "ابلاغ" and m.reply_to_message:
        text = f"{k} تم ابلاغ المشرفين"
        cc = 0
        for mm in c.get_chat_members(
            m.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
        ):
            if not mm.user.is_deleted and not mm.user.is_bot:
                cc += 1
                text += f"[⁪⁬⁪⁬⁮⁪⁬⁪⁬⁮](tg://user?id={mm.user.id})"
        if cc == 0:
            return False
        return m.reply(
            text,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("⚠️", callback_data="delAdminMSG")]]
            ),
        )

    if text == "المقيدين":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الأمر يخص ( المدير وفوق ) بس")
        else:
            co = 0
            cc = 1
            text = "المقيدين:\n\n"
            for mm in c.get_chat_members(
                m.chat.id, filter=ChatMembersFilter.RESTRICTED
            ):
                if co == 100:
                    break
                if not mm.user.is_deleted:
                    co += 1
                    user = (
                        f"@{mm.user.username}"
                        if mm.user.username
                        else f"[@{channel}](tg://user?id={mm.user.id})"
                    )
                    text += f"{cc} ➣ {user} ☆ ( `{mm.user.id}` )\n"
                    cc += 1
            text += "☆"
            if co == 0:
                return m.reply(f"{k} ماكو مقيدين")
            else:
                return m.reply(text)

    if text == "مسح المقيدين":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الأمر يخص ( المدير وفوق ) بس")
        else:
            co = 0
            for mm in c.get_chat_members(
                m.chat.id, filter=ChatMembersFilter.RESTRICTED
            ):
                co += 1
                c.restrict_chat_member(
                    m.chat.id,
                    mm.user.id,
                    ChatPermissions(
                        can_send_messages=True,
                        can_send_media_messages=True,
                        can_send_other_messages=True,
                        can_send_polls=True,
                        can_invite_users=True,
                        can_add_web_page_previews=True,
                        can_change_info=True,
                        can_pin_messages=True,
                    ),
                )
            if co == 0:
                return m.reply(f"{k} ماكو مقيديين")
            else:
                return m.reply(f"{k} تمام مسحت ( {co} ) من المقيدين")

    if text == "تثبيت" and m.reply_to_message:
        if mod_pls(m.from_user.id, m.chat.id):
            m.reply_to_message.pin(disable_notification=False)
            m.reply(f"{k} تمام ثبتت الرسالة ")

    if text == "الغاء التثبيت" and m.reply_to_message:
        if mod_pls(m.from_user.id, m.chat.id):
            m.reply_to_message.unpin()
            m.reply(f"{k} تمام لغيت تثبيت الرسالة ")

    if text.startswith("تقييد ") and len(text.split()) == 2:
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الأمر يخص ( المدير وفوق ) بس")
        else:
            try:
                user = int(text.split()[1])
            except:
                user = text.split()[1].replace("@", "")
            try:
                get = m.chat.get_member(user)
                if m.from_user.id == get.user.id:
                    return m.reply("شبيك تريد تنزل نفسك")
                if pre_pls(get.user.id, m.chat.id):
                    rank = get_rank(get.user.id, m.chat.id)
                    return m.reply(f"{k} هييه ما تكدر تقيد {rank} ياغبي!")
                if get.status == ChatMemberStatus.RESTRICTED:
                    return m.reply(f"「 {get.user.mention} 」 \n{k} مقيد من قبل\n✔")
            except:
                return m.reply(f"{k} ماكو عضو بهذا اليوزر")
            c.restrict_chat_member(
                m.chat.id, get.user.id, ChatPermissions(can_send_messages=False)
            )
            return m.reply(f"「 {get.user.mention} 」 \n{k} قيدته\n✔")

    if text == "تقييد" and m.reply_to_message and m.reply_to_message.from_user:
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الأمر يخص ( المدير وفوق ) بس")
        else:
            if m.from_user.id == m.reply_to_message.from_user.id:
                return m.reply("شبيك تريد تنزل نفسك")
            get = m.chat.get_member(m.reply_to_message.from_user.id)
            if pre_pls(m.reply_to_message.from_user.id, m.chat.id):
                rank = get_rank(m.reply_to_message.from_user.id, m.chat.id)
                return m.reply(f"{k} هييه ما تكدر تقيد {rank} ياغبي!")
            if get.status == ChatMemberStatus.RESTRICTED:
                return m.reply(
                    f"「 {m.reply_to_message.from_user.mention} 」 \n{k} مقيد من قبل\n✔"
                )
            c.restrict_chat_member(
                m.chat.id,
                m.reply_to_message.from_user.id,
                ChatPermissions(can_send_messages=False),
            )
            return m.reply(
                f"「 {m.reply_to_message.from_user.mention} 」 \n{k} قيدته\n✔"
            )

    if (
        text.startswith("الغاء تقييد ")
        or text.startswith("الغاء التقييد ")
        and len(text.split()) == 3
    ):
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الأمر يخص ( الادمن وفوق ) بس")
        else:
            try:
                user = int(text.split()[2])
            except:
                user = text.split()[2].replace("@", "")
            try:
                get = m.chat.get_member(user)
                if not get.status == ChatMemberStatus.RESTRICTED:
                    return m.reply(f"「 {get.user.mention} 」 \n{k} مو مقيد من قبل\n✔")
            except:
                return m.reply(f"{k} ماكو عضو بهذا اليوزر")
            c.restrict_chat_member(
                m.chat.id,
                get.user.id,
                ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_send_polls=True,
                    can_invite_users=True,
                    can_add_web_page_previews=True,
                    can_change_info=True,
                    can_pin_messages=True,
                ),
            )
            return m.reply(f"「 {get.user.mention} 」 \n{k} تمام الغيت تقييده\n✔")

    if (
        text == "الغاء تقييد"
        or text == "الغاء التقييد"
        and m.reply_to_message
        and m.reply_to_message.from_user
    ):
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الأمر يخص ( الادمن وفوق ) بس")
        else:
            get = m.chat.get_member(m.reply_to_message.from_user.id)
            if not get.status == ChatMemberStatus.RESTRICTED:
                return m.reply(
                    f"「 {m.reply_to_message.from_user.mention} 」 \n{k} مو مقيد من قبل\n✔"
                )
            c.restrict_chat_member(
                m.chat.id,
                m.reply_to_message.from_user.id,
                ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_send_polls=True,
                    can_invite_users=True,
                    can_add_web_page_previews=True,
                    can_change_info=True,
                    can_pin_messages=True,
                ),
            )
            return m.reply(
                f"「 {m.reply_to_message.from_user.mention} 」 \n{k} تمام الغيت تقييده\n✔"
            )

    if text == "المحظورين":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الأمر يخص ( المدير وفوق ) بس")
        else:
            co = 0
            cc = 1
            text = "المحظورين:\n\n"
            for mm in c.get_chat_members(m.chat.id, filter=ChatMembersFilter.BANNED):
                if co == 100:
                    break
                if mm.user:
                    if not mm.user.is_deleted:
                        co += 1
                        user = (
                            f"@{mm.user.username}"
                            if mm.user.username
                            else f"[@{channel}](tg://user?id={mm.user.id})"
                        )
                        text += f"{cc} ➣ {user} ☆ ( `{mm.user.id}` )\n"
                        cc += 1
                if mm.chat:
                    co += 1
                    user = f"@{mm.chat.username}"
                    text += f"{cc} ➣ {user} ☆ (`{mm.chat.id}`)\n"
                    cc += 1
            text += "☆"
            if co == 0:
                return m.reply(f"{k} ماكو محظورين")
            else:
                return m.reply(text)

    if text == "مسح المحظورين":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الأمر يخص ( الادمن وفوق ) بس")
        else:
            co = 0
            for mm in c.get_chat_members(m.chat.id, filter=ChatMembersFilter.BANNED):
                if mm.user:
                    co += 1
                    c.unban_chat_member(m.chat.id, mm.user.id)
                if mm.chat:
                    co += 1
                    c.unban_chat_member(m.chat.id, mm.chat.id)
            if co == 0:
                return m.reply(f"{k} ماكو محظورين")
            else:
                return m.reply(f"{k} تمام مسحت ( {co} ) من المحظورين")

    if text.startswith("حظر ") and len(text.split()) == 2:
        if not "@" in text and not re.findall("[0-9]+", text):
            return
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الأمر يخص ( المدير وفوق ) بس")
        else:
            try:
                user = int(text.split()[1])
            except:
                user = text.split()[1].replace("@", "")
            try:
                get = m.chat.get_member(user)
                if m.from_user.id == get.user.id:
                    return m.reply("شبيك تريد تنزل نفسك")
                if pre_pls(get.user.id, m.chat.id):
                    rank = get_rank(get.user.id, m.chat.id)
                    return m.reply(f"{k} هييه ما تكدر تحظر {rank} ياغبي!")
                if get.status == ChatMemberStatus.BANNED:
                    return m.reply(f"「 {get.user.mention} 」 \n{k} محظور من قبل\n✔")
            except:
                return m.reply(f"{k} ماكو عضو بهذا اليوزر")
            m.chat.ban_member(get.user.id)
            return m.reply(f"「 {get.user.mention} 」 \n{k} حظرته\n✔")

    if text == "حظر" and m.reply_to_message and m.reply_to_message.from_user:
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الأمر يخص ( المدير وفوق ) بس")
        else:
            if m.from_user.id == m.reply_to_message.from_user.id:
                return m.reply("شبيك تريد تنزل نفسك")
            get = m.chat.get_member(m.reply_to_message.from_user.id)
            if pre_pls(m.reply_to_message.from_user.id, m.chat.id):
                rank = get_rank(m.reply_to_message.from_user.id, m.chat.id)
                return m.reply(f"{k} هييه ما تكدر تحظر {rank} ياغبي!")
            if get.status == ChatMemberStatus.BANNED:
                return m.reply(
                    f"「 {m.reply_to_message.from_user.mention} 」 \n{k} محظور من قبل\n✔"
                )
            m.chat.ban_member(m.reply_to_message.from_user.id)
            return m.reply(
                f"「 {m.reply_to_message.from_user.mention} 」 \n{k} حظرته\n✔"
            )

    if text == "طرد البوتات":
        if not owner_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الأمر يخص ( المالك وفوق ) بس")
        else:
            co = 0
            for mm in m.chat.get_members(filter=ChatMembersFilter.BOTS):
                try:
                    m.chat.ban_member(mm.user.id)
                    co += 1
                except:
                    pass
            if co == 0:
                return m.reply(f"{k} ماكو بوتات")
            else:
                return m.reply(f"{k} تمام حظر ( {co} ) بوت")

    if text.startswith("طرد ") and len(text.split()) == 2:
        if not "@" in text and not re.findall("[0-9]+", text):
            return
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الأمر يخص ( الادمن وفوق ) بس")
        else:
            try:
                user = int(text.split()[1])
            except:
                user = text.split()[1].replace("@", "")
            try:
                get = m.chat.get_member(user)
                if m.from_user.id == get.user.id:
                    return m.reply("شبيك تريد تنزل نفسك")
                if pre_pls(get.user.id, m.chat.id):
                    rank = get_rank(get.user.id, m.chat.id)
                    return m.reply(f"{k} هييه ما تكدر تطرد {rank} ياغبي!")
                if get.status == ChatMemberStatus.BANNED:
                    return m.reply(f"「 {get.user.mention} 」 \n{k} مطرود من قبل\n✔")
            except:
                return m.reply(f"{k} ماكو عضو بهذا اليوزر")
            m.chat.ban_member(get.user.id)
            m.chat.unban_member(get.user.id)
            return m.reply(f"「 {get.user.mention} 」 \n{k} طردته\n✔")

    if text == "اهمس" and m.reply_to_message and m.reply_to_message.from_user:
        if r.get(f"{m.chat.id}:disableWHISPER:{Dev_Neptune}"):
            return m.reply(f"{k} امر اهمس معطل")
        user_id = m.reply_to_message.from_user.id
        if user_id == m.from_user.id:
            return m.reply(f"{k} مابيك تهمس لنفسك ياغبي")
        else:
            import uuid

            id = str(uuid.uuid4())[:6]
            a = m.reply(
                f"{k} تم تحديد الهمسة الى [ {m.reply_to_message.from_user.mention} ]",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                f"اهمس الى [ {m.reply_to_message.from_user.first_name[:25]} ]",
                                url=f"t.me/{c.me.username}?start=hmsa{id}",
                            )
                        ]
                    ]
                ),
            )
            data = {
                "from": m.from_user.id,
                "to": user_id,
                "chat": m.chat.id,
                "id": a.id,
            }
            # wsdb.set(str(id), data)
            wsdb.setex(key=id, ttl=3600, value=data)
            return True





    if text == "طرد" and m.reply_to_message and m.reply_to_message.from_user:
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الأمر يخص ( المدير وفوق ) بس")
        else:
            try:
                if m.from_user.id == m.reply_to_message.from_user.id:
                    return m.reply("شبيك تريد تنزل نفسك")
                get = m.chat.get_member(m.reply_to_message.from_user.id)
                if pre_pls(m.reply_to_message.from_user.id, m.chat.id):
                    rank = get_rank(m.reply_to_message.from_user.id, m.chat.id)
                    return m.reply(f"{k} هييه ما تكدر تطرد {rank} ياغبي!")
                if get.status == ChatMemberStatus.BANNED:
                    return m.reply(
                        f"「 {m.reply_to_message.from_user.mention} 」 \n{k} مطرود من قبل\n✔"
                    )
                m.chat.ban_member(m.reply_to_message.from_user.id)
                m.reply(f"「 {m.reply_to_message.from_user.mention} 」 \n{k} طردته\n✔")
                return m.chat.unban_member(m.reply_to_message.from_user.id)
            except:
                return m.reply(f"{k} العضو مو بالمجموعة")

    if (
        text.startswith("رفع الحظر ")
        or text.startswith("الغاء الحظر ")
        and len(text.split()) == 3
    ):
        if not "@" in text and not re.findall("[0-9]+", text):
            return
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الأمر يخص ( المدير وفوق ) بس")
        else:
            try:
                user = int(text.split()[2])
            except:
                user = text.split()[2].replace("@", "")
            try:
                get = m.chat.get_member(user)
                if not get.status == ChatMemberStatus.BANNED:
                    return m.reply(f"「 {get.user.mention} 」 \n{k} مو محظور من قبل\n✔")
            except:
                return m.reply(f"{k} ماكو عضو بهذا اليوزر")
            m.chat.unban_member(get.user.id)
            return m.reply(f"「 {get.user.mention} 」 \n{k} تمام الغيت حظره\n✔")

    if (
        text == "رفع الحظر"
        or text == "الغاء الحظر"
        and m.reply_to_message
        and m.reply_to_message.from_user
    ):
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الأمر يخص ( المدير وفوق ) بس")
        else:
            try:
                get = m.chat.get_member(m.reply_to_message.from_user.id)
                if not get.status == ChatMemberStatus.BANNED:
                    return m.reply(
                        f"「 {m.reply_to_message.from_user.mention} 」 \n{k} مو محظور من قبل\n✔"
                    )
                m.chat.unban_member(m.reply_to_message.from_user.id)
                return m.reply(
                    f"「 {m.reply_to_message.from_user.mention} 」 \n{k} تمام الغيت حظره\n✔"
                )
            except:
                return m.reply(f"{k} العضو مو بالمجموعة")

    if text.startswith("رفع القيود ") and len(text.split()) == 3:
        if not "@" in text and not re.findall("[0-9]+", text):
            return
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الأمر يخص ( المدير وفوق ) بس")
        else:
            try:
                user = int(text.split()[2])
            except:
                user = text.split()[2].replace("@", "")
            co = 0
            text = ""
            try:
                get = m.chat.get_member(user)
                if get.status == ChatMemberStatus.BANNED:
                    m.chat.unban_member(get.user.id)
                    text += "حظر\n"
                    co += 1
                if get.status == ChatMemberStatus.RESTRICTED:
                    c.restrict_chat_member(
                        m.chat.id,
                        get.user.id,
                        ChatPermissions(
                            can_send_messages=True,
                            can_send_media_messages=True,
                            can_send_other_messages=True,
                            can_send_polls=True,
                            can_invite_users=True,
                            can_add_web_page_previews=True,
                            can_change_info=True,
                            can_pin_messages=True,
                        ),
                    )
                    text += "تقييد\n"
                    co += 1
                if r.get(f"{get.user.id}:mute:{m.chat.id}{Dev_Neptune}"):
                    r.delete(f"{get.user.id}:mute:{m.chat.id}{Dev_Neptune}")
                    r.srem(f"{m.chat.id}:listMUTE:{Dev_Neptune}", get.user.id)
                    text += "كتم\n"
                    co += 1
                if co > 0:
                    return m.reply(f"رفعت القيود التالية:\n{text}\n✔")
                else:
                    return m.reply(f"「 {get.user.mention} 」\n{k} ماله قيود من قبل\n✔")

            except:
                return m.reply(f"{k} ماكو عضو بهذا اليوزر")
            m.chat.unban_member(get.user.id)
            return m.reply(f"「 {get.user.mention} 」 \n{k} تمام الغيت حظره\n✔")

    if text == "رفع القيود" and m.reply_to_message and m.reply_to_message.from_user:
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الأمر يخص ( المدير وفوق ) بس")
        else:
            try:
                text = ""
                co = 0
                get = m.chat.get_member(m.reply_to_message.from_user.id)
                if get.status == ChatMemberStatus.BANNED:
                    m.chat.unban_member(get.user.id)
                    text += "حظر\n"
                    co += 1
                if get.status == ChatMemberStatus.RESTRICTED:
                    c.restrict_chat_member(
                        m.chat.id,
                        get.user.id,
                        ChatPermissions(
                            can_send_messages=True,
                            can_send_media_messages=True,
                            can_send_other_messages=True,
                            can_send_polls=True,
                            can_invite_users=True,
                            can_add_web_page_previews=True,
                            can_change_info=True,
                            can_pin_messages=True,
                        ),
                    )
                    text += "تقييد\n"
                    co += 1
                if r.get(f"{get.user.id}:mute:{m.chat.id}{Dev_Neptune}"):
                    r.delete(f"{get.user.id}:mute:{m.chat.id}{Dev_Neptune}")
                    r.srem(f"{m.chat.id}:listMUTE:{Dev_Neptune}", get.user.id)
                    text += "كتم\n"
                    co += 1
                if co > 0:
                    return m.reply(f"رفعت القيود التالية:\n{text}\n✔")
                else:
                    return m.reply(f"「 {get.user.mention} 」\n{k} ماله قيود من قبل\n✔")
            except:
                return m.reply(f"{k} العضو مو بالمجموعة")

    if text == "كشف البوتات":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الأمر يخص ( المدير وفوق ) بس")
        else:
            co = 0
            text = "بوتات المجموعة:\n\n"
            cc = 1
            for mm in m.chat.get_members(filter=ChatMembersFilter.BOTS):
                if co == 100:
                    break
                text += f"{cc}) {mm.user.mention}"
                if mm.status == ChatMemberStatus.ADMINISTRATOR:
                    text += "👑"
                text += "\n"
                cc += 1
                co += 1
            text += "☆"
            if co == 0:
                return m.reply(f"{k} ماكو بوتات")
            else:
                return m.reply(text)

    # كشف القيود بالرد على الرسالة
    if text == "كشف القيود" and m.reply_to_message and m.reply_to_message.from_user:
        if not admin_pls(m.from_user.id, m.chat.id):
            return m.reply(f'{k} هذا الامر يخص ( الادمن وفوق ) بس')

        get = m.reply_to_message.from_user
        mention = get.mention
        id = get.id

        # فحص جميع القيود
        restrictions = []

        # فحص الكتم المحلي
        if r.get(f'{id}:mute:{m.chat.id}{Dev_Neptune}'):
            restrictions.append("➤ مكتوم في المجموعة")

        # فحص الكتم العام
        if r.get(f'{id}:mute:{Dev_Neptune}'):
            restrictions.append("➤ مكتوم عام")

        # فحص الحظر المحلي (التحقق من عضوية المجموعة)
        try:
            member = c.get_chat_member(m.chat.id, id)
            if member.status == ChatMemberStatus.BANNED:
                restrictions.append("➤ محظور من المجموعة")
        except:
            restrictions.append("➤ محظور من المجموعة")

        # فحص الحظر العام
        if r.get(f'{id}:gban:{Dev_Neptune}'):
            restrictions.append("➤ محظور عام")

        # فحص الحظر من الألعاب
        if r.get(f'{id}:gbangames:{Dev_Neptune}'):
            restrictions.append("➤ محظور من الألعاب")

        # فحص التقييد
        try:
            member = c.get_chat_member(m.chat.id, id)
            if member.status == ChatMemberStatus.RESTRICTED:
                restrictions.append("➤ مقيد في المجموعة")
        except:
            pass

        # إعداد الرد
        if restrictions:
            result_text = f"🔍 قيود العضو:\n\n「 {mention} 」\n\n"
            for restriction in restrictions:
                result_text += f"{restriction}\n"
            result_text += "\n✔"
        else:
            result_text = f"✅ العضو نظيف:\n\n「 {mention} 」\n{k} ماله قيود\n✔"

        return m.reply(result_text)

    # كشف القيود باليوزر أو الايدي
    if re.match("^كشف القيود (.*?)$", text) and len(text.split()) == 3:
        if not '@' in text and not re.findall('[0-9]+', text):
            return
        if not admin_pls(m.from_user.id, m.chat.id):
            return m.reply(f'{k} هذا الامر يخص ( الادمن وفوق ) بس')

        user = text.split()[2]
        try:
            id = int(user)
        except:
            id = user.replace('@','')

        try:
            get = c.get_chat(user)
            mention = f'[{get.first_name}](tg://user?id={get.id})'
            id = get.id
        except:
            return m.reply(f'{k} ماكو يوزر هيج')

        # فحص جميع القيود
        restrictions = []

        # فحص الكتم المحلي
        if r.get(f'{id}:mute:{m.chat.id}{Dev_Neptune}'):
            restrictions.append("➤ مكتوم في المجموعة")

        # فحص الكتم العام
        if r.get(f'{id}:mute:{Dev_Neptune}'):
            restrictions.append("➤ مكتوم عام")

        # فحص الحظر المحلي (التحقق من عضوية المجموعة)
        try:
            member = c.get_chat_member(m.chat.id, id)
            if member.status == ChatMemberStatus.BANNED:
                restrictions.append("➤ محظور من المجموعة")
        except:
            restrictions.append("➤ محظور من المجموعة")

        # فحص الحظر العام
        if r.get(f'{id}:gban:{Dev_Neptune}'):
            restrictions.append("➤ محظور عام")

        # فحص الحظر من الألعاب
        if r.get(f'{id}:gbangames:{Dev_Neptune}'):
            restrictions.append("➤ محظور من الألعاب")

        # فحص التقييد
        try:
            member = c.get_chat_member(m.chat.id, id)
            if member.status == ChatMemberStatus.RESTRICTED:
                restrictions.append("➤ مقيد في المجموعة")
        except:
            pass

        # إعداد الرد
        if restrictions:
            result_text = f"🔍 قيود العضو:\n\n「 {mention} 」\n\n"
            for restriction in restrictions:
                result_text += f"{restriction}\n"
            result_text += "\n✔"
        else:
            result_text = f"✅ العضو نظيف:\n\n「 {mention} 」\n{k} ماله قيود\n✔"

        return m.reply(result_text)

    if text == "منو ضافني":
        get = m.chat.get_member(m.from_user.id).invited_by
        if not get:
            return m.reply(f"{k} محد ضافك")
        else:
            return m.reply(get.mention)

    if text == "بايو عشوائي":
        return m.reply(f"{k} تحت الصيانة")

    if text == "غنيلي" or text == "غ":
        # قائمة روابط الموسيقى
        music_links = [
            "https://t.me/PRrR1/69",
            "https://t.me/PRrR1/70",
            "https://t.me/PRrR1/71",
            "https://t.me/PRrR1/73",
            "https://t.me/PRrR1/75",
            "https://t.me/PRrR1/76",
            "https://t.me/PRrR1/77",
            "https://t.me/PRrR1/78"
        ]

        try:
            # اختيار رابط عشوائي
            selected_link = random.choice(music_links)

            # استخراج معرف القناة ومعرف الرسالة من الرابط
            # مثال: https://t.me/PRrR1/69 -> channel: PRrR1, message_id: 69
            link_parts = selected_link.replace("https://t.me/", "").split("/")
            channel_username = link_parts[0]
            message_id = int(link_parts[1])

            # نسخ الرسالة من القناة
            copied_message = c.copy_message(
                chat_id=m.chat.id,
                from_chat_id=channel_username,
                message_id=message_id,
                caption="- تم اختيار الاغنيه لك .",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("sᴏᴜʀᴄᴇ ᴊᴀᴄᴋ", url="https://t.me/Jack_Vib")]
                ])
            )

        except Exception as e:
            print(f"خطأ في أمر غنيلي: {e}")
            return m.reply(f"{k} عذراً، حدث خطأ في جلب الموسيقى")

        return True

    if text == "اشعرلي" or text == "ش":
        # قائمة روابط الشعر
        poetry_links = [
            "https://t.me/Sppppl/19",
            "https://t.me/Sppppl/20",
            "https://t.me/Sppppl/21",
            "https://t.me/Sppppl/22",
            "https://t.me/Sppppl/23",
            "https://t.me/Sppppl/24",
            "https://t.me/Sppppl/25",
            "https://t.me/Sppppl/26",
            "https://t.me/Sppppl/27",
            "https://t.me/Sppppl/28",
            "https://t.me/Sppppl/29",
            "https://t.me/Sppppl/30",
            "https://t.me/Sppppl/31",
            "https://t.me/Sppppl/32",
            "https://t.me/Sppppl/33",
            "https://t.me/Sppppl/34",
            "https://t.me/Sppppl/35",
            "https://t.me/Sppppl/36",
            "https://t.me/Sppppl/37"
        ]

        try:
            # اختيار رابط عشوائي
            selected_link = random.choice(poetry_links)

            # استخراج معرف القناة ومعرف الرسالة من الرابط
            # مثال: https://t.me/Sppppl/19 -> channel: Sppppl, message_id: 19
            link_parts = selected_link.replace("https://t.me/", "").split("/")
            channel_username = link_parts[0]
            message_id = int(link_parts[1])

            # نسخ الرسالة من القناة
            copied_message = c.copy_message(
                chat_id=m.chat.id,
                from_chat_id=channel_username,
                message_id=message_id,
                caption="- تم اختيار الشعر لك .",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("sᴏᴜʀᴄᴇ ᴊᴀᴄᴋ", url="https://t.me/Jack_Vib")]
                ])
            )

        except Exception as e:
            print(f"خطأ في أمر شعر: {e}")
            return m.reply(f"{k} عذراً، حدث خطأ في جلب الشعر")

        return True

    if text == "جمالي" or text == "ج":
        # توليد رقم عشوائي من 0 إلى 100
        beauty_percentage = random.randint(0, 100)

        # الرد بنسبة الجمال
        return m.reply(f"- اني اشوف نسبه جمالك هي ( {beauty_percentage} )")







    if text == "مسح" and m.reply_to_message:
        # تقييد عرض أزرار الأوامر للمبرمج فقط
        if devp_pls(m.from_user.id, m.chat.id):
            m.reply_to_message.delete()
            m.delete()
        else:
            m.delete()

    if (
        text.startswith("مسح ")
        and len(text.split()) == 2
        and re.findall("[0-9]+", text)
    ):
        count = int(re.findall("[0-9]+", text)[0])
        if not admin_pls(m.from_user.id, m.chat.id):
            return m.delete()
        else:
            if count > 400:
                return m.reply(f"{k} اختار من 1 الى 400")
            else:
                for msg in range(m.id, m.id - count, -1):
                    try:
                        c.delete_messages(m.chat.id, msg)
                    except:
                        pass

    if text == "تنزيل مشرف" and m.reply_to_message and m.reply_to_message.from_user:
        if not owner_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الأمر يخص ( المالك وفوق ) بس")
        else:
            try:
                c.promote_chat_member(
                    m.chat.id,
                    m.reply_to_message.from_user.id,
                    privileges=ChatPrivileges(
                        can_manage_chat=False,
                        can_delete_messages=False,
                        can_manage_video_chats=False,
                        can_restrict_members=False,
                        can_promote_members=False,
                        can_pin_messages=False,
                        can_change_info=False,
                        can_invite_users=False,
                    ),
                )
                return m.reply(
                    f"「 {m.reply_to_message.from_user.mention} 」\n{k} نزلته من الاشراف"
                )
            except:
                return m.reply(
                    f"「 {m.reply_to_message.from_user.mention} 」\n{k} مو انا الي رفعته او ماعندي صلاحيات"
                )

    if text == "رفع مشرف" and m.reply_to_message and m.reply_to_message.from_user:
        if not owner_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الأمر يخص ( المالك وفوق ) بس")
        else:
            get = m.chat.get_member(c.me.id)
            priv = get.privileges
            if (
                not priv.can_manage_chat
                or not priv.can_delete_messages
                or not priv.can_restrict_members
                or not priv.can_pin_messages
                or not priv.can_invite_users
                or not priv.can_change_info
                or not priv.can_promote_members
            ):
                return m.reply("هات كل الصلاحيات بعدين سولف")
            else:
                r.set(
                    f"{m.from_user.id}:promote:{m.chat.id}",
                    m.reply_to_message.from_user.id,
                    ex=600,
                )
                return m.reply(
                    """
⇜ تمام هسة ارسل صلاحيات المشرف

* ⇠ لرفع كل الصلاحيات ما عدا رفع المشرفين
** ⇠ لرفع كل الصلاحيات مع رفع المشرفين

⇜ تكدر تختار الصلاحيات وتعيين لقب للمشرف في سطر واحد

مثال: ** الزمال
☆""",
                    reply_markup=ForceReply(selective=True),
                    parse_mode=ParseMode.HTML,
                )

    if r.get(f"{m.from_user.id}:promote:{m.chat.id}") and owner_pls(
        m.from_user.id, m.chat.id
    ):
        id = int(r.get(f"{m.from_user.id}:promote:{m.chat.id}"))
        if text.startswith("*"):
            r.delete(f"{m.from_user.id}:promote:{m.chat.id}")
            if text.startswith("**"):
                can_promote_members = True
                type = 1
            else:
                can_promote_members = False
                type = 0
            if len(text.split()) > 1:
                title = text.split(None, 1)[1][:15:]
            else:
                title = None
            c.promote_chat_member(
                m.chat.id,
                id,
                privileges=ChatPrivileges(
                    can_manage_chat=True,
                    can_delete_messages=True,
                    can_manage_video_chats=True,
                    can_restrict_members=True,
                    can_promote_members=can_promote_members,
                    can_change_info=True,
                    can_invite_users=True,
                    can_pin_messages=True,
                ),
            )
            if title:
                try:
                    c.set_administrator_title(m.chat.id, id, title)
                except:
                    pass
            get = m.chat.get_member(id)
            if type == 1:
                r.set(f"{m.chat.id}:rankADMIN:{get.user.id}{Dev_Neptune}", 1)
                r.sadd(f"{m.chat.id}:listADMIN:{Dev_Neptune}", get.user.id)
                return m.reply(
                    f"الحلو 「 {get.user.mention} 」\n{k} رفعته مشرف بكل صلاحيات "
                )
            else:
                r.set(f"{m.chat.id}:rankADMIN:{get.user.id}{Dev_Neptune}", 1)
                r.sadd(f"{m.chat.id}:listADMIN:{Dev_Neptune}", get.user.id)
                return m.reply(
                    f"الحلو 「 {get.user.mention} 」\n{k} رفعته مشرف بكل الصلاحيات عدا رفع المشرفين"
                )

    if text == "مسح قائمة التثبيت":
        if not mod_pls(m.from_user.id, m.chat.id):
            return m.reply(f"{k} هذا الأمر يخص ( المدير وفوق ) بس")
        else:
            c.unpin_all_chat_messages(m.chat.id)
            return m.reply(f"{k} تمام مسحت قائمة التثبيت")

    if (
        text == "الاوامر"
        or text.lower() == "/commands"
        or text.lower() == f"/commands@{botUsername.lower()}"
    ):
        if admin_pls(m.from_user.id, m.chat.id):
            channel = (
                r.get(f"{Dev_Neptune}:BotChannel")
                if r.get(f"{Dev_Neptune}:BotChannel")
                else "ltsMIKEY"
            )
            return m.reply(
                f"⌔︙اوامــر البــوت الرئيسيـة\n—————————————\n⌔︙م1 ← اوامر الادمنـية\n⌔︙م2 ← اوامر الاعـدادات \n⌔︙م3 ← اوامر القـفل والفـتح \n⌔︙م4 ← اوامر الالعـاب \n—————————————\n⌔︙اختر ماتريد عرضه من القائمة :",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "- 𝟭 -", callback_data=f"commands1:{m.from_user.id}"
                            ),
                            InlineKeyboardButton(
                                "- 𝟮 -", callback_data=f"commands2:{m.from_user.id}"
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                "- 𝟯 -", callback_data=f"commands3:{m.from_user.id}"
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                "- 𝟰 -", callback_data=f"commands4:{m.from_user.id}"
                            ),
                            InlineKeyboardButton(
                                "- 𝟱 -", callback_data=f"commands5:{m.from_user.id}"
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                "- اليوتيوب -", callback_data=f"commands6:{m.from_user.id}"
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                "- البنك -", callback_data=f"commands7:{m.from_user.id}"
                            ),
                            InlineKeyboardButton(
                                "- الزواج -", callback_data=f"commands8:{m.from_user.id}"
                            ),
                        ],
                    ]
                ),
            )
        else:
            return m.reply(f"{k} هذا الأمر يخص ( الادمن وفوق ) بس")


@Client.on_callback_query(group=1)
def CallbackQueryHandler(c, m):
    channel = (
        r.get(f"{Dev_Neptune}:BotChannel") if r.get(f"{Dev_Neptune}:BotChannel") else "ltsMIKEY"
    )
    Thread(target=CallbackQueryResponse, args=(c, m, channel)).start()


def CallbackQueryResponse(c, m, channel):
    k = r.get(f"{Dev_Neptune}:botkey")
    if m.data == f"commands1:{m.from_user.id}":
        m.edit_message_text(
            f"""
❨ اوامر الرفع والتنزيل ❩

⌯ رفع ↣ ↢ تنزيل مطور اساسي
⌯ رفع ↣ ↢ تنزيل مطور ثانوي
⌯ رفع ↣ ↢ تنزيل مشرف
⌯ رفع ↣ ↢ تنزيل مالك اساسي
⌯ رفع ↣ ↢ تنزيل مالك
⌯ رفع ↣ ↢ تنزيل مدير
⌯ رفع ↣ ↢ تنزيل ادمن
⌯ رفع ↣ ↢ تنزيل مميز
⌯ تنزيل الكل  ↢ بالرد  ↢ لتنزيل الشخص من جميع رتبه
⌯ مسح الكل  ↢ بدون رد  ↢ لتنزيل كل رتب المجموعة

❨ اوامر المسح ❩

⌯ مسح المطورين الاساسيين
⌯ مسح المطورين الثانويين
⌯ مسح المالكيين
⌯ مسح المدراء
⌯ مسح الادمنيه
⌯ مسح المميزين
⌯ مسح المحظورين
⌯ مسح المكتومين
⌯ مسح قائمة المنع
⌯ مسح رتبه
⌯ مسح الرتب
⌯ مسح الردود
⌯ مسح الاوامر
⌯ مسح + العدد
⌯ مسح بالرد
⌯ مسح الترحيب
⌯ مسح قائمة التثبيت

❨ اوامر الطرد الحظر الكتم ❩

⌯ حظر ↢ ❨ بالرد،بالمعرف،بالايدي ❩
⌯ طرد ↢ ❨ بالرد،بالمعرف،بالايدي ❩
⌯ كتم ↢ ❨ بالرد،بالمعرف،بالايدي ❩
⌯ تقيد ↢ ❨ بالرد،بالمعرف،بالايدي ❩
⌯ الغاء الحظر ↢ ❨ بالرد،بالمعرف،بالايدي ❩
⌯ الغاء الكتم ↢ ❨ بالرد،بالمعرف،بالايدي ❩
⌯ الغاء التقييد ↢ ❨ بالرد،بالمعرف،بالايدي ❩
⌯ رفع القيود ↢ لحذف الكتم,الحظر,التقييد
⌯ منع الكلمة
⌯ منع بالرد على قيف او ستيكر
⌯ الغاء منع الكلمة
⌯ طرد البوتات
⌯ كشف البوتات
⌯ كشف القيود ↢ ❨ بالرد،بالمعرف،بالايدي ❩

❨ اوامر النطق ❩

⌯ انطقي + الكلمة
⌯ شنو يكول؟ + بالرد على فويس لترجمه المحتوى

❨ اوامر اخرى ❩

⌯ الرابط
⌯ معلومات الرابط
⌯ انشاء رابط
⌯ بايو
⌯ بايو عشوائي
⌯ ايدي
⌯ الانشاء
⌯ مجموعاتي
⌯ ابلاغ
⌯ نقل ملكية
⌯ صوره
⌯ افتاري
⌯ افتار + باليوزر او الرد
⌯ منو ضافني؟
⌯ شازام، قرآن، سورة + اسم السورة
""",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("- الادمنية ‣ -", callback_data="None"),
                        InlineKeyboardButton(
                            "- الاعدادات -", callback_data=f"commands2:{m.from_user.id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "- قفل او الفتح -", callback_data=f"commands3:{m.from_user.id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "- الالعاب -", callback_data=f"commands4:{m.from_user.id}"
                        ),
                        InlineKeyboardButton(
                            "- التسلية -", callback_data=f"commands5:{m.from_user.id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "- اليوتيوب -", callback_data=f"commands6:{m.from_user.id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "- البنك -", callback_data=f"commands7:{m.from_user.id}"
                        ),
                        InlineKeyboardButton(
                            "- الزواج -", callback_data=f"commands8:{m.from_user.id}"
                        ),
                    ],
                ]
            ),
        )
        return

    if m.data == f"commands2:{m.from_user.id}":
        m.edit_message_text(
            f"""
❨ اوامر الوضع ❩

⌯ وضع ترحيب
⌯ وضع قوانين
⌯ تغيير رتبه
⌯ تغيير امر

❨ اوامر رؤية الاعدادات ❩

⌯ المطورين الاساسيين
⌯ المطورين الثانويين
⌯ المالكيين الاساسيين
⌯ المالكيين
⌯ الادمنيه
⌯ المدراء
⌯ المشرفين
⌯ المميزين
⌯ القوانين
⌯ قائمه المنع
⌯ المكتومين
⌯ المطور
⌯ معلوماتي
⌯ الاعدادت
⌯ المجموعه
⌯ الساعه
⌯ التاريخ
⌯ صلاحياتي
⌯ لقبي
⌯ صلاحياته + بالرد

❨ اوامر مسح الميديا ❩

⌯ امسح ↢ مسح جميع الميديا من المحادثة
⌯ عدد الميديا ↢ عرض إحصائيات الميديا
⌯ تفعيل المسح التلقائي ↢ تفعيل المسح التلقائي
⌯ تعطيل المسح التلقائي ↢ تعطيل المسح التلقائي
⌯ تعيين المسح التلقائي + العدد ↢ تعيين حد المسح التلقائي
⌯ اعدادات المسح ↢ عرض جميع إعدادات المسح

❨ اوامر المميز التلقائي ❩

⌯ تفعيل مميز تلقائي ↢ تفعيل الترقية التلقائية للمميز
⌯ تعطيل مميز تلقائي ↢ تعطيل الترقية التلقائية للمميز
⌯ مميز ↢ كتابة هذه الكلمة ترقي العضو تلقائياً لمميز

❨ اوامر التاك التلقائي ❩

⌯ تفعيل التاك التلقائي ↢ تفعيل التاك التلقائي للأعضاء كل 10 ثواني يسوي تاك
⌯ تعطيل التاك التلقائي ↢ تعطيل التاك التلقائي

❨ اوامر الوضع الليلي ❩

⌯ الوضع الليلي ↢ إدارة الوضع الليلي (للمالك الأساسي وفوق فقط)
⌯ يمنع الوضع الليلي إرسال المحتوى المحدد من المالك وما دون
⌯ يتحكم بالروابط، التوجيه، الجهات، الصور، الفيديو، المتحركات، الملصقات، الملفات
⌯ يعني اي شخص رتبته ليس مالك اساسي ميكدر يدز الاشياء المقفوله في الوضع الليلي
""",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "- الادمنية -", callback_data=f"commands1:{m.from_user.id}"
                        ),
                        InlineKeyboardButton("- الاعدادات ‣ -", callback_data="None"),
                    ],
                    [
                        InlineKeyboardButton(
                            "- قفل او فتح -", callback_data=f"commands3:{m.from_user.id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "- الالعاب -", callback_data=f"commands4:{m.from_user.id}"
                        ),
                        InlineKeyboardButton(
                            "- التسلية -", callback_data=f"commands5:{m.from_user.id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "- اليوتيوب -", callback_data=f"commands6:{m.from_user.id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "- البنك -", callback_data=f"commands7:{m.from_user.id}"
                        ),
                        InlineKeyboardButton(
                            "- الزواج -", callback_data=f"commands8:{m.from_user.id}"
                        ),
                    ],
                ]
            ),
        )
        return

    if m.data == f"commands3:{m.from_user.id}":
        m.edit_message_text(
            f"""
❨ اوامر الردود ❩

⌯ الردود ↢ تشوف كل الردود المضافه
⌯ الردود المتعدده ↢ تشوف كل الردود المتعدده المضافه
⌯ اضف رد ↢ علمود تضيف رد
⌯ اضف رد متعدد ↢ علمود تضيف أكثر من رد
⌯ اضف رد متعدد ↢ خاص بالاعضاء
⌯ حذف رد ↢ علمود تمسح الرد
⌯ حذف رد متعدد ↢ علمود تمسح رد متعدد
⌯ مسح ردي ↢ علمود تمسح ردك اذا كان بردود الأعضاء
⌯ مسح الردود ↢ تمسح كل الردود
⌯ مسح الردود المتعدده ↢ علمود تمسح كل الردود المتعدده
⌯ الرد + كلمة الرد
-

❨ اوامر القفل والفتح بالمسح ❩

⌯ قفل ↣ ↢ فتح  التعديل
⌯ قفل ↣ ↢ فتح  الفويسات
⌯ قفل ↣ ↢ فتح  الفيديو
⌯ قفل ↣ ↢ فتح  الـصــور
⌯ قفل ↣ ↢ فتح  الملصقات
⌯ قفل ↣ ↢ فتح  الدخول
⌯ قفل ↣ ↢ فتح  الفارسية
⌯ قفل ↣ ↢ فتح  الملفات
⌯ قفل ↣ ↢ فتح  المتحركات
⌯ قفل ↣ ↢ فتح  تعديل الميديا
⌯ قفل ↣ ↢ فتح  تعديل الميديا بالتقييد
⌯ قفل ↣ ↢ فتح  الدردشه
⌯ قفل ↣ ↢ فتح  الروابط
⌯ قفل ↣ ↢ فتح  الهشتاق
⌯ قفل ↣ ↢ فتح  البوتات
⌯ قفل ↣ ↢ فتح  اليوزرات
⌯ قفل ↣ ↢ فتح  الاشعارات
⌯ قفل ↣ ↢ فتح  الكلام الكثير
⌯ قفل ↣ ↢ فتح  التكرار
⌯ قفل ↣ ↢ فتح  التوجيه
⌯ قفل ↣ ↢ فتح  الانلاين
⌯ قفل ↣ ↢ فتح  الجهات
⌯ قفل ↣ ↢ فتح  الــكـــل
⌯ قفل ↣ ↢ فتح  السب
⌯ قفل ↣ ↢ فتح  الاضافه
⌯ قفل ↣ ↢ فتح  الصوت
⌯ قفل ↣ ↢ فتح  القنوات
⌯ قفل ↣ ↢ فتح الايراني
⌯ قفل ↣ ↢ فتح الإباحي

❨ اوامر التفعيل والتعطيل ❩

⌯ تفعيل ↣ ↢ تعطيل الترحيب
⌯ تفعيل ↣ ↢ تعطيل الترحيب بالصورة
⌯ تفعيل ↣ ↢ تعطيل الردود
⌯ تفعيل ↣ ↢ تعطيل ردود الاعضاء
⌯ تفعيل ↣ ↢ تعطيل الايدي
⌯ تفعيل ↣ ↢ تعطيل الرابط
⌯ تفعيل ↣ ↢ تعطيل اطردني
⌯ تفعيل ↣ ↢ تعطيل الحماية
⌯ تفعيل ↣ ↢ تعطيل المنشن
⌯ تفعيل ↣ ↢ تعطيل التحقق
⌯ تفعيل ↣ ↢ تعطيل ردود المطور
⌯ تفعيل ↣ ↢ تعطيل التحذير
⌯ تفعيل ↣ ↢ تعطيل البايو
⌯ تفعيل ↣ ↢ تعطيل انطقي
⌯ تفعيل ↣ ↢ تعطيل شازام
""",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "- الادمنية -", callback_data=f"commands1:{m.from_user.id}"
                        ),
                        InlineKeyboardButton(
                            "- الاعدادات -", callback_data=f"commands2:{m.from_user.id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton("- قفل او فتح ‣ -", callback_data="None"),
                    ],
                    [
                        InlineKeyboardButton(
                            "- الالعاب -", callback_data=f"commands4:{m.from_user.id}"
                        ),
                        InlineKeyboardButton(
                            "- التسلية -", callback_data=f"commands5:{m.from_user.id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "- اليوتيوب -", callback_data=f"commands6:{m.from_user.id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "- البنك -", callback_data=f"commands7:{m.from_user.id}"
                        ),
                        InlineKeyboardButton(
                            "- الزواج -", callback_data=f"commands8:{m.from_user.id}"
                        ),
                    ],
                ]
            ),
        )
        return

    if m.data == f"commands4:{m.from_user.id}":
        m.edit_message_text(
            """
☤ تفعيل الالعاب
☤ تعطيل الالعاب
    ╼╾
✽ جمل
✽ كلمات
✽ اغاني
✽ دين
✽ عربي
✽ اكمل
✽ صور
✽ كت تويت
✽ مؤقت
✽ اعلام
✽ معاني
✽ تخمين
✽ احكام
✽ ارقام
✽ احسب
✽ خواتم
✽ انقليزي
✽ ترتيب
✽ انمي
✽ تركيب
✽ تفكيك
✽ عواصم
✽ روليت
✽ سيارات
✽ ايموجي
✽ حجره
✽ تشفير
✽ كره قدم
✽ ديمون
✽ اكس او
✽ جمالي
╼╾
❖ فلوسي ↼ علمود تشوف فلوسك
❖ بيع فلوسي + العدد ↼ للأستبدال
""",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "- الادمنية -", callback_data=f"commands1:{m.from_user.id}"
                        ),
                        InlineKeyboardButton(
                            "- الاعدادات -", callback_data=f"commands2:{m.from_user.id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "- قفل او فتح -", callback_data=f"commands3:{m.from_user.id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton("- الالعاب ‣ -", callback_data="None"),
                        InlineKeyboardButton(
                            "- التسلية -", callback_data=f"commands5:{m.from_user.id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "- اليوتيوب -", callback_data=f"commands6:{m.from_user.id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "- البنك -", callback_data=f"commands7:{m.from_user.id}"
                        ),
                        InlineKeyboardButton(
                            "- الزواج -", callback_data=f"commands8:{m.from_user.id}"
                        ),
                    ],
                ]
            ),
        )
        return

    if m.data == f"commands5:{m.from_user.id}":
        m.edit_message_text(
            f"""
⌯ رفع ↣ ↢ تنزيل كيكه
⌯ رفع ↣ ↢ تنزيل عسل
⌯ رفع ↣ ↢ تنزيل زق
⌯ رفع ↣ ↢ تنزيل نصاب
⌯ فع ↣ ↢ تنزيل حمار
⌯ رفع ↣ ↢ تنزيل بقره
⌯ رفع ↣ ↢ تنزيل كلب
⌯ رفع ↣ ↢ تنزيل قرد
⌯ رفع ↣ ↢ تنزيل تيس
⌯ رفع ↣ ↢ تنزيل ثور
⌯ رفع ↣ ↢ تنزيل هكر
⌯ رفع ↣ ↢ تنزيل دجاجه
⌯ رفع ↣ ↢ تنزيل ملكه
⌯ رفع ↣ ↢ تنزيل صياد
⌯ رفع ↣ ↢ تنزيل خاروف
⌯ رفع لقلبي ↣ ↢ تنزيل من قلبي

⌯ قائمة الكيك
⌯ قائمة العسل
⌯ قائمة الزق
⌯ قائمة النصابين
⌯ قائمة الحمير
⌯ قائمة البقر
⌯ قائمة الكلاب
⌯ قائمة القرود
⌯ قائمة التيس
⌯ قائمة الثور
⌯ قائمة الهكر
⌯ قائمة الدجاج
⌯ قائمة الهطوف
⌯ قائمة الصيادين
⌯ قائمة الخرفان

⌯ غنيلي ↢ يختار لك موسيقى عشوائية
⌯ غ ↢ اختصار لأمر غنيلي

⌯ شعر ↢ يختار لك شعر عشوائي
⌯ ش ↢ اختصار لأمر شعر

⌯ جمالي ↢ يقيس نسبة جمالك
⌯ ج ↢ اختصار لأمر جمالي

 ❨ اوامر التاك المخصص ❩

⌯ اضف تاك ↢ لإضافة تاك مخصص للأعضاء
⌯ التاكات ↢ لعرض قائمة التاكات المحفوظة
⌯ حذف تاك ↢ لحذف تاك معين
⌯ مسح التاكات ↢ لمسح جميع التاكات (المالك فقط)
⌯ اوامر التاك ↢ لعرض مساعدة التاك المخصص
⌯ الغاء ↢ لإلغاء العملية الحالية
""",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "- الادمنية -", callback_data=f"commands1:{m.from_user.id}"
                        ),
                        InlineKeyboardButton(
                            "- الاعدادات -", callback_data=f"commands2:{m.from_user.id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "- قفل او فتح -", callback_data=f"commands3:{m.from_user.id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "- الالعاب -", callback_data=f"commands4:{m.from_user.id}"
                        ),
                        InlineKeyboardButton("- التسلية ‣ -", callback_data="None"),
                    ],
                    [
                        InlineKeyboardButton(
                            "- اليوتيوب -", callback_data=f"commands6:{m.from_user.id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "- البنك -", callback_data=f"commands7:{m.from_user.id}"
                        ),
                        InlineKeyboardButton(
                            "- الزواج -", callback_data=f"commands8:{m.from_user.id}"
                        ),
                    ],
                ]
            ),
        )
        return

    if m.data == f"commands6:{m.from_user.id}":
        m.edit_message_text(
            """
⚘ اليـوتيوب

تفعيل اليوتيوب
تعطيل اليوتيوب

❋ البـحث عن اغنية ↓

بحث اسم الاغنية

يوت اسم الاغنية
⚘ الساوند كلاود

تفعيل الساوند
تعطيل الساوند

❋ البـحث عن اغنية ↓

رابط الاغنية أو ساوند + اسم الاغنية


⚘ التيك توك

تفعيل التيك
تعطيل للتيك

❋ للتحميل من التيك ↓

تيك ورابط المقطع
""",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "- الادمنية -", callback_data=f"commands1:{m.from_user.id}"
                        ),
                        InlineKeyboardButton(
                            "- الاعدادات -", callback_data=f"commands2:{m.from_user.id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "- قفل او فتح -", callback_data=f"commands3:{m.from_user.id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "- الالعاب -", callback_data=f"commands4:{m.from_user.id}"
                        ),
                        InlineKeyboardButton(
                            "- التسلية -", callback_data=f"commands5:{m.from_user.id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton("- اليوتيوب ‣ -", callback_data="None"),
                    ],
                    [
                        InlineKeyboardButton(
                            "- البنك -", callback_data=f"commands7:{m.from_user.id}"
                        ),
                        InlineKeyboardButton(
                            "- الزواج -", callback_data=f"commands8:{m.from_user.id}"
                        ),
                    ],
                ]
            ),
        )
        return

    if m.data == f"commands7:{m.from_user.id}":
        m.edit_message_text(
            """
✜ اوامر البنك

⌯ انشاء حساب بنكي  ↢ تسوي حساب وتكدر تحول فلوس مع مزايا ثانيه

⌯ مسح حساب بنكي  ↢ تلغي حسابك البنكي

⌯ تحويل ↢ تطلب رقم حساب الشخص وتحول له فلوس

⌯ حسابي  ↢ يطلع لك رقم حسابك علمود تعطيه للشخص اللي بيحول لك

⌯ فلوسي ↢ يعلمك كم فلوسك

⌯ راتب ↢ ينطيك راتبك كل ٥ دقيقة

⌯ بخشيش ↢ ينطيك بخشيش كل ٥ دقايق

⌯ خمط ↢ تخمط فلوس اشخاص كل ٥ دقايق

⌯ كنز ↢ ينطيك كنز كل ١٠ دقايق

⌯ استثمار ↢ تستثمر بالمبلغ اللي تريده مع نسبة ربح مضمونه من ١٪؜ الى ١٥٪؜ ( او استثمار فلوسي )

⌯ حظ ↢ تلعبها بأي مبلغ ياتدبله ياتخسره انت وحظك ( او حظ فلوسي )

⌯ عجله ↢ تلعب عجله الحظ ولو تشابهو ال ٣ ايموجيات تكسب من ١٠٠ الف لحد ٣٠٠ الف انت وحظك

⌯ توب الفلوس ↢ يطلع توب اكثر ناس وياهم فلوس بكل الكروبات

⌯ توب الحراميه ↢ يطلع لك اكثر ناس خمطوا
""",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "- الادمنية -", callback_data=f"commands1:{m.from_user.id}"
                        ),
                        InlineKeyboardButton(
                            "- الاعدادات -", callback_data=f"commands2:{m.from_user.id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "- قفل او فتح -", callback_data=f"commands3:{m.from_user.id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "- الالعاب -", callback_data=f"commands4:{m.from_user.id}"
                        ),
                        InlineKeyboardButton(
                            "- التسلية -", callback_data=f"commands5:{m.from_user.id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "- اليوتيوب -", callback_data=f"commands6:{m.from_user.id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton("- البنك ‣ -", callback_data="None"),
                        InlineKeyboardButton(
                            "- الزواج -", callback_data=f"commands8:{m.from_user.id}"
                        ),
                    ],
                ]
            ),
        )
        return

    if m.data == f"commands8:{m.from_user.id}":
        m.edit_message_text(
            """
✜ اوامر الزواج

⌯ زواج  ↢ يطلب الزواج من الشخص (يحتاج موافقة العروس)

⌯ زوجني  ↢ يزوجك من شخص عشوائي من المجموعة

⌯ زز  ↢ اختصار لأمر زوجني (زواج عشوائي)

⌯ زواجي  ↢ يطلع وثيقة زواجك اذا متزوج

⌯ طلاق ↢ يطلقك اذا متزوج

⌯ طط  ↢ اختصار لأمر طلاق

⌯ طلكني  ↢ يطلقك زوجك

⌯ المتزوجين ↢ لعرض المتزوجين في المجموعة
""",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "- الادمنية -", callback_data=f"commands1:{m.from_user.id}"
                        ),
                        InlineKeyboardButton(
                            "- الاعدادات -", callback_data=f"commands2:{m.from_user.id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "- قفل او فتح -", callback_data=f"commands3:{m.from_user.id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "- الالعاب -", callback_data=f"commands4:{m.from_user.id}"
                        ),
                        InlineKeyboardButton(
                            "- التسلية -", callback_data=f"commands5:{m.from_user.id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "- اليوتيوب -", callback_data=f"commands6:{m.from_user.id}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "- البنك -", callback_data=f"commands7:{m.from_user.id}"
                        ),
                        InlineKeyboardButton("- الزواج ‣ -", callback_data="None"),
                    ],
                ]
            ),
        )
        return

    if m.data == "delAdminMSG":
        if str(m.from_user.id) in m.message.text.html:
            return m.message.delete()

    if m.data == f"yes:{m.from_user.id}":
        try:
            c.restrict_chat_member(
                m.message.chat.id,
                m.from_user.id,
                ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_send_polls=True,
                    can_invite_users=True,
                    can_add_web_page_previews=True,
                    can_change_info=True,
                    can_pin_messages=True,
                ),
            )
        except:
            return False
        m.edit_message_text(
            f"""
{k} تم التحقق منك وطلعت مو زومبي
{k} هسة تكدر تسولف بالكروب
☆
""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("sᴏᴜʀᴄᴇ ᴊᴀᴄᴋ", url=f"t.me/{channel}")]]
            ),
        )

    if m.data == f"no:{m.from_user.id}":
        return m.edit_message_text(
            f"""
{k} للأسف طلعت زومبي 🧟‍♀️
{k} مالك غير تنطر حد من المشرفين يجي يتوسطلك
☆
""",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "رفع التقييد والسماح",
                            callback_data=f"yesVER:{m.from_user.id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "طرد", callback_data=f"noVER:{m.from_user.id}"
                        )
                    ],
                ]
            ),
        )

    if m.data.startswith("yesVER"):
        user_id = int(m.data.split(":")[1])
        if not admin_pls(m.from_user.id, m.message.chat.id):
            return m.answer(f"{k} هذا الزر يخص ( الادمن وفوق ) بس", show_alert=True)
        else:
            m.edit_message_text(f"{k} توسطلك واحد من الادمن ورفعت عنك القيود")
            try:
                c.restrict_chat_member(
                    m.message.chat.id,
                    user_id,
                    ChatPermissions(
                        can_send_messages=True,
                        can_send_media_messages=True,
                        can_send_other_messages=True,
                        can_send_polls=True,
                        can_invite_users=True,
                        can_add_web_page_previews=True,
                        can_change_info=True,
                        can_pin_messages=True,
                    ),
                )
            except:
                return False

    if m.data.startswith("noVER"):
        user_id = int(m.data.split(":")[1])
        if not admin_pls(m.from_user.id, m.message.chat.id):
            return m.answer(f"{k} هذا الزر يخص ( الادمن وفوق ) بس", show_alert=True)
        else:
            m.edit_message_text(f"{k} انقلع برا الكروب يلا")
            try:
                m.message.chat.ban_member(user_id)
                m.message.chat.unban_member(user_id)
            except:
                pass

    if m.data == "yes:del:bank":
        if not devp_pls(m.from_user.id, m.message.chat.id):
            return m.answer("تعجبني ثقتك")
        else:
            m.edit_message_text("تمام صفرت البنك")
            keys = r.keys("*:Floos")
            for a in keys:
                r.delete(a)
            for a in r.keys("*:BankWait"):
                r.delete(a)
            for a in r.keys("*:BankWaitB5"):
                r.delete(a)
            for a in r.keys("*:BankWaitZRF"):
                r.delete(a)
            for a in r.keys("*:BankWaitEST"):
                r.delete(a)
            for a in r.keys("*:BankWaitHZ"):
                r.delete(a)
            for a in r.keys("*:BankWait3JL"):
                r.delete(a)
            for a in r.keys("*:Zrf"):
                r.delete(a)
            r.delete("BankTop")
            r.delete("BankTopZRF")
            return True

    if m.data == "no:del:bank":
        if not devp_pls(m.from_user.id, m.message.chat.id):
            return m.answer("تعجبني ثقتك")
        else:
            m.message.delete()

    if m.data == f"topfloos:{m.from_user.id}":
        if not r.smembers("BankList"):
            return m.answer(f"{k} ماكو حسابات بالبنك", show_alert=True)
        else:
            rep = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("‣ 💸", callback_data="None"),
                        InlineKeyboardButton(
                            "توب الحرامية 💰", callback_data=f"topzrf:{m.from_user.id}"
                        ),
                    ],
                    [InlineKeyboardButton("sᴏᴜʀᴄᴇ ᴊᴀᴄᴋ", url=f"t.me/{channel}")],
                ]
            )
            if r.get("BankTop"):
                text = r.get("BankTop")
                if not r.get(f"{m.from_user.id}:Floos"):
                    floos = 0
                else:
                    floos = int(r.get(f"{m.from_user.id}:Floos"))
                get = r.ttl("BankTop")
                wait = time.strftime("%M:%S", time.gmtime(get))
                text += "\n━━━━━━━━━"
                text += f"\n# You ) {floos:,} 💸 l {m.from_user.first_name}"
                text += f"\n\n[قوانين التُوب](https://t.me/{botUsername}?start=rules)"
                text += f"\n\nالقائمة تتحدث بعد {wait} دقيقة"
                return m.edit_message_text(
                    text, disable_web_page_preview=True, reply_markup=rep
                )
            else:
                users = []
                ccc = 0
                for user in r.smembers("BankList"):
                    ccc += 1
                    id = int(user)
                    if r.get(f"{id}:bankName"):
                        name = r.get(f"{id}:bankName")[:10]
                    else:
                        try:
                            name = c.get_chat(id).first_name
                            r.set(f"{id}:bankName", name)
                        except:
                            name = "INVALID_NAME"
                            r.set(f"{id}:bankName", name)
                    if not r.get(f"{id}:Floos"):
                        floos = 0
                    else:
                        floos = int(r.get(f"{id}:Floos"))
                    users.append({"name": name, "money": floos})
                top = get_top(users)
                text = "توب 20 اغنى اشخاص:\n\n"
                count = 0
                for user in top:
                    count += 1
                    if count == 21:
                        break
                    emoji = get_emoji_bank(count)
                    floos = user["money"]
                    name = user["name"]
                    text += f'**{emoji}{floos:,}** 💸 l {name.replace("*","").replace("`","").replace("|","").replace("#","").replace("<","").replace(">","").replace("_","")}\n'
                r.set("BankTop", text, ex=300)
                if not r.get(f"{m.from_user.id}:Floos"):
                    floos_from_user = 0
                else:
                    floos_from_user = int(r.get(f"{m.from_user.id}:Floos"))
                text += "\n━━━━━━━━━"
                text += f"\n# You ) {floos_from_user:,} 💸 l {m.from_user.first_name}"
                text += f"\n\n[قوانين التُوب](https://t.me/{botUsername}?start=rules)"
                get = r.ttl("BankTop")
                wait = time.strftime("%M:%S", time.gmtime(get))
                text += f"\n\nالقائمة تتحدث بعد {wait} دقيقة"
                m.edit_message_text(
                    text, disable_web_page_preview=True, reply_markup=rep
                )

    if m.data == f"topzrf:{m.from_user.id}":
        if not r.smembers("BankList"):
            return m.answer(f"{k} ماكو حسابات بالبنك", show_alert=True)
        else:
            rep = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "توب الفلوس 💸", callback_data=f"topfloos:{m.from_user.id}"
                        ),
                        InlineKeyboardButton("‣ 💰", callback_data="None"),
                    ],
                    [InlineKeyboardButton("sᴏᴜʀᴄᴇ ᴊᴀᴄᴋ", url=f"t.me/{channel}")],
                ]
            )
            if r.get("BankTopZRF"):
                text = r.get("BankTopZRF")
                if not r.get(f"{m.from_user.id}:Zrf"):
                    zrf = 0
                else:
                    zrf = int(r.get(f"{m.from_user.id}:Zrf"))
                get = r.ttl("BankTopZRF")
                wait = time.strftime("%M:%S", time.gmtime(get))
                text += "\n━━━━━━━━━"
                text += f"\n# You ) {zrf:,} 💰 l {m.from_user.first_name}"
                text += f"\n\n[قوانين التُوب](https://t.me/{botUsername}?start=rules)"
                text += f"\n\nالقائمة تتحدث بعد {wait} دقيقة"
                return m.edit_message_text(
                    text, disable_web_page_preview=True, reply_markup=rep
                )
            else:
                users = []
                ccc = 0
                for user in r.smembers("BankList"):
                    ccc += 1
                    id = int(user)
                    if r.get(f"{id}:bankName"):
                        name = r.get(f"{id}:bankName")[:10]
                    else:
                        try:
                            name = c.get_chat(id).first_name
                            r.set(f"{id}:bankName", name)
                        except:
                            name = "INVALID_NAME"
                            r.set(f"{id}:bankName", name)
                    if not r.get(f"{id}:Zrf"):
                        pass
                    else:
                        zrf = int(r.get(f"{id}:Zrf"))
                        users.append({"name": name, "money": zrf})
                top = get_top(users)
                text = "توب 20 اكثر الحراميه خمطًا:\n\n"
                count = 0
                for user in top:
                    count += 1
                    if count == 21:
                        break
                    emoji = get_emoji_bank(count)
                    floos = user["money"]
                    name = user["name"]
                    text += f'**{emoji}{floos}** 💰 l {name.replace("*","").replace("`","").replace("|","").replace("#","").replace("<","").replace(">","").replace("_","")}\n'
                r.set("BankTopZRF", text, ex=300)
                if not r.get(f"{m.from_user.id}:Zrf"):
                    floos_from_user = 0
                else:
                    floos_from_user = int(r.get(f"{m.from_user.id}:Zrf"))
                text += "\n━━━━━━━━━"
                text += f"\n# You ) {floos_from_user} 💰 l {m.from_user.first_name}"
                text += f"\n\n[قوانين التُوب](https://t.me/{botUsername}?start=rules)"
                get = r.ttl("BankTopZRF")
                wait = time.strftime("%M:%S", time.gmtime(get))
                text += f"\n\nالقائمة تتحدث بعد {wait} دقيقة"
                m.edit_message_text(
                    text, disable_web_page_preview=True, reply_markup=rep
                )

    """
   if m.data == f'toplast:{m.from_user.id}':
     if not r.get(f'BankTopLast') and not r.get(f'BankTopLastZrf'):
       return m.answer(f'{k} ماكو توب اسبوع الي فات',show_alert=True)
     else:
       text = 'توب أوائل الأسبوع الي راح:\n'
       text += r.get(f'BankTopLast')
       text += '\n\nتوب حرامية الاسبوع اللي راح:\n'
       text += r.get(f'BankTopLastZrf')
       text += '\n༄'
       rep = InlineKeyboardMarkup (
         [[InlineKeyboardButton ('sᴏᴜʀᴄᴇ ᴊᴀᴄᴋ', url=f't.me/{channel}')]]
       )
       m.edit_message_text(text, disable_web_page_preview=True,reply_markup=rep)
   """

    name = r.get(f"{Dev_Neptune}:BotName") if r.get(f"{Dev_Neptune}:BotName") else "Neptune"
    if m.data == f"RPS:rock++{m.from_user.id}":
        RPS = ["paper", "scissors", "rock"]
        kk = random.choice(RPS)
        if kk == "scissors":
            if r.get(f"{m.from_user.id}:Floos"):
                get = int(r.get(f"{m.from_user.id}:Floos"))
                r.set(f"{m.from_user.id}:Floos", get + 1)
            else:
                r.set(f"{m.from_user.id}:Floos", 1)
            rep = InlineKeyboardMarkup(
                [[InlineKeyboardButton("sᴏᴜʀᴄᴇ ᴊᴀᴄᴋ", url=f"t.me/{channel}")]]
            )
            m.edit_message_text(
                f"""
أنت: 🪨
أنا: ✂️

النتيجة: ⁪⁬⁪⁬ 🏆 {m.from_user.first_name}
""",
                disable_web_page_preview=True,
                reply_markup=rep,
            )

        if kk == "paper":
            rep = InlineKeyboardMarkup(
                [[InlineKeyboardButton("sᴏᴜʀᴄᴇ ᴊᴀᴄᴋ", url=f"t.me/{channel}")]]
            )
            m.edit_message_text(
                f"""
أنت: 🪨
أنا: 📃

النتيجة: ⁪⁬⁪⁬ 🏆️ {name.replace("*","").replace("`","").replace("|","").replace("#","").replace("<","").replace(">","").replace("_","")}
""",
                disable_web_page_preview=True,
                reply_markup=rep,
            )
        if kk == "rock":
            rep = InlineKeyboardMarkup(
                [[InlineKeyboardButton("sᴏᴜʀᴄᴇ ᴊᴀᴄᴋ", url=f"t.me/{channel}")]]
            )
            m.edit_message_text(
                f"""
أنت: 🪨
أنا: 🪨

النتيجة: ⁪⁬⁪⁬ ⚖️ {name.replace("*","").replace("`","").replace("|","").replace("#","").replace("<","").replace(">","").replace("_","")}
""",
                disable_web_page_preview=True,
                reply_markup=rep,
            )

    if m.data == f"gowner+{m.from_user.id}":
        if not gowner_pls(m.from_user.id, m.message.chat.id):
            m.asnwer("هذا الامر للمالك الاساسي و فوق بس", show_alert=True)
            return m.message.delete()
        else:
            command = m.message.reply_to_message.text.split(None, 2)[2]
            r.hset(Dev_Neptune + f"locks-{m.message.chat.id}", command, 0)
            return m.edit_message_text(
                f"- تم تعيين الامر ( {command} ) للمالك الاساسي وفوق فقط"
            )

    if m.data == f"owner+{m.from_user.id}":
        if not gowner_pls(m.from_user.id, m.message.chat.id):
            m.asnwer("هذا الامر للمالك الاساسي و فوق بس", show_alert=True)
            return m.message.delete()
        else:
            command = m.message.reply_to_message.text.split(None, 2)[2]
            r.hset(Dev_Neptune + f"locks-{m.message.chat.id}", command, 1)
            return m.edit_message_text(
                f"- تم تعيين الامر ( {command} ) للمالك وفوق فقط"
            )

    if m.data == f"mod+{m.from_user.id}":
        if not gowner_pls(m.from_user.id, m.message.chat.id):
            m.asnwer("هذا الامر للمالك الاساسي و فوق بس", show_alert=True)
            return m.message.delete()
        else:
            command = m.message.reply_to_message.text.split(None, 2)[2]
            r.hset(Dev_Neptune + f"locks-{m.message.chat.id}", command, 2)
            return m.edit_message_text(
                f"- تم تعيين الامر ( {command} ) للمدير وفوق فقط"
            )

    if m.data == f"admin+{m.from_user.id}":
        if not gowner_pls(m.from_user.id, m.message.chat.id):
            m.asnwer("هذا الامر للمالك الاساسي و فوق بس", show_alert=True)
            return m.message.delete()
        else:
            command = m.message.reply_to_message.text.split(None, 2)[2]
            r.hset(Dev_Neptune + f"locks-{m.message.chat.id}", command, 3)
            return m.edit_message_text(
                f"- تم تعيين الامر ( {command} ) للادمن وفوق فقط"
            )

    if m.data == f"pre+{m.from_user.id}":
        if not gowner_pls(m.from_user.id, m.message.chat.id):
            m.asnwer("هذا الامر للمالك الاساسي و فوق بس", show_alert=True)
            return m.message.delete()
        else:
            command = m.message.reply_to_message.text.split(None, 2)[2]
            r.hset(Dev_Neptune + f"locks-{m.message.chat.id}", command, 4)
            return m.edit_message_text(
                f"- تم تعيين الامر ( {command} ) للمميز وفوق فقط"
            )

    if m.data == f"RPS:paper++{m.from_user.id}":
        RPS = ["paper", "scissors", "rock"]
        kk = random.choice(RPS)
        if kk == "rock":
            if r.get(f"{m.from_user.id}:Floos"):
                get = int(r.get(f"{m.from_user.id}:Floos"))
                r.set(f"{m.from_user.id}:Floos", get + 1)
            else:
                r.set(f"{m.from_user.id}:Floos", 1)
            rep = InlineKeyboardMarkup(
                [[InlineKeyboardButton("sᴏᴜʀᴄᴇ ᴊᴀᴄᴋ", url=f"t.me/{channel}")]]
            )
            m.edit_message_text(
                f"""
أنت: 📃
أنا: 🪨

النتيجة: ⁪⁬⁪⁬ 🏆 {m.from_user.first_name}
""",
                disable_web_page_preview=True,
                reply_markup=rep,
            )

        if kk == "scissors":
            rep = InlineKeyboardMarkup(
                [[InlineKeyboardButton("sᴏᴜʀᴄᴇ ᴊᴀᴄᴋ", url=f"t.me/{channel}")]]
            )
            m.edit_message_text(
                f"""
أنت: 📃
أنا: ✂️

النتيجة: ⁪⁬⁪⁬ 🏆️ {name.replace("*","").replace("`","").replace("|","").replace("#","").replace("<","").replace(">","").replace("_","")}
""",
                disable_web_page_preview=True,
                reply_markup=rep,
            )
        if kk == "paper":
            rep = InlineKeyboardMarkup(
                [[InlineKeyboardButton("sᴏᴜʀᴄᴇ ᴊᴀᴄᴋ", url=f"t.me/{channel}")]]
            )
            m.edit_message_text(
                f"""
أنت: 📃
أنا: 📃

النتيجة: ⁪⁬⁪⁬ ⚖️ {name.replace("*","").replace("`","").replace("|","").replace("#","").replace("<","").replace(">","").replace("_","")}
""",
                disable_web_page_preview=True,
                reply_markup=rep,
            )

    if m.data == f"RPS:scissors++{m.from_user.id}":
        RPS = ["paper", "scissors", "rock"]
        kk = random.choice(RPS)
        if kk == "paper":
            if r.get(f"{m.from_user.id}:Floos"):
                get = int(r.get(f"{m.from_user.id}:Floos"))
                r.set(f"{m.from_user.id}:Floos", get + 1)
            else:
                r.set(f"{m.from_user.id}:Floos", 1)
            rep = InlineKeyboardMarkup(
                [[InlineKeyboardButton("sᴏᴜʀᴄᴇ ᴊᴀᴄᴋ", url=f"t.me/{channel}")]]
            )
            m.edit_message_text(
                f"""
أنت: ✂️
أنا: 📃

النتيجة: ⁪⁬⁪⁬ 🏆 {m.from_user.first_name}
""",
                disable_web_page_preview=True,
                reply_markup=rep,
            )

        if kk == "rock":
            rep = InlineKeyboardMarkup(
                [[InlineKeyboardButton("sᴏᴜʀᴄᴇ ᴊᴀᴄᴋ", url=f"t.me/{channel}")]]
            )
            m.edit_message_text(
                f"""
أنت: ✂️
أنا: 🪨

النتيجة: ⁪⁬⁪⁬ 🏆️ {name.replace("*","").replace("`","").replace("|","").replace("#","").replace("<","").replace(">","").replace("_","")}
""",
                disable_web_page_preview=True,
                reply_markup=rep,
            )
        if kk == "scissors":
            rep = InlineKeyboardMarkup(
                [[InlineKeyboardButton("sᴏᴜʀᴄᴇ ᴊᴀᴄᴋ", url=f"t.me/{channel}")]]
            )
            m.edit_message_text(
                f"""
أنت: ✂️
أنا: ✂️

النتيجة: ⁪⁬⁪⁬ ⚖️ {name.replace("*","").replace("`","").replace("|","").replace("#","").replace("<","").replace(">","").replace("_","")}
""",
                disable_web_page_preview=True,
                reply_markup=rep,
            )

    # معالج أزرار لعبة إكس أو
    if m.data.startswith("XO:"):
        from helpers.xo_game import get_game_from_redis, save_game_to_redis, delete_game_from_redis

        def escape_markdown(text):
            """إزالة الرموز الخاصة من النص لتجنب مشاكل HTML/XML"""
            return text.replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')

        parts = m.data.split(":")
        action = parts[1]

        if action == "accept":
            game_id = parts[2]
            game = get_game_from_redis(r, game_id)

            if not game:
                return m.answer("⚠️ اللعبة غير موجودة أو انتهت صلاحيتها!")

            if game.player1["id"] == m.from_user.id:
                return m.answer("❌ لا يمكنك اللعب مع نفسك! انتظر شخص آخر للعب معك 🎮")

            if game.player2:
                return m.answer("⚠️ شخص آخر قبل التحدي بالفعل!")

            # إضافة اللاعب الثاني
            game.player2 = {
                "id": m.from_user.id,
                "name": m.from_user.first_name
            }
            save_game_to_redis(r, game)

            # تحديث الرسالة لبدء اللعبة
            p1_name = escape_markdown(game.player1['name'])
            p2_name = escape_markdown(game.player2['name'])
            p1_mention = f"[{p1_name}](tg://user?id={game.player1['id']})"
            p2_mention = f"[{p2_name}](tg://user?id={game.player2['id']})"

            game_text = f"🎮 **لعبة إكس أو**\n\n❌ {p1_mention} vs ⭕ {p2_mention}\n\n🎯 دور: **{p1_mention}** (❌)"

            m.edit_message_text(
                game_text,
                reply_markup=game.get_board_markup()
            )

        elif action == "move":
            row, col, game_id = int(parts[2]), int(parts[3]), parts[4]
            game = get_game_from_redis(r, game_id)

            if not game:
                return m.answer("⚠️ اللعبة غير موجودة أو انتهت صلاحيتها!")

            if not game.player2:
                return m.answer("⚠️ انتظر حتى ينضم لاعب آخر!")

            # فحص أن اللاعب من ضمن اللاعبين المسموح لهم
            if m.from_user.id not in [game.player1["id"], game.player2["id"]]:
                return m.answer("⚠️ هذه اللعبة بين لاعبين آخرين!")

            # فحص دور اللاعب
            current_player_id = game.player1["id"] if game.whose_turn else game.player2["id"]
            if m.from_user.id != current_player_id:
                return m.answer("⚠️ ليس دورك!")

            # محاولة ملء الخانة
            if not game.fill_board(m.from_user.id, (row, col)):
                return m.answer("⚠️ هذه الخانة محجوزة بالفعل!")

            # فحص الفائز
            if game.check_winner():
                p1_name = escape_markdown(game.player1['name'])
                p2_name = escape_markdown(game.player2['name'])
                winner_name = escape_markdown(game.winner['name'])

                p1_mention = f"[{p1_name}](tg://user?id={game.player1['id']})"
                p2_mention = f"[{p2_name}](tg://user?id={game.player2['id']})"
                winner_mention = f"[{winner_name}](tg://user?id={game.winner['id']})"

                game_text = f"🎮 **لعبة إكس أو**\n\n❌ {p1_mention} vs ⭕ {p2_mention}\n\n🏆 **الفائز: {winner_mention}!**"

                # إضافة فلوس للفائز
                if r.get(f"{game.winner['id']}:Floos"):
                    current_floos = int(r.get(f"{game.winner['id']}:Floos"))
                    r.set(f"{game.winner['id']}:Floos", current_floos + 50)
                else:
                    r.set(f"{game.winner['id']}:Floos", 50)

                game_text += f"\n💰 +50 دينار عراقي للفائز!"

            elif game.is_draw():
                p1_name = escape_markdown(game.player1['name'])
                p2_name = escape_markdown(game.player2['name'])
                p1_mention = f"[{p1_name}](tg://user?id={game.player1['id']})"
                p2_mention = f"[{p2_name}](tg://user?id={game.player2['id']})"

                game_text = f"🎮 **لعبة إكس أو**\n\n❌ {p1_mention} vs ⭕ {p2_mention}\n\n🤝 **تعادل!**"
                # تحديث الأزرار للتعادل
                game._update_board_keys_for_end(is_draw=True)
            else:
                # تبديل الدور
                game.whose_turn = not game.whose_turn
                current_player = game.player1 if game.whose_turn else game.player2
                current_symbol = "❌" if game.whose_turn else "⭕"

                p1_name = escape_markdown(game.player1['name'])
                p2_name = escape_markdown(game.player2['name'])
                current_name = escape_markdown(current_player['name'])

                p1_mention = f"[{p1_name}](tg://user?id={game.player1['id']})"
                p2_mention = f"[{p2_name}](tg://user?id={game.player2['id']})"
                current_mention = f"[{current_name}](tg://user?id={current_player['id']})"

                game_text = f"🎮 **لعبة إكس أو**\n\n❌ {p1_mention} vs ⭕ {p2_mention}\n\n🎯 دور: **{current_mention}** ({current_symbol})"

            save_game_to_redis(r, game)
            m.edit_message_text(
                game_text,
                reply_markup=game.get_board_markup()
            )

        elif action == "reset":
            game_id = parts[2]
            game = get_game_from_redis(r, game_id)

            if not game:
                return m.answer("⚠️ اللعبة غير موجودة أو انتهت صلاحيتها!")

            if not game.player2:
                return m.answer("⚠️ يجب أن يكون هناك لاعبان لإعادة اللعب!")

            # فحص أن اللاعب من ضمن اللاعبين المسموح لهم
            if m.from_user.id not in [game.player1["id"], game.player2["id"]]:
                return m.answer("⚠️ هذه اللعبة بين لاعبين آخرين!")

            # إعادة تعيين اللعبة
            game.reset_game()
            save_game_to_redis(r, game)

            p1_name = escape_markdown(game.player1['name'])
            p2_name = escape_markdown(game.player2['name'])
            p1_mention = f"[{p1_name}](tg://user?id={game.player1['id']})"
            p2_mention = f"[{p2_name}](tg://user?id={game.player2['id']})"

            game_text = f"🎮 **لعبة إكس أو**\n\n❌ {p1_mention} vs ⭕ {p2_mention}\n\n🎯 دور: **{p1_mention}** (❌)"

            m.edit_message_text(
                game_text,
                reply_markup=game.get_board_markup()
            )

        elif action in ["filled", "ended"]:
            return m.answer("⚠️ هذه الخانة غير متاحة!")
