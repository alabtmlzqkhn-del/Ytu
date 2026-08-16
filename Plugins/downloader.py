import yt_dlp, os, requests, re, time, wget, random, json
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch as Y88F8
from threading import Thread
from pyrogram import Client, filters
from pyrogram.enums import ChatType
from shazamio import Shazam
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent
try:
    from config import *
except ImportError:
    # في حالة عدم وجود ملف config بعد (يتم إنشاؤه بعد تشغيل البوت)
    Dev_Neptune = "default"
from helpers.Ranks import admin_pls, isLockCommand
from PIL import Image, ImageFilter
import redis
import logging
#from pySmartDL import SmartDL

logging.getLogger("yt_dlp").setLevel(logging.CRITICAL)

# الحصول على مسار مجلد البوت الأساسي (bmqa أو أي اسم آخر) تلقائياً
bot_main_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cookies_path = os.path.join(bot_main_dir, 'cookies.txt')



r = redis.Redis(decode_responses=True)
ytdb = redis.Redis(decode_responses=True, db=1)
sounddb = redis.Redis(decode_responses=True, db=2)

shazam = Shazam()

def time_to_seconds(time):
    stringt = str(time)
    return sum(
        int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":")))
    )

def Find(text):
  m = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s!()\[\]{};:'\".,<>?«»“”‘’]))"
  url = re.findall(m,text)
  return [x[0] for x in url]

@Client.on_message(filters.text & filters.group, group=32)
def ytdownloaderHandler(c, m):
    k = r.get(f'{Dev_Neptune}:botkey') or ""
    channel = r.get(f'{Dev_Neptune}:BotChannel') or 'Jack_Vib'
    Thread(target=yt_func_timed, args=(c, m, k, channel)).start()

def yt_func_timed(c, m, k, channel):
    result = yt_func(c, m, k, channel)
    if result and isinstance(result, dict) and 'message' in result:
        message = result['message']
        message.edit_caption(f"@{channel} ~ {message.caption.split('~')[1]}")
    elif result and isinstance(result, dict) and 'reply' in result:
        pass  # لا حاجة لتعديل شيء في حالة الرد الكتابي فقط

