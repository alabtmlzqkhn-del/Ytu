import yt_dlp, os, requests, re, time, wget, random, json
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch as Y88F8
from threading import Thread
from pyrogram import Client, filters
from pyrogram.enums import ChatType
from shazamio import Shazam
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InlineQueryResultArticle,
    InputTextMessageContent
)

try:
    from config import *
except ImportError:
    Dev_Neptune = "default"

from helpers.Ranks import admin_pls, isLockCommand
from PIL import Image, ImageFilter
from localdb import LocalDB
import logging

logging.getLogger("yt_dlp").setLevel(logging.CRITICAL)

bot_main_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cookies_path = os.path.join(bot_main_dir, "cookies.txt")

# SQLite بدل Redis
r = LocalDB(os.getenv("LOCAL_DB_PATH", "jack.db"))
ytdb = LocalDB(os.getenv("YT_DB_PATH", "ytdb.db"))
sounddb = LocalDB(os.getenv("SOUND_DB_PATH", "sounddb.db"))

shazam = Shazam()


def time_to_seconds(time_value):
    stringt = str(time_value)
    return sum(
        int(x) * 60 ** i
        for i, x in enumerate(reversed(stringt.split(":")))
    )


def Find(text):
    pattern = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(pattern, text)
    return [x[0] for x in url]


@Client.on_message(filters.text & filters.group, group=32)
def ytdownloaderHandler(c, m):
    k = r.get(f"{Dev_Neptune}:botkey") or ""
    channel = r.get(f"{Dev_Neptune}:BotChannel") or "Jack_Vib"

    Thread(
        target=yt_func_timed,
        args=(c, m, k, channel)
    ).start()


def yt_func_timed(c, m, k, channel):
    result = yt_func(c, m, k, channel)

    if result and isinstance(result, dict) and "message" in result:
        message = result["message"]
        try:
            message.edit_caption(
                f"@{channel} ~ {message.caption.split('~')[1]}"
            )
        except Exception:
            pass


def yt_func(c, m, k, channel):

    if not r.get(f"{m.chat.id}:enable:{Dev_Neptune}"):
        return

    if r.get(f"{m.from_user.id}:mute:{m.chat.id}{Dev_Neptune}"):
        return

    if r.get(f"{m.chat.id}:mute:{Dev_Neptune}") and not admin_pls(
        m.from_user.id, m.chat.id
    ):
        return

    if r.get(f"{m.from_user.id}:mute:{Dev_Neptune}"):
        return

    text = m.text

    if isLockCommand(m.from_user.id, m.chat.id, text):
        return

    # =========================
    # YouTube Search
    # =========================

    if text.startswith("بحث "):

        if r.get(f"{m.chat.id}:disableYT:{Dev_Neptune}"):
            return True

        if r.get(f":disableYT:{Dev_Neptune}"):
            return True

        query = text.split(None, 1)[1]

        processing_key = f"yt_processing:{m.from_user.id}:{query}"

        if r.get(processing_key):
            return True

        r.set(processing_key, 1, ex=30)

        try:

            results = Y88F8(
                query,
                max_results=1
            ).to_dict()

            if not results:
                m.reply("لم يتم العثور على نتائج")
                r.delete(processing_key)
                return True

            res = results[0]
            vid_id = res["id"]

            url = f"https://youtu.be/{vid_id}"

            # Cache
            cached = ytdb.get(f"ytvideo{vid_id}")

            if cached:

                if isinstance(cached, str):
                    aud_data = json.loads(cached)
                else:
                    aud_data = cached

                duration_string = time.strftime(
                    "%M:%S",
                    time.gmtime(aud_data["duration"])
                )

                rep = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "🇮🇶",
                            url=f"https://t.me/{channel}"
                        )
                    ]
                ])

                m.reply_audio(
                    aud_data["audio"],
                    caption=f"@{channel} ~ {duration_string} ⏳",
                    reply_markup=rep
                )

                r.delete(processing_key)
                return True

            # yt-dlp
            ydl_opts = {
                "format": "bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio",
                "outtmpl": f"{vid_id}.%(ext)s",
                "quiet": True,
                "no_warnings": True,
                "prefer_ffmpeg": False,
            }

            if os.path.exists(cookies_path):
                ydl_opts["cookiefile"] = cookies_path

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:

                info = ydl.extract_info(
                    url,
                    download=False
                )

                if info.get("duration", 0) > 1500:

                    rep = InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton(
                                "🇮🇶",
                                url=f"https://t.me/{channel}"
                            )
                        ]
                    ])

                    m.reply(
                        "صوت فوق 25 دقيقة ما اقدر انزله",
                        reply_markup=rep
                    )

                    r.delete(processing_key)
                    return True

                ydl.download([url])

            audio_file = None

            for file in os.listdir("."):

                if (
                    file.startswith(vid_id)
                    and file.endswith(
                        (".m4a", ".mp3", ".webm")
                    )
                ):
                    audio_file = file
                    break

            if not audio_file:

                rep = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "🇮🇶",
                            url=f"https://t.me/{channel}"
                        )
                    ]
                ])

                m.reply(
                    "فشل في تحميل الملف الصوتي",
                    reply_markup=rep
                )

                r.delete(processing_key)
                return True

            duration_string = time.strftime(
                "%M:%S",
                time.gmtime(info.get("duration", 0))
            )

            rep = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🇮🇶",
                        url=f"https://t.me/{channel}"
                    )
                ]
            ])

            a = m.reply_audio(
                audio_file,
                title=info.get("title", "Unknown"),
                duration=info.get("duration", 0),
                caption=f"@{channel} ~ {duration_string} ⏳",
                performer=info.get("uploader", "Unknown"),
                reply_markup=rep
            )

            if a and a.audio:

                ytdb.set(
                    f"ytvideo{vid_id}",
                    json.dumps({
                        "type": "audio",
                        "audio": a.audio.file_id,
                        "duration": a.audio.duration
                    })
                )

            try:
                os.remove(audio_file)
            except Exception:
                pass

            r.delete(processing_key)

            return True

        except Exception as e:

            rep = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🇮🇶",
                        url=f"https://t.me/{channel}"
                    )
                ]
            ])

            m.reply(
                f"خطأ في التحميل: {str(e)}",
                reply_markup=rep
            )

            r.delete(processing_key)

            return True

    # =========================
    # SoundCloud
    # =========================

    if text.startswith("ساوند "):

        if r.get(f"{m.chat.id}:disableSound:{Dev_Neptune}"):
            return

        if r.get(f":disableYT:{Dev_Neptune}"):
            return

        try:

            query = text.split(None, 1)[1]

            data = requests.get(
                f"https://m.soundcloud.com/search?q={query}",
                timeout=10
            )

            urls = re.findall(
                r'data-testid="cell-entity-link" href="([^"]+)',
                data.text
            )

            names = re.findall(
                r'<div class="Information_CellTitle__2KitR">([^<]+)',
                data.text
            )

            if not urls or not names:
                return m.reply(
                    f"{k} لم يتم العثور على نتائج للبحث: {query}"
                )

            min_count = min(
                len(urls),
                len(names)
            )

            result = []

            for i in range(min_count):

                result.append({
                    "name": names[i],
                    "url": urls[i]
                })

            # باقي كود SoundCloud الأصلي يكمل من هنا

        except Exception as e:

            logging.exception(e)

            try:
                return m.reply(
                    f"حدث خطأ: {str(e)}"
                )
            except Exception:
                return
