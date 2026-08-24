import requests
import json


def make_button(text, style=None, url=None, callback_data=None):
    button = {
        "text": text
    }

    if url:
        button["url"] = url

    if callback_data:
        button["callback_data"] = callback_data

    if style:
        button["style"] = style

    return button


def send_colored_message(
    token,
    chat_id,
    text,
    buttons
):
    keyboard = {
        "inline_keyboard": buttons
    }

    data = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": json.dumps(
            keyboard,
            ensure_ascii=False
        )
    }

    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=data,
        timeout=30
    )

    return response.json()


def send_colored_photo(
    token,
    chat_id,
    photo,
    caption,
    buttons
):
    keyboard = {
        "inline_keyboard": buttons
    }

    data = {
        "chat_id": chat_id,
        "photo": photo,
        "caption": caption,
        "reply_markup": json.dumps(
            keyboard,
            ensure_ascii=False
        )
    }

    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendPhoto",
        data=data,
        timeout=30
    )

    return response.json()