def yt_func(c, m, k, channel):
    if not r.get(f'{m.chat.id}:enable:{Dev_Neptune}'):
        return
    if r.get(f'{m.from_user.id}:mute:{m.chat.id}{Dev_Neptune}'): return
    if r.get(f'{m.chat.id}:mute:{Dev_Neptune}') and not admin_pls(m.from_user.id, m.chat.id): return
    if r.get(f'{m.from_user.id}:mute:{Dev_Neptune}'): return
    text = m.text
    if isLockCommand(m.from_user.id, m.chat.id, text): return

    if text.startswith('بحث '):
        if r.get(f'{m.chat.id}:disableYT:{Dev_Neptune}'):  return True
        if r.get(f':disableYT:{Dev_Neptune}'):  return True
        query = text.split(None,1)[1]

        # منع الرد المزدوج
        processing_key = f'yt_processing:{m.from_user.id}:{query}'
        if r.get(processing_key):
            return True
        r.set(processing_key, 1, ex=30)  # منع المعالجة لمدة 30 ثانية

        # البحث وتحميل أول نتيجة مباشرة كصوت
        try:
            results = Y88F8(query, max_results=1).to_dict()
            if not results:
                m.reply("لم يتم العثور على نتائج")
                r.delete(processing_key)  # حذف مفتاح المعالجة
                return True

            res = results[0]
            vid_id = res['id']
            url = f'https://youtu.be/{vid_id}'

            # التحقق من وجود الملف في التخزين المؤقت
            if ytdb.get(f'ytvideo{vid_id}'):
                aud_data = json.loads(ytdb.get(f'ytvideo{vid_id}'))
                duration_string = time.strftime('%M:%S', time.gmtime(aud_data["duration"]))
                rep = InlineKeyboardMarkup([[InlineKeyboardButton('🇮🇶', url=f'https://t.me/{channel}')]])
                m.reply_audio(aud_data["audio"], caption=f'@{channel} ~ {duration_string} ⏳', reply_markup=rep)
                r.delete(processing_key)  # حذف مفتاح المعالجة
                return True

            # إعدادات yt-dlp لتحميل الصوت مباشرة بدون ffmpeg
            ydl_opts = {
                'format': 'bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio',
                'outtmpl': f'{vid_id}.%(ext)s',
                'cookiefile': cookies_path if os.path.exists(cookies_path) else None,
                'quiet': True,
                'no_warnings': True,
                'prefer_ffmpeg': False,  # عدم استخدام ffmpeg
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info['duration'] > 1500:  # 25 دقيقة
                    rep = InlineKeyboardMarkup([[InlineKeyboardButton('🇮🇶', url=f'https://t.me/{channel}')]])
                    m.reply("صوت فوق 25 دقيقة ما اقدر انزله", reply_markup=rep)
                    r.delete(processing_key)  # حذف مفتاح المعالجة
                    return True

                ydl.download([url])

            # العثور على الملف المحمل
            audio_file = None
            for file in os.listdir('.'):
                if file.startswith(vid_id) and file.endswith(('.m4a', '.mp3', '.webm')):
                    audio_file = file
                    break

            if not audio_file:
                rep = InlineKeyboardMarkup([[InlineKeyboardButton('🇮🇶', url=f'https://t.me/{channel}')]])
                m.reply("فشل في تحميل الملف الصوتي", reply_markup=rep)
                r.delete(processing_key)  # حذف مفتاح المعالجة
                return True

            duration_string = time.strftime('%M:%S', time.gmtime(info['duration']))
            rep = InlineKeyboardMarkup([[InlineKeyboardButton('🇮🇶', url=f'https://t.me/{channel}')]])

            a = m.reply_audio(
                audio_file,
                title=info['title'],
                duration=info['duration'],
                caption=f'@{channel} ~ {duration_string} ⏳',
                performer=info.get('uploader', 'Unknown'),
                reply_markup=rep
            )

            ytdb.set(f'ytvideo{vid_id}', json.dumps({"type": "audio", "audio": a.audio.file_id, "duration": a.audio.duration}))
            os.remove(audio_file)
            r.delete(processing_key)  # حذف مفتاح المعالجة
            return True

        except Exception as e:
            rep = InlineKeyboardMarkup([[InlineKeyboardButton('🇮🇶', url=f'https://t.me/{channel}')]])
            m.reply(f"خطأ في التحميل: {str(e)}", reply_markup=rep)
            r.delete(processing_key)  # حذف مفتاح المعالجة حتى في حالة الخطأ
            return True  # إيقاف المعالجة لتجنب الرد المزدوج

# تم حذف الوظيفة المكررة لتجنب الرد المزدوج

    if text == "نسخة اليوتيوب" and m.from_user.id == 651286114:
        if not ytdb.keys():
            return m.reply("تخزين اليوتيوب فارغ")
        else:
            videos = []
            audios = []
            for key in ytdb.keys():
                get = {"key":key[0],"value":ytdb.get(key[0])}
                if get["value"]["type"] == "audio":
                    audios.append(get)
                if get["value"]["type"] == "video":
                    videos.append(get)
            id = random.randint(1,10000)
            if audios:
                with open(f"audios-{id}.json","w+") as f:
                    f.write(json.dumps(audios, indent=4, ensure_ascii=False))
                m.reply_document(f"audios-{id}.json")
                os.remove(f"audios-{id}.json")
            if videos:
                with open(f"videos-{id}.json","w+") as f:
                    f.write(json.dumps(videos, indent=4, ensure_ascii=False))
                m.reply_document(f"videos-{id}.json")
                os.remove(f"videos-{id}.json")
            return True

    if text.startswith('ساوند '):
        if r.get(f'{m.chat.id}:disableSound:{Dev_Neptune}'):  return
        if r.get(f':disableYT:{Dev_Neptune}'):  return

        try:
            query = text.split(None,1)[1]
            data = requests.get(f"https://m.soundcloud.com/search?q={query}", timeout=10)
            urls = re.findall(r'data-testid="cell-entity-link" href="([^"]+)', data.text)
            names = re.findall(r'<div class="Information_CellTitle__2KitR">([^<]+)', data.text)

            # التأكد من تطابق عدد الروابط والأسماء
            if not urls or not names:
                return m.reply(f'{k} لم يتم العثور على نتائج للبحث: {query}')

            # أخذ أقل عدد لتجنب الخطأ
            min_count = min(len(urls), len(names))
            result = []

            for i in range(min_count):
                if i >= 5:  # حد أقصى 5 نتائج
                    break
                result.append({'name': names[i], 'url': f'{urls[i]}'})

            if not result:
                return m.reply(f'{k} لم يتم العثور على نتائج صالحة للبحث: {query}')

            buttons = []
            for i, a in enumerate(result):
                url = a['url']
                buttons.append([
                    InlineKeyboardButton(a['name'], callback_data=f'sound_download:{i}:{m.from_user.id}')
                ])

            # حفظ النتائج مؤقتاً مع معرف الرسالة الأصلية
            temp_key = f'sound_results:{m.from_user.id}:{m.chat.id}'
            data_to_save = {
                'results': result,
                'original_message_id': m.id
            }
            r.setex(temp_key, 300, json.dumps(data_to_save))  # حفظ لمدة 5 دقائق

            btns = InlineKeyboardMarkup(buttons)
            m.reply(f'{k} بحث الساوند ~ {query}', reply_markup=btns)
            return True

        except Exception as e:
            return m.reply(f'{k} خطأ في البحث: {str(e)}')

    if text.startswith('تيك '):
        if r.get(f'{m.chat.id}:disableTik:{Dev_Neptune}'):  return
        if r.get(f':disableYT:{Dev_Neptune}'):  return
        if Find(text):
            query = Find(text)[0]
        else:
            return False

        # إعدادات yt-dlp محسّنة لتيك توك بدون كوكيز
        ydl_opts = {
            'format': 'best[height<=720]/best[height<=480]/best/mp4/any',
            'outtmpl': 'tiktok_%(id)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'referer': 'https://www.tiktok.com/',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            },
            'extractor_args': {
                'tiktok': {
                    'api_hostname': 'api.tiktokv.com',
                    'webpage_url_basename': 'video'
                }
            }
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ytdl:
                vid_data = ytdl.extract_info(query, download=False)

            title = vid_data['fulltitle']
            duration = int(vid_data['duration'])
            string_d = time.strftime('%M:%S', time.gmtime(duration))
            uploader = vid_data.get('uploader', 'Unknown')
            uploader_url = vid_data.get('uploader_url', '')
            creator = vid_data.get('creator', 'Unknown')
            likes = vid_data.get('like_count', 0)
            comments = vid_data.get('comment_count', 0)
            views = vid_data.get('view_count', 0)
            reposts = vid_data.get('repost_count', 0)

            caption = f"`{title}`\n{k} طول المقطع : {string_d}\n{k} المشاهدات : {views:,}\n{k} اللايكات : {likes:,}\n{k} الكومنت : {comments:,}\n{k} الاكسبلور : {reposts:,}\n\n~ @{channel}"
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(f"{creator} - @{uploader}", url=uploader_url)]
            ])

            # تحميل الفيديو
            with yt_dlp.YoutubeDL(ydl_opts) as ytdl:
                ytdl.download([query])

            # العثور على الملف المحمل
            file_name = None
            # البحث بالاسم المحدد
            for file in os.listdir('.'):
                if file.startswith('tiktok_') and vid_data['id'] in file and file.endswith(('.mp4', '.mkv', '.webm', '.mov')):
                    file_name = file
                    break

            if not file_name:
                # البحث بطريقة أخرى - أي ملف يحتوي على ID
                for file in os.listdir('.'):
                    if vid_data['id'] in file and file.endswith(('.mp4', '.mkv', '.webm', '.mov')):
                        file_name = file
                        break

            if not file_name:
                # البحث بالوقت - أحدث ملف فيديو
                for file in os.listdir('.'):
                    if file.endswith(('.mp4', '.mkv', '.webm', '.mov')) and os.path.getmtime(file) > time.time() - 60:
                        file_name = file
                        break

            if file_name:
                m.reply_video(file_name, caption=caption, reply_markup=reply_markup)
                os.remove(file_name)
                return True
            else:
                rep = InlineKeyboardMarkup([[InlineKeyboardButton('🇮🇶', url=f'https://t.me/{channel}')]])
                return m.reply("فشل في العثور على الملف المحمل", reply_markup=rep)

        except Exception as e:
            rep = InlineKeyboardMarkup([[InlineKeyboardButton('🇮🇶', url=f'https://t.me/{channel}')]])
            error_msg = str(e).replace('[0;31mERROR: [0m', '').replace('[TikTok]', 'تيك توك')
            return m.reply(f"خطأ في تحميل تيك توك: {error_msg}", reply_markup=rep)

    if text.endswith(' #AUDIO'):
        find = Find(text)
        if find:
            url = find[0]
            if 'soundcloud' in url:
                if r.get(f'{m.chat.id}:disableSound:{Dev_Neptune}'):  return
                if r.get(f':disableYT:{Dev_Neptune}'):  return
                id = url.split('soundcloud.com/')[1]
                if sounddb.get(f'{id}:sound'):
                    return m.reply_audio(sounddb.get(f'{id}:sound'))
                with yt_dlp.YoutubeDL({}) as ytdl:
                    ytdl_dataa = ytdl.extract_info(url, download=False)
                    if int(ytdl_dataa['duration']) > 155555555:
                        return m.reply('مقطع اكثر من ٢٥ دقيقة مقدر انزله')
                with yt_dlp.YoutubeDL({}) as ytdl:
                    ytdl_dataa = ytdl.extract_info(url, download=True)
                    file_name = ytdl.prepare_filename(ytdl_dataa)
                title = ytdl_dataa['title']
                a = m.reply_audio(file_name,title=title, performer=f'@{channel}', duration=int(ytdl_dataa['duration']))
                sounddb.set(f'{id}:sound',a.audio.file_id)
                os.remove(file_name)
                return True

    if text.endswith(' #VOICE'):
        find = Find(text)
        if find:
            url = find[0]
            if 'soundcloud' in url:
                if r.get(f'{m.chat.id}:disableSound:{Dev_Neptune}'):  return
                if r.get(f':disableYT:{Dev_Neptune}'):  return
                idd = url.split('soundcloud.com/')[1]
                if sounddb.get(f'{idd}:soundVoice'):
                    return m.reply_voice(sounddb.get(f'{idd}:soundVoice'))
                with yt_dlp.YoutubeDL({}) as ytdl:
                    ytdl_dataa = ytdl.extract_info(url, download=False)
                    if int(ytdl_dataa['duration']) > 55555252:
                        return m.reply('مقطع اكثر من ٢٥ دقيقة مقدر انزله')
                with yt_dlp.YoutubeDL({}) as ytdl:
                    ytdl_dataa = ytdl.extract_info(url, download=True)
                    file_name = ytdl.prepare_filename(ytdl_dataa)
                id = random.randint(1,100)
                os.rename(file_name, f"Neptune{id}.mp3")
                os.system(f'ffmpeg -i Neptune{id}.mp3 -ac 1 -strict -2 -codec:a libopus -b:a 128k -vbr off -ar 24000 Neptune{id}.ogg')
                a = m.reply_voice(f"Neptune{id}.ogg")
                sounddb.set(f'{idd}:soundVoice',a.voice.file_id)
                os.remove(f"Neptune{id}.mp3")
                os.remove(f"Neptune{id}.ogg")
                return True

    find = Find(text)
    if find:
        url = find[0]
        if 'soundcloud' in url:
            if r.get(f'{m.chat.id}:disableSound:{Dev_Neptune}'):  return
            if r.get(f':disableYT:{Dev_Neptune}'):  return
            id = url.split('soundcloud.com')[1]
            return m.reply(f"@{channel} - ☁️",reply_markup=InlineKeyboardMarkup ([
                [InlineKeyboardButton ("اضغط هنا لاختيار صيغة التحميل", switch_inline_query_current_chat=f'{id}#SOUND')],
                [InlineKeyboardButton ("☁️", url=f't.me/{channel}')],
            ]))



