from pyrogram import *
from pyrogram.enums import *
from pyrogram.types import *
from pyrogram.errors import UserNotParticipant, FloodWait
from config import *
from helpers.Ranks import *

@Client.on_message(filters.all, group=-999999999)
async def forceSubscribeAll(c: Client, m: Message):
    """تم إيقاف نظام الاشتراك الإجباري"""
    return
