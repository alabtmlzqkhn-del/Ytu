import asyncio
import logging
import math
import os
import re
import sys
import time
import uuid
from datetime import datetime, timedelta
import requests
import telegram
from telegram import (
    Chat,
    ChatMember,
    ChatPermissions,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    KeyboardButtonStyle,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.error import BadRequest, Forbidden, TelegramError, TimedOut
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

SAVED_GROUPS_LINKS = {}

async def set_custom_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    msg = update.message
    if chat.type not in ("group", "supergroup"):
        await msg.reply_text("- هذا الأمر يعمل داخل المجموعات فقط .")
        return
    text_parts = msg.text.strip().split(maxsplit=2)
    if len(text_parts) < 3:
        await msg.reply_text("- أرسل الأمر مع الرابط بالطريقة التالية:\nضع رابط [الرابط هنا]")
        return
    raw_url = text_parts[2].strip()
    if not (raw_url.startswith("http://") or raw_url.startswith("https://") or raw_url.startswith("t.me/")):
        await msg.reply_text("- يرجى إرسال رابط صحيح يبتدئ بـ http أو https أو t.me .")
        return
    if raw_url.startswith("t.me/"):
        raw_url = "https://" + raw_url
    SAVED_GROUPS_LINKS[chat.id] = raw_url
    await msg.reply_text("✅ - تم حفظ رابط المجموعة بنجاح .")

async def get_group_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    msg = update.message
    if chat.type not in ("group", "supergroup"):
        await msg.reply_text("- هذا الأمر يعمل داخل المجموعات فقط .")
        return
    saved_link = SAVED_GROUPS_LINKS.get(chat.id)
    if saved_link:
        await msg.reply_text(
            f"🔗 رابط المجموعة:\n{saved_link}",
            disable_web_page_preview=True
        )
        return
    try:
        if chat.username:
            link = f"https://t.me/{chat.username}"
        else:
            link = await context.bot.export_chat_invite_link(chat.id)
        await msg.reply_text(
            f"🔗 رابط المجموعة:\n{link}",
            disable_web_page_preview=True
        )
    except TelegramError:
        await msg.reply_text("- لم يتم تعيين رابط لهذه المجموعة ، أرسل (ضع رابط [الرابط]) لتعيينه .")

async def create_interactive_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    msg = update.message
    if chat.type not in ("group", "supergroup"):
        await msg.reply_text("- هذا الأمر يعمل داخل المجموعات فقط .")
        return
    try:
        if chat.username:
            direct_link = f"https://t.me/{chat.username}"
        else:
            direct_link = await context.bot.export_chat_invite_link(chat.id)
        approval_invite = await context.bot.create_chat_invite_link(
            chat_id=chat.id,
            creates_join_request=True
        )
        approval_link = approval_invite.invite_link
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("انضمام 🔗", url=direct_link),
                InlineKeyboardButton("خاص 🔒", url=approval_link)
            ]
        ])
        await msg.reply_text(
            "🔗 خيارات انضمام المجموعة:\n\n- انضمام: دخول مباشر بدون موافقة.\n- خاص: يتطلب موافقة المشرفين.",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    except TelegramError as e:
        await msg.reply_text("- فشل إنشاء الروابط ، تأكد من رفع البوت مشرف وإعطائه صلاحية (دعوة المستخدمين عبر رابط) .")

def setup_missing_handlers(app):
    app.add_handler(
        MessageHandler(
            filters.Regex(r"^(ضع رابط|ضع الرابط)\s+") & ~filters.COMMAND,
            set_custom_link
        )
    )
    app.add_handler(
        MessageHandler(
            filters.Regex(r"^(الرابط|رابط)") & ~filters.COMMAND,
            get_group_link
        )
    )
    app.add_handler(
        MessageHandler(
            filters.Regex(r"^(انشاء رابط|إنشاء رابط)") & ~filters.COMMAND,
            create_interactive_links
        )
    )