@Client.on_message(filters.regex("^شازام$") & filters.group)
async def shazamFunc(c,m):
   if r.get(f'{m.chat.id}:disableShazam:{Dev_Neptune}'):  return False
   if m.reply_to_message and (m.reply_to_message.audio or m.reply_to_message.voice or m.reply_to_message.video):
     if m.reply_to_message.audio:
       duration=m.reply_to_message.audio.duration if m.reply_to_message.audio.duration else 301
       fileSize=m.reply_to_message.audio.file_size
     if m.reply_to_message.voice:
       duration=m.reply_to_message.voice.duration if m.reply_to_message.voice.duration else 301
       fileSize=m.reply_to_message.voice.file_size
     if m.reply_to_message.video:
       duration=m.reply_to_message.video.duration if m.reply_to_message.video.duration else 301
       fileSize=m.reply_to_message.video.file_size
     if duration > 300:
       return await m.reply("🇮🇶 مدة المقطع أكثر من 5 دقايق ..")
     if fileSize > 26214400:
       return await m.reply("🇮🇶 حجم المقطع أكثر من 25 ميجابايت ..")
     id = random.randint(1,1000)
     msg = await m.reply("جاري المعالجة ...")
     audio = await m.reply_to_message.download(f'./shazam{id}.ogg')
     out = await shazam.recognize_song(f'shazam{id}.ogg')
     os.remove(f'shazam{id}.ogg')
     await msg.delete()
     if not out["matches"]:
       return await m.reply("فشل بالتعرف على الصوت")
     else:
       title = out["track"]["title"]
       author = out["track"]["subtitle"]
       try:
         photo = out["track"]["images"]["background"]
       except:
         photo = "https://telegra.ph/file/49ace69e7c43c0041fb63.jpg"
       k = r.get(f'{Dev_Neptune}:botkey')
       channel = r.get(f'{Dev_Neptune}:BotChannel') if r.get(f'{Dev_Neptune}:BotChannel') else 'IIIIIlI8'
       url = out["track"]["url"]
       TEXT = f"""
{k} اسم الصوت ( [{title}]({url}) )
{k} اسم الفنان : {author}
"""
       key = InlineKeyboardMarkup ([[InlineKeyboardButton ("🇮🇶",url=f"t.me/{channel}")]])
       await m.reply_photo(
         photo,caption=TEXT,reply_markup=key)

