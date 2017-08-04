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
import psycopg2
from flask_sqlalchemy import SQLAlchemy
import currency_search
from datetime import datetime
import pytz

# timezone set
tpe = pytz.timezone('Asia/Taipei')

AccessToken = os.environ["ChannelAccessToken"]
ChannelSecret = os.environ["ChannelSecret"]
ChannelID = os.environ["UserID"]

app = Flask(__name__)

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    reply_token = db.Column(db.String(100), unique=True)

    def __init__(self, user_id, reply_token):
        self.user_id = user_id
        self.reply_token = reply_token

    def __repr__(self):
        return '<ID %r>' % self.user_id

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

    # 查詢日幣匯率
    if event.message.text == "日幣":
        yen_info = currency_search.yen()
        message = "日幣 " + datetime.strftime(datetime.now(tz=tpe), "%m/%d %H:%M")
        message += "\n 現金買入  賣出  即期買入  賣出\n"
        for info in yen_info:
            message += " " + info + "  "
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