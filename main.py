```python
# -*- coding: utf-8 -*-

"""
Main launcher
يشغل bot22.py فقط.
كل عملية إنشاء وتشغيل البوت موجودة داخل bot22.py
"""

import sys
import traceback


def main():
    print("=" * 50)
    print("⚡ جاري تشغيل البوت...")
    print("=" * 50)

    try:
        # استيراد ملف البوت الرئيسي
        import bot22

        print("✓ تم تحميل bot22.py بنجاح")

        # التأكد من وجود دالة main
        if not hasattr(bot22, "main"):
            print("❌ خطأ: لا توجد دالة main() داخل bot22.py")
            sys.exit(1)

        print("✓ تم العثور على دالة main()")
        print("⚡ بدء تشغيل البوت...")
        print("=" * 50)

        # تشغيل البوت
        bot22.main()

    except KeyboardInterrupt:
        print()
        print("🛑 تم إيقاف البوت.")

    except ModuleNotFoundError as e:
        print()
        print("❌ خطأ في استيراد ملف أو مكتبة:")
        print(f"   {e}")
        print()
        print("تأكد من:")
        print("1. bot22.py موجود بنفس مجلد main.py")
        print("2. botvv.py موجود بنفس المجلد")
        print("3. جميع المكتبات المطلوبة مثبتة.")
        print()

        traceback.print_exc()
        sys.exit(1)

    except Exception as e:
        print()
        print("❌ حدث خطأ أثناء تشغيل البوت:")
        print(f"   {e}")
        print()
        print("تفاصيل الخطأ:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
```
