import logging
import bot22
from botvv import setup_missing_handlers
​def main():
# 1. جلب كائن الـ application المعرّف داخل ملف bot2.py
# (تأكد أن اسم المتغير داخل bot2 هو app أو application أو bot)
if hasattr(bot2, "app"):
app = bot2.app
elif hasattr(bot2, "application"):
app = bot2.application
else:
raise AttributeError("لم يتم العثور على متغير التطبيق (app أو application) داخل ملف bot2.py")
​# 2. تسجيل الأوامر الناقصة من ملف botvv.py داخل التطبيق الرئيسي
setup_missing_handlers(app)
​print("⚡ تم ربط الملفين bot2 و botvv بنجاح وجاري تشغيل البوت...")
​# 3. تشغيل البوت
app.run_polling()
​if name == "main":
main()
