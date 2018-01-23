# -*- coding: utf-8 -*-
import os
import pytz

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

import currency

# timezone set
tpe = pytz.timezone('Asia/Taipei')

AccessToken = os.environ["ChannelAccessToken"]
ChannelSecret = os.environ["ChannelSecret"]
ChannelID = os.environ["UserID"]
cur_list = currency.get_name()

app = Flask(__name__)

line_bot_api = LineBotApi(AccessToken)
handler = WebhookHandler(ChannelSecret)


# Webhook get request and parse to handler
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handel_message(event):
    text = event.message.text

    # If user have specific word in text
    # Do the command
    if text.find("匯率") != -1 or text in cur_list:
        for cur in cur_list:
            if text.find(cur) != -1:
                cur_info = currency.get_currency(cur)
                message = "{cur}現在的匯率是 {info}".format(cur=cur, info=cur_info)
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=message))
                break
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="請告訴我要查甚麼的匯率!"))

    # Echo
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text))


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
