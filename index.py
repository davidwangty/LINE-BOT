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

app = Flask(__name__)

line_bot_api = LineBotApi('IwOD34uw9ug6aY6y7G2OC+okmTvLXsyY6VrRl37L41lF/pyCXCrr8lFheBoydFpIpcGPT7xDV8tLyW8iXjnBfkf77GPWlNZpVXStFIz9n2vF2PeezIFlYAEZ2WY9Fx6FWdFJmRasi4bgfdIm6PAzuQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('d71cebb18b3eebb9fc915a1287e9c713')

@app.route("/")
def hello():
    return "Hello World!"

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
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


if __name__ == "__main__":
    app.run()