@Client.on_message(filters.regex("^شازام ") & filters.group)
async def shazamLyrics(c,m):
   if r.get(f'{m.chat.id}:disableShazam:{Dev_Neptune}'):  return False
   query = m.text.split(None,1)[1]
   out = await shazam.search_track(query=query, limit=1)
   if not out:
     return await m.reply("فشل العثور")
   else:
    try:
     key = int(out["tracks"]["hits"][0]["key"])
     title = out["tracks"]["hits"][0]["heading"]["title"][:35]
     author = out["tracks"]["hits"][0]["heading"]["subtitle"]
     url = out["tracks"]["hits"][0]["url"]
     track_id = key
     about_track = await shazam.track_about(track_id=track_id)
     text=about_track["sections"][1]["text"]
     lyrics=""
     for tt in text:
       lyrics+=tt+"\n"
     return await m.reply(lyrics[:4096],reply_markup=InlineKeyboardMarkup (
       [[InlineKeyboardButton (f"{title} - {author}",url=url)]]
     )
     )
    except:
     return await m.reply("فشل العثور")

@Client.on_inline_query(filters.regex("SOUND"))
async def SoundCloud(c, query):
  url = query.query.split("#SOUND")[0]
  channel = r.get(f'{Dev_Neptune}:BotChannel') if r.get(f'{Dev_Neptune}:BotChannel') else 'iJUCK'
  if url.count('/') > 1:
    await query.answer(
        results=[
            InlineQueryResultArticle(
                title="اضغط هنا للتحميل - صوت",
                thumb_url='https://t.me/D7BotResources/161',
                description='~ @iJUCK ',
                url='https://t.me/iJUCK',
                reply_markup=InlineKeyboardMarkup ([[InlineKeyboardButton ("🇮🇶", url=f't.me/{channel}')]]),
                input_message_content=InputTextMessageContent(f'https://soundcloud.com{url} #AUDIO',disable_web_page_preview=True)
            ),
            InlineQueryResultArticle(
                title="اضغط هنا للتحميل - بصمة",
                thumb_url='https://t.me/D7BotResources/163',
                description='~ @iJUCK ',
                url='https://t.me/iJUCK',
                reply_markup=InlineKeyboardMarkup ([[InlineKeyboardButton ("🇮🇶", url=f't.me/{channel}')]]),
                input_message_content=InputTextMessageContent(f'https://soundcloud.com{url} #VOICE',disable_web_page_preview=True)
            ),
        ],
        cache_time=1
        )
  else:
    await query.answer(
        results=[
            InlineQueryResultArticle(
                title="اضغط هنا للتحميل - صوت",
                thumb_url='https://t.me/D7BotResources/161',
                description='~ @iJUCK ',
                url='https://t.me/iJUCK',
                reply_markup=InlineKeyboardMarkup ([[InlineKeyboardButton ("🇮🇶", url=f't.me/{channel}')]]),
                input_message_content=InputTextMessageContent(f'https://on.soundcloud.com{url} #AUDIO',disable_web_page_preview=True)
            ),
            InlineQueryResultArticle(
                title="اضغط هنا للتحميل - بصمة",
                thumb_url='https://t.me/D7BotResources/163',
                description='~ @iJUCK ',
                url='https://t.me/iJUCK',
                reply_markup=InlineKeyboardMarkup ([[InlineKeyboardButton ("🇮🇶", url=f't.me/{channel}')]]),
                input_message_content=InputTextMessageContent(f'https://on.soundcloud.com{url} #VOICE',disable_web_page_preview=True)
            ),
        ],
        cache_time=1
        )



