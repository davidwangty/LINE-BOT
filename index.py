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
import urlparse3
import currency_search
from datetime import datetime
import pytz

# timezone set
tpe = pytz.timezone('Asia/Taipei')

# Database
urlparse3.uses_netloc.append("postgres")
url = urlparse3.urlparse(os.environ["DATABASE_URL"])

conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)

AccessToken = os.environ["ChannelAccessToken"]
ChannelSecret = os.environ["ChannelSecret"]
ChannelID = os.environ["UserID"]

app = Flask(__name__)

line_bot_api = LineBotApi(AccessToken)
handler = WebhookHandler(ChannelSecret)

# Echo功能
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
    if event.message.text == "日幣":
        yen_info = currency_search.yen()
        message = "日幣 " + datetime.strftime(datetime.now(tz=tpe), "%m/%d %H:%M")
        message += "\n 現金買入  賣出  即期買入  賣出\n"
        for info in yen_info:
            message += " " + info + "  "
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=message))
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