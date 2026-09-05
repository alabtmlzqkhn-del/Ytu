# -*- coding: utf-8 -*-

import sys
import traceback


def main():
    print("=" * 60)
    print("Starting Telegram Bot...")
    print("Loading bot22.py + botvv.py")
    print("=" * 60)

    try:
        import bot22

        print("✓ bot22.py loaded successfully")

        if not hasattr(bot22, "main"):
            print("❌ ERROR: main() not found in bot22.py")
            sys.exit(1)

        print("✓ bot22.py main() found")
        print("✓ botvv.py is connected from bot22.py")
        print("⚡ Starting bot...")
        print("=" * 60)

        bot22.main()

    except KeyboardInterrupt:
        print("\n🛑 Bot stopped.")

    except ModuleNotFoundError as e:
        print("\n❌ Missing module:")
        print(e)
        traceback.print_exc()
        sys.exit(1)

    except Exception as e:
        print("\n❌ Bot crashed:")
        print(e)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