# معالج أزرار ساوند كلاود
@Client.on_callback_query(filters.regex("^sound_download:"))
def handle_sound_download(c, query):
    Thread(target=sound_download_handler, args=(c, query)).start()

def sound_download_handler(c, query):
    try:
        # استخراج البيانات من callback_data
        data_parts = query.data.split(':')
        result_index = int(data_parts[1])
        user_id = int(data_parts[2])

        # التحقق من أن المستخدم هو نفسه الذي طلب البحث
        if query.from_user.id != user_id:
            return query.answer("هذا الزر ليس لك!", show_alert=True)

        # استرجاع النتائج المحفوظة
        temp_key = f'sound_results:{user_id}:{query.message.chat.id}'
        saved_results = r.get(temp_key)

        if not saved_results:
            return query.answer("انتهت صلاحية النتائج، ابحث مرة أخرى", show_alert=True)

        saved_data = json.loads(saved_results)
        results = saved_data['results']
        original_message_id = saved_data['original_message_id']

        if result_index >= len(results):
            return query.answer("خطأ في اختيار النتيجة", show_alert=True)

        selected_result = results[result_index]
        url = f"https://soundcloud.com{selected_result['url']}"

        # تحديث الرسالة لإظهار أنه يتم التحميل
        query.edit_message_text(f"🎵 جاري تحميل: {selected_result['name']}\n⏳ انتظر قليلاً...")

        # تحميل الصوت
        channel = r.get(f'{Dev_Neptune}:BotChannel') if r.get(f'{Dev_Neptune}:BotChannel') else 'Jack_Vib'

        # التحقق من التخزين المؤقت
        id = selected_result['url'].split('/')[-1]
        if sounddb.get(f'{id}:sound'):
            audio_file_id = sounddb.get(f'{id}:sound')
            # الرد على الرسالة الأصلية باستخدام معرف الرسالة المحفوظ
            try:
                original_message = query.message.chat.get_messages(original_message_id)
                original_message.reply_audio(audio_file_id, caption=f"🎵 {selected_result['name']}\n~ @{channel}")
            except:
                # في حالة فشل العثور على الرسالة الأصلية، أرسل كرد عادي
                query.message.reply_audio(audio_file_id, caption=f"🎵 {selected_result['name']}\n~ @{channel}")
            query.message.delete()
            return

        # تحميل جديد
        with yt_dlp.YoutubeDL({'quiet': True}) as ytdl:
            ytdl_data = ytdl.extract_info(url, download=False)
            if int(ytdl_data['duration']) > 1500:  # 25 دقيقة
                return query.edit_message_text("❌ مقطع أكثر من 25 دقيقة لا يمكن تحميله")

        with yt_dlp.YoutubeDL({'quiet': True}) as ytdl:
            ytdl_data = ytdl.extract_info(url, download=True)
            file_name = ytdl.prepare_filename(ytdl_data)

        title = ytdl_data['title']
        duration = int(ytdl_data['duration'])

        # إرسال الصوت كرد على الرسالة الأصلية
        try:
            original_message = query.message.chat.get_messages(original_message_id)
            a = original_message.reply_audio(
                file_name,
                title=title,
                performer=f'@{channel}',
                duration=duration,
                caption=f"🎵 {title}\n~ @{channel}"
            )
        except:
            # في حالة فشل العثور على الرسالة الأصلية، أرسل كرد عادي
            a = query.message.reply_audio(
                file_name,
                title=title,
                performer=f'@{channel}',
                duration=duration,
                caption=f"🎵 {title}\n~ @{channel}"
            )

        # حفظ في التخزين المؤقت
        sounddb.set(f'{id}:sound', a.audio.file_id)

        # حذف الملف المحلي
        os.remove(file_name)

        # حذف رسالة البحث
        query.message.delete()

    except Exception as e:
        query.edit_message_text(f"❌ خطأ في التحميل: {str(e)}")

