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
import os
import currency
import ck_crawler
from datetime import datetime
import pytz

# timezone set
tpe = pytz.timezone('Asia/Taipei')

AccessToken = os.environ["ChannelAccessToken"]
ChannelSecret = os.environ["ChannelSecret"]
ChannelID = os.environ["UserID"]
cur_list = currency.get_name()

app = Flask(__name__)

line_bot_api = LineBotApi(AccessToken)
handler = WebhookHandler(ChannelSecret)

# Webhook 處理 驗證後交給hander
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
    print("userID:", event.source.user_id)
    print("reply_token:", event.reply_token)
    text = event.message.text

    # 查詢匯率
    if text.find("匯率") != -1 or text in cur_list:
        for cur in cur_list:
            if text.find(cur) != -1:
                cur_info = currency.get_currency(cur)
                message = "{cur}現在的匯率是 {info}".format(cur = cur, info = cur_info)
                # message += "\n 現金買入  賣出  即期買入  賣出\n"
                # for info in yen_info:
                #     message += " " + info + "  "
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=message))
                break
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="請告訴我要查甚麼的匯率!"))

    # 小說更新
    elif event.message.text == "小說":
        novel_update = ck_crawler.get_novel_title()
        if novel_update == "":
            message = "目前都沒有小說更新唷!"
        else:
            message = novel_update
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=message))

    # 建立使用者資料
    elif event.message.text == "建立":
        user = User(event.source.user_id, event.reply_token)
        db.session.add(user)
        db.session.commit()
        all_users = User.query.all()
        print(all_users)

    # 查詢所有使用者資料 
    elif event.message.text == "所有使用者":
        all_users = User.query.all()
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=all_users))

    # Echo
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text))
# def handle_message(event):
#     line_bot_api.reply_message(
#         event.reply_token,
#         TextSendMessage(text=event.message.text))


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)