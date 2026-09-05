import logging
import bot22
from botvv import setup_missing_handlers

def main():
    if hasattr(bot22, "app"):
        app = bot22.app
    elif hasattr(bot22, "get_app"):
        app = bot22.get_app()
    elif hasattr(bot22, "application"):
        app = bot22.application
    else:
        raise AttributeError("لم يتم العثور على متغير التطبيق داخل ملف bot22.py")

    setup_missing_handlers(app)
    print("⚡ تم ربط الملفين bot22 و botvv بنجاح وجاري تشغيل البوت...")
    app.run_polling()

if __name__ == "__main__":
    main()