# تم حذف وظائف الأزرار القديمة - التحميل مباشر الآن


"""
@Client.on_callback_query(filters.regex("AUDIO"))
def get_audii(c, query):
    Thread(target=audio_down,args=(c,query)).start()

def audio_down(c, query):
    user_id = query.data.split("AUDIO")[0]
    vid_id = query.data.split("AUDIO")[1]
    if not query.from_user.id == int(user_id):
      return
    if r.get(f'{query.message.chat.id}:disableYT:{Dev_Neptune}'):  return
    if r.get(f':disableYT:{Dev_Neptune}'):  return
    channel = r.get(f'{Dev_Neptune}:BotChannel') if r.get(f'{Dev_Neptune}:BotChannel') else 'IIIIIlI8'
    rep = InlineKeyboardMarkup (
     [[
       InlineKeyboardButton ('🇮🇶', url=f'https://t.me/{channel}')
     ]]
    )
    url = f'https://youtu.be/{vid_id}'
    if r.get(f'ytvideo{vid_id}'):
       aud = r.get(f'ytvideo{vid_id}')
       query.edit_message_caption(f"@{channel} :)", reply_markup=rep)
       yt = YouTube(url)
       duration= int(yt.length)
       sec = time.strftime('%M:%S', time.gmtime(duration))
       return query.message.reply_audio(aud,caption=f'@{channel} ~ ⏳ {sec}')
    query.edit_message_caption("جاري التحميل ..", reply_markup=rep)
    yt = YouTube(url)
    duration= int(yt.length)
    sec = time.strftime('%M:%S', time.gmtime(duration))
    if duration > 1505:
      return query.edit_message_caption("صوت اكثر من 25 دقيقة مقدر انزله",reply_markup=rep)
    yt.streams.get_audio_only().download(filename=f'{vid_id}.mp3')
    query.edit_message_caption("✈️✈️✈️✈️✈️", reply_markup=rep)
    a = query.message.reply_audio(
      f'{vid_id}.mp3',
      title=yt.title,
      duration=yt.length,
      performer=yt.author,
      caption=f'@{channel} ~ ⏳ {sec}',
    )
    query.edit_message_caption(f"@{channel} :)", reply_markup=rep)

    r.set(f'ytvideo{vid_id}',b.link)
    os.remove(f'{vid_id}.mp3')
"""

# تم حذف وظائف الفيديو - التحميل مباشر كصوت فقط

"""
@Client.on_callback_query(filters.regex("VIDEO"))
async def get_video(c, query):
    Thread(target=video_down,args=(c,query)).start()

def video_down(c, query):
    user_id = query.data.split("VIDEO")[0]
    vid_id = query.data.split("VIDEO")[1]
    if not query.from_user.id == int(user_id):
      return
    if r.get(f'{query.message.chat.id}:disableYT:{Dev_Neptune}'):  return
    if r.get(f':disableYT:{Dev_Neptune}'):  return
    channel = r.get(f'{Dev_Neptune}:BotChannel') if r.get(f'{Dev_Neptune}:BotChannel') else 'IIIIIlI8'
    rep = InlineKeyboardMarkup (
     [[
       InlineKeyboardButton ('🇮🇶', url=f'https://t.me/{channel}')
     ]]
    )
    url = f'https://youtu.be/{vid_id}'
    if r.get(f'ytvideoV{vid_id}'):
       vid = r.get(f'ytvideoV{vid_id}')
       query.edit_message_caption(f"@{channel} :)", reply_markup=rep)
       yt = YouTube(url)
       duration= int(yt.length)
       sec = time.strftime('%M:%S', time.gmtime(duration))
       return query.message.reply_video(vid,caption=f'@{channel} ~ ⏳ {sec}')
    query.edit_message_caption("جاري التحميل ..", reply_markup=rep)
    yt = YouTube(url)
    duration= int(yt.length)
    sec = time.strftime('%M:%S', time.gmtime(duration))
    if duration > 1505:
      return query.edit_message_caption("صوت اكثر من 25 دقيقة مقدر انزله",reply_markup=rep)
    yt.streams.get_highest_resolution().download(filename=f'{vid_id}.mp4')
    query.edit_message_caption("✈️✈️✈️✈️✈️", reply_markup=rep)
    a = query.message.reply_video(
      f'{vid_id}.mp4',
      duration=duration,
      caption=f'@{channel} ~ ⏳ {sec}',
    )
    query.edit_message_caption(f"@{channel} :)", reply_markup=rep)

    r.set(f'ytvideoV{vid_id}',b.link)
    os.remove(f'{vid_id}.mp4')
"